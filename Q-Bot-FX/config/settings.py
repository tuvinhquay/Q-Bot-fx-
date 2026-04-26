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
        self.GEMINI_API_KEY = self._get_required("GEMINI_API_KEY")
        self.MT5_LOGIN = self._get_required("MT5_LOGIN")
        self.MT5_PASSWORD = self._get_required("MT5_PASSWORD")
        self.MT5_SERVER = self._get_required("MT5_SERVER")

        self.RISK_PERCENT = 1
        self.SYMBOLS = ["EURUSD"]
        self.TIMEFRAME_H4 = "H4"
        self.TIMEFRAME_D1 = "D1"

    @staticmethod
    def _get_required(name: str) -> str:
        value = os.getenv(name)
        if not value:
            raise ValueError(f"Missing required environment variable: {name}")
        return value
