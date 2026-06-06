"""Telegram heartbeat generator."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any

from backend.notifications.telegram_notifier import TelegramNotifier
from backend.services.device.device_health import get_device_health


class HeartbeatEngine:
    def __init__(self, interval_minutes: int = 30) -> None:
        self.interval = timedelta(minutes=interval_minutes)
        self.last_sent: datetime | None = None

    def should_send(self, now: datetime | None = None) -> bool:
        current = now or datetime.now(timezone.utc)
        return self.last_sent is None or current - self.last_sent >= self.interval

    def build_message(self, account: dict[str, Any] | None = None, mt5_status: str = "UNKNOWN") -> str:
        account = account or {}
        device = get_device_health()
        return (
            "BOT HEARTBEAT\n\n"
            f"MT5 Status: {mt5_status}\n"
            f"Balance: {account.get('balance', 'N/A')}\n"
            f"Equity: {account.get('equity', 'N/A')}\n"
            f"CPU: {device.cpu_percent:.2f}%\n"
            f"RAM: {device.ram_percent:.2f}%\n"
            f"Open Trades: {account.get('open_trades', 'N/A')}\n"
            f"Market Status: {account.get('market_status', 'UNKNOWN')}"
        )

    def send_if_due(self, notifier: TelegramNotifier, account: dict[str, Any] | None = None, mt5_status: str = "UNKNOWN") -> bool:
        now = datetime.now(timezone.utc)
        if not self.should_send(now):
            return False
        notifier.send(self.build_message(account, mt5_status))
        self.last_sent = now
        return True
