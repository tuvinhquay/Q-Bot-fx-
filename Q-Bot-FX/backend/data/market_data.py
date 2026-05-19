"""Market data helpers for MVP pipeline."""

from __future__ import annotations

import pandas as pd
import MetaTrader5 as mt5

from backend.mt5.connector import MT5Connector


def get_latest_market_data(connector: MT5Connector) -> pd.DataFrame:
    """Fetch latest market candle data from MT5 connector."""
    symbol = connector.settings.SYMBOLS[0] if connector.settings.SYMBOLS else "EURUSD"
    return connector.get_rates(symbol=symbol, timeframe=mt5.TIMEFRAME_M5, n=50)
