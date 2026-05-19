"""Trading scheduler for continuous auto-trading loop."""

from __future__ import annotations

import logging
import time
from datetime import datetime

from backend.core.signal_pipeline import run_signal_pipeline
from config.settings import Settings

LOGGER = logging.getLogger(__name__)


def start_trading_loop(settings: Settings, run_once: bool = False) -> None:
    """Start continuous trading loop with configured interval."""
    print("QBOT Trading Engine Started")
    print(f"Run interval: {settings.TRADE_INTERVAL_MINUTES} minutes")

    while True:
        try:
            print("\n==============================")
            print(f"Scan time: {datetime.now()}")

            run_signal_pipeline(settings)

            print("Cycle completed")
            print("==============================")

        except Exception as e:
            LOGGER.error("Loop error: %s", e)
            print(f"Loop error: {e}")

        if run_once:
            print("Test cycle finished. Exiting.")
            break

        time.sleep(settings.TRADE_INTERVAL_MINUTES * 60)

    print("Q-Bot stopped safely.")
