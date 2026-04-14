import os
import sounddevice as sd
import numpy as np
import queue
import sys
import json
import datetime
import time
from pathlib import Path
from collections import Counter
from google.cloud import speech
import re

# =======================
# 路徑設定（支援 py / exe）
# =======================
def get_app_dirs():
    if getattr(sys, "frozen", False):
        # exe 執行時：
        # 資源檔從 _MEIPASS 讀
        # 輸出檔寫到 exe 同層
        resource_dir = Path(sys._MEIPASS)
        output_dir = Path(sys.executable).resolve().parent
    else:
        # 直接執行 py 時：
        # 資源與輸出都放在 py 同層
        resource_dir = Path(__file__).resolve().parent
        output_dir = Path(__file__).resolve().parent
    return resource_dir, output_dir

RESOURCE_DIR, OUTPUT_DIR = get_app_dirs()

# =======================
# 商品模式 & Speech Context
# =======================
PRODUCT_MODE = "clothing"
CONTEXT_DIR = RESOURCE_DIR / "speech_contexts" / PRODUCT_MODE

def load_speech_context(path: Path) -> speech.SpeechContext:
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return speech.SpeechContext(
        phrases=data["phrases"],
        boost=data.get("boost", 10.0)
    )

CONTEXTS = {}
for file in CONTEXT_DIR.glob("*.json"):
    CONTEXTS[file.stem] = load_speech_context(file)

SPEECH_CONTEXT_LIST = list(CONTEXTS.values())

print(f"✅ 商品模式：{PRODUCT_MODE}")
print(f"🔹 載入 context：{list(CONTEXTS.keys())}")

# =======================
# Intent Rules
# =======================
INTENT_RULES = {
    "PRODUCT_TRADE_ACTION": CONTEXTS.get("base_context", speech.SpeechContext()).phrases,
    "PRODUCT_COLOR_DESC": CONTEXTS.get("color_context", speech.SpeechContext()).phrases,
    "PRODUCT_MATERIAL": CONTEXTS.get("fabric_context", speech.SpeechContext()).phrases,
    "PRODUCT_SIZE_SPEC": CONTEXTS.get("size_context", speech.SpeechContext()).phrases,
    "PRODUCT_STYLE_DESC": CONTEXTS.get("style_context", speech.SpeechContext()).phrases,
}

def detect_intents(text: str):
    matched = []
    for intent, keywords in INTENT_RULES.items():
        if any(k in text for k in keywords):
            matched.append(intent)
    return matched[0] if matched else "CHAT", matched[1:]

# =======================
# 同音字
# =======================
HOMOPHONE_MAP = {
    "0": ["零", "靈", "鄰"],
    "一": ["醫", "依"],
    "二": ["耳", "而", "兒"],
    "三": ["山", "散", "參"],
    "四": ["死", "絲", "思"],
    "五": ["舞", "伍", "屋"],
    "塊": ["快", "筷", "寬", "會"],
    "件": ["建", "見", "簡", "間"],
    "元": ["院", "願", "遠"],
    "號": ["豪", "浩"],
    "XL": ["叉L", "X L", "ex L"]
}

def resolve_homophones(text: str):
    replaced = []
    for correct, possibles in HOMOPHONE_MAP.items():
        for p in possibles:
            if p in text:
                text = text.replace(p, correct)
                replaced.append((p, correct))
    return text, replaced

def detect_misrecognition(text: str):
    flagged = re.findall(r"\d+|[a-zA-Z]{2,}", text)
    for correct, possibles in HOMOPHONE_MAP.items():
        for p in possibles:
            if p in text:
                flagged.append(p)
    return list(set(flagged))

# =======================
# Entity 抽取
# =======================
def extract_entities(text: str, contexts: dict):
    entities = {
        "trade_action": [],
        "color": [],
        "material": [],
        "size": [],
        "style": []
    }

    if "base_context" in contexts:
        entities["trade_action"] = [p for p in contexts["base_context"].phrases if p in text]
    if "color_context" in contexts:
        entities["color"] = [p for p in contexts["color_context"].phrases if p in text]
    if "fabric_context" in contexts:
        entities["material"] = [p for p in contexts["fabric_context"].phrases if p in text]
    if "size_context" in contexts:
        entities["size"] = [p for p in contexts["size_context"].phrases if p in text]
    if "style_context" in contexts:
        entities["style"] = [p for p in contexts["style_context"].phrases if p in text]

    return entities

