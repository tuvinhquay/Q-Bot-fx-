"""Market order execution helpers for Q-Bot-FX."""

from __future__ import annotations

import logging
from typing import Any

import MetaTrader5 as mt5

LOGGER = logging.getLogger(__name__)


class TradeExecutor:
    """Execute market orders through MetaTrader5."""

    def __init__(self) -> None:
        self.deviation = 20
        self.magic = 2025
        self.comment = "QBOT"

    def open_market_order(self, symbol: str, signal: str, lot: float) -> tuple[bool, int | None]:
        """Open a market order for the given symbol, signal and lot size."""
        order_type = self._get_order_type(signal)
        if order_type is None:
            LOGGER.error("Invalid trade signal: %s", signal)
            return False, None

        if not mt5.symbol_select(symbol, True):
            LOGGER.warning("Could not select symbol %s before order send.", symbol)

        tick = mt5.symbol_info_tick(symbol)
        if tick is None:
            LOGGER.error("Failed to fetch tick data for %s.", symbol)
            return None

        price = tick.ask if order_type == mt5.ORDER_TYPE_BUY else tick.bid
        request = {
            "action": mt5.TRADE_ACTION_DEAL,
            "symbol": symbol,
            "volume": float(lot),
            "type": order_type,
            "price": price,
            "deviation": self.deviation,
            "magic": self.magic,
            "comment": self.comment,
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": mt5.ORDER_FILLING_IOC,
        }

        result = mt5.order_send(request)
        if result is None:
            LOGGER.error("Order send returned None for %s.", symbol)
            return False, None

        if result.retcode != mt5.TRADE_RETCODE_DONE:
            LOGGER.error(
                "Order failed for %s: retcode=%s comment=%s",
                symbol,
                result.retcode,
                getattr(result, "comment", "n/a"),
            )
            return False, None

        price_result = getattr(result, "price_current", price)
        LOGGER.info("Order sent success: ticket=%s price=%s", result.order, price_result)
        return True, int(result.order)

    def has_open_position(self, symbol: str) -> bool:
        """Return True if there is an open position for the given symbol."""
        positions = mt5.positions_get(symbol=symbol)
        return bool(positions)

    @staticmethod
    def _get_order_type(signal: str) -> int | None:
        if signal == "BUY":
            return mt5.ORDER_TYPE_BUY
        if signal == "SELL":
            return mt5.ORDER_TYPE_SELL
        return None
