// =======================================================
// ✅ FB Live Auto Comment - Final Version
// =======================================================

console.log("✅ FB Live Finder loaded");

// ===============================
// 🔧 使用者固定設定區
// ===============================

// ⚠️ exe 會打開這個網址（Extension 只負責自動化）
const TARGET_LIVE_URL =
  "https://www.facebook.com/watch/live/?v=XXXXXXXX";

// ✅ 要送出的固定留言內容
const AUTO_COMMENT = "請問現在有優惠嗎";

// ✅ 等待直播頁穩定後再留言（毫秒）
const COMMENT_DELAY = 5000;

// ===============================
// 🔴 自動尋找並點擊直播
// ===============================

function findAndClickLive() {
  const cards = Array.from(
    document.querySelectorAll('a[href*="/videos/"]')
  );

  if (cards.length === 0) {
    console.warn("❌ 尚未載入影片卡片");
    return false;
  }

  // 1️⃣ 優先尋找「直播」影片
  for (const a of cards) {
    const href = a.href;

    if (
      href.includes("comment_id") ||
      href.includes("notif") ||
      href.includes("/watch/?")
    ) continue;

    const card = a.closest("div");
    if (!card) continue;

    const isLive =
      card.innerText.includes("直播") ||
      card.innerText.includes("LIVE");

    if (isLive) {
      console.log("🔴 點擊直播：", href);
      a.click();
      return true;
    }
  }

  // 2️⃣ 找不到直播 → 點第一個影片作為 fallback
  const fallback = cards.find(
    a =>
      !a.href.includes("comment_id") &&
      !a.href.includes("notif") &&
      a.href.includes("/videos/")
  );

  if (fallback) {
    console.log("⚠️ 無直播標籤，使用 fallback：", fallback.href);
    fallback.click();
    return true;
  }

  return false;
}

// ===============================
// 🔁 穩定版 Retry 機制
// ===============================

let triedCount = 0;
const MAX_TRY = 15;

const observer = new MutationObserver(() => {
  if (triedCount >= MAX_TRY) {
    console.warn("❌ 多次嘗試仍未找到直播，停止偵測");
    observer.disconnect();
    return;
  }

  const success = findAndClickLive();

  if (success) {
    console.log("✅ 成功進入直播頁");
    observer.disconnect();
  } else {
    triedCount++;
    console.log(`⏳ 重試中... (${triedCount}/${MAX_TRY})`);
  }
});

observer.observe(document.body, {
  childList: true,
  subtree: true
});

// ===============================
// 💬 自動留言功能
// ===============================

let commentSent = false;

function postComment(text) {
  const box = document.querySelector('[role="textbox"]');

  if (!box) {
    console.warn("❌ 找不到留言輸入框");
    return;
  }

  box.focus();

  // 模擬真人輸入
  document.execCommand("insertText", false, text);

  // 模擬 Enter 鍵送出
  setTimeout(() => {
    box.dispatchEvent(
      new KeyboardEvent("keydown", {
        bubbles: true,
        cancelable: true,
        key: "Enter",
        code: "Enter",
        keyCode: 13,
        which: 13
      })
    );

    console.log("✅ 留言已送出：", text);
  }, 300);
}

// ===============================
// ⏱ 等直播頁穩定後送出留言
// ===============================

setTimeout(() => {
  if (!commentSent) {
    postComment(AUTO_COMMENT);
    commentSent = true;
  }
}, COMMENT_DELAY);
