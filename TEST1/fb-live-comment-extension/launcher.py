import tkinter as tk
from tkinter import messagebox
import subprocess
import os
import sys

def get_base_dir():
    if getattr(sys, "frozen", False):
        return os.path.dirname(os.path.abspath(sys.executable))
    return os.path.dirname(os.path.abspath(__file__))

BASE_DIR = get_base_dir()
STT_EXE = os.path.join(BASE_DIR, "stt_worker.exe")

CHROME_PATH = r"C:\Program Files\Google\Chrome\Application\chrome.exe"

PROFILES = {
    "帳號 A（Default）": "Default",
    "帳號 B（Profile 1）": "Profile 1",
    "帳號 C（Profile 2）": "Profile 2"
}

def start_all():
    url = entry_url.get().strip()
    profile_name = profile_var.get()

    if not url:
        messagebox.showwarning("錯誤", "請輸入直播網址")
        return

    if not url.startswith("http"):
        messagebox.showwarning("錯誤", "請輸入正確網址（需包含 http / https）")
        return

    if not os.path.exists(STT_EXE):
        messagebox.showerror("錯誤", f"找不到 STT 執行檔：\n{STT_EXE}")
        return

    if not os.path.exists(CHROME_PATH):
        messagebox.showerror("錯誤", f"找不到 Chrome：\n{CHROME_PATH}")
        return

    try:
        subprocess.Popen(
            [STT_EXE],
            cwd=BASE_DIR,
            creationflags=subprocess.CREATE_NEW_CONSOLE
        )
    except Exception as e:
        messagebox.showerror("錯誤", f"啟動 STT 失敗：\n{e}")
        return

    try:
        subprocess.Popen([
            CHROME_PATH,
            f'--profile-directory={PROFILES[profile_name]}',
            url
        ])
    except Exception as e:
        messagebox.showerror("錯誤", f"啟動 Chrome 失敗：\n{e}")
        return

root = tk.Tk()
root.title("FB 直播自動留言系統")
root.geometry("500x280")
root.resizable(False, False)

tk.Label(root, text="選擇 Facebook 帳號（Chrome Profile）").pack(pady=5)

profile_var = tk.StringVar(value="帳號 A（Default）")

for name in PROFILES:
    tk.Radiobutton(
        root,
        text=name,
        variable=profile_var,
        value=name
    ).pack(anchor="w", padx=50)

tk.Label(root, text="Facebook 直播網址").pack(pady=5)

entry_url = tk.Entry(root, width=60)
entry_url.pack()

tk.Button(
    root,
    text="開始執行",
    height=2,
    width=20,
    command=start_all
).pack(pady=20)

root.mainloop()