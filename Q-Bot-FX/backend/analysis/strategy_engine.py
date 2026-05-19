"""Main strategy engine orchestrating multi-timeframe signal generation."""

from __future__ import annotations

import logging
from dataclasses import dataclass

import MetaTrader5 as mt5
import pandas as pd

from backend.mt5.connector import MT5Connector
from config.settings import Settings

from .confluence_engine import check as check_confluence
from .sl_tp_engine import calculate_stop_loss, calculate_take_profit
from .structure_detector import analyze as analyze_structure
from .trend_engine import detect_trend

LOGGER = logging.getLogger(__name__)


@dataclass
class TradeSignal:
    action: str  # BUY / SELL / HOLD
    sl: float
    tp: float
    confidence: float


def _empty_signal() -> TradeSignal:
    return TradeSignal(action="HOLD", sl=0.0, tp=0.0, confidence=0.0)


def _load_candles(connector: MT5Connector, symbol: str) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    d1 = connector.get_rates(symbol=symbol, timeframe=mt5.TIMEFRAME_D1, n=300)
    h4 = connector.get_rates(symbol=symbol, timeframe=mt5.TIMEFRAME_H4, n=300)
    h1 = connector.get_rates(symbol=symbol, timeframe=mt5.TIMEFRAME_H1, n=300)
    return d1, h4, h1


def generate_signal(symbol: str) -> TradeSignal:
    """Generate BUY/SELL/HOLD signal using D1->H4->H1 pipeline."""
    settings = Settings()
    connector = MT5Connector(settings)
    if not connector.connect():
        LOGGER.warning("[FINAL SIGNAL] MT5 not connected, forcing HOLD")
        return _empty_signal()

    d1, h4, h1 = _load_candles(connector, symbol)
    if d1.empty or h4.empty or h1.empty:
        LOGGER.info("[FINAL SIGNAL] Missing candles, forcing HOLD")
        return _empty_signal()

    trend = detect_trend(d1, h4)
    LOGGER.info("[D1 TREND] %s", trend.trend)
    LOGGER.info("[H4 CONFIRM] %s", trend.trend)

    if trend.trend == "SIDEWAYS":
        LOGGER.info("[FINAL SIGNAL] HOLD due to sideways trend")
        return _empty_signal()

    structure = analyze_structure(h1)
    LOGGER.info(
        "[H1 STRUCTURE] bos=%s liquidity_sweep=%s order_block=%s fvg=%s",
        structure.bos,
        structure.liquidity_sweep,
        structure.order_block,
        structure.fvg,
    )

    confluence = check_confluence(h1, structure)
    LOGGER.info("[CONFLUENCE SCORE] score=%s valid=%s", confluence.score, confluence.valid)
    if not confluence.valid:
        LOGGER.info("[FINAL SIGNAL] HOLD due to low confluence")
        return _empty_signal()

    action = "BUY" if trend.trend == "BULLISH" else "SELL"
    entry_price = float(h1["close"].iloc[-1])
    account_info = connector.get_account_info()
    balance = float(account_info.get("balance") or 0.0)

    sl_result = calculate_stop_loss(h1, action, entry_price, balance)
    if not sl_result.valid:
        LOGGER.info("[SL/TP] SL invalid or risk > 2%% (risk=%.4f)", sl_result.risk_percent)
        LOGGER.info("[FINAL SIGNAL] HOLD due to risk guard")
        return _empty_signal()

    tp_result = calculate_take_profit(h1, action, entry_price, sl_result.sl_price)
    LOGGER.info(
        "[SL/TP] action=%s entry=%.5f sl=%.5f risk%%=%.4f tp=%.5f rr=%.3f",
        action,
        entry_price,
        sl_result.sl_price,
        sl_result.risk_percent,
        tp_result.tp_price,
        tp_result.rr_ratio,
    )

    confidence = min(confluence.score / 5.0, 1.0)
    signal = TradeSignal(
        action=action,
        sl=sl_result.sl_price,
        tp=tp_result.tp_price,
        confidence=confidence,
    )
    LOGGER.info("[FINAL SIGNAL] action=%s confidence=%.2f", signal.action, signal.confidence)
    return signal
