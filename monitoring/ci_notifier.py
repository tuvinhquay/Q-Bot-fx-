"""Notify Telegram with the CI Mini result."""

from __future__ import annotations

import sys

from telegram_alert import send_telegram_message


def notify(status: str) -> None:
    """Send a success or failure message for a CI Mini run."""
    if status == "success":
        msg = "✅ <b>CI MINI PASSED</b>\nSystem is healthy."
    else:
        msg = "🚨 <b>CI MINI FAILED</b>\nCheck GitHub Actions immediately!"

    send_telegram_message(msg)


if __name__ == "__main__":
    status = sys.argv[1]
    notify(status)
