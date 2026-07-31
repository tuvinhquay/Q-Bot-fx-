"""Telegram heartbeat generator."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any

from backend.notifications.telegram_notifier import TelegramNotifier
from backend.services.telegram.monitoring_center import build_live_dashboard


class HeartbeatEngine:
    def __init__(self, interval_seconds: int = 5) -> None:
        self.interval = timedelta(seconds=interval_seconds)
        self.last_sent: datetime | None = None

    def should_send(self, now: datetime | None = None) -> bool:
        current = now or datetime.now(timezone.utc)
        return self.last_sent is None or current - self.last_sent >= self.interval

    def build_message(self, context: dict[str, Any] | None = None) -> str:
        return build_live_dashboard(context)

    def send_if_due(self, notifier: TelegramNotifier, context: dict[str, Any] | None = None) -> bool:
        now = datetime.now(timezone.utc)
        if not self.should_send(now):
            return False
        notifier.send(self.build_message(context))
        self.last_sent = now
        return True
