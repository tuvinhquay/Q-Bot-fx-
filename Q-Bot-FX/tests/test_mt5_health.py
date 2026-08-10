"""Tests for MT5 health checks."""

from __future__ import annotations

import sys
from pathlib import Path
from types import SimpleNamespace

PROJECT_DIR = Path(__file__).resolve().parents[1]
if str(PROJECT_DIR) not in sys.path:
    sys.path.insert(0, str(PROJECT_DIR))

from backend.mt5_gateway import mt5_health


class FakeHealthyConnector:
    shutdown_called = False

    def connect(self):
        return True

    def account_info(self):
        return SimpleNamespace(equity=100.0)

    def shutdown(self):
        self.shutdown_called = True


class FakeZeroEquityConnector(FakeHealthyConnector):
    def account_info(self):
        return SimpleNamespace(equity=0.0)


def test_check_mt5_health_returns_true_for_positive_equity(monkeypatch) -> None:
    """MT5 health should pass when connection works and equity is positive."""
    monkeypatch.setattr(mt5_health, "MT5Connector", FakeHealthyConnector)

    assert mt5_health.check_mt5_health() is True


def test_check_mt5_health_returns_false_for_zero_equity(monkeypatch) -> None:
    """MT5 health should fail when equity is zero or unavailable."""
    monkeypatch.setattr(mt5_health, "MT5Connector", FakeZeroEquityConnector)

    assert mt5_health.check_mt5_health() is False


def test_mt5_health_endpoint_reports_ok(monkeypatch) -> None:
    """FastAPI MT5 health endpoint should expose ok/error status."""
    from backend import health_api

    monkeypatch.setattr(health_api, "check_mt5_health", lambda: True)

    assert health_api.mt5_health()["status"] == "ok"


class FakeTradeMT5:
    TRADE_ACTION_DEAL = 1
    ORDER_TYPE_BUY = 0
    ORDER_TIME_GTC = 0
    ORDER_FILLING_IOC = 1
    TRADE_RETCODE_DONE = 10009

    def initialize(self, **kwargs):
        return True

    def shutdown(self):
        pass

    def last_error(self):
        return (0, "ok")

    def account_info(self):
        return SimpleNamespace(equity=100.0)

    def symbol_info(self, symbol):
        return SimpleNamespace(name=symbol, visible=True)

    def symbol_select(self, symbol, enabled):
        return True

    def symbol_info_tick(self, symbol):
        return SimpleNamespace(ask=1.2345)

    def order_send(self, request):
        self.last_request = request
        return SimpleNamespace(retcode=self.TRADE_RETCODE_DONE, comment="done")


def test_send_test_trade_sends_safe_buy_order(monkeypatch) -> None:
    """Trade test should submit a tiny BUY order with the CI_TEST comment."""
    from backend.mt5_gateway import mt5_trade_test

    from backend.mt5_gateway.mt5_connector import MT5Connector

    fake_mt5 = FakeTradeMT5()
    monkeypatch.setenv("MT5_LOGIN", "123456")
    monkeypatch.setenv("MT5_PASSWORD", "demo-password")
    monkeypatch.setenv("MT5_SERVER", "Demo-Server")
    monkeypatch.setattr(mt5_trade_test, "MT5Connector", lambda: MT5Connector(fake_mt5))

    success, message = mt5_trade_test.send_test_trade("EURUSD")

    assert success is True
    assert "successfully" in message
    assert fake_mt5.last_request["volume"] == 0.01
    assert fake_mt5.last_request["type"] == fake_mt5.ORDER_TYPE_BUY
    assert fake_mt5.last_request["comment"] == "CI_TEST"
