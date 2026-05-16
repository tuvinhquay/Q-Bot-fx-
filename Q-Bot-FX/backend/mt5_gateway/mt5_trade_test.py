"""Safe demo trade helper for MetaTrader 5 smoke tests."""

from __future__ import annotations

import logging
from typing import Any

from .mt5_connector import MT5Connector


LOGGER = logging.getLogger(__name__)


def _success_code(mt5: Any) -> int | None:
    return getattr(mt5, "TRADE_RETCODE_DONE", None)


def send_test_trade(symbol: str) -> tuple[bool, str]:
    """Send a very small BUY order with comment CI_TEST for demo verification."""
    connector = MT5Connector()
    try:
        if not connector.connect():
            return False, "MT5 connection/login failed"

        mt5 = connector.mt5
        if mt5 is None:
            return False, "MetaTrader5 module unavailable"

        symbol_data = connector.symbol_info(symbol)
        if symbol_data is None:
            return False, f"Symbol {symbol} not found"

        if not getattr(symbol_data, "visible", True) and not mt5.symbol_select(symbol, True):
            return False, f"Symbol {symbol} is not visible and could not be selected"

        tick = mt5.symbol_info_tick(symbol)
        if tick is None or getattr(tick, "ask", 0) <= 0:
            return False, f"No valid ask price for {symbol}"

        request = {
            "action": mt5.TRADE_ACTION_DEAL,
            "symbol": symbol,
            "volume": 0.01,
            "type": mt5.ORDER_TYPE_BUY,
            "price": tick.ask,
            "deviation": 20,
            "magic": 130013,
            "comment": "CI_TEST",
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": mt5.ORDER_FILLING_IOC,
        }
        result = mt5.order_send(request)
        if result is None:
            return False, f"order_send returned None: {mt5.last_error()}"

        retcode = getattr(result, "retcode", None)
        if retcode == _success_code(mt5):
            return True, f"Test trade sent successfully: retcode={retcode}"

        message = getattr(result, "comment", "unknown MT5 response")
        LOGGER.error("Test trade failed: retcode=%s message=%s", retcode, message)
        return False, f"Test trade failed: retcode={retcode} message={message}"
    finally:
        connector.shutdown()
