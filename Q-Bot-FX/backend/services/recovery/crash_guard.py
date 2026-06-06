"""Crash and disconnect guard for infrastructure recovery."""

from __future__ import annotations

import logging
from collections.abc import Callable

from backend.notifications.telegram_notifier import TelegramNotifier
from backend.services.telegram.monitoring_center import ALERT_CRITICAL, ALERT_WARNING, format_alert

LOGGER = logging.getLogger(__name__)


class CrashGuard:
    def __init__(self, notifier: TelegramNotifier | None = None) -> None:
        self.notifier = notifier

    def notify(self, level: str, message: str) -> None:
        LOGGER.warning("%s: %s", level, message)
        if self.notifier:
            self.notifier.send(format_alert(level, message))

    def handle_exception(self, error: Exception, recover: Callable[[], bool] | None = None) -> dict[str, object]:
        self.notify(ALERT_CRITICAL, f"Bot exception detected: {error}")
        recovered = bool(recover()) if recover else False
        return {"error": str(error), "recovered": recovered}

    def handle_mt5_disconnect(self, recover: Callable[[], bool] | None = None) -> dict[str, object]:
        self.notify(ALERT_WARNING, "MT5 disconnected, attempting recovery")
        recovered = bool(recover()) if recover else False
        if not recovered:
            self.notify(ALERT_CRITICAL, "MT5 recovery failed")
        return {"recovered": recovered}
