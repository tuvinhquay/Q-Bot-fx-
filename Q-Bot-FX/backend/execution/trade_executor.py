"""Market order execution helpers for Q-Bot-FX."""

from __future__ import annotations

import logging
from typing import Any

from config.settings import LIVE_TRADING_ENABLED, TRADING_ENABLED, TRADING_MODE
import MetaTrader5 as mt5

LOGGER = logging.getLogger(__name__)


class TradeExecutor:
    """Execute market orders through MetaTrader5."""

    def __init__(self, live_trading_enabled: bool | None = None) -> None:
        self.deviation = 20
        self.magic = 2025
        self.comment = "QBOT"
        self.live_trading_enabled = (
            LIVE_TRADING_ENABLED
            if live_trading_enabled is None
            else live_trading_enabled
        )
        self.trading_enabled = TRADING_ENABLED
        self.trading_mode = TRADING_MODE

    def _normalize_volume(
        self,
        volume: float,
        min_volume: float,
        max_volume: float,
        volume_step: float,
    ) -> float:
        if volume_step <= 0:
            return float(volume)

        normalized = round(volume / volume_step) * volume_step
        normalized = max(normalized, min_volume)
        if max_volume > 0:
            normalized = min(normalized, max_volume)

        return float(round(normalized, 8))

    @staticmethod
    def _is_sl_tp_valid(
        signal: str,
        price: float,
        stop_loss: float | None,
        take_profit: float | None,
    ) -> bool:
        if stop_loss is None or take_profit is None:
            return False
        if stop_loss <= 0 or take_profit <= 0:
            return False

        if signal == "BUY":
            return stop_loss < price < take_profit
        if signal == "SELL":
            return take_profit < price < stop_loss
        return False

    def open_market_order(
        self,
        symbol: str,
        signal: str,
        lot: float,
        stop_loss: float | None = None,
        take_profit: float | None = None,
    ) -> tuple[bool, int | None]:
        """Open a market order for the given symbol, signal and lot size."""
        order_type = self._get_order_type(signal)
        if order_type is None:
            LOGGER.error("Invalid trade signal: %s", signal)
            return False, None

        if not self.trading_enabled:
            LOGGER.info(
                "Execution disabled by configuration (mode=%s). Order not sent: %s %s %s",
                self.trading_mode,
                signal,
                symbol,
                lot,
            )
            return False, None

        if not self.live_trading_enabled:
            LOGGER.info(
                "Live trading disabled. Dry-run mode active. Order not sent: %s %s %s",
                signal,
                symbol,
                lot,
            )
            return False, None

        symbol_info = mt5.symbol_info(symbol)
        if symbol_info is None:
            LOGGER.error("Symbol information unavailable for %s.", symbol)
            return False, None

        if not mt5.symbol_select(symbol, True):
            LOGGER.error(
                "Could not select symbol %s before order send: %s",
                symbol,
                mt5.last_error(),
            )
            return False, None

        tick = mt5.symbol_info_tick(symbol)
        if tick is None:
            LOGGER.error("Failed to fetch tick data for %s.", symbol)
            return False, None

        price = tick.ask if order_type == mt5.ORDER_TYPE_BUY else tick.bid

        if not self._is_sl_tp_valid(signal, price, stop_loss, take_profit):
            LOGGER.error(
                "Invalid SL/TP levels for %s order: price=%s sl=%s tp=%s",
                signal,
                price,
                stop_loss,
                take_profit,
            )
            return False, None

        volume = float(lot)
        volume_min = float(getattr(symbol_info, "volume_min", 0.0) or 0.0)
        volume_max = float(getattr(symbol_info, "volume_max", 0.0) or 0.0)
        volume_step = float(getattr(symbol_info, "volume_step", 0.0) or 0.0)
        if volume_min > 0 and volume < volume_min:
            LOGGER.error(
                "Volume below minimum for %s: %s < %s",
                symbol,
                volume,
                volume_min,
            )
            return False, None
        if volume_max > 0 and volume > volume_max:
            LOGGER.error(
                "Volume above maximum for %s: %s > %s",
                symbol,
                volume,
                volume_max,
            )
            return False, None

        if volume_step > 0:
            normalized_volume = self._normalize_volume(volume, volume_min or 0.01, volume_max, volume_step)
            if normalized_volume != volume:
                LOGGER.info(
                    "Adjusting volume for %s: requested=%s normalized=%s step=%s",
                    symbol,
                    volume,
                    normalized_volume,
                    volume_step,
                )
            volume = normalized_volume

        request = {
            "action": mt5.TRADE_ACTION_DEAL,
            "symbol": symbol,
            "volume": float(volume),
            "type": order_type,
            "price": price,
            "deviation": self.deviation,
            "magic": self.magic,
            "comment": self.comment,
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": mt5.ORDER_FILLING_IOC,
        }

        if stop_loss is not None and stop_loss > 0:
            request["sl"] = float(stop_loss)
        if take_profit is not None and take_profit > 0:
            request["tp"] = float(take_profit)

        result = mt5.order_send(request)
        if result is None:
            LOGGER.error("Order send returned None for %s.", symbol)
            return False, None

        success_codes = {
            mt5.TRADE_RETCODE_DONE,
            getattr(mt5, "TRADE_RETCODE_PLACED", None),
        }

        if result.retcode not in success_codes:
            LOGGER.error(
                "Order failed for %s: retcode=%s comment=%s",
                symbol,
                result.retcode,
                getattr(result, "comment", "n/a"),
            )
            return False, None

        order_ticket = getattr(result, "order", None)
        if order_ticket is None:
            LOGGER.warning(
                "Order send completed without a ticket for %s: retcode=%s",
                symbol,
                result.retcode,
            )
            return False, None

        try:
            positions = mt5.positions_get(ticket=order_ticket)
        except Exception as error:
            LOGGER.warning(
                "Unable to verify open position for order %s: %s",
                order_ticket,
                error,
            )
            positions = None

        if positions is None or len(positions) == 0:
            LOGGER.warning(
                "Order %s for %s returned success retcode but open position could not be verified.",
                order_ticket,
                symbol,
            )
        else:
            LOGGER.info(
                "Verified open position for ticket=%s symbol=%s",
                order_ticket,
                symbol,
            )

        price_result = getattr(result, "price_current", price)
        LOGGER.info(
            "Order sent success: ticket=%s price=%s retcode=%s",
            order_ticket,
            price_result,
            result.retcode,
        )
        return True, int(order_ticket)

    def has_open_position(self, symbol: str) -> bool:
        """Return True if there is an open position for the given symbol."""
        positions = mt5.positions_get(symbol=symbol)
        return bool(positions)

    def count_open_positions(self) -> int:
        """Return the total number of currently open MT5 positions."""
        positions = mt5.positions_get()
        if positions is None:
            return 0
        return len(positions)

    @staticmethod
    def _get_order_type(signal: str) -> int | None:
        if signal == "BUY":
            return mt5.ORDER_TYPE_BUY
        if signal == "SELL":
            return mt5.ORDER_TYPE_SELL
        return None
