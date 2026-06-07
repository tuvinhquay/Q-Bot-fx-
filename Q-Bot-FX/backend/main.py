"""Q-Bot-FX trading engine entrypoint."""

from __future__ import annotations

import logging
import sys
from pathlib import Path

import MetaTrader5 as mt5

# ===== FIX PYINSTALLER =====

if getattr(sys, "frozen", False):
    BASE_DIR = Path(sys.executable).parent
else:
    BASE_DIR = Path(__file__).resolve().parents[1]

if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from backend.core.scheduler import start_trading_loop
from backend.notifications.telegram_notifier import TelegramNotifier
from backend.services.mt5.auto_login_engine import MT5AutoLoginEngine
from backend.services.deployment.runtime_checker import (
    check_runtime_environment,
    format_runtime_report,
)
from backend.services.telegram.monitoring_center import build_startup_report
from config.settings import Settings

logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s - %(message)s",
)

LOGGER = logging.getLogger("QBotFX")


def enable_mt5_autotrading() -> None:
    """Verify MT5 connection and ensure AutoTrading is enabled."""
    terminal_info = mt5.terminal_info()

    if not terminal_info:
        raise RuntimeError("Cannot read MT5 terminal info")

    if not terminal_info.trade_allowed:
        raise RuntimeError("Please enable AutoTrading on MT5")

    print("MT5 connected")
    print(f"Trading allowed: {terminal_info.trade_allowed}")


def main() -> None:
    """Main entrypoint."""
    run_once = "--once" in sys.argv

    print("Q-Bot-FX starting...")

    runtime_state = check_runtime_environment(BASE_DIR)

    if runtime_state["status"] == "PASS":
        print("[STARTUP CHECK] OK")
    else:
        print("[STARTUP CHECK] WARNING")
        print(format_runtime_report(runtime_state))

    if run_once:
        print("TEST MODE: run once then exit")
    else:
        print("PRODUCTION MODE: running forever")

    try:
        settings = Settings()
    except ValueError as error:
        print(f"Settings error: {error}")
        return

    print("Starting MT5 Auto Login Engine...")

    login_result = MT5AutoLoginEngine().connect()

    if not login_result.success:
        print(f"MT5 Login Failed: {login_result.error}")
        return

    print("MT5 Auto Login Success")
    print(f"Account: {login_result.account_login}")
    print(f"Trade Allowed: {login_result.trade_allowed}")

    try:
        enable_mt5_autotrading()
    except RuntimeError as error:
        print(f"MT5 Error: {error}")
        return

    account = {}

    account_info = mt5.account_info()
    if account_info:
        account = {
            "balance": float(account_info.balance),
            "equity": float(account_info.equity),
        }
        print(f"Balance: {account['balance']} USD")
        print(f"Equity : {account['equity']} USD")
    else:
        print("Unable to read account info from MT5.")

    try:
        TelegramNotifier(settings).send(
            build_startup_report(
                mt5_state={"status": "CONNECTED"},
                account=account,
            )
        )
    except Exception as error:
        LOGGER.warning("Startup report failed: %s", error)

    start_trading_loop(
        settings,
        run_once=run_once,
    )


if __name__ == "__main__":
    main()
