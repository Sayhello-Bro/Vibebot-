打包的指令
pyinstaller --noconfirm --onefile --console --name stt_worker --distpath ..\release --add-data "speech_contexts;speech_contexts" --add-data "service_account.json;." WASAPI_test.py

# 🎧 即時語音辨識（Google Streaming STT + Stereo Mix）

本專案是一個基於 **Google Cloud Speech-to-Text** 的即時語音辨識系統，  
主要用於 **直播帶貨 / 商品語音分析**，可即時：

- 辨識中文（zh-TW）
- 套用商品語境（Speech Context）
- 偵測意圖（下單、顏色、尺寸、材質等）
- 修正常見同音誤判
- 將結果輸出為 `.jsonl` 紀錄檔

---

## 🖥 系統需求（非常重要）

- ✅ **Windows 10 / 11**
- ❌ 不支援 macOS / Linux（因為使用 Stereo Mix）
- Python  (我是3.13.2 其他版本我不確定)
- 有網路（Google STT）

---

## 🔊 音訊來源需求

本程式使用 **Stereo Mix（立體聲混音）** 來擷取「系統播放的聲音」。

請先確認你的電腦有支援：

1. 右鍵點擊音量圖示 →「聲音設定」
2. 進入「錄音裝置」
3. 啟用：
   - `Stereo Mix` 或
   - `立體聲混音`

⚠️ 若你的電腦沒有 Stereo Mix，此版本程式將無法執行。

---

## 📁 專案結構

請確保資料夾結構如下：

stt_project/
│
├─ WASAPI_test.py
├─ requirements.txt
├─ README.md
│如果有其他鬼東西應該不重要
└─ speech_contexts/
└─ clothing/
├─ base_context.json
├─ color_context.json
├─ fabric_context.json
├─ size_context.json
└─ style_context.json


⚠️ **路徑不可更改，否則 Speech Context 會載入失敗**

---

## 🔑 Google Cloud 憑證設定（必要）

本程式使用 Google Cloud Speech-to-Text API，  
**每台電腦都必須設定 Service Account 憑證**。

### 步驟 1：準備金鑰
請向專案負責人索取一個 `.json` 憑證檔案，例如：

---

### 步驟 2：設定環境變數（推薦做法）

#### Windows（CMD）

```bat
setx GOOGLE_APPLICATION_CREDENTIALS "C:\完整路徑\service_account.json"


📦 安裝套件

在專案資料夾中執行：

pip install -r requirements.txt

▶️ 執行程式
python main.py


若成功，你會看到類似輸出：

✅ 商品模式：clothing
🔹 載入 context：['base_context', 'color_context', ...]
✅ 使用裝置：Stereo Mix
🎧 開始錄音（Ctrl+C 結束）

📝 輸出檔案說明
1️⃣ stt_annotated_output.jsonl

每一句完整語音辨識結果，包含：

原始文字

修正後文字

Intent（主要 / 次要）

Entities（顏色、尺寸、材質等）

同音字修正紀錄

2️⃣ misrecognition_stats.txt

用於統計常見誤判詞彙（若有啟用）

⚠️ 常見問題
Q1：找不到 Stereo Mix？

音效卡或驅動不支援

USB 音效卡通常沒有

Q2：程式會不定期顯示 Streaming 重啟？

正常現象

Google Streaming STT 最長約 305 秒

程式已自動在 280 秒內重啟

Q3：沒有任何辨識結果？

系統目前沒有播放聲音

Stereo Mix 抓的是「系統輸出」

⛔ 結束程式

按下：

Ctrl + C


程式會正常結束並關閉檔案。