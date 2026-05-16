"""Tests for the MT5 gateway connector."""

from __future__ import annotations

import sys
from pathlib import Path
from types import SimpleNamespace

PROJECT_DIR = Path(__file__).resolve().parents[1]
if str(PROJECT_DIR) not in sys.path:
    sys.path.insert(0, str(PROJECT_DIR))

from backend.mt5_gateway.mt5_connector import MT5Connector


class FakeMT5:
    """Small fake MetaTrader5 module for connector tests."""

    def __init__(self, initialize_result: bool = True) -> None:
        self.initialize_result = initialize_result
        self.initialize_kwargs = None
        self.shutdown_called = False

    def initialize(self, **kwargs):
        self.initialize_kwargs = kwargs
        return self.initialize_result

    def last_error(self):
        return (1, "fake error")

    def shutdown(self):
        self.shutdown_called = True

    def account_info(self):
        return SimpleNamespace(balance=1000.0, equity=999.0)

    def symbol_info(self, symbol):
        return SimpleNamespace(name=symbol, visible=True)


def test_mt5_connector_connects_with_env_credentials(monkeypatch) -> None:
    """Connector should login with credentials from environment variables."""
    monkeypatch.setenv("MT5_LOGIN", "123456")
    monkeypatch.setenv("MT5_PASSWORD", "demo-password")
    monkeypatch.setenv("MT5_SERVER", "Demo-Server")
    fake_mt5 = FakeMT5()

    connector = MT5Connector(mt5_module=fake_mt5)

    assert connector.connect() is True
    assert connector.connected is True
    assert fake_mt5.initialize_kwargs == {
        "login": 123456,
        "password": "demo-password",
        "server": "Demo-Server",
    }
    assert connector.account_info().equity == 999.0
    assert connector.symbol_info("EURUSD").name == "EURUSD"

    connector.shutdown()
    assert fake_mt5.shutdown_called is True
    assert connector.connected is False


def test_mt5_connector_returns_false_when_login_fails(monkeypatch) -> None:
    """Connector should return False when MT5 initialize/login fails."""
    monkeypatch.setenv("MT5_LOGIN", "123456")
    monkeypatch.setenv("MT5_PASSWORD", "demo-password")
    monkeypatch.setenv("MT5_SERVER", "Demo-Server")
    connector = MT5Connector(mt5_module=FakeMT5(initialize_result=False))

    assert connector.connect() is False
    assert connector.connected is False


def test_mt5_connector_returns_false_for_missing_env(monkeypatch) -> None:
    """Connector should fail safely when credentials are not configured."""
    monkeypatch.delenv("MT5_LOGIN", raising=False)
    monkeypatch.delenv("MT5_PASSWORD", raising=False)
    monkeypatch.delenv("MT5_SERVER", raising=False)

    assert MT5Connector(mt5_module=FakeMT5()).connect() is False
