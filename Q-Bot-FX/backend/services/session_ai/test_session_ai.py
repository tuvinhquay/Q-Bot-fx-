"""Standalone test for Prompt 29 session timing intelligence."""

from __future__ import annotations

import sys
from datetime import datetime, timezone
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[3]
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from backend.services.learning.memory_store import MemoryStore
from backend.services.session_ai.session_detector import detect_session
from backend.services.session_ai.session_memory import infer_best_worst_session
from backend.services.session_ai.spread_guard import evaluate_spread, is_rollover_danger
from backend.services.session_ai.timing_report import build_session_report
from backend.services.session_ai.timing_score import compute_timing_score
from backend.services.session_ai.volatility_trap import detect_volatility_trap


def main() -> None:
    test_file = BASE_DIR / "data" / "learning_memory.session_test.json"
    if test_file.exists():
        test_file.unlink()
    store = MemoryStore(test_file)
    store.save(
        [
            {"session": "LONDON", "pnl": 20},
            {"session": "LONDON", "pnl": 12},
            {"session": "ASIAN", "pnl": -8},
            {"session": "NEW_YORK", "pnl": 5},
        ]
    )

    session_info = detect_session(datetime(2026, 5, 25, 13, 0, tzinfo=timezone.utc))
    spread = evaluate_spread(18)
    trap = {"trap_score": 22.0, "is_trap": False, "message": "Volatility dang tu nhien"}
    timing = compute_timing_score(
        session_name=str(session_info["session"]),
        spread_quality=str(spread["spread_quality"]),
        trap_score=float(trap["trap_score"]),
    )
    memory = infer_best_worst_session(store.load())
    state = {
        **session_info,
        **timing,
        **memory,
        "spread_quality": spread["spread_quality"],
        "trap_score": trap["trap_score"],
        "note": spread["message"],
        "rollover_danger": is_rollover_danger(22),
    }
    print("[SESSION AI] state:", state)
    print("[SESSION AI REPORT]\n" + build_session_report(state))

    # additional call to ensure trap detector never crashes on empty input
    print("[SESSION AI] trap empty:", detect_volatility_trap(None))

    if test_file.exists():
        test_file.unlink()


if __name__ == "__main__":
    main()
