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
        timeframe: int | str,
        n: int,
    ) -> pd.DataFrame:
        """Fetch latest candle data from MT5 safely."""

        if not self.is_connected:
            LOGGER.warning("MT5 not connected, skipping rates fetch.")
            return pd.DataFrame()

        try:
            timeframe_map = {
                "M1": mt5.TIMEFRAME_M1,
                "M2": mt5.TIMEFRAME_M2,
                "M3": mt5.TIMEFRAME_M3,
                "M4": mt5.TIMEFRAME_M4,
                "M5": mt5.TIMEFRAME_M5,
                "M6": mt5.TIMEFRAME_M6,
                "M10": mt5.TIMEFRAME_M10,
                "M12": mt5.TIMEFRAME_M12,
                "M15": mt5.TIMEFRAME_M15,
                "M20": mt5.TIMEFRAME_M20,
                "M30": mt5.TIMEFRAME_M30,
                "H1": mt5.TIMEFRAME_H1,
                "H2": mt5.TIMEFRAME_H2,
                "H3": mt5.TIMEFRAME_H3,
                "H4": mt5.TIMEFRAME_H4,
                "H6": mt5.TIMEFRAME_H6,
                "H8": mt5.TIMEFRAME_H8,
                "H12": mt5.TIMEFRAME_H12,
                "D1": mt5.TIMEFRAME_D1,
                "W1": mt5.TIMEFRAME_W1,
                "MN1": mt5.TIMEFRAME_MN1,
            }

            if isinstance(timeframe, str):
                normalized_timeframe = timeframe.strip().upper()

                if normalized_timeframe not in timeframe_map:
                    LOGGER.error(
                        "Unsupported MT5 timeframe: %s",
                        timeframe,
                    )
                    return pd.DataFrame()

                timeframe = timeframe_map[normalized_timeframe]

            if not isinstance(timeframe, int):
                LOGGER.error(
                    "Invalid MT5 timeframe type: %s",
                    type(timeframe).__name__,
                )
                return pd.DataFrame()

            if n <= 0:
                LOGGER.error(
                    "Candle count must be greater than zero: %s",
                    n,
                )
                return pd.DataFrame()

            symbol_info = mt5.symbol_info(symbol)

            if symbol_info is None:
                LOGGER.warning(
                    "Symbol %s not found on broker.",
                    symbol,
                )
                return pd.DataFrame()

            if not getattr(symbol_info, "visible", True):
                LOGGER.info(
                    "Enabling symbol %s in MarketWatch.",
                    symbol,
                )

                if not mt5.symbol_select(symbol, True):
                    LOGGER.error(
                        "Failed to select symbol %s: %s",
                        symbol,
                        mt5.last_error(),
                    )
                    return pd.DataFrame()

            rates = mt5.copy_rates_from_pos(
                symbol,
                timeframe,
                0,
                int(n),
            )

            if rates is None or len(rates) == 0:
                LOGGER.warning(
                    "No rates returned for %s timeframe=%s.",
                    symbol,
                    timeframe,
                )
                return pd.DataFrame()

            df = pd.DataFrame(rates)

            if df.empty:
                LOGGER.warning(
                    "MT5 returned empty DataFrame for %s.",
                    symbol,
                )
                return pd.DataFrame()

            LOGGER.info(
                "Fetched %s candles for %s timeframe=%s.",
                len(df),
                symbol,
                timeframe,
            )

            return df

        except Exception as error:
            LOGGER.exception(
                "MT5 get_rates error: %s",
                error,
            )
            return pd.DataFrame()
