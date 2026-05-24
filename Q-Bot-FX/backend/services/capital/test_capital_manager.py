"""Standalone test for Prompt 26 smart capital manager."""

from __future__ import annotations

import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[3]
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from backend.services.capital.capital_manager import CapitalManager
from backend.services.learning.memory_store import MemoryStore


def main() -> None:
    test_file = BASE_DIR / "data" / "learning_memory.capital_test.json"
    if test_file.exists():
        test_file.unlink()

    store = MemoryStore(file_path=test_file)
    store.save(
        [
            {"trade_result": "LOSS", "market_regime": "HIGH_VOLATILITY", "pnl": -20, "symbol": "GBPJPYm"},
            {"trade_result": "LOSS", "market_regime": "HIGH_VOLATILITY", "pnl": -18, "symbol": "GBPJPYm"},
            {"trade_result": "LOSS", "market_regime": "HIGH_VOLATILITY", "pnl": -12, "symbol": "EURUSDm"},
            {"trade_result": "WIN", "market_regime": "LOW_VOLATILITY", "pnl": 10, "symbol": "EURUSDm"},
            {"trade_result": "LOSS", "market_regime": "HIGH_VOLATILITY", "pnl": -9, "symbol": "GBPJPYm"},
            {"trade_result": "LOSS", "market_regime": "HIGH_VOLATILITY", "pnl": -7, "symbol": "GBPJPYm"},
        ]
    )

    manager = CapitalManager(memory_store=store)
    state = manager.evaluate(
        base_risk_percent=1.0,
        market_regime="HIGH_VOLATILITY",
        volatility_score=0.82,
        daily_drawdown_pct=-4.2,
        weekly_drawdown_pct=-5.4,
        floating_drawdown_pct=-3.1,
    )

    print("[CAPITAL] state:", state)
    print("[CAPITAL REPORT]\n" + state["capital_report"])

    if test_file.exists():
        test_file.unlink()


if __name__ == "__main__":
    main()
