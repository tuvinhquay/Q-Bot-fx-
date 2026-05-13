"""CI Mini Level 1.5 runner for detailed local system monitoring."""

from __future__ import annotations

import os
from datetime import datetime

import requests

from service_checker import (
    check_backend_api,
    check_smoke_trade,
    check_telegram,
    check_trading_api,
)

TELEGRAM_API_URL = "https://api.telegram.org/bot{token}/sendMessage"
REPORT_LABELS = {
    "backend_api": "Backend API",
    "trading_api": "Trading API",
    "telegram": "Telegram",
    "smoke_trade": "Smoke Trade",
}


def send_telegram_message(message: str) -> bool:
    """Send the detailed CI Mini report to Telegram when credentials exist."""
    token = os.getenv("TELEGRAM_BOT_TOKEN") or os.getenv("CI_MINI_TELEGRAM_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID") or os.getenv("CI_MINI_TELEGRAM_CHAT_ID")

    if not token or not chat_id:
        print("Telegram env not set. Skip alert.")
        return False

    response = requests.post(
        TELEGRAM_API_URL.format(token=token),
        json={"chat_id": chat_id, "text": message},
        timeout=10,
    )
    response.raise_for_status()
    print("Telegram CI Mini report sent")
    return True


def run_checks() -> dict[str, bool]:
    """Run each CI Mini service checker and return per-service results."""
    return {
        "backend_api": check_backend_api(),
        "trading_api": check_trading_api(),
        "telegram": check_telegram(),
        "smoke_trade": check_smoke_trade(),
    }


def build_report(results: dict[str, bool]) -> str:
    """Build the detailed CI Mini Telegram report."""
    lines = [
        "CI MINI REPORT",
        f"Time: {datetime.now().isoformat(timespec='seconds')}",
        "",
    ]

    for key, label in REPORT_LABELS.items():
        status = "OK" if results.get(key, False) else "FAIL"
        lines.append(f"{label}: {status}")

    system_status = "HEALTHY" if all(results.values()) else "ERROR"
    lines.extend(["", f"SYSTEM STATUS: {system_status}"])
    return "\n".join(lines)


def main() -> int:
    """Run detailed monitoring checks, print the report, and notify Telegram."""
    results = run_checks()
    report = build_report(results)
    print(report)

    try:
        send_telegram_message(report)
    except requests.RequestException as exc:
        print(f"Telegram error: {exc}")
        results["telegram_send"] = False

    return 0 if all(results.values()) else 1


if __name__ == "__main__":
    raise SystemExit(main())
