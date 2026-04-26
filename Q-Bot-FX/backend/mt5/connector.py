"""MT5 connector abstraction for Q-Bot-FX MVP pipeline."""

from __future__ import annotations

import logging
import sys
from pathlib import Path

import MetaTrader5 as mt5
import pandas as pd

BASE_DIR = Path(__file__).resolve().parents[2]
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from config.settings import Settings


LOGGER = logging.getLogger(__name__)


class MT5Connector:
    """Simple MT5 connector with account and candle helper methods."""

    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.is_connected = False

    def connect(self) -> bool:
        """Connect to MT5 terminal using credentials from settings."""
        try:
            login = int(self.settings.MT5_LOGIN)
        except ValueError:
            LOGGER.warning("MT5 login must be numeric: %s", self.settings.MT5_LOGIN)
            self.is_connected = False
            return False

        self.is_connected = mt5.initialize(
            login=login,
            password=self.settings.MT5_PASSWORD,
            server=self.settings.MT5_SERVER,
        )

        if self.is_connected:
            LOGGER.info("MT5 connection established.")
            return True

        LOGGER.warning("MT5 connection failed: %s", mt5.last_error())
        return False

    def get_account_info(self) -> dict:
        """Return basic account info (balance/equity)."""
        if not self.is_connected:
            return {"balance": None, "equity": None}

        info = mt5.account_info()
        if info is None:
            LOGGER.warning("Failed to fetch account info.")
            return {"balance": None, "equity": None}

        return {"balance": info.balance, "equity": info.equity}

    def get_rates(self, symbol: str = "EURUSD", timeframe: int = mt5.TIMEFRAME_M5, n: int = 50) -> pd.DataFrame:
        """Fetch latest candle data and return DataFrame."""
        if not self.is_connected:
            LOGGER.warning("Skipping get_rates because MT5 is not connected.")
            return pd.DataFrame()

        rates = mt5.copy_rates_from_pos(symbol, timeframe, 0, n)
        if rates is None:
            LOGGER.warning("No rates returned for %s.", symbol)
            return pd.DataFrame()

        return pd.DataFrame(rates)
