"""CI Mini runner for Q-Bot-FX local health + smoke testing."""

from __future__ import annotations

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Any

import requests

# local tests
from test_trade import test_trade
from service_checker import (
    check_backend_api,
    check_trading_api,
    check_telegram,
    check_smoke_trade,
)

BASE_DIR = Path(__file__).resolve().parent
CONFIG_PATH = BASE_DIR / "config.json"
TELEGRAM_API_URL = "https://api.telegram.org/bot{token}/sendMessage"


# ============================================================
# TELEGRAM
# ============================================================

def send_telegram(message: str) -> bool:
    """Send CI report to Telegram if env exists."""
    token = os.getenv("TELEGRAM_BOT_TOKEN") or os.getenv("CI_MINI_TELEGRAM_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID") or os.getenv("CI_MINI_TELEGRAM_CHAT_ID")

    if not token or not chat_id:
        print("⚠️ Telegram env chưa cấu hình → bỏ qua gửi alert.")
        return False

    response = requests.post(
        TELEGRAM_API_URL.format(token=token),
        json={"chat_id": chat_id, "text": message},
        timeout=10,
    )
    response.raise_for_status()
    print("📩 Telegram report sent")
    return True


# ============================================================
# CONFIG HEALTH CHECK (Level 1)
# ============================================================

def load_config() -> dict[str, Any]:
    with CONFIG_PATH.open("r", encoding="utf-8") as f:
        return json.load(f)


def check_service(url: str) -> tuple[bool, str]:
    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            return True, "OK"
        return False, f"HTTP {response.status_code}"
    except Exception as exc:
        return False, str(exc)


# ============================================================
# SERVICE CHECKER (Level 1.5)
# ============================================================

def run_service_checks() -> dict[str, bool]:
    return {
        "backend_api": check_backend_api(),
        "trading_api": check_trading_api(),
        "telegram_bot": check_telegram(),
        "smoke_trade": check_smoke_trade(),
    }


# ============================================================
# REPORT BUILDER
# ============================================================

def build_report(results: list[tuple[str, bool, str]], services: dict[str, bool]) -> tuple[bool, str]:
    all_ok = all(ok for _, ok, _ in results) and all(services.values())

    status_line = "🟢 SYSTEM HEALTHY" if all_ok else "🔴 SYSTEM ERROR"

    report = f"{status_line}\n"
    report += "🧠 CI MINI REPORT\n"
    report += f"⏰ {datetime.now().isoformat(timespec='seconds')}\n\n"

    report += "=== HEALTH CHECK ===\n"
    for name, ok, msg in results:
        report += f"{'✅ PASS' if ok else '❌ FAIL'} — {name}\n{msg}\n"

    report += "\n=== SERVICE CHECKER ===\n"
    for name, ok in services.items():
        report += f"{'✅ PASS' if ok else '❌ FAIL'} — {name}\n"

    return all_ok, report


# ============================================================
# MAIN RUNNER
# ============================================================

def main() -> int:
    print("🚀 Running CI Mini...\n")

    # Level 1: config services
    config = load_config()
    results: list[tuple[str, bool, str]] = []

    for service in config.get("services", {}).values():
        ok, msg = check_service(service["health_url"])
        results.append((service["name"], ok, msg))

    # trade simulation
    trade_cfg = config.get("tests", {}).get("trade_simulation")
    if trade_cfg:
        ok, msg = test_trade(trade_cfg["url"])
        results.append((trade_cfg["name"], ok, msg))

    # Level 1.5: service checker
    services = run_service_checks()

    # build report
    all_ok, report = build_report(results, services)
    print(report)

    # send telegram
    try:
        send_telegram(report)
    except Exception as exc:
        print("❌ Telegram error:", exc)
        all_ok = False

    return 0 if all_ok else 1


if __name__ == "__main__":
    raise SystemExit(main())