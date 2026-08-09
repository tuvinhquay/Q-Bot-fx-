"""Tests for TradeExecutor market order safety and SL/TP handling."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

PROJECT_DIR = Path(__file__).resolve().parents[1]
if str(PROJECT_DIR) not in sys.path:
    sys.path.insert(0, str(PROJECT_DIR))

from backend.execution import trade_executor as trade_executor_module
from backend.execution.trade_executor import TradeExecutor


class DummySymbolInfo:
    volume_min = 0.01
    volume_max = 100.0
    volume_step = 0.01


class DummyTick:
    bid = 1.2000
    ask = 1.2010


class DummyResult:
    def __init__(self, retcode: int, order: int, price_current: float) -> None:
        self.retcode = retcode
        self.order = order
        self.price_current = price_current
        self.comment = "ok"


def test_open_market_order_dry_run_does_not_send(monkeypatch) -> None:
    monkeypatch.setattr(trade_executor_module, "LIVE_TRADING_ENABLED", False)
    monkeypatch.setattr(trade_executor_module.mt5, "symbol_info", lambda symbol: DummySymbolInfo())
    monkeypatch.setattr(trade_executor_module.mt5, "symbol_select", lambda symbol, select: True)
    monkeypatch.setattr(trade_executor_module.mt5, "symbol_info_tick", lambda symbol: DummyTick())

    sent = {"called": False}

    def fake_order_send(request: dict[str, any]) -> None:
        sent["called"] = True
        return None

    monkeypatch.setattr(trade_executor_module.mt5, "order_send", fake_order_send)

    executor = TradeExecutor()
    success, ticket = executor.open_market_order(
        symbol="EURUSDm",
        signal="BUY",
        lot=0.01,
        stop_loss=1.1900,
        take_profit=1.2100,
    )

    assert success is False
    assert ticket is None
    assert sent["called"] is False


def test_open_market_order_includes_sl_tp_in_request(monkeypatch) -> None:
    monkeypatch.setattr(trade_executor_module, "LIVE_TRADING_ENABLED", True)
    monkeypatch.setattr(trade_executor_module.mt5, "symbol_info", lambda symbol: DummySymbolInfo())
    monkeypatch.setattr(trade_executor_module.mt5, "symbol_select", lambda symbol, select: True)
    monkeypatch.setattr(trade_executor_module.mt5, "symbol_info_tick", lambda symbol: DummyTick())

    captured_request: dict[str, Any] = {}

    def fake_order_send(request: dict[str, Any]) -> DummyResult:
        captured_request.update(request)
        return DummyResult(
            retcode=trade_executor_module.mt5.TRADE_RETCODE_DONE,
            order=123,
            price_current=1.2010,
        )

    monkeypatch.setattr(trade_executor_module.mt5, "order_send", fake_order_send)

    executor = TradeExecutor()
    success, ticket = executor.open_market_order(
        symbol="EURUSDm",
        signal="BUY",
        lot=0.01,
        stop_loss=1.1900,
        take_profit=1.2100,
    )

    assert success is True
    assert ticket == 123
    assert captured_request["sl"] == 1.1900
    assert captured_request["tp"] == 1.2100
    assert captured_request["volume"] == 0.01
    assert captured_request["type"] == trade_executor_module.mt5.ORDER_TYPE_BUY
