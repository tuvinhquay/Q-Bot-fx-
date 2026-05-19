"""
Generate trading chart image for Telegram alerts.
"""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd


OUTPUT_DIR = Path("charts")
OUTPUT_DIR.mkdir(exist_ok=True)


def generate_chart(
    df: pd.DataFrame,
    symbol: str,
    entry: float,
    sl: float,
    tp: float,
) -> str:
    """
    Create candlestick-like chart and draw entry/SL/TP lines.
    Return path to saved image.
    """

    if df.empty:
        raise ValueError("DataFrame empty, cannot draw chart")

    # Convert time column if exists
    if "time" in df.columns:
        df = df.copy()
        df["time"] = pd.to_datetime(df["time"], unit="s")

    plt.figure(figsize=(12, 6))
    plt.plot(df["close"], label="Price")

    # Draw trading levels
    plt.axhline(entry, linestyle="--")
    plt.axhline(sl, linestyle="--")
    plt.axhline(tp, linestyle="--")

    plt.title(f"{symbol} Signal")
    plt.legend()

    file_path = OUTPUT_DIR / f"{symbol}_signal.png"
    plt.savefig(file_path)
    plt.close()

    return str(file_path)
