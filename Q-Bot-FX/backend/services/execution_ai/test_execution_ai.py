"""Standalone tests for execution intelligence layer."""

from __future__ import annotations

import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[3]
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

import pandas as pd

from backend.services.execution_ai.candle_confirmation import evaluate_candle_confirmation
from backend.services.execution_ai.entry_optimizer import optimize_entry
from backend.services.execution_ai.execution_cooldown import evaluate_cooldown
from backend.services.execution_ai.execution_report import build_execution_report
from backend.services.execution_ai.fomo_detector import detect_fomo
from backend.services.execution_ai.patience_engine import evaluate_patience


def main() -> None:
    candles = pd.DataFrame(
        [
            {"open": 1.10, "high": 1.11, "low": 1.09, "close": 1.108},
            {"open": 1.108, "high": 1.112, "low": 1.104, "close": 1.111},
            {"open": 1.111, "high": 1.116, "low": 1.109, "close": 1.115},
        ]
    )
    confirm = evaluate_candle_confirmation(candles)
    entry = optimize_entry(entry=1.115, stop_loss=1.110, take_profit=1.128, trap_score=24)
    fomo = detect_fomo(current_price=1.1162, suggested_entry=entry["optimized_entry"], spread_quality="GOOD", trap_score=24)
    cooldown = evaluate_cooldown(loss_streak=2, emotional_risk_score=52, market_danger_score=44)
    patience = evaluate_patience(
        adaptive_score=72,
        timing_score=78,
        trap_score=24,
        spread_quality="GOOD",
        confidence_score=69,
        candle_confirmed=bool(confirm["confirmed"]),
        loss_streak=2,
        market_danger_score=44,
    )
    state = {
        **patience,
        "rr_score": entry["rr_score"],
        "candle_strength": confirm["strength"],
        "fomo_severity": fomo["severity"],
    }
    print("[EXECUTION AI] candle:", confirm)
    print("[EXECUTION AI] entry:", entry)
    print("[EXECUTION AI] fomo:", fomo)
    print("[EXECUTION AI] cooldown:", cooldown)
    print("[EXECUTION AI] patience:", patience)
    print("[EXECUTION AI REPORT]\n" + build_execution_report(state))


if __name__ == "__main__":
    main()
