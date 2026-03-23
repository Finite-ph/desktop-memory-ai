"""
聊天窗口 - Claude Code风格
"""
import os
import sys
import json
import threading
import requests
from datetime import datetime

MEMORY_PATH = "D:/Claude/memory/"
CHAT_FILE = os.path.join(MEMORY_PATH, "chat_window.md")  # 单独给聊天窗口用
CONFIG_PATH = os.path.join(os.path.dirname(__file__), "config.json")

def load_config():
    try:
        if os.path.exists(CONFIG_PATH):
            with open(CONFIG_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
    except:
        pass
    return {"apiKey": ""}

def save_config(config):
    try:
        with open(CONFIG_PATH, "w", encoding="utf-8") as f:
            json.dump(config, f, ensure_ascii=False, indent=2)
    except:
        pass

def read_memory(filename):
    try:
        file_path = os.path.join(MEMORY_PATH, filename)
        if os.path.exists(file_path):
            with open(file_path, "r", encoding="utf-8") as f:
                return f.read()
    except:
        pass
    return ""

def append_memory(filename, content):
    try:
        file_path = os.path.join(MEMORY_PATH, filename)
        existing = ""
        if os.path.exists(file_path):
            with open(file_path, "r", encoding="utf-8") as f:
                existing = f.read()
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(existing + content)
    except:
        pass

def main():
    import tkinter as tk
    from tkinter import scrolledtext, Entry, Label, Frame, Text

    config = load_config()
    conversation_history = []

    # 加载用户记忆
    profile = read_memory("user_profile.md")
    if profile:
        conversation_history.append({"role": "user", "content": f"用户信息：{profile}"})

    # 加载聊天记录作为上下文
    chat_history = ""
    try:
        if os.path.exists(CHAT_FILE):
            with open(CHAT_FILE, "r", encoding="utf-8") as f:
                chat_history = f.read()
    except:
        pass
    if chat_history:
        conversation_history.append({
            "role": "user",
            "content": f"请阅读以下聊天记录，了解用户的聊天风格和偏好：\n{chat_history}"
        })
        conversation_history.append({
            "role": "assistant",
            "content": "好的，我已经阅读了聊天记录。我会保持之前的聊天风格：随意、不端着、像朋友聊天、有话直说。"
        })

    root = tk.Tk()
    root.title("Claude")
    root.geometry("900x700")
    root.configure(bg="#1a1a1a")

    # 顶部标题栏
    top_frame = Frame(root, bg="#161616", height=40)
    top_frame.pack(fill="x")
    top_frame.pack_propagate(False)

    title_label = Label(top_frame, text="Claude Code", bg="#161616", fg="#ffffff",
                       font=("Consolas", 12, "bold"), padx=15, pady=8)
    title_label.pack(side="left")

    # 主内容区
    main_frame = Frame(root, bg="#1a1a1a")
    main_frame.pack(fill="both", expand=True, padx=10, pady=(10, 0))

    # 消息显示区
    msg_frame = Frame(main_frame, bg="#1a1a1a")
    msg_frame.pack(fill="both", expand=True)

    msg_text = Text(msg_frame, bg="#1a1a1a", fg="#e0e0e0",
                    font=("Consolas", 11), relief="flat", bd=0,
                    wrap="word", state="disabled", spacing1=5, spacing2=3)
    msg_text.pack(fill="both", expand=True, side="left")

    # 滚动条
    scrollbar = tk.Scrollbar(msg_frame, command=msg_text.yview, bg="#333333")
    scrollbar.pack(side="right", fill="y")
    msg_text.config(yscrollcommand=scrollbar.set)

    # 消息样式
    msg_text.tag_config("ai", foreground="#a0a0a0")
    msg_text.tag_config("user", foreground="#60a0ff")
    msg_text.tag_config("system", foreground="#505050")

    def add_message(text, tag="ai"):
        msg_text.config(state="normal")
        msg_text.insert("end", text + "\n\n", tag)
        msg_text.config(state="disabled")
        msg_text.see("end")

    def clear_thinking():
        content = msg_text.get("1.0", "end").rstrip()
        if content.endswith("Thinking...\n\n"):
            content = content[:-12]
            msg_text.delete("1.0", "end")
            if content:
                msg_text.insert("end", content)

    # 底部输入区
    input_area = Frame(root, bg="#1a1a1a", pady=10)
    input_area.pack(fill="x", side="bottom")

    # 输入框
    input_entry = Entry(input_area, bg="#252525", fg="#e0e0e0",
                       font=("Consolas", 12), relief="flat", bd=0,
                       insertbackground="#ffffff")
    input_entry.pack(fill="x", padx=10, ipady=15)

    # API Key提示
    if not config.get("apiKey"):
        add_message("请先设置API Key:\n在输入框上方输入您的Anthropic API Key", "system")

    def call_claude(message):
        nonlocal conversation_history
        if not config.get("apiKey"):
            return {"error": "请先输入API Key"}

        conversation_history.append({"role": "user", "content": message})

        try:
            msgs = [m for m in conversation_history if m.get("role") != "system"]
            payload = {
                "model": "MiniMax-M2.7-highspeed",
                "max_tokens": 1024,
                "messages": msgs
            }

            response = requests.post(
                "https://newapi.hizui.cn/v1/messages",
                headers={
                    "Content-Type": "application/json",
                    "x-api-key": config["apiKey"],
                    "anthropic-version": "2023-06-01",
                    "anthropic-dangerous-direct-browser-access": "true"
                },
                json=payload,
                timeout=60
            )

            if response.status_code == 200:
                data = response.json()
                # 找到text类型的回复
                ai_response = ""
                for item in data.get("content", []):
                    if item.get("type") == "text":
                        ai_response = item.get("text", "")
                        break
                if ai_response:
                    conversation_history.append({"role": "assistant", "content": ai_response})
                    return {"content": ai_response}
                else:
                    return {"error": "No text response found"}
            else:
                return {"error": f"Error: {response.status_code}"}
        except Exception as e:
            return {"error": str(e)}

    def save_conversation(user_msg, ai_msg):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        content = f"\n## {timestamp}\n\nUser: {user_msg}\n\nClaude: {ai_msg}\n"
        try:
            with open(CHAT_FILE, "a", encoding="utf-8") as f:
                f.write(content)
        except:
            pass

    def send_message(text):
        if not text.strip():
            return

        user_text = text

        # 如果是API Key
        if not config.get("apiKey") and user_text.startswith("sk-"):
            config["apiKey"] = user_text
            save_config(config)
            add_message("API Key已设置，现在可以开始对话了", "system")
            input_entry.delete(0, "end")
            return

        add_message(f"> {user_text}", "user")
        input_entry.delete(0, "end")
        add_message("Thinking...", "system")

        def async_send():
            response = call_claude(user_text)
            root.after(0, lambda: on_response(response, user_text))

        threading.Thread(target=async_send, daemon=True).start()

    def on_response(response, user_text):
        clear_thinking()
        if response.get("error"):
            add_message(f"Error: {response['error']}", "system")
        else:
            add_message(response.get("content", ""), "ai")
            save_conversation(user_text, response.get("content", ""))

    def on_enter(event):
        send_message(input_entry.get().strip())

    input_entry.bind("<Return>", on_enter)
    input_entry.focus_set()

    add_message("Hello, I'm Claude. How can I help you today?", "ai")

    root.mainloop()

if __name__ == "__main__":
    main()