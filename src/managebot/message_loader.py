# managebot/message_tools.py
import json
from pathlib import Path

DATA_PATH = Path(__file__).parent.parent.parent / "data" / "message.json"

def load_messages():
    global _messages
    if _messages is None:
        with open(DATA_PATH, "r", encoding="utf-8") as f:
            _messages = json.load(f)

    return _messages

# 加载消息配置文件，只加载一次
_messages = None

def get_message(key: str) -> str:
    _messages = load_messages()
    return _messages.get(key, f"[消息未配置: {key}]")