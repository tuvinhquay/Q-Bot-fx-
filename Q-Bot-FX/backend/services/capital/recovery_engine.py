"""Recovery risk ladder after loss streaks."""

from __future__ import annotations


def recovery_risk_step(consecutive_losses: int) -> float:
    if consecutive_losses >= 5:
        return 0.3
    if consecutive_losses == 4:
        return 0.4
    if consecutive_losses == 3:
        return 0.5
    if consecutive_losses == 2:
        return 0.6
    return 1.0
