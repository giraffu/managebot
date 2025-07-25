# managebot/user_status_storage.py
import json
from pathlib import Path

DATA_PATH = Path(__file__).parent.parent.parent / "data" / "user_status.json"

def load_user_status():
    if not DATA_PATH.exists() or DATA_PATH.stat().st_size == 0:
        return {}
    with open(DATA_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

def save_user_status(data: dict):
    with open(DATA_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        