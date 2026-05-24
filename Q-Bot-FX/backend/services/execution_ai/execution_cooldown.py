"""Execution cooldown logic."""

from __future__ import annotations


def evaluate_cooldown(
    *,
    loss_streak: int,
    emotional_risk_score: float,
    market_danger_score: float,
) -> dict[str, object]:
    active = loss_streak >= 3 or emotional_risk_score >= 75 or market_danger_score >= 80
    remaining = 3 if loss_streak >= 3 else 2 if emotional_risk_score >= 75 else 1 if market_danger_score >= 80 else 0
    reason = "Loss streak danger" if loss_streak >= 3 else "Emotional risk high" if emotional_risk_score >= 75 else "Market danger high" if market_danger_score >= 80 else "Stable"
    return {"cooldown_active": active, "remaining_cycles": remaining, "reason": reason}
