"""Basic risk validation for demo pipeline."""

from __future__ import annotations


def check_risk(signal: str) -> bool:
    """Allow BUY/SELL and reject HOLD."""
    return signal in {"BUY", "SELL"}
