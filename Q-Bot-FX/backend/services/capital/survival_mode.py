"""Survival mode decision engine."""

from __future__ import annotations


def resolve_survival_mode(
    drawdown_level: str,
    consecutive_losses: int,
    volatility_score: float,
) -> tuple[bool, str]:
    if drawdown_level in {"DANGER", "EMERGENCY"}:
        return True, "Drawdown tang manh"
    if consecutive_losses >= 3:
        return True, "Chuoi thua dang lon"
    if volatility_score >= 0.75:
        return True, "Bien dong thi truong qua manh"
    return False, "Thi truong dang on dinh"
