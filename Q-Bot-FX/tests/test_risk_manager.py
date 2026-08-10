"""Tests for RiskManager position sizing and guard rails."""

from __future__ import annotations

import json
import sys
from datetime import date
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parents[1]
if str(PROJECT_DIR) not in sys.path:
    sys.path.insert(0, str(PROJECT_DIR))

from backend.risk.risk_manager import RiskManager


def test_lot_size_is_positive(monkeypatch, tmp_path) -> None:
    monkeypatch.setenv("RISK_PER_TRADE", "0.01")
    risk = RiskManager(daily_guard_path=tmp_path / "daily_guard.json")

    lot = risk.calculate_lot_size(balance=1000, stop_loss_pips=50)

    assert lot > 0
    assert lot == 0.02


def test_calculate_lot_size_from_price_distance_uses_symbol_parameters(monkeypatch, tmp_path) -> None:
    monkeypatch.setenv("RISK_PER_TRADE", "0.01")

    risk = RiskManager(daily_guard_path=tmp_path / "daily_guard.json")

    monkeypatch.setattr(
        risk,
        "_get_symbol_pip_parameters",
        lambda symbol: (0.0001, 5.0),
    )

    lot = risk.calculate_lot_size_from_price_distance(
        balance=1000,
        entry_price=1.20000,
        stop_loss_price=1.19000,
        symbol="EURUSDm",
    )

    assert lot > 0
    assert lot == 0.02


def test_cannot_exceed_max_open_trades(monkeypatch, tmp_path) -> None:
    monkeypatch.setenv("MAX_OPEN_TRADES", "3")
    risk = RiskManager(daily_guard_path=tmp_path / "daily_guard.json")

    assert risk.can_open_new_trade(2) is True
    assert risk.can_open_new_trade(3) is False


def test_daily_drawdown_over_limit_blocks_trade(monkeypatch, tmp_path) -> None:
    monkeypatch.setenv("MAX_DAILY_DRAWDOWN", "0.05")
    guard_path = tmp_path / "daily_guard.json"
    guard_path.write_text(
        json.dumps(
            {
                "start_balance": 1000,
                "current_balance": 1000,
                "date": date.today().isoformat(),
            }
        ),
        encoding="utf-8",
    )
    risk = RiskManager(daily_guard_path=guard_path)

    assert risk.check_daily_drawdown(949) is False
