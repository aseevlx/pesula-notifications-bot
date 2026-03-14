import os
import shelve
from typing import Iterable


# Persistent storage for session and seen messages
db = shelve.open("storage.db")


# Nortec API credentials
api_username: str | None = os.getenv("API_USERNAME")
api_password: str | None = os.getenv("API_PASSWORD")


# Telegram configuration
tg_bot_token: str | None = os.getenv("TG_BOT_TOKEN")
tg_chat_id: str | None = os.getenv("TG_CHAT_ID")
tg_error_chat_id: str | None = os.getenv("TG_ERROR_CHAT_ID")
tg_base_url: str = f"https://api.telegram.org/bot{tg_bot_token}" if tg_bot_token else ""


def validate_required_env(required_names: Iterable[str] | None = None) -> None:
    """
    Validate that all required environment variables are present.

    Raises:
        RuntimeError: if any required environment variable is missing.
    """
    if required_names is None:
        required_names = ("API_USERNAME", "API_PASSWORD", "TG_BOT_TOKEN", "TG_CHAT_ID")

    current_values = {
        "API_USERNAME": api_username,
        "API_PASSWORD": api_password,
        "TG_BOT_TOKEN": tg_bot_token,
        "TG_CHAT_ID": tg_chat_id,
    }

    missing = [name for name in required_names if not current_values.get(name)]
    if missing:
        raise RuntimeError(f"Missing required environment variables: {', '.join(missing)}")


# Polling configuration for long-running container mode
POLL_INTERVAL_SEC: int = int(os.getenv("POLL_INTERVAL_SEC", "60"))
SLEEP_OUTSIDE_WORKING_HOURS_SEC: int = int(
    os.getenv("SLEEP_OUTSIDE_WORKING_HOURS_SEC", str(60 * 30))
)
WORKING_HOURS_START: int = int(os.getenv("WORKING_HOURS_START", "8"))
WORKING_HOURS_END: int = int(os.getenv("WORKING_HOURS_END", "24"))
MAX_POLL_INTERVAL_SEC: int = int(os.getenv("MAX_POLL_INTERVAL_SEC", "600"))
