"""Q-Bot-FX trading engine entrypoint."""

from __future__ import annotations

import logging
import sys
from pathlib import Path

import MetaTrader5 as mt5

BASE_DIR = Path(__file__).resolve().parents[1]
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from config.settings import Settings
from backend.core.scheduler import start_trading_loop

logging.basicConfig(level=logging.INFO, format="%(levelname)s - %(message)s")


def enable_mt5_autotrading() -> None:
    """Verify MT5 connection and ensure AutoTrading is enabled."""
    if not mt5.initialize():
        raise RuntimeError("❌ Không kết nối được MT5")

    terminal_info = mt5.terminal_info()

    if not terminal_info.trade_allowed:
        raise RuntimeError("❌ Hãy bật AutoTrading trên MT5")

    print("✅ MT5 đã kết nối")
    print(f"💰 Trading allowed: {terminal_info.trade_allowed}")


def main() -> None:
    """Main entrypoint for Q-Bot-FX trading engine."""
    print("Q-Bot-FX starting...")

    try:
        settings = Settings()
    except ValueError as error:
        print(f"Settings error: {error}")
        return

    try:
        enable_mt5_autotrading()
    except RuntimeError as error:
        print(f"MT5 Error: {error}")
        return

    # Start continuous trading loop
    start_trading_loop(settings)


if __name__ == "__main__":
    main()
