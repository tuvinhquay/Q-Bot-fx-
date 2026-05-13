"""Service-level checks for CI Mini local monitoring."""

from __future__ import annotations

import os

import requests

BACKEND_HEALTH_URL = "http://localhost:3000/api/health"
TRADING_HEALTH_URL = "http://localhost:8000/health"
SMOKE_TRADE_URL = "http://localhost:8000/test-trade"
REQUEST_TIMEOUT_SECONDS = 5


def _check_get(url: str) -> bool:
    """Return True when a GET endpoint responds with HTTP 200."""
    try:
        response = requests.get(url, timeout=REQUEST_TIMEOUT_SECONDS)
    except requests.RequestException as exc:
        print(f"FAIL GET {url}: {exc}")
        return False

    if response.status_code == 200:
        print(f"OK GET {url}")
        return True

    print(f"FAIL GET {url}: HTTP {response.status_code}")
    return False


def check_backend_api() -> bool:
    """Check the NodeJS Backend Health API."""
    return _check_get(BACKEND_HEALTH_URL)


def check_trading_api() -> bool:
    """Check the Python Trading Engine Health API."""
    return _check_get(TRADING_HEALTH_URL)


def check_smoke_trade() -> bool:
    """Run the safe trading smoke-test endpoint."""
    try:
        response = requests.post(SMOKE_TRADE_URL, timeout=REQUEST_TIMEOUT_SECONDS)
    except requests.RequestException as exc:
        print(f"FAIL POST {SMOKE_TRADE_URL}: {exc}")
        return False

    if response.status_code == 200:
        print(f"OK POST {SMOKE_TRADE_URL}")
        return True

    print(f"FAIL POST {SMOKE_TRADE_URL}: HTTP {response.status_code}")
    return False


def check_telegram() -> bool:
    """Check Telegram credentials without sending a real message."""
    token = os.getenv("TELEGRAM_BOT_TOKEN") or os.getenv("CI_MINI_TELEGRAM_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID") or os.getenv("CI_MINI_TELEGRAM_CHAT_ID")

    if token and chat_id:
        print("OK Telegram env configured")
        return True

    print("FAIL Telegram env missing")
    return False
