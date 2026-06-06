"""Q-Bot-FX trading engine entrypoint."""

from __future__ import annotations

import logging
import sys
from pathlib import Path

import MetaTrader5 as mt5

BASE_DIR = Path(__file__).resolve().parents[1]
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from backend.core.scheduler import start_trading_loop
from backend.mt5.connector import MT5Connector
from backend.notifications.telegram_notifier import TelegramNotifier
from backend.services.deployment.runtime_checker import check_runtime_environment, format_runtime_report
from backend.services.telegram.monitoring_center import build_startup_report
from config.settings import Settings

logging.basicConfig(level=logging.INFO, format="%(levelname)s - %(message)s")


def enable_mt5_autotrading() -> None:
    """Verify MT5 connection and ensure AutoTrading is enabled."""
    if not mt5.initialize():
        raise RuntimeError("MT5 connection failed")

    terminal_info = mt5.terminal_info()
    if not terminal_info.trade_allowed:
        raise RuntimeError("Please enable AutoTrading on MT5")

    print("MT5 connected")
    print(f"Trading allowed: {terminal_info.trade_allowed}")


def main() -> None:
    """Main entrypoint for Q-Bot-FX trading engine."""
    RUN_ONCE = "--once" in sys.argv

    print("Q-Bot-FX starting...")
    runtime_state = check_runtime_environment(BASE_DIR)
    if runtime_state["status"] == "PASS":
        print("[STARTUP CHECK] OK")
    else:
        print("[STARTUP CHECK] WARNING")
        print(format_runtime_report(runtime_state))

    if RUN_ONCE:
        print("TEST MODE: run once then exit")
    else:
        print("PRODUCTION MODE: running forever")

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

    mt5_connector = MT5Connector(settings)
    account = {}
    if mt5_connector.connect():
        account = mt5_connector.get_account_info()
        print(f"Balance: {account['balance']} USD")
        print(f"Equity : {account['equity']} USD")
    else:
        print("Unable to read account info from MT5 connector.")

    try:
        TelegramNotifier(settings).send(
            build_startup_report(
                mt5_state={"status": "CONNECTED"},
                account=account,
            )
        )
    except Exception as error:
        LOGGER.warning("Startup report failed: %s", error)

    # Start continuous trading loop
    start_trading_loop(settings, run_once=RUN_ONCE)


if __name__ == "__main__":
    main()
