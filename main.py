import email
import imaplib
import os
from datetime import datetime
from email.header import decode_header
from time import sleep
from typing import Optional
from zoneinfo import ZoneInfo

import requests


EMAIL_USERNAME = os.getenv("EMAIL_USERNAME")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
IMAP_SERVER = os.getenv("IMAP_SERVER")
TG_BOT_TOKEN = os.getenv("TG_BOT_TOKEN")
TG_CHAT_ID = os.getenv("TG_CHAT_ID")
TG_ERROR_CHAT_ID = os.getenv("TG_ERROR_CHAT_ID")

TG_BASE_URL = f"https://api.telegram.org/bot{TG_BOT_TOKEN}"


def get_new_emails(connection: imaplib.IMAP4_SSL) -> Optional[list]:
    """
    Fetching unread messages from INBOX
    """
    connection.select("INBOX")
    status, messages = connection.search(None, '(UNSEEN)')

    if status != 'OK':
        raise ConnectionError("Error fetching new messages")

    if messages == [b'']:
        return None

    message_numbers = str(messages[0].decode()).split(' ')[::-1]
    return message_numbers


def search_for_pesula_messages(connection: imaplib.IMAP4_SSL, message_numbers: list):
    for message_number in message_numbers:
        print(f'Processing: {message_number}')

        res, msg = connection.fetch(str(message_number), "(RFC822)")
        for response in msg:
            if not isinstance(response, tuple):
                continue

            msg = email.message_from_bytes(response[1])
            subject, encoding = decode_header(msg["Subject"])[0]
            if isinstance(subject, bytes):
                # if it's a bytes, decode to str
                subject = subject.decode(encoding)

            if "Færdig" not in subject:
                continue

            if not msg.is_multipart():
                continue

            for part in msg.walk():
                content_type = part.get_content_type()
                content_disposition = str(part.get("Content-Disposition"))

                try:
                    # get the email body
                    body = part.get_payload(decode=True).decode()
                except:
                    continue

                if content_type == "text/plain" and "attachment" not in content_disposition:
                    if "Vaskemaskine" in body:
                        start = body.find("Vaskemaskine")
                        washing_machine = body[start:].split(",")[0]
                        msg = f"Washing machine {washing_machine[-1]} is done"
                        send_message_to_telegram(msg)

                    if "Tørretumbler" in body:
                        start = body.find("Tørretumbler")
                        dryer = body[start:].split(",")[0]
                        msg = f"Dryer {dryer[-1]} is done"
                        send_message_to_telegram(msg)


def send_message_to_telegram(message: str, error: bool = False):
    payload = {'chat_id': TG_CHAT_ID, 'text': message}
    if error:
        payload['chat_id'] = TG_ERROR_CHAT_ID
        payload['text'] = f"Pesula bot error: {message}"
    requests.get(f"{TG_BASE_URL}/sendMessage", params=payload)


def is_working_hours():
    """
    Check current time in Helsinki.
    If it's between 00:00 and 08:00, return False
    """
    current_hour = int(datetime.now(tz=ZoneInfo("Europe/Helsinki")).strftime("%H"))
    if 0 <= current_hour < 8:
        return False
    return True


def main():
    imap = imaplib.IMAP4_SSL(IMAP_SERVER)
    imap.login(EMAIL_USERNAME, EMAIL_PASSWORD)

    while True:
        if not is_working_hours():
            print("Right now the laundry room is not working, sleep for 30 minutes")
            sleep(60 * 30)
            continue

        try:
            messages_numbers = get_new_emails(imap)
        except ConnectionError as e:
            send_message_to_telegram(f"Error fetching new messages: {e}, sleep for 5 minutes", error=True)
            sleep(60 * 5)
            continue

        if messages_numbers is None:
            print("No new messages, sleep for 60 seconds")
            sleep(60)
            continue

        search_for_pesula_messages(imap, messages_numbers)


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("Interrupted by user")
        exit(0)
    except Exception as e:
        send_message_to_telegram(f"Error: {e}", error=True)
        exit(1)
