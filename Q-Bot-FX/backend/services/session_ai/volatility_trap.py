"""Detect fake volatility and breakout traps."""

from __future__ import annotations

from typing import Any


def detect_volatility_trap(candles: Any) -> dict[str, object]:
    if candles is None or getattr(candles, "empty", True):
        return {"trap_score": 0.0, "is_trap": False, "message": "Khong du du lieu candle"}

    recent = candles.tail(10)
    body = (recent["close"] - recent["open"]).abs()
    wick = (recent["high"] - recent["low"]).abs() - body
    wick_ratio = float((wick / (body + 1e-6)).mean())
    spike = float(((recent["high"] - recent["low"]).pct_change().abs().fillna(0)).max())

    score = min(100.0, wick_ratio * 25.0 + spike * 100.0)
    is_trap = score >= 65.0
    message = "Co dau hieu fake breakout/candle bay" if is_trap else "Volatility dang tu nhien"
    return {"trap_score": round(score, 2), "is_trap": is_trap, "message": message}
