"""Standalone test for multi-symbol AI brain."""

from __future__ import annotations

import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[3]
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from backend.services.learning.memory_store import MemoryStore
from backend.services.multi_symbol_ai.portfolio_brain import MultiSymbolPortfolioBrain
from backend.services.multi_symbol_ai.reporting import build_top_setup_report


def main() -> None:
    test_file = BASE_DIR / "data" / "learning_memory.multisymbol_test.json"
    if test_file.exists():
        test_file.unlink()
    store = MemoryStore(test_file)
    store.save(
        [
            {"symbol": "EURUSDm", "trade_result": "WIN", "pnl": 22},
            {"symbol": "EURUSDm", "trade_result": "WIN", "pnl": 18},
            {"symbol": "XAUUSDm", "trade_result": "WIN", "pnl": 9},
            {"symbol": "GBPJPYm", "trade_result": "LOSS", "pnl": -15},
        ]
    )
    brain = MultiSymbolPortfolioBrain(memory_store=store)
    state = brain.evaluate(
        ["EURUSDm", "XAUUSDm", "GBPJPYm"],
        {"EURUSDm": 0.35, "XAUUSDm": 0.55, "GBPJPYm": 0.82},
    )
    print("[MULTI-SYMBOL] state:", state)
    print("[MULTI-SYMBOL REPORT]\n" + build_top_setup_report(state))
    if test_file.exists():
        test_file.unlink()


if __name__ == "__main__":
    main()
