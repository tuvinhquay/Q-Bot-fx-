"""Basic risk validation and lot sizing for demo pipeline."""

from __future__ import annotations


def check_risk(signal: str) -> bool:
    """Allow BUY/SELL and reject HOLD."""
    return signal in {"BUY", "SELL"}


def calculate_lot(balance: float | None, risk_percent: float = 1) -> float:
    """Calculate a demo lot size using account balance and risk percent."""
    if balance is None or balance <= 0:
        return 0.01

    lot = round((balance * risk_percent) / 10000, 2)
    lot = max(lot, 0.01)
    lot = min(lot, 1.0)
    return lot
