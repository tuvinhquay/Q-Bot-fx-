"""Application settings loader for Q-Bot-FX."""

from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

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

        # Risk
        self.RISK_PERCENT = 1

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

        print("SETTINGS FILE LOADED SUCCESSFULLY")
        print("SYMBOL LIST:", self.SYMBOLS)
        print("TIMEFRAMES:", self.TIMEFRAME_D1, self.TIMEFRAME_H4, self.TIMEFRAME_H1)

    @staticmethod
    def _get_required(name: str) -> str:
        value = os.getenv(name)
        if not value:
            raise ValueError(f"Missing required environment variable: {name}")
        return value
