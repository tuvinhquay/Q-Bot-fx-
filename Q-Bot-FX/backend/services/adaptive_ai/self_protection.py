"""Adaptive self-protection rules."""

from __future__ import annotations


def evaluate_self_protection(
    *,
    adaptive_confidence: float,
    market_danger_score: float,
    survival_mode: bool,
    loss_streak: int,
) -> dict[str, object]:
    cooldown = loss_streak >= 5 or market_danger_score >= 85
    should_block = adaptive_confidence < 40 or cooldown or (survival_mode and loss_streak >= 3)
    risk_multiplier = 0.6 if should_block else 0.8 if survival_mode else 1.0
    status = "COOLDOWN" if cooldown else "PROTECTED" if survival_mode else "STABLE"
    return {
        "should_block_trade": should_block,
        "risk_multiplier": risk_multiplier,
        "adaptive_status": status,
    }
