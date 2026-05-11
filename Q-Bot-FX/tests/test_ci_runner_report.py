"""Tests for CI Mini Level 1.5 detailed reports."""

from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
CI_MINI_DIR = REPO_ROOT / "ci-mini"
if str(CI_MINI_DIR) not in sys.path:
    sys.path.insert(0, str(CI_MINI_DIR))

from ci_runner import build_report
from service_checker import check_telegram


def test_build_report_healthy() -> None:
    report = build_report(
        {
            "backend_api": True,
            "trading_api": True,
            "telegram": True,
            "smoke_trade": True,
        }
    )

    assert "Backend API: OK" in report
    assert "Trading API: OK" in report
    assert "Telegram: OK" in report
    assert "Smoke Trade: OK" in report
    assert "SYSTEM STATUS: HEALTHY" in report


def test_build_report_error() -> None:
    report = build_report(
        {
            "backend_api": True,
            "trading_api": False,
            "telegram": True,
            "smoke_trade": False,
        }
    )

    assert "Backend API: OK" in report
    assert "Trading API: FAIL" in report
    assert "Smoke Trade: FAIL" in report
    assert "SYSTEM STATUS: ERROR" in report


def test_check_telegram_uses_env_only(monkeypatch) -> None:
    monkeypatch.setenv("TELEGRAM_BOT_TOKEN", "token")
    monkeypatch.setenv("TELEGRAM_CHAT_ID", "chat")

    assert check_telegram() is True
