"""Telegram alert helper for CI Mini health monitoring."""

from __future__ import annotations

import os

import requests

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
        requests.post(url, json=payload, timeout=10)
        print("Telegram alert sent")
    except Exception as e:
        print("Telegram error:", e)
