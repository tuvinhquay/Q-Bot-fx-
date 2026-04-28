"""MT5 connection module for Q-Bot-FX.

This module only handles connecting to MetaTrader 5 and validating
a demo account connection.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[2]
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from dotenv import load_dotenv
import MetaTrader5 as mt5

from config import settings


load_dotenv(BASE_DIR / ".env")


def _get_mt5_credentials() -> tuple[int, str, str]:
    """Load MT5 credentials from .env first, then fallback to settings.py."""
    login_raw = os.getenv("MT5_LOGIN") or settings.MT5_LOGIN
    password = os.getenv("MT5_PASSWORD") or settings.MT5_PASSWORD
    server = os.getenv("MT5_SERVER") or settings.MT5_SERVER

    try:
        login = int(login_raw)
    except (TypeError, ValueError):
        login = 0

    return login, password, server


def connect_mt5() -> bool:
    """Connect to MT5 terminal and print account demo balance status."""
    login, password, server = _get_mt5_credentials()

    if not mt5.initialize(login=login, password=password, server=server):
        print("Failed")
        error = mt5.last_error()
        print(f"MT5 initialize error: {error}")
        mt5.shutdown()
        return False

    account_info = mt5.account_info()
    if account_info is None:
        print("Failed")
        print("Unable to fetch account info after successful initialization.")
        mt5.shutdown()
        return False

    print(f"Connected to MT5 account: {account_info.login}")
    print(f"Balance: {account_info.balance} USD")
    return True


if __name__ == "__main__":
    connect_mt5()
    mt5.shutdown()
