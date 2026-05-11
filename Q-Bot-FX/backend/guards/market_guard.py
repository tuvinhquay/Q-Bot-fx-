"""Market-open guard for Forex trading sessions."""

from __future__ import annotations

from datetime import datetime, timezone


def is_market_open() -> bool:
    """
    Forex market closed on Saturday (5) and Sunday (6).
    Monday=0 ... Sunday=6.
    """
    now = datetime.now(timezone.utc)
    weekday = now.weekday()

    if weekday in [5, 6]:
        print("🚫 Market closed: Weekend detected")
        return False

    print("✅ Market open: Weekday detected")
    return True