# =======================
# 設定
# =======================
INPUT_FS = 44100
TARGET_FS = 16000
CHANNELS = 1
CHUNK_DURATION = 0.35
CHUNK_SIZE = int(INPUT_FS * CHUNK_DURATION)

VOLUME_THRESHOLD = 0.012
SILENCE_GAP_SEC = 1.2
MIN_SENTENCE_LEN = 3
INTERIM_STABLE_SEC = 2.0

STREAMING_LIMIT = 280

LOG_FILE = str(OUTPUT_DIR / "stt_annotated_output.jsonl")
MISREC_LOG_FILE = str(OUTPUT_DIR / "misrecognition_stats.txt")
LIVE_FILE = str(OUTPUT_DIR / "live_transcript.txt")

# =======================
# Google 憑證
# =======================
SERVICE_JSON = RESOURCE_DIR / "service_account.json"
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = str(SERVICE_JSON)

# =======================
# Stereo Mix
# =======================
def find_stereo_mix():
    for i, d in enumerate(sd.query_devices()):
        name = d["name"].lower()
        if ("stereo mix" in name or "立體聲混音" in name) and d["max_input_channels"] > 0:
            return i, d["name"]
    return None, None

device_index, device_name = find_stereo_mix()
if device_index is None:
    print("❌ 找不到 Stereo Mix")
    sys.exit(1)

print(f"✅ 使用裝置：{device_name}")

# =======================
# Resample
# =======================
def resample_numpy(signal, src, dst):
    duration = len(signal) / src
    src_t = np.linspace(0, duration, len(signal), endpoint=False)
    dst_len = int(len(signal) * dst / src)
    dst_t = np.linspace(0, duration, dst_len, endpoint=False)
    return np.interp(dst_t, src_t, signal)

# =======================
# Google STT
# =======================
client = speech.SpeechClient()

config = speech.RecognitionConfig(
    encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
    sample_rate_hertz=TARGET_FS,
    language_code="zh-TW",
    enable_automatic_punctuation=True,
    speech_contexts=SPEECH_CONTEXT_LIST
)

streaming_config = speech.StreamingRecognitionConfig(
    config=config,
    interim_results=True,
)

audio_queue = queue.Queue()

def audio_callback(indata, frames, time_info, status):
    mono = indata.mean(axis=1)
    mono_16k = resample_numpy(mono, INPUT_FS, TARGET_FS)

    mono_16k = mono_16k / 32768.0
    mono_16k = np.clip(mono_16k, -1.0, 1.0)

    rms = np.sqrt(np.mean(mono_16k ** 2))
    if rms < VOLUME_THRESHOLD:
        return

    pcm16 = (mono_16k * 32767).astype(np.int16).tobytes()
    audio_queue.put(pcm16)

def request_generator(start_time):
    while True:
        if time.time() - start_time > STREAMING_LIMIT:
            print("⏱ 重啟 Streaming")
            return
        data = audio_queue.get()
        if data is None:
            return
        yield speech.StreamingRecognizeRequest(audio_content=data)

# =======================
# 儲存函式
# =======================
def save_sentence(log_fp, misrec_counter, text):
    if len(text.strip()) < MIN_SENTENCE_LEN:
        return

    resolved, replaced = resolve_homophones(text)
    flagged = detect_misrecognition(text)

    for f in flagged:
        misrec_counter[f] += 1

    intent, secondary = detect_intents(resolved)
    entities = extract_entities(resolved, CONTEXTS)

    log_fp.write(json.dumps({
        "time": datetime.datetime.now().isoformat(),
        "raw_text": text,
        "resolved_text": resolved,
        "intent": intent,
        "secondary_intents": secondary,
        "entities": entities,
        "misrecognitions": flagged,
        "homophone_resolution": replaced
    }, ensure_ascii=False) + "\n")
    log_fp.flush()

    print(f"\n💾 存檔：{resolved}")

