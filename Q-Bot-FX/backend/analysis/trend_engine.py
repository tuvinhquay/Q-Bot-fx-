"""Trend engine for multi-timeframe directional bias."""

from __future__ import annotations

from dataclasses import dataclass

import pandas as pd


@dataclass
class TrendSignal:
    trend: str  # BULLISH | BEARISH | SIDEWAYS


def _ema(series: pd.Series, period: int = 200) -> pd.Series:
    return series.ewm(span=period, adjust=False).mean()


def _has_hh_hl(df: pd.DataFrame) -> bool:
    if len(df) < 4:
        return False
    highs = df["high"].tail(4).tolist()
    lows = df["low"].tail(4).tolist()
    return highs[-1] > highs[-3] and lows[-1] > lows[-3]


def _has_lh_ll(df: pd.DataFrame) -> bool:
    if len(df) < 4:
        return False
    highs = df["high"].tail(4).tolist()
    lows = df["low"].tail(4).tolist()
    return highs[-1] < highs[-3] and lows[-1] < lows[-3]


def _single_tf_trend(df: pd.DataFrame) -> str:
    if df is None or df.empty or len(df) < 20:
        return "SIDEWAYS"
    if not {"close", "high", "low"}.issubset(df.columns):
        return "SIDEWAYS"

    ema200 = _ema(df["close"], 200)
    latest_close = float(df["close"].iloc[-1])
    latest_ema = float(ema200.iloc[-1])
    ema_slope_up = float(ema200.iloc[-1] - ema200.iloc[-2]) > 0
    ema_slope_down = float(ema200.iloc[-1] - ema200.iloc[-2]) < 0

    if ema_slope_up and latest_close > latest_ema and _has_hh_hl(df):
        return "BULLISH"
    if ema_slope_down and latest_close < latest_ema and _has_lh_ll(df):
        return "BEARISH"
    return "SIDEWAYS"


def detect_trend(d1_df: pd.DataFrame, h4_df: pd.DataFrame) -> TrendSignal:
    """Return final trend only when H4 confirms D1 direction."""
    d1_trend = _single_tf_trend(d1_df)
    if d1_trend == "SIDEWAYS":
        return TrendSignal(trend="SIDEWAYS")

    h4_trend = _single_tf_trend(h4_df)
    if h4_trend == d1_trend:
        return TrendSignal(trend=d1_trend)
    return TrendSignal(trend="SIDEWAYS")
