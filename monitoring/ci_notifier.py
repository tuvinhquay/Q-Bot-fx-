import os
import sys
import requests
from datetime import datetime

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")


def send_message(text: str):
    if not BOT_TOKEN or not CHAT_ID:
        print("⚠️ Missing TELEGRAM env variables")
        return

    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

    payload = {
        "chat_id": CHAT_ID,
        "text": text,
        "parse_mode": "HTML"
    }

    requests.post(url, json=payload)


def notify(status: str):
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    if status == "success":
        msg = f"✅ <b>CI MINI PASSED</b>\nTime: {now}"
    else:
        msg = f"❌ <b>CI MINI FAILED</b>\nTime: {now}"

    send_message(msg)


if __name__ == "__main__":
    status = sys.argv[1]
    notify(status)
