"""Confluence scoring for entry validation."""

from __future__ import annotations

from dataclasses import dataclass

import pandas as pd

from .structure_detector import MarketStructure


@dataclass
class ConfluenceResult:
    score: int
    valid: bool


def _ema(series: pd.Series, period: int) -> pd.Series:
    return series.ewm(span=period, adjust=False).mean()


def _rsi(series: pd.Series, period: int = 14) -> pd.Series:
    delta = series.diff()
    up = delta.clip(lower=0).rolling(period).mean()
    down = (-delta.clip(upper=0)).rolling(period).mean()
    rs = up / down.replace(0, 1e-9)
    return 100 - (100 / (1 + rs))


def check(df_h1: pd.DataFrame, structure: MarketStructure) -> ConfluenceResult:
    if df_h1 is None or df_h1.empty or len(df_h1) < 30:
        return ConfluenceResult(score=0, valid=False)

    score = 0
    close = float(df_h1["close"].iloc[-1])

    rsi_val = float(_rsi(df_h1["close"]).iloc[-1])
    if 45 <= rsi_val <= 55:
        score += 1

    ema50 = float(_ema(df_h1["close"], 50).iloc[-1])
    ema200 = float(_ema(df_h1["close"], 200).iloc[-1])
    touch_ema = abs(close - ema50) / max(abs(close), 1e-9) < 0.002 or abs(close - ema200) / max(abs(close), 1e-9) < 0.003
    if touch_ema:
        score += 1

    vol_ma20 = float(df_h1["tick_volume"].tail(20).mean()) if "tick_volume" in df_h1.columns else 0.0
    last_vol = float(df_h1["tick_volume"].iloc[-1]) if "tick_volume" in df_h1.columns else 0.0
    if vol_ma20 > 0 and last_vol > 1.2 * vol_ma20:
        score += 1

    structure_score = int(structure.bos) + int(structure.liquidity_sweep) + int(structure.order_block) + int(structure.fvg)
    if structure_score >= 1:
        score += 1
    if structure_score >= 3:
        score += 1

    return ConfluenceResult(score=score, valid=score >= 3)
