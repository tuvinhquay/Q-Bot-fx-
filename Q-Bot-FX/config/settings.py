"""Application settings loader for Q-Bot-FX."""

from __future__ import annotations

import os
import sys
from pathlib import Path

from dotenv import load_dotenv

if getattr(sys, "frozen", False):
    BASE_DIR = Path(sys.executable).parent
else:
    BASE_DIR = Path(__file__).resolve().parents[1]

load_dotenv(BASE_DIR / ".env")


class Settings:
    """Load required environment variables for the bot."""

    def __init__(self) -> None:
        print("Loading Settings...")

        # API keys
        self.GEMINI_API_KEY = self._get_required("GEMINI_API_KEY")
        self.TELEGRAM_BOT_TOKEN = self._get_required("TELEGRAM_BOT_TOKEN")
        self.TELEGRAM_CHAT_ID = self._get_required("TELEGRAM_CHAT_ID")

        # MT5 login
        self.MT5_LOGIN = int(self._get_required("MT5_LOGIN"))
        self.MT5_PASSWORD = self._get_required("MT5_PASSWORD")
        self.MT5_SERVER = self._get_required("MT5_SERVER")
        self.MT5_PATH = os.getenv("MT5_PATH", "")

        # Risk
        self.RISK_PER_TRADE = self._get_float_env("RISK_PER_TRADE", 0.01)
        self.RISK_PERCENT = self.RISK_PER_TRADE * 100.0

        # Live trading safety guard
        self.LIVE_TRADING_ENABLED = os.getenv("LIVE_TRADING_ENABLED", "false").lower() == "true"
        self.TRADING_MODE = os.getenv("TRADING_MODE", "TEST" if not self.LIVE_TRADING_ENABLED else "LIVE").upper()
        self.EXECUTION_MODE = os.getenv("EXECUTION_MODE", self.TRADING_MODE).upper()
        self.TRADING_ENABLED = os.getenv("TRADING_ENABLED", "true" if self.LIVE_TRADING_ENABLED or self.TRADING_MODE in {"TEST", "LIVE"} else "false").lower() == "true"

        # Symbol portfolio
        self.SYMBOLS = [
            "EURUSDm", "GBPUSDm", "USDJPYm", "USDCHFm",
            "AUDUSDm", "USDCADm", "NZDUSDm",
            "EURGBPm", "EURJPYm", "GBPJPYm", "AUDJPYm",
            "XAUUSDm", "XAGUSDm",
            "USOILm", "UKOILm",
        ]

        # Timeframes
        self.TIMEFRAME_D1 = "D1"
        self.TIMEFRAME_H4 = "H4"
        self.TIMEFRAME_H1 = "H1"

        # Candle history
        self.CANDLES_D1 = 120
        self.CANDLES_H4 = 200
        self.CANDLES_H1 = 300

        # Scheduler
        self.TRADE_INTERVAL_MINUTES = 5

        # Force signal test mode
        self.FORCE_SIGNAL_MODE = os.getenv("FORCE_SIGNAL_MODE", "false").lower() == "true"
        self.FORCE_SIGNAL_TYPE = os.getenv("FORCE_SIGNAL_TYPE", "BUY")
        self.FORCE_SIGNAL_SYMBOL = os.getenv("FORCE_SIGNAL_SYMBOL", "EURUSDm")

        print("SETTINGS FILE LOADED SUCCESSFULLY")
        print("SYMBOL LIST:", self.SYMBOLS)
        print("TIMEFRAMES:", self.TIMEFRAME_D1, self.TIMEFRAME_H4, self.TIMEFRAME_H1)

    @staticmethod
    def _get_required(name: str) -> str:
        value = os.getenv(name)
        if not value:
            raise ValueError(f"Missing required environment variable: {name}")
        return value

    @staticmethod
    def _get_float_env(name: str, default: float) -> float:
        value = os.getenv(name)
        if value is None:
            return default
        try:
            return float(value)
        except (TypeError, ValueError):
            return default


# ===== RISK CONFIG =====
RISK_PER_TRADE = float(os.getenv("RISK_PER_TRADE", "0.01"))
RISK_PERCENT = RISK_PER_TRADE * 100.0

# ===== LIVE TRADING SAFETY =====
LIVE_TRADING_ENABLED = os.getenv("LIVE_TRADING_ENABLED", "false").lower() == "true"
TRADING_MODE = os.getenv("TRADING_MODE", "TEST" if not LIVE_TRADING_ENABLED else "LIVE").upper()
EXECUTION_MODE = os.getenv("EXECUTION_MODE", TRADING_MODE).upper()
TRADING_ENABLED = os.getenv("TRADING_ENABLED", "true" if LIVE_TRADING_ENABLED or TRADING_MODE in {"TEST", "LIVE"} else "false").lower() == "true"

# ===== FORCE SIGNAL TEST MODE =====
FORCE_SIGNAL_MODE = os.getenv("FORCE_SIGNAL_MODE", "false").lower() == "true"
FORCE_SIGNAL_TYPE = os.getenv("FORCE_SIGNAL_TYPE", "BUY")
FORCE_SIGNAL_SYMBOL = os.getenv("FORCE_SIGNAL_SYMBOL", "EURUSDm")
