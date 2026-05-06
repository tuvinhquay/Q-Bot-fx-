"""Telegram delivery service for Q-Bot-FX."""

from __future__ import annotations

import logging

import requests

LOGGER = logging.getLogger(__name__)


class TelegramService:
    """Send Telegram notifications for executed trades."""

    def __init__(self, bot_token: str, chat_id: str) -> None:
        self.bot_token = bot_token
        self.chat_id = chat_id
        self.endpoint = f"https://api.telegram.org/bot{bot_token}/sendMessage"

    def send_message(self, text: str) -> bool:
        payload = {"chat_id": self.chat_id, "text": text}

        try:
            response = requests.post(self.endpoint, json=payload, timeout=10)
        except requests.RequestException as error:
            LOGGER.error("Telegram send_message failed: %s", error)
            return False

        if not response.ok:
            LOGGER.error("Telegram API error: %s", response.text)
            return False

        LOGGER.info("Telegram message sent successfully.")
        return True
