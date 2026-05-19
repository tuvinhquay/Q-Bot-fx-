"""Smart SL/TP calculations based on structure and liquidity."""

from __future__ import annotations

from dataclasses import dataclass

import pandas as pd

from .structure_detector import find_recent_swing_high_low


@dataclass
class StopLossResult:
    sl_price: float
    risk_percent: float
    valid: bool


@dataclass
class TakeProfitResult:
    tp_price: float
    rr_ratio: float


def calculate_stop_loss(
    df_h1: pd.DataFrame,
    action: str,
    entry_price: float,
    balance: float,
    max_risk_percent: float = 2.0,
) -> StopLossResult:
    swing_high, swing_low = find_recent_swing_high_low(df_h1, lookback=30)
    if swing_high is None or swing_low is None:
        return StopLossResult(sl_price=entry_price, risk_percent=100.0, valid=False)

    pad = max(entry_price * 0.001, 0.0001)
    if action == "BUY":
        sl = swing_low - pad
        risk_percent = ((entry_price - sl) / max(entry_price, 1e-9)) * 100.0
    else:
        sl = swing_high + pad
        risk_percent = ((sl - entry_price) / max(entry_price, 1e-9)) * 100.0

    return StopLossResult(sl_price=float(sl), risk_percent=float(risk_percent), valid=risk_percent <= max_risk_percent and balance > 0)


def calculate_take_profit(
    df_h1: pd.DataFrame,
    action: str,
    entry_price: float,
    sl_price: float,
) -> TakeProfitResult:
    swing_high, swing_low = find_recent_swing_high_low(df_h1, lookback=40)
    risk_dist = abs(entry_price - sl_price)
    if risk_dist <= 0:
        return TakeProfitResult(tp_price=entry_price, rr_ratio=0.0)

    fib_target = entry_price + (1.618 * risk_dist if action == "BUY" else -1.618 * risk_dist)

    if action == "BUY":
        liquidity_target = swing_high if swing_high is not None and swing_high > entry_price else None
        prev_hl_target = float(df_h1["high"].iloc[-10:-1].max()) if len(df_h1) > 10 else None
        candidates = [x for x in [liquidity_target, prev_hl_target, fib_target] if x is not None and x > entry_price]
        tp = min(candidates) if candidates else fib_target
        rr = (tp - entry_price) / risk_dist
    else:
        liquidity_target = swing_low if swing_low is not None and swing_low < entry_price else None
        prev_hl_target = float(df_h1["low"].iloc[-10:-1].min()) if len(df_h1) > 10 else None
        candidates = [x for x in [liquidity_target, prev_hl_target, fib_target] if x is not None and x < entry_price]
        tp = max(candidates) if candidates else fib_target
        rr = (entry_price - tp) / risk_dist

    return TakeProfitResult(tp_price=float(tp), rr_ratio=float(rr))
