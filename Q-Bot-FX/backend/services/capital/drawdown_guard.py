"""Drawdown guard utilities."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class DrawdownStatus:
    level: str
    message: str


def classify_drawdown(
    daily_drawdown_pct: float,
    weekly_drawdown_pct: float,
    floating_drawdown_pct: float,
    warning_threshold: float = -3.0,
    danger_threshold: float = -5.0,
    emergency_threshold: float = -8.0,
) -> DrawdownStatus:
    worst = min(daily_drawdown_pct, weekly_drawdown_pct, floating_drawdown_pct)
    if worst <= emergency_threshold:
        return DrawdownStatus("EMERGENCY", "Drawdown vuot nguong khan cap")
    if worst <= danger_threshold:
        return DrawdownStatus("DANGER", "Drawdown dang cao, can phong thu")
    if worst <= warning_threshold:
        return DrawdownStatus("WARNING", "Drawdown dang tang, can than trong")
    return DrawdownStatus("SAFE", "Drawdown dang on dinh")
