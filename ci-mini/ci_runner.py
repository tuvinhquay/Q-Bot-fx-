"""CI Mini runner for Q-Bot-FX service health and smoke checks."""

from __future__ import annotations

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Any

import requests

from test_trade import test_trade

BASE_DIR = Path(__file__).resolve().parent
CONFIG_PATH = BASE_DIR / "config.json"
TELEGRAM_API_URL = "https://api.telegram.org/bot{token}/sendMessage"


def send_telegram(message: str) -> bool:
    """Send the CI report to Telegram when credentials are configured."""
    token = os.getenv("TELEGRAM_BOT_TOKEN") or os.getenv("CI_MINI_TELEGRAM_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID") or os.getenv("CI_MINI_TELEGRAM_CHAT_ID")

    if not token or not chat_id:
        print("⚠️ Bỏ qua Telegram: thiếu TELEGRAM_BOT_TOKEN/TELEGRAM_CHAT_ID.")
        return False

    response = requests.post(
        TELEGRAM_API_URL.format(token=token),
        json={"chat_id": chat_id, "text": message},
        timeout=10,
    )
    response.raise_for_status()
    return True


def check_service(url: str) -> tuple[bool, str]:
    """Run a GET health check against one service."""
    try:
        response = requests.get(url, timeout=5)
    except requests.RequestException as exc:
        return False, str(exc)

    if response.status_code == 200:
        return True, "OK"

    return False, f"Lỗi HTTP {response.status_code}: {response.text[:200]}"


def load_config() -> dict[str, Any]:
    """Read the CI Mini JSON configuration file."""
    with CONFIG_PATH.open("r", encoding="utf-8") as config_file:
        return json.load(config_file)


def build_report(results: list[tuple[str, bool, str]]) -> tuple[bool, str]:
    """Build the human-readable CI Mini report."""
    all_ok = all(ok for _, ok, _ in results)
    status_line = (
        "🟢 HỆ THỐNG HOẠT ĐỘNG BÌNH THƯỜNG"
        if all_ok
        else "🔴 PHÁT HIỆN LỖI HỆ THỐNG"
    )

    report = f"{status_line}\n\n"
    report += "🧠 CI MINI REPORT\n"
    report += f"⏰ {datetime.now().isoformat(timespec='seconds')}\n\n"

    for name, ok, message in results:
        status = "✅ PASS" if ok else "❌ FAIL"
        report += f"{status} — {name}\n{message}\n\n"

    return all_ok, report


def main() -> int:
    """Run all configured checks and publish the report."""
    config = load_config()
    results: list[tuple[str, bool, str]] = []

    for service in config.get("services", {}).values():
        ok, message = check_service(service["health_url"])
        results.append((service["name"], ok, message))

    trade_config = config.get("tests", {}).get("trade_simulation")
    if trade_config:
        ok, message = test_trade(trade_config["url"])
        results.append((trade_config["name"], ok, message))

    all_ok, report = build_report(results)
    print(report)

    try:
        send_telegram(report)
    except requests.RequestException as exc:
        print(f"❌ Gửi Telegram thất bại: {exc}")
        all_ok = False

    return 0 if all_ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
