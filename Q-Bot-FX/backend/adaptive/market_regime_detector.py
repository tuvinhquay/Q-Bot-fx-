from __future__ import annotations

import pandas as pd


def _ema(series: pd.Series, period: int = 200) -> pd.Series:
    return series.ewm(span=period, adjust=False).mean()


def _atr(df: pd.DataFrame, period: int = 14) -> pd.Series:
    high_low = df["high"] - df["low"]
    high_close = (df["high"] - df["close"].shift(1)).abs()
    low_close = (df["low"] - df["close"].shift(1)).abs()
    tr = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
    return tr.rolling(period).mean()


def detect_market_regime(df):
    if df is None or df.empty or len(df) < 30:
        return {
            "regime": "RANGING",
            "volatility_score": 0.0,
            "trend_strength": 0.0,
        }

    atr_series = _atr(df, period=14)
    atr = float(atr_series.iloc[-1]) if not atr_series.empty else 0.0
    price = float(df["close"].iloc[-1])
    vol_score = (atr / max(abs(price), 1e-9)) * 10000

    ema = _ema(df["close"], 200)
    slope = float(ema.iloc[-1] - ema.iloc[-2]) if len(ema) > 2 else 0.0
    trend_strength = abs(slope) / max(abs(price), 1e-9) * 10000

    if vol_score > 40:
        regime = "VOLATILE"
    elif vol_score < 8:
        regime = "LOW_VOLATILITY"
    elif trend_strength > 2.5:
        regime = "TRENDING"
    else:
        regime = "RANGING"

    return {
        "regime": regime,
        "volatility_score": vol_score,
        "trend_strength": trend_strength,
    }
