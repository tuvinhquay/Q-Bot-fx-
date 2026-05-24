"""Adaptive confidence adjustment."""

from __future__ import annotations


def adjust_confidence(
    *,
    base_confidence: float,
    in_best_regime: bool,
    survival_mode: bool,
    loss_streak: int,
    volatility_score: float,
) -> float:
    score = base_confidence
    if in_best_regime:
        score += 8
    if survival_mode:
        score -= 15
    score -= min(loss_streak * 4, 20)
    score -= max((volatility_score - 0.5) * 20, 0)
    return round(min(max(score, 5.0), 95.0), 2)
