"""CI mini tests for Telegram monitoring center."""

from __future__ import annotations

from backend.services.telegram.monitoring_center import build_startup_report, format_alert, handle_monitoring_command


def test_alert_format():
    assert format_alert("INFO", "Bot Online") == "INFO\nBot Online"


def test_command_balance():
    text = handle_monitoring_command("/balance", {"balance": 100})

    assert "100" in text


def test_startup_report_contains_core_fields():
    text = build_startup_report(mt5_state={"status": "CONNECTED"}, account={"balance": 100, "equity": 99})

    assert "Q-BOT-FX ONLINE" in text
    assert "CONNECTED" in text
    assert "Balance" in text


if __name__ == "__main__":
    test_alert_format()
    test_command_balance()
    test_startup_report_contains_core_fields()
