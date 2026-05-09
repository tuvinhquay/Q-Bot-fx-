"""Trading scheduler for continuous auto-trading loop."""

from __future__ import annotations

import logging
import time
from datetime import datetime

from backend.core.signal_pipeline import run_signal_pipeline
from config.settings import Settings

LOGGER = logging.getLogger(__name__)


def start_trading_loop(settings: Settings) -> None:
    """Start continuous trading loop with configured interval."""
    print("🚀 QBOT Trading Engine Started")
    print(f"⏱ Chu kỳ chạy: {settings.TRADE_INTERVAL_MINUTES} phút")

    while True:
        try:
            print("\n==============================")
            print(f"🕒 Scan lúc: {datetime.now()}")

            run_signal_pipeline(settings)

            print("✅ Hoàn thành chu kỳ")
            print("==============================")

        except Exception as e:
            LOGGER.error("❌ Lỗi vòng lặp: %s", e)
            print(f"❌ Lỗi vòng lặp: {e}")

        # ngủ theo số phút cấu hình
        time.sleep(settings.TRADE_INTERVAL_MINUTES * 60)
