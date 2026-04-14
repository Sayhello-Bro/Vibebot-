import tkinter as tk
from tkinter import messagebox
import subprocess
import webbrowser
import os

# ===============================
# 使用者可自行修改的設定
# ===============================

CHROME_PATH = r"C:\Program Files\Google\Chrome\Application\chrome.exe"

PROFILES = {
    "帳號 A（Default）": "Default",
    "帳號 B（Profile 1）": "Profile 1",
    "帳號 C（Profile 2）": "Profile 2"
}

# ===============================
# 開啟 Chrome
# ===============================

def open_live():
    url = entry_url.get().strip()
    profile_name = profile_var.get()

    if not url:
        messagebox.showwarning("錯誤", "請輸入直播網址")
        return

    if profile_name not in PROFILES:
        messagebox.showwarning("錯誤", "請選擇帳號")
        return

    profile_dir = PROFILES[profile_name]

    try:
        subprocess.Popen([
            CHROME_PATH,
            f'--profile-directory={profile_dir}',
            url
        ])
    except Exception as e:
        messagebox.showerror("錯誤", str(e))


# ===============================
# GUI
# ===============================

root = tk.Tk()
root.title("FB 直播自動留言啟動器")
root.geometry("460x260")
root.resizable(False, False)

tk.Label(root, text="選擇 Facebook 帳號（Chrome Profile）").pack(pady=5)

profile_var = tk.StringVar(value="帳號 A（Default）")

for name in PROFILES:
    tk.Radiobutton(
        root,
        text=name,
        variable=profile_var,
        value=name
    ).pack(anchor="w", padx=40)

tk.Label(root, text="直播網址").pack(pady=5)

entry_url = tk.Entry(root, width=55)
entry_url.pack()

tk.Button(root, text="開始執行", height=2, command=open_live).pack(pady=15)

root.mainloop()
