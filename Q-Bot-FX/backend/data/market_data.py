"""Market data helpers for MVP pipeline."""

from __future__ import annotations

import pandas as pd

from backend.mt5.connector import MT5Connector


def get_latest_market_data(connector: MT5Connector) -> pd.DataFrame:
    """Fetch latest market candle data from MT5 connector."""
    return connector.get_rates()