def save_live_text(text: str):
    with open(LIVE_FILE, "w", encoding="utf-8") as f:
        f.write(text)

def normalize_text(text: str) -> str:
    return re.sub(r"\s+", "", text.strip())

# =======================
# 主程式
# =======================
def main():
    print("🎧 開始錄音（Ctrl+C 結束）")
    print(f"📂 資源目錄：{RESOURCE_DIR}")
    print(f"📂 輸出目錄：{OUTPUT_DIR}")
    print(f"📝 LOG_FILE：{LOG_FILE}")
    print(f"📝 LIVE_FILE：{LIVE_FILE}")

    log_fp = open(LOG_FILE, "a", encoding="utf-8")
    misrec_counter = Counter()

    current_sentence = ""
    sentence_confidences = []
    last_final_time = time.time()

    last_interim_text = ""
    last_interim_change_time = time.time()
    last_saved_text = ""

    with sd.InputStream(
        samplerate=INPUT_FS,
        channels=CHANNELS,
        dtype="int16",
        device=device_index,
        blocksize=CHUNK_SIZE,
        callback=audio_callback,
    ):
        while True:
            start_time = time.time()
            requests = request_generator(start_time)
            responses = client.streaming_recognize(streaming_config, requests)

            try:
                for response in responses:
                    for result in response.results:
                        alt = result.alternatives[0]
                        text = alt.transcript.strip()
                        now = time.time()

                        if not text:
                            continue

                        # ✅ 即時文字永遠寫進 live_transcript.txt
                        save_live_text(text)

                        if result.is_final:
                            current_sentence += text
                            last_final_time = now

                            if hasattr(alt, "confidence"):
                                sentence_confidences.append(alt.confidence)

                            print(f"\n📝 {text}")
                            print(f"✅ FINAL: {text}")

                            # ✅ final 立刻存檔
                            if current_sentence != last_saved_text:
                                save_sentence(log_fp, misrec_counter, current_sentence)
                                last_saved_text = current_sentence

                            current_sentence = ""
                            sentence_confidences.clear()
                            last_interim_text = ""
                            last_interim_change_time = now

                        else:
                            print(f"⏳ {text}", end="\r")

                            # interim 有變化就更新時間
                            if text != last_interim_text:
                                last_interim_text = text
                                last_interim_change_time = now

                            normalized_interim = normalize_text(last_interim_text)
                            normalized_saved = normalize_text(last_saved_text)

                            # ✅ interim 穩定 2 秒就存
                            if (
                                last_interim_text
                                and (now - last_interim_change_time) >= INTERIM_STABLE_SEC
                                and len(normalized_interim) >= MIN_SENTENCE_LEN
                                and normalized_interim != normalized_saved
                            ):
                                print(f"\n⌛ STABLE INTERIM: {last_interim_text}")
                                save_sentence(log_fp, misrec_counter, last_interim_text)
                                last_saved_text = last_interim_text
                                last_interim_change_time = now

            except KeyboardInterrupt:
                audio_queue.put(None)
                break
            except Exception as e:
                # ✅ Timeout / Streaming 重啟前，先把最後一段 interim 強制存檔
                if last_interim_text:
                    normalized_interim = normalize_text(last_interim_text)
                    normalized_saved = normalize_text(last_saved_text)

                    if (
                        len(normalized_interim) >= MIN_SENTENCE_LEN
                        and normalized_interim != normalized_saved
                    ):
                        print(f"\n⌛ TIMEOUT SAVE: {last_interim_text}")
                        save_sentence(log_fp, misrec_counter, last_interim_text)
                        last_saved_text = last_interim_text

                print("⚠️ Streaming 重啟：", e)
                continue

    log_fp.close()
    print("✅ 程式正常結束")

# =======================
# exe / subprocess 入口
# =======================
def start_stt():
    main()

if __name__ == "__main__":
    start_stt()