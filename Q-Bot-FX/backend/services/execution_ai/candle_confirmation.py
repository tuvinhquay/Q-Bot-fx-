"""Candle confirmation checks before execution."""

from __future__ import annotations

from typing import Any


def evaluate_candle_confirmation(candles: Any) -> dict[str, object]:
    if candles is None or getattr(candles, "empty", True) or len(candles) < 3:
        return {"confirmed": False, "strength": "WEAK", "fake_breakout_risk": "HIGH"}

    last = candles.iloc[-1]
    body = abs(float(last["close"]) - float(last["open"]))
    full = max(float(last["high"]) - float(last["low"]), 1e-9)
    wick_ratio = 1.0 - (body / full)

    confirmed = bool(candles.index.is_monotonic_increasing)
    fake_risk = "HIGH" if wick_ratio > 0.65 else "MEDIUM" if wick_ratio > 0.45 else "LOW"
    strength = "STRONG" if body / full > 0.55 else "MEDIUM" if body / full > 0.35 else "WEAK"
    if not confirmed:
        strength = "WEAK"
    return {"confirmed": confirmed, "strength": strength, "fake_breakout_risk": fake_risk}
