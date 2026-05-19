import logging

import requests

from config.settings import Settings

LOGGER = logging.getLogger(__name__)


class TelegramNotifier:
    def __init__(self, settings: Settings):
        self.token = settings.TELEGRAM_BOT_TOKEN
        self.chat_id = settings.TELEGRAM_CHAT_ID
        self.base_url = f"https://api.telegram.org/bot{self.token}/sendMessage"

    def send(self, message: str):
        try:
            payload = {
                "chat_id": self.chat_id,
                "text": message,
                "parse_mode": "HTML"
            }
            requests.post(self.base_url, json=payload, timeout=10)
            LOGGER.info("Telegram alert sent.")
        except Exception as e:
            LOGGER.warning(f"Telegram send failed: {e}")

    def send_photo(self, image_path: str, caption: str) -> None:
        url = f"https://api.telegram.org/bot{self.token}/sendPhoto"

        with open(image_path, "rb") as img:
            files = {"photo": img}
            data = {"chat_id": self.chat_id, "caption": caption}
            requests.post(url, files=files, data=data)
