"""
Tests for CI Mini report builder (Prompt 13 version)
Compatible with new build_report(results, services)
"""

from ci_mini.ci_runner import build_report


# ============================================================
# HELPER DATA
# ============================================================


def sample_success_results():
    return [
        ("Bot Telegram", True, "OK"),
        ("Backend API", True, "OK"),
        ("Python Trading Engine", True, "OK"),
        ("Trading Simulation", True, "OK"),
    ]


def sample_fail_results():
    return [
        ("Bot Telegram", False, "Connection error"),
        ("Backend API", True, "OK"),
    ]


def all_services_ok():
    return {
        "backend_api": True,
        "trading_api": True,
        "telegram_bot": True,
        "smoke_trade": True,
    }


def some_services_fail():
    return {
        "backend_api": False,
        "trading_api": True,
        "telegram_bot": True,
        "smoke_trade": False,
    }


# ============================================================
# TESTS
# ============================================================


def test_report_all_ok():
    """System should be HEALTHY when everything passes"""
    results = sample_success_results()
    services = all_services_ok()

    ok, report = build_report(results, services)

    assert ok is True
    assert "HỆ THỐNG HOẠT ĐỘNG ỔN ĐỊNH" in report
    assert "✅ HOẠT ĐỘNG — Bot Telegram" in report
    assert "✅ HOẠT ĐỘNG — backend_api" in report


def test_report_health_check_fail():
    """System should be ERROR when health check fails"""
    results = sample_fail_results()
    services = all_services_ok()

    ok, report = build_report(results, services)

    assert ok is False
    assert "PHÁT HIỆN LỖI HỆ THỐNG" in report
    assert "❌ LỖI — Bot Telegram" in report


def test_report_service_fail():
    """System should be ERROR when service checker fails"""
    results = sample_success_results()
    services = some_services_fail()

    ok, report = build_report(results, services)

    assert ok is False
    assert "PHÁT HIỆN LỖI HỆ THỐNG" in report
    assert "❌ LỖI — backend_api" in report
    assert "❌ LỖI — smoke_trade" in report


def test_report_contains_timestamp():
    """Report must contain timestamp"""
    results = sample_success_results()
    services = all_services_ok()

    ok, report = build_report(results, services)

    assert "⏰" in report


def test_report_contains_sections():
    """Report must contain both sections"""
    results = sample_success_results()
    services = all_services_ok()

    ok, report = build_report(results, services)

    assert "KIỂM TRA SỨC KHỎE HỆ THỐNG" in report
    assert "KIỂM TRA DỊCH VỤ" in report
