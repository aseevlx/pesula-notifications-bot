from collections import defaultdict
from datetime import datetime
from time import sleep
from zoneinfo import ZoneInfo
import logging
from typing import Iterable

import requests

from api_handler import NortecApiWrapper, Message
import config

logging.basicConfig(level=logging.INFO, format="[%(asctime)s] %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)
db = config.db


def get_new_messages(api: NortecApiWrapper) -> list[Message]:
    """
    Fetch new messages from the Nortec API and persist them to the DB.

    Returns only messages that have not been seen before.
    """
    all_messages = api.get_messages()
    db_messages: dict[str, Message] = db.get("messages", {})
    new_messages: list[Message] = []

    for message in all_messages:
        if message.Name not in db_messages:
            db_messages[message.Name] = message
            new_messages.append(message)

    db["messages"] = db_messages
    return new_messages


def parse_messages(messages: Iterable[Message]) -> dict[str, dict[str, str]]:
    """
    Parse raw Nortec messages into an internal representation with status and message text.
    """
    message_data: dict[str, dict[str, str]] = defaultdict(lambda: {"status": "", "message": ""})

    for message in messages:
        logger.info("Processing %s", message.Name)
        for row in message.Rows:
            if row.Columns2.Type == 11:
                match row.Columns2.Cells[0]:
                    case "Færdig":
                        message_data[message.Name]["status"] = "Done"
                    case "Booking":
                        message_data[message.Name]["status"] = "Booking"
                continue

            if row.Columns2.Type == 12:
                data = row.Columns2.Cells[0]
                if "Vaskemaskine" in data:
                    start = data.find("Vaskemaskine")
                    washing_machine = data[start:].split(",")[0]
                    message_data[message.Name]["message"] = f"Washing machine {washing_machine[-1]}"
                elif "Tørretumbler" in data:
                    start = data.find("Tørretumbler")
                    dryer = data[start:].split(",")[0]
                    message_data[message.Name]["message"] = f"Dryer {dryer[-1]}"

    return message_data


def build_notifications(messages: Iterable[Message]) -> list[str]:
    """
    Convert raw Nortec messages into human-readable notification strings.
    """
    parsed = parse_messages(messages)
    notifications: list[str] = []

    for data in parsed.values():
        status = data.get("status", "")
        text = data.get("message", "")
        if status and text:
            notifications.append(f"{status}: {text}")

    return notifications


def send_message_to_telegram(message: str, error: bool = False) -> requests.Response:
    """
    Send a message to Telegram. When error=True, send it to the error chat with a prefix.
    """
    payload = {"chat_id": config.tg_chat_id, "text": message}
    if error:
        payload["chat_id"] = config.tg_error_chat_id
        payload["text"] = f"Pesula bot error: {message}"

    response = requests.get(f"{config.tg_base_url}/sendMessage", params=payload)
    logger.info("Telegram response status: %s", response.status_code)
    return response


def are_working_hours() -> bool:
    """
    Check current time in Helsinki against configured working hours.
    """
    current_hour = int(datetime.now(tz=ZoneInfo("Europe/Helsinki")).strftime("%H"))
    return config.WORKING_HOURS_START <= current_hour < config.WORKING_HOURS_END


def run_iteration(api: NortecApiWrapper, poll_interval: int) -> tuple[int, bool]:
    """
    Execute a single polling iteration.

    Returns:
        next_poll_interval: Interval to use for the next iteration.
        should_sleep_outside_hours: True if we are outside working hours and the caller
            should sleep using SLEEP_OUTSIDE_WORKING_HOURS_SEC instead of next_poll_interval.
    """
    # update session in the db
    db["session"] = api.session

    if not are_working_hours():
        logger.info(
            "Right now the laundry room is not working, next check in %s seconds",
            config.SLEEP_OUTSIDE_WORKING_HOURS_SEC,
        )
        return poll_interval, True

    new_messages = get_new_messages(api)
    if new_messages:
        notifications = build_notifications(new_messages)
        for notification in notifications:
            send_message_to_telegram(notification)
        next_interval = config.POLL_INTERVAL_SEC
    else:
        next_interval = min(poll_interval * 2, config.MAX_POLL_INTERVAL_SEC)

    return next_interval, False


def main():
    api = NortecApiWrapper(
        session=db.get("session"),
        username=config.api_username,
        password=config.api_password,
    )

    poll_interval = config.POLL_INTERVAL_SEC

    while True:
        poll_interval, should_sleep_outside_hours = run_iteration(api, poll_interval)

        if should_sleep_outside_hours:
            sleep_seconds = config.SLEEP_OUTSIDE_WORKING_HOURS_SEC
        else:
            sleep_seconds = poll_interval

        logger.info("Sleeping for %s seconds", sleep_seconds)
        sleep(sleep_seconds)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("Interrupted by user")
        exit(0)
    except Exception as e:
        send_message_to_telegram(f"Error: {e}", error=True)
        exit(1)
