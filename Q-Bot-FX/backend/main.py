# ==========================================================
# PART 1
# TELEGRAM SERVICES
# ==========================================================
import logging
import sys
import time

from pathlib import Path

import MetaTrader5 as mt5

BASE_DIR = Path(__file__).resolve().parents[1]
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from backend.bootstrap import ensure_project_root_on_path

ensure_project_root_on_path()

from backend.notifications.telegram_notifier import TelegramNotifier

from backend.services.telegram.monitoring_center import (
    build_startup_report,
    build_live_dashboard,
)

from backend.services.telegram.telegram_service import (
    get_telegram_service,
)

from backend.services.telegram.dashboard_updater import (
    get_dashboard_updater,
)

# ===== FIX PYINSTALLER =====

if getattr(sys, "frozen", False):
    BASE_DIR = Path(sys.executable).parent
else:
    BASE_DIR = Path(__file__).resolve().parents[1]

if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from backend.core.scheduler import start_trading_loop
from backend.services.mt5.auto_login_engine import MT5AutoLoginEngine
from backend.services.deployment.runtime_checker import (
    check_runtime_environment,
    format_runtime_report,
)
from backend.services.recovery.crash_guard import CrashGuard
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
    
    print("=" * 60)
    print("TELEGRAM TOKEN :", settings.TELEGRAM_BOT_TOKEN[:15] + "...")
    print("CHAT ID        :", settings.TELEGRAM_CHAT_ID)
    print("=" * 60)

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
        LOGGER.error("MT5 startup blocked: %s", error)
        try:
            TelegramNotifier(settings).send(f"⚠️ MT5 BLOCKED\n\n{error}")
        except Exception as telegram_error:
            LOGGER.warning("Startup Telegram alert failed: %s", telegram_error)
        return

    # ==========================================================
    # PART 2
    # ACCOUNT INFORMATION
    # ==========================================================

    account = {}

    account_info = mt5.account_info()

    if account_info:

        account = {
            "balance": float(account_info.balance),
            "equity": float(account_info.equity),
        }

        print(f"Balance : {account['balance']} USD")
        print(f"Equity  : {account['equity']} USD")

    else:

        LOGGER.warning(
            "Cannot read MT5 account information."
        )

    # ==========================================================
    # PART 3
    # INITIALIZE TELEGRAM CORE
    # ==========================================================

    telegram_service = get_telegram_service()

    telegram_service.initialize(

        settings.TELEGRAM_BOT_TOKEN

    )

    LOGGER.info(

        "Telegram Service initialized."

    )

    dashboard_updater = get_dashboard_updater()

    dashboard_updater.initialize(

        telegram_service

    )

    dashboard_updater.set_interval(5)

    LOGGER.info(

        "Dashboard Updater initialized."

    )

    # ==========================================================
    # PART 4
    # INITIALIZE LIVE DASHBOARD
    # ==========================================================

    if settings.TELEGRAM_CHAT_ID:

        telegram_service.initialize_dashboard(

            int(settings.TELEGRAM_CHAT_ID)

        )

        LOGGER.info(

            "Telegram Dashboard initialized."

        )

    else:

        LOGGER.warning(

            "Telegram Chat ID not configured."

        )

    # ==========================================================
    # PART 5
    # SEND STARTUP REPORT
    # ==========================================================

    try:

        notifier = TelegramNotifier(settings)

        notifier.send(

            build_startup_report(

                mt5_state={

                    "status": "CONNECTED"

                },

                account=account,

            )

        )

        LOGGER.info(

            "Startup report sent."

        )

    except Exception as error:

        LOGGER.warning(

            "Startup report failed: %s",

            error,

        )

    # ==========================================================
    # PART 6
    # VERIFY AUTOTRADING
    # ==========================================================

    try:

        enable_mt5_autotrading()

    except RuntimeError as error:

        LOGGER.error(str(error))

        try:

            TelegramNotifier(settings).send(

                f"⚠️ MT5 WARNING\n\n{error}"

            )

        except Exception:

            pass

    # ==========================================================
    # PART 7
    # START TRADING LOOP
    # ==========================================================

    crash_guard = CrashGuard(
        TelegramNotifier(settings)
    )

    while True:

        try:

            start_trading_loop(
                settings,
                run_once=run_once,
            )

            break

        except Exception as error:

            crash_guard.handle_exception(error)

            if run_once:
                break

            LOGGER.warning(
                "Restarting Q-Bot-FX after crash..."
            )

            time.sleep(5)

if __name__ == "__main__":
    main()            