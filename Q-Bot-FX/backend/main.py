"""Q-Bot-FX MVP pipeline entrypoint."""

from __future__ import annotations

import logging
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from config.settings import Settings
from backend.core.signal_pipeline import run_signal_pipeline


logging.basicConfig(level=logging.INFO, format="%(levelname)s - %(message)s")


def main() -> None:
    print("Q-Bot-FX starting...")

    try:
        settings = Settings()
    except ValueError as error:
        print(f"Settings error: {error}")
        print("Pipeline finished.")
        return

    run_signal_pipeline(settings)
    print("Pipeline finished.")


if __name__ == "__main__":
    main()
