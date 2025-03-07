from datetime import datetime
from time import sleep
from zoneinfo import ZoneInfo
from collections import defaultdict

import requests

from api_handler import NortecApiWrapper, Message
import config
import logging

logging.basicConfig(level=logging.INFO, format="[%(asctime)s] %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)
db = config.db


def get_new_messages(api: NortecApiWrapper) -> list[Message] | None:
    """
    Fetching new messages from messages API and storing them in the db
    """
    all_messages = api.get_messages()
    db_messages = db.get("messages", {})
    new_messages = []
    for message in all_messages:
        if message.Name not in db_messages:
            db_messages[message.Name] = message
            new_messages.append(message)

    db["messages"] = db_messages
    return new_messages


def parse_messages(messages: list[Message]) -> dict[str, dict[str, str]]:
    message_data = defaultdict(lambda: {"status": "", "message": ""})
    for message in messages:
        logger.info(f"Processing {message.Name}")
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
                    message_data[message.Name][
                        "message"
                    ] = f"Washing machine {washing_machine[-1]}"
                elif "Tørretumbler" in row.Columns2.Cells[0]:
                    start = data.find("Tørretumbler")
                    dryer = data[start:].split(",")[0]
                    message_data[message.Name]["message"] = f"Dryer {dryer[-1]}"

    return message_data


def send_message_to_telegram(message: str, error: bool = False):
    payload = {"chat_id": config.tg_chat_id, "text": message}
    if error:
        payload["chat_id"] = config.tg_error_chat_id
        payload["text"] = f"Pesula bot error: {message}"
    requests.get(f"{config.tg_base_url}/sendMessage", params=payload)


def are_working_hours():
    """
    Check current time in Helsinki.
    If it's between 00:00 and 08:00, return False
    """
    current_hour = int(datetime.now(tz=ZoneInfo("Europe/Helsinki")).strftime("%H"))
    if 0 <= current_hour < 8:
        return False
    return True


def main():
    api = NortecApiWrapper(
        session=db.get("session"),
        username=config.api_username,
        password=config.api_password,
    )

    while True:
        # update session in the db
        db["session"] = api.session

        if not are_working_hours():
            logger.info("Right now the laundry room is not working, sleep for 30 minutes")
            sleep(60 * 30)
            continue

        new_messages = get_new_messages(api)
        if new_messages:
            parsed_messages = parse_messages(new_messages)
            for message in parsed_messages.values():
                send_message_to_telegram(f"{message['status']}: {message['message']}")

        logger.info("Sleeping for 60 seconds")
        sleep(60)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("Interrupted by user")
        exit(0)
    except Exception as e:
        send_message_to_telegram(f"Error: {e}", error=True)
        exit(1)
