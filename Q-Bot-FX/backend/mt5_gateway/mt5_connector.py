"""MetaTrader 5 connector that reads credentials from environment variables."""

from __future__ import annotations

import importlib
import logging
import os
from pathlib import Path
from types import ModuleType
from typing import Any

from dotenv import load_dotenv


LOGGER = logging.getLogger(__name__)
PROJECT_DIR = Path(__file__).resolve().parents[2]
load_dotenv(PROJECT_DIR / ".env")


class MT5Connector:
    """Small gateway around the MetaTrader5 package for login and data reads."""

    def __init__(self, mt5_module: ModuleType | Any | None = None) -> None:
        self.mt5 = mt5_module
        self.connected = False

    def _load_mt5(self) -> ModuleType | Any | None:
        """Load MetaTrader5 lazily so tests and non-Windows CI can mock it."""
        if self.mt5 is not None:
            return self.mt5

        if importlib.util.find_spec("MetaTrader5") is None:
            LOGGER.error("MetaTrader5 package is not installed. Install dependency: MetaTrader5")
            return None

        self.mt5 = importlib.import_module("MetaTrader5")
        return self.mt5

    @staticmethod
    def _credentials() -> tuple[int | None, str | None, str | None]:
        """Read and validate MT5 credentials from the environment."""
        login_raw = os.getenv("MT5_LOGIN")
        password = os.getenv("MT5_PASSWORD")
        server = os.getenv("MT5_SERVER")

        missing = [name for name, value in {
            "MT5_LOGIN": login_raw,
            "MT5_PASSWORD": password,
            "MT5_SERVER": server,
        }.items() if not value]
        if missing:
            LOGGER.error("Missing MT5 environment variables: %s", ", ".join(missing))
            return None, password, server

        try:
            login = int(str(login_raw))
        except ValueError:
            LOGGER.error("MT5_LOGIN must be numeric: %s", login_raw)
            return None, password, server

        return login, password, server

    def connect(self) -> bool:
        """Connect and login to MetaTrader 5 using MT5_LOGIN, MT5_PASSWORD, and MT5_SERVER."""
        mt5 = self._load_mt5()
        if mt5 is None:
            self.connected = False
            return False

        login, password, server = self._credentials()
        if login is None or not password or not server:
            self.connected = False
            return False

        initialized = bool(mt5.initialize(login=login, password=password, server=server))
        if not initialized:
            LOGGER.error("MT5 login failed: %s", mt5.last_error())
            self.connected = False
            return False

        LOGGER.info("MT5 connected successfully to server %s with login %s.", server, login)
        self.connected = True
        return True

    def shutdown(self) -> None:
        """Close the MT5 terminal connection when available."""
        mt5 = self._load_mt5()
        if mt5 is not None:
            mt5.shutdown()
        self.connected = False
        LOGGER.info("MT5 connection shut down.")

    def account_info(self) -> Any | None:
        """Return raw MT5 account_info data, or None if unavailable."""
        mt5 = self._load_mt5()
        if mt5 is None:
            return None

        info = mt5.account_info()
        if info is None:
            LOGGER.error("Unable to read MT5 account info: %s", mt5.last_error())
        return info

    def symbol_info(self, symbol: str) -> Any | None:
        """Return raw MT5 symbol_info data for a symbol, or None if unavailable."""
        mt5 = self._load_mt5()
        if mt5 is None:
            return None

        info = mt5.symbol_info(symbol)
        if info is None:
            LOGGER.error("Unable to read MT5 symbol info for %s: %s", symbol, mt5.last_error())
        return info
