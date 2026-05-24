"""Detect active FX session windows in UTC."""

from __future__ import annotations

from datetime import datetime, timezone


def detect_session(now_utc: datetime | None = None) -> dict[str, str]:
    now = now_utc or datetime.now(timezone.utc)
    hour = now.hour
    if 0 <= hour < 8:
        session = "ASIAN"
    elif 8 <= hour < 13:
        session = "LONDON"
    elif 13 <= hour < 17:
        session = "LONDON_NEWYORK_OVERLAP"
    else:
        session = "NEW_YORK"
    return {"session": session, "hour_utc": f"{hour:02d}:00"}
