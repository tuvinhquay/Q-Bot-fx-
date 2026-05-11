"""Telegram alert helper for CI Mini health monitoring."""

from __future__ import annotations

import os
import requests
from dotenv import load_dotenv

# 🔥 LOAD FILE .env (rất quan trọng)
load_dotenv()

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")


def send_telegram_message(text: str) -> None:
    """Send an HTML-formatted Telegram message when secrets are configured."""
    
    if not BOT_TOKEN or not CHAT_ID:
        print("Telegram env not set. Skip alert.")
        return

    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

    payload = {
        "chat_id": CHAT_ID,
        "text": text,
        "parse_mode": "HTML",
    }

    try:
        response = requests.post(url, json=payload, timeout=10)

        if response.status_code == 200:
            print("Telegram alert sent ✅")
        else:
            print("Telegram API error:", response.text)

    except Exception as e:
        print("Telegram error:", e)