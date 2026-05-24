"""Standalone test mode for Prompt 25 learning layer."""

from __future__ import annotations

import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[3]
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from backend.services.learning.learning_analyzer import analyze_learning
from backend.services.learning.memory_engine import LearningMemoryEngine
from backend.services.learning.memory_store import MemoryStore
from backend.services.learning.performance_tracker import calculate_performance_snapshot


def main() -> None:
    test_file = BASE_DIR / "data" / "learning_memory.test.json"
    if test_file.exists():
        test_file.unlink()

    engine = LearningMemoryEngine(store=MemoryStore(test_file))
    sample_rows = [
        ("EURUSDm", "BUY", "LOW_VOLATILITY", 72, "SAFE", "LOW", "NEUTRAL", "WIN", 25),
        ("GBPJPYm", "BUY", "HIGH_VOLATILITY", 51, "WARNING", "HIGH", "LONG_HEAVY", "LOSS", -30),
        ("GBPJPYm", "BUY", "HIGH_VOLATILITY", 49, "WARNING", "HIGH", "LONG_HEAVY", "LOSS", -22),
        ("GBPJPYm", "SELL", "HIGH_VOLATILITY", 46, "DANGER", "MEDIUM", "SHORT_HEAVY", "LOSS", -18),
        ("EURUSDm", "BUY", "LOW_VOLATILITY", 75, "SAFE", "LOW", "NEUTRAL", "WIN", 19),
    ]
    for row in sample_rows:
        engine.record_trade(
            symbol=row[0],
            signal=row[1],
            market_regime=row[2],
            ai_score=row[3],
            risk_level=row[4],
            correlation_risk=row[5],
            directional_bias=row[6],
            trade_result=row[7],
            pnl=row[8],
            timeframe="H1",
        )

    entries = engine.store.load()
    snapshot = calculate_performance_snapshot(entries)
    analysis = analyze_learning(entries)
    report = engine.build_report()

    print("[LEARNING] Test entries:", len(entries))
    print("[PERFORMANCE] Snapshot:", snapshot)
    print("[LEARNING] Analysis:", analysis)
    print("[LEARNING REPORT]\n" + report)

    if test_file.exists():
        test_file.unlink()


if __name__ == "__main__":
    main()
