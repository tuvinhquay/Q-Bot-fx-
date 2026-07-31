import logging

import requests

from config.settings import Settings

LOGGER = logging.getLogger(__name__)


class TelegramNotifier:
    def __init__(self, settings: Settings):
        self.token = settings.TELEGRAM_BOT_TOKEN
        self.chat_id = settings.TELEGRAM_CHAT_ID
        self.base_url = f"https://api.telegram.org/bot{self.token}/sendMessage"
        self.edit_url = f"https://api.telegram.org/bot{self.token}/editMessageText"

    def _post(self, url: str, payload: dict[str, object]) -> dict[str, object] | None:
        try:
            response = requests.post(url, json=payload, timeout=10)
            response.raise_for_status()
            data = response.json()
            if isinstance(data, dict):
                return data
        except Exception as error:
            LOGGER.warning("[TELEGRAM] request failed: %s", error)
        return None

    def send(self, message: str):
        try:
            LOGGER.info("[TELEGRAM] Sending text alert...")
            payload = {
                "chat_id": self.chat_id,
                "text": message,
                "parse_mode": "HTML"
            }
            self._post(self.base_url, payload)
            LOGGER.info("[TELEGRAM] Text alert sent successfully")
        except Exception as e:
            LOGGER.warning("[TELEGRAM] Text alert failed: %s", e)

    def send_dashboard_message(self, message: str) -> int | None:
        payload = {
            "chat_id": self.chat_id,
            "text": message,
            "parse_mode": "HTML",
            "disable_web_page_preview": True,
        }
        data = self._post(self.base_url, payload)
        try:
            return int(data["result"]["message_id"]) if data else None
        except Exception:
            return None

    def edit_dashboard_message(self, message_id: int, message: str) -> bool:
        payload = {
            "chat_id": self.chat_id,
            "message_id": message_id,
            "text": message,
            "parse_mode": "HTML",
            "disable_web_page_preview": True,
        }
        return self._post(self.edit_url, payload) is not None

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
