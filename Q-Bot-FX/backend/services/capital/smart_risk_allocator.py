"""Smart allocator for dynamic risk percent."""

from __future__ import annotations


def allocate_smart_risk(
    *,
    base_risk_percent: float,
    confidence_score: float,
    market_danger_score: float,
    survival_mode: bool,
    recovery_risk_percent: float,
    hard_cap_percent: float = 1.5,
) -> float:
    risk = float(base_risk_percent)

    if survival_mode:
        risk = min(risk, 0.5)
    if market_danger_score >= 70:
        risk -= 0.3
    elif confidence_score >= 70 and market_danger_score < 40:
        risk += 0.3

    risk = min(risk, recovery_risk_percent)
    risk = max(risk, 0.2)
    risk = min(risk, hard_cap_percent)
    return round(risk, 2)
