"""Tests for the live demo validation runner."""

from __future__ import annotations

import sys
from pathlib import Path
from types import SimpleNamespace

import pandas as pd

PROJECT_DIR = Path(__file__).resolve().parents[1]
if str(PROJECT_DIR) not in sys.path:
    sys.path.insert(0, str(PROJECT_DIR))

from backend.validation import live_demo_validation as live_validation_module


class DummyLoginResult:
    def __init__(self, success: bool, attempts: int, account_login: int, trade_allowed: bool, error: str | None = None) -> None:
        self.success = success
        self.attempts = attempts
        self.account_login = account_login
        self.trade_allowed = trade_allowed
        self.error = error


class DummySignal:
    action = "BUY"
    sl = 1.1900
    tp = 1.2100
    confidence = 0.85


class DummySymbolInfo:
    pass


class DummyTick:
    bid = 1.2000
    ask = 1.2010


def _setup_env(monkeypatch) -> None:
    monkeypatch.setenv("GEMINI_API_KEY", "test-gemini")
    monkeypatch.setenv("TELEGRAM_BOT_TOKEN", "test-telegram-token")
    monkeypatch.setenv("TELEGRAM_CHAT_ID", "123456789")
    monkeypatch.setenv("MT5_LOGIN", "123456")
    monkeypatch.setenv("MT5_PASSWORD", "testpassword")
    monkeypatch.setenv("MT5_SERVER", "TestServer")
    monkeypatch.setenv("LIVE_TRADING_ENABLED", "false")
    monkeypatch.setenv("TRADING_ENABLED", "true")
    monkeypatch.setenv("EXECUTION_MODE", "TEST")
    monkeypatch.setenv("FORCE_SIGNAL_MODE", "false")


def test_run_live_demo_validation_dry_run(monkeypatch) -> None:
    _setup_env(monkeypatch)
    monkeypatch.setattr(live_validation_module, "check_runtime_environment", lambda root: {"status": "PASS"})
    monkeypatch.setattr(live_validation_module.MT5AutoLoginEngine, "connect", lambda self: DummyLoginResult(True, 1, 123456, True))
    monkeypatch.setattr(live_validation_module.mt5, "terminal_info", lambda: SimpleNamespace(trade_allowed=True))
    monkeypatch.setattr(live_validation_module.mt5, "account_info", lambda: SimpleNamespace(balance=1000.0, equity=1000.0))
    monkeypatch.setattr(live_validation_module.mt5, "symbol_info", lambda symbol: DummySymbolInfo())
    monkeypatch.setattr(live_validation_module.mt5, "symbol_select", lambda symbol, select: True)
    monkeypatch.setattr(live_validation_module.mt5, "symbol_info_tick", lambda symbol: DummyTick())
    monkeypatch.setattr(live_validation_module, "generate_signal", lambda symbol: DummySignal())
    monkeypatch.setattr(live_validation_module.MT5Connector, "connect", lambda self: True)
    monkeypatch.setattr(live_validation_module.MT5Connector, "get_rates", lambda self, symbol, timeframe, n: pd.DataFrame({"close": [1.2000] * 50}))

    result = live_validation_module.run_live_demo_validation(execute_demo_order=False, notify_telegram=False)

    assert result.success is True
    assert result.mt5_connected is True
    assert result.trade_allowed is True
    assert result.signal == "BUY"
    assert result.order_sent is False
    assert result.errors == []
    assert "Signal generator returned HOLD" not in "\n".join(result.warnings)


def test_run_live_demo_validation_execute_requires_live_trading_enabled(monkeypatch) -> None:
    _setup_env(monkeypatch)
    monkeypatch.setenv("LIVE_TRADING_ENABLED", "false")
    monkeypatch.setattr(live_validation_module, "check_runtime_environment", lambda root: {"status": "PASS"})
    monkeypatch.setattr(live_validation_module.MT5AutoLoginEngine, "connect", lambda self: DummyLoginResult(True, 1, 123456, True))
    monkeypatch.setattr(live_validation_module.mt5, "terminal_info", lambda: SimpleNamespace(trade_allowed=True))
    monkeypatch.setattr(live_validation_module.mt5, "account_info", lambda: SimpleNamespace(balance=1000.0, equity=1000.0))
    monkeypatch.setattr(live_validation_module.mt5, "symbol_info", lambda symbol: DummySymbolInfo())
    monkeypatch.setattr(live_validation_module.mt5, "symbol_select", lambda symbol, select: True)
    monkeypatch.setattr(live_validation_module.mt5, "symbol_info_tick", lambda symbol: DummyTick())
    monkeypatch.setattr(live_validation_module, "generate_signal", lambda symbol: DummySignal())
    monkeypatch.setattr(live_validation_module.MT5Connector, "connect", lambda self: True)
    monkeypatch.setattr(live_validation_module.MT5Connector, "get_rates", lambda self, symbol, timeframe, n: pd.DataFrame({"close": [1.2000] * 50}))

    result = live_validation_module.run_live_demo_validation(execute_demo_order=True, notify_telegram=False)

    assert result.success is False
    assert result.order_sent is False
    assert any("Live trading is disabled" in error for error in result.errors)
