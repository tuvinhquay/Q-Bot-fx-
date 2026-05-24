"""Spread and rollover guard."""

from __future__ import annotations


def evaluate_spread(spread_points: float) -> dict[str, object]:
    if spread_points >= 35:
        return {"spread_quality": "DANGER", "allow_trade": False, "message": "Spread dang mo rong bat thuong"}
    if spread_points >= 20:
        return {"spread_quality": "WARNING", "allow_trade": True, "message": "Spread dang cao, can than trong"}
    return {"spread_quality": "GOOD", "allow_trade": True, "message": "Spread on dinh"}


def is_rollover_danger(hour_utc: int) -> bool:
    return hour_utc in {21, 22, 23}
