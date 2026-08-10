"""CI mini tests for Telegram monitoring center."""

from __future__ import annotations

from backend.services.telegram.monitoring_center import build_live_dashboard, build_startup_report, format_alert, handle_monitoring_command


def test_alert_format():
    assert format_alert("INFO", "Bot Online") == "INFO\nBot Online"


def test_command_balance():
    text = handle_monitoring_command("/balance", {"balance": 100})

    assert "100" in text


def test_startup_report_contains_core_fields():
    text = build_startup_report(mt5_state={"status": "CONNECTED"}, account={"balance": 100, "equity": 99})

    assert "Q-BOT-FX ONLINE" in text
    assert "MT5 Connected" in text
    assert "Balance" in text


def test_live_dashboard_contains_monitoring_sections():
    text = build_live_dashboard({"mt5": "CONNECTED", "balance": 100, "equity": 99})

    assert "Q-BOT-FX ONLINE" in text
    assert "SYSTEM" in text
    assert "SERVICES" in text
    assert "ACCOUNT" in text
    assert "MARKET" in text
    assert "SERVER HEALTH" in text
    assert "AI STATUS" in text
    assert "RISK STATUS" in text
    assert "BRAIN STATUS" in text
    assert "Q-BOT READY FOR TRADING" in text


def test_telegram_notifier_import():
    from backend.notifications.telegram_notifier import TelegramNotifier

    assert TelegramNotifier is not None


if __name__ == "__main__":
    test_alert_format()
    test_command_balance()
    test_startup_report_contains_core_fields()
