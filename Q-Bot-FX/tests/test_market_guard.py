"""Tests for the weekend market guard."""

from __future__ import annotations

import sys
from datetime import datetime
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parents[1]
if str(PROJECT_DIR) not in sys.path:
    sys.path.insert(0, str(PROJECT_DIR))

from backend.guards.market_guard import is_market_open


def test_market_guard_weekday(monkeypatch) -> None:
    """Market guard should allow weekday trading."""

    class MockDate(datetime):
        @classmethod
        def now(cls, tz=None):
            return cls(2024, 1, 3)  # Wednesday

    monkeypatch.setattr("backend.guards.market_guard.datetime", MockDate)
    assert is_market_open() is True


def test_market_guard_weekend(monkeypatch) -> None:
    """Market guard should block Saturday and Sunday trading."""

    class MockDate(datetime):
        @classmethod
        def now(cls, tz=None):
            return cls(2024, 1, 6)  # Saturday

    monkeypatch.setattr("backend.guards.market_guard.datetime", MockDate)
    assert is_market_open() is False
