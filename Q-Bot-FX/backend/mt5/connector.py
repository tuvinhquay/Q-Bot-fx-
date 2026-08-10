"""MT5 connector abstraction for Q-Bot-FX MVP pipeline."""

from __future__ import annotations

import logging
import sys
from pathlib import Path
from typing import Dict

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
        terminal = mt5.terminal_info()
        if terminal is not None:
            LOGGER.info("MT5 already connected - reusing existing session")
            self.is_connected = True
            return True

        try:
            login = int(self.settings.MT5_LOGIN)
        except ValueError:
            LOGGER.warning("MT5 login must be numeric: %s", self.settings.MT5_LOGIN)
            self.is_connected = False
            return False

        initialize_params = {
            "login": login,
            "password": self.settings.MT5_PASSWORD,
            "server": self.settings.MT5_SERVER,
        }
        if self.settings.MT5_PATH:
            initialize_params["path"] = self.settings.MT5_PATH

        self.is_connected = mt5.initialize(**initialize_params)

        if self.is_connected:
            LOGGER.info("MT5 connection established.")
            return True

        LOGGER.warning("MT5 connection failed: %s", mt5.last_error())
        return False

    def get_account_info(self) -> Dict[str, float | None]:
        """Return account balance & equity safely."""
        if not self.is_connected:
            return {"balance": None, "equity": None}

        info = mt5.account_info()
        if info is None:
            LOGGER.warning("Failed to fetch account info.")
            return {"balance": None, "equity": None}

        return {
            "balance": float(info.balance),
            "equity": float(info.equity),
        }

    def get_rates(
        self,
        symbol: str,
        timeframe: int,
        n: int
    ) -> pd.DataFrame:
        """Fetch latest candle data from MT5 safely."""

        if not self.is_connected:
            LOGGER.warning("MT5 not connected, skipping rates fetch.")
            return pd.DataFrame()

        try:
            # ensure symbol exists in broker
            symbol_info = mt5.symbol_info(symbol)
            if symbol_info is None:
                LOGGER.warning("Symbol %s not found on broker.", symbol)
                return pd.DataFrame()

            # ensure symbol visible in MarketWatch
            if not getattr(symbol_info, "visible", True):
                LOGGER.info("Enabling symbol %s in MarketWatch", symbol)
                mt5.symbol_select(symbol, True)

            rates = mt5.copy_rates_from_pos(symbol, timeframe, 0, n)

            if rates is None or len(rates) == 0:
                LOGGER.warning("No rates returned for %s.", symbol)
                return pd.DataFrame()

            df = pd.DataFrame(rates)
            LOGGER.info("Fetched %s candles for %s", len(df), symbol)
            return df

        except Exception as e:
            LOGGER.exception("MT5 get_rates error: %s", e)
            return pd.DataFrame()
