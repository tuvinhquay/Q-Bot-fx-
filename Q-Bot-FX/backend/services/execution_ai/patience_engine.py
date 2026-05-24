"""Patience decision engine for execution gating."""

from __future__ import annotations


def evaluate_patience(
    *,
    adaptive_score: float,
    timing_score: float,
    trap_score: float,
    spread_quality: str,
    confidence_score: float,
    candle_confirmed: bool,
    loss_streak: int,
    market_danger_score: float,
) -> dict[str, object]:
    score = 0.25 * adaptive_score + 0.25 * timing_score + 0.25 * confidence_score + 0.25 * (100.0 - market_danger_score)
    score -= min(trap_score * 0.3, 25.0)
    score -= min(loss_streak * 6.0, 18.0)

    if spread_quality == "DANGER" or trap_score >= 75:
        return {
            "allow_execution": False,
            "patience_score": round(max(score, 0.0), 2),
            "decision": "BLOCK",
            "reason": "Spread xau hoac fake volatility cao",
        }
    if not candle_confirmed:
        return {
            "allow_execution": False,
            "patience_score": round(max(score, 0.0), 2),
            "decision": "WAIT",
            "reason": "Candle chua confirm",
        }
    if score < 55:
        return {
            "allow_execution": False,
            "patience_score": round(max(score, 0.0), 2),
            "decision": "WAIT",
            "reason": "Patience score thap",
        }
    return {
        "allow_execution": True,
        "patience_score": round(min(max(score, 0.0), 100.0), 2),
        "decision": "EXECUTE",
        "reason": "Timing dep va candle da confirm",
    }
