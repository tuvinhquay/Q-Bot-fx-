"""Standalone tests for adaptive AI layer."""

from __future__ import annotations

import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[3]
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from backend.services.adaptive_ai.adaptive_engine import AdaptiveIntelligenceEngine
from backend.services.adaptive_ai.adaptive_report import build_adaptive_report
from backend.services.adaptive_ai.regime_memory import AdaptiveMemoryStore
from backend.services.learning.memory_store import MemoryStore


def main() -> None:
    learning_test = BASE_DIR / "data" / "learning_memory.adaptive_test.json"
    adaptive_test = BASE_DIR / "data" / "adaptive_memory.test.json"
    for p in [learning_test, adaptive_test]:
        if p.exists():
            p.unlink()

    learning_store = MemoryStore(learning_test)
    learning_store.save(
        [
            {"symbol": "EURUSDm", "market_regime": "LOW_VOLATILITY", "trade_result": "WIN", "pnl": 20},
            {"symbol": "EURUSDm", "market_regime": "LOW_VOLATILITY", "trade_result": "WIN", "pnl": 18},
            {"symbol": "GBPJPYm", "market_regime": "HIGH_VOLATILITY", "trade_result": "LOSS", "pnl": -15},
            {"symbol": "GBPJPYm", "market_regime": "HIGH_VOLATILITY", "trade_result": "LOSS", "pnl": -12},
        ]
    )
    engine = AdaptiveIntelligenceEngine(
        learning_store=learning_store,
        adaptive_store=AdaptiveMemoryStore(adaptive_test),
    )
    state = engine.evaluate(
        symbol="EURUSDm",
        market_regime="LOW_VOLATILITY",
        base_confidence=72.0,
        capital_state={"survival_mode": False, "consecutive_losses": 1, "market_danger_score": 30},
        volatility_score=0.35,
    )
    print("[ADAPTIVE AI] state:", state)
    print("[ADAPTIVE REPORT]\n" + build_adaptive_report(state))

    for p in [learning_test, adaptive_test]:
        if p.exists():
            p.unlink()


if __name__ == "__main__":
    main()
