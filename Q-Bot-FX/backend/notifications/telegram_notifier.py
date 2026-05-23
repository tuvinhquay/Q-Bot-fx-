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
            LOGGER.info("[TELEGRAM] Sending text alert...")
            payload = {
                "chat_id": self.chat_id,
                "text": message,
                "parse_mode": "HTML"
            }
            response = requests.post(self.base_url, json=payload, timeout=10)
            response.raise_for_status()
            LOGGER.info("[TELEGRAM] Text alert sent successfully")
        except Exception as e:
            LOGGER.warning("[TELEGRAM] Text alert failed: %s", e)

    def send_photo(self, image_path: str, caption: str) -> None:
        url = f"https://api.telegram.org/bot{self.token}/sendPhoto"
        LOGGER.info("[TELEGRAM] Sending photo alert...")
        try:
            with open(image_path, "rb") as img:
                files = {"photo": img}
                data = {"chat_id": self.chat_id, "caption": caption}
                response = requests.post(url, files=files, data=data, timeout=20)
                response.raise_for_status()
            LOGGER.info("[TELEGRAM] Photo alert sent successfully")
        except Exception as error:
            LOGGER.warning("[TELEGRAM] Photo alert failed: %s", error)
