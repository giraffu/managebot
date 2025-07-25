# cspell: disable
import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
TELETHON_API_ID = os.getenv("TELETHON_API_ID")
TELETHON_API_HASH = os.getenv("TELETHON_API_HASH")
GROUP_ID = os.getenv("GROUP_ID")
PHONE = os.getenv("PHONE")
PASSWORD = os.getenv("PASSWORD")