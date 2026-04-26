"""Q-Bot-FX MVP pipeline entrypoint."""

from __future__ import annotations

import logging
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from config.settings import Settings
from backend.data.market_data import get_latest_market_data
from backend.mt5.connector import MT5Connector
from backend.risk.risk_manager import check_risk
from backend.strategy.demo_strategy import generate_signal


logging.basicConfig(level=logging.INFO, format="%(levelname)s - %(message)s")


def main() -> None:
    print("Q-Bot-FX starting...")

    try:
        settings = Settings()
    except ValueError as error:
        print(f"Settings error: {error}")
        print("Pipeline finished.")
        return

    connector = MT5Connector(settings)
    connected = connector.connect()
    print(f"MT5 connected: {'OK' if connected else 'WARNING'}")

    candles = get_latest_market_data(connector)
    print(f"Fetched candles: {len(candles)}")

    signal_data = generate_signal(candles)
    signal = signal_data["signal"]
    print(f"Signal: {signal}")

    risk_ok = check_risk(signal)
    print(f"Risk check: {'PASSED' if risk_ok else 'FAILED'}")

    print("Pipeline finished.")


if __name__ == "__main__":
    main()
