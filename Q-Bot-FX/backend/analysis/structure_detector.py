"""Market structure detection primitives for SMC-like signals."""

from __future__ import annotations

from dataclasses import dataclass

import pandas as pd


@dataclass
class MarketStructure:
    bos: bool
    liquidity_sweep: bool
    order_block: bool
    fvg: bool


def find_recent_swing_high_low(df: pd.DataFrame, lookback: int = 20) -> tuple[float | None, float | None]:
    if df is None or df.empty or len(df) < 3:
        return None, None
    window = df.tail(lookback)
    return float(window["high"].max()), float(window["low"].min())


def detect_break_of_structure(df: pd.DataFrame) -> bool:
    if df is None or df.empty or len(df) < 6:
        return False
    recent_high, recent_low = find_recent_swing_high_low(df.iloc[:-1], lookback=20)
    if recent_high is None or recent_low is None:
        return False
    close = float(df["close"].iloc[-1])
    return close > recent_high or close < recent_low


def detect_liquidity_sweep(df: pd.DataFrame) -> bool:
    if df is None or df.empty or len(df) < 6:
        return False
    prev_high = float(df["high"].iloc[-6:-1].max())
    prev_low = float(df["low"].iloc[-6:-1].min())
    last = df.iloc[-1]
    swept_high = float(last["high"]) > prev_high and float(last["close"]) < prev_high
    swept_low = float(last["low"]) < prev_low and float(last["close"]) > prev_low
    return swept_high or swept_low


def detect_order_block(df: pd.DataFrame) -> bool:
    if df is None or df.empty or len(df) < 3:
        return False
    prev = df.iloc[-2]
    last = df.iloc[-1]
    body_prev = abs(float(prev["close"]) - float(prev["open"]))
    body_last = abs(float(last["close"]) - float(last["open"]))
    engulf_up = float(last["close"]) > float(prev["high"])
    engulf_down = float(last["close"]) < float(prev["low"])
    return body_last > body_prev and (engulf_up or engulf_down)


def detect_fair_value_gap(df: pd.DataFrame) -> bool:
    if df is None or df.empty or len(df) < 3:
        return False
    c1 = df.iloc[-3]
    c3 = df.iloc[-1]
    bullish_gap = float(c1["high"]) < float(c3["low"])
    bearish_gap = float(c1["low"]) > float(c3["high"])
    return bullish_gap or bearish_gap


def analyze(df: pd.DataFrame) -> MarketStructure:
    return MarketStructure(
        bos=detect_break_of_structure(df),
        liquidity_sweep=detect_liquidity_sweep(df),
        order_block=detect_order_block(df),
        fvg=detect_fair_value_gap(df),
    )
