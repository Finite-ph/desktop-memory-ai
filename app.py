"""
桌面悬浮球AI助手 - 简化版
托盘 + 独立聊天窗口
"""
import os
import sys
import json
import subprocess
import platform
from datetime import datetime

MEMORY_PATH = "D:/Claude/memory/"
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

def get_python_path():
    """获取当前Python解释器路径"""
    return sys.executable

def create_tray_icon():
    """创建托盘图标"""
    from PIL import Image, ImageDraw, ImageFont

    size = 64
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    center = size // 2
    radius = 28
    draw.ellipse([center-radius, center-radius, center+radius, center+radius],
                 fill=(255, 100, 100, 255))
    try:
        font = ImageFont.truetype("arial.ttf", 20)
    except:
        font = ImageFont.load_default()
    draw.text((center - 10, center - 12), "AI", fill=(255, 255, 255, 255), font=font)
    return img

def run_chat_window():
    """运行聊天窗口（独立进程）"""
    chat_script = os.path.join(os.path.dirname(__file__), "chat_window.py")
    subprocess.Popen([get_python_path(), chat_script])

def main():
    import pystray

    config = load_config()

    def show_chat(icon=None, item=None):
        run_chat_window()

    def exit_app(icon=None, item=None):
        icon.stop()
        sys.exit(0)

    icon = pystray.Icon("ai_assistant")
    icon.icon = create_tray_icon()
    icon.title = "AI 助手"
    icon.menu = pystray.Menu(
        pystray.MenuItem("打开聊天", show_chat),
        pystray.MenuItem("退出", exit_app)
    )
    icon.on_left_click = show_chat

    print("AI助手已启动，点击托盘图标打开聊天...")
    icon.run()

if __name__ == "__main__":
    main()