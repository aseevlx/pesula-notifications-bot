import shelve
import os


db = shelve.open("storage.db")

api_username: str = os.getenv("API_USERNAME")
api_password: str = os.getenv("API_PASSWORD")

tg_bot_token: str = os.getenv("TG_BOT_TOKEN")
tg_chat_id: str = os.getenv("TG_CHAT_ID")
tg_error_chat_id = os.getenv("TG_ERROR_CHAT_ID")
tg_base_url = f"https://api.telegram.org/bot{tg_bot_token}"
