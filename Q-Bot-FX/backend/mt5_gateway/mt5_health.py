"""Health checks for the MetaTrader 5 gateway."""

from __future__ import annotations

import logging

from .mt5_connector import MT5Connector


LOGGER = logging.getLogger(__name__)


def check_mt5_health() -> bool:
    """Return True when MT5 connects, account info is readable, and equity is positive."""
    connector = MT5Connector()
    try:
        if not connector.connect():
            LOGGER.error("MT5 health failed: connection/login unsuccessful.")
            return False

        account = connector.account_info()
        equity = getattr(account, "equity", 0) if account is not None else 0
        if equity is None or equity <= 0:
            LOGGER.error("MT5 health failed: account equity is not positive (%s).", equity)
            return False

        LOGGER.info("MT5 health ok: equity=%s.", equity)
        return True
    finally:
        connector.shutdown()
