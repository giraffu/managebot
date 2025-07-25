from telethon.sync import TelegramClient
import config

proxy = ('socks5', '127.0.0.1', 10808)

with TelegramClient('session_test', config.TELETHON_API_ID, config.TELETHON_API_HASH, proxy=proxy) as client:
    me = client.get_me()
    print(me.stringify())
