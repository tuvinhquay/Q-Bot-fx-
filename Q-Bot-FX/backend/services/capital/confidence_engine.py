"""Confidence engine from learning memory and market conditions."""

from __future__ import annotations

from typing import Any


def compute_confidence_scores(
    recent_entries: list[dict[str, Any]],
    regime: str,
    volatility_score: float,
) -> dict[str, float]:
    if not recent_entries:
        return {
            "confidence_score": 50.0,
            "emotional_risk_score": 50.0,
            "market_danger_score": min(max(volatility_score * 100.0, 0.0), 100.0),
        }

    recent = recent_entries[-20:]
    wins = sum(1 for x in recent if str(x.get("trade_result", "")).upper() == "WIN")
    losses = sum(1 for x in recent if str(x.get("trade_result", "")).upper() == "LOSS")
    total = max(len(recent), 1)
    win_rate = wins / total
    loss_rate = losses / total

    regime_rows = [x for x in recent_entries if str(x.get("market_regime", "")).upper() == regime.upper()]
    regime_pnl = sum(float(x.get("pnl", 0) or 0) for x in regime_rows[-10:]) if regime_rows else 0.0

    confidence = 40.0 + (win_rate * 50.0) + (5.0 if regime_pnl > 0 else -5.0)
    confidence = min(max(confidence, 5.0), 95.0)
    emotional_risk = min(max((loss_rate * 100.0) + (15.0 if losses >= 3 else 0.0), 0.0), 100.0)
    market_danger = min(max((volatility_score * 100.0) + (10.0 if regime_pnl < 0 else 0.0), 0.0), 100.0)

    return {
        "confidence_score": round(confidence, 2),
        "emotional_risk_score": round(emotional_risk, 2),
        "market_danger_score": round(market_danger, 2),
    }
