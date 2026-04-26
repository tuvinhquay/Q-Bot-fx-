"""Demo strategy that emits mock BUY/SELL/HOLD signal from close prices."""

from __future__ import annotations

import pandas as pd


def generate_signal(df: pd.DataFrame) -> dict:
    """Generate a demo signal based on last two close candles."""
    if df is None or df.empty or "close" not in df.columns or len(df) < 2:
        return {"signal": "HOLD"}

    latest_close = df["close"].iloc[-1]
    prev_close = df["close"].iloc[-2]

    if latest_close > prev_close:
        return {"signal": "BUY"}
    if latest_close < prev_close:
        return {"signal": "SELL"}
    return {"signal": "HOLD"}
