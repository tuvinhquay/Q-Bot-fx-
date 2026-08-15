"""Market order execution helpers for Q-Bot-FX."""

from __future__ import annotations

import logging
from typing import Any

from config.settings import (
    LIVE_TRADING_ENABLED,
    TRADING_ENABLED,
    TRADING_MODE,
)

import MetaTrader5 as mt5

LOGGER = logging.getLogger(__name__)


# ==========================================================
# PART 1 — FOUNDATION / CONFIGURATION
# ==========================================================

class TradeExecutor:
    """Execute market orders through MetaTrader5."""

    def __init__(
        self,
        live_trading_enabled: bool | None = None,
    ) -> None:

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



    # ==========================================================
    # PART 2 — VOLUME NORMALIZATION / VALIDATION
    # ==========================================================

    def _normalize_volume(
        self,
        volume: float,
        min_volume: float,
        max_volume: float,
        volume_step: float,
    ) -> float:
        """Normalize trade volume according to broker constraints."""

        if volume_step <= 0:
            return float(volume)

        normalized = round(
            volume / volume_step
        ) * volume_step

        normalized = max(
            normalized,
            min_volume,
        )

        if max_volume > 0:
            normalized = min(
                normalized,
                max_volume,
            )

        return float(
            round(
                normalized,
                8,
            )
        )

    # ==========================================================
    # PART 3 — SL / TP VALIDATION
    # ==========================================================

    @staticmethod
    def _is_sl_tp_valid(
        signal: str,
        price: float,
        stop_loss: float | None,
        take_profit: float | None,
    ) -> bool:
        """Validate stop-loss and take-profit price levels."""

        if stop_loss is None or take_profit is None:
            return False

        if stop_loss <= 0 or take_profit <= 0:
            return False

        if signal == "BUY":
            return stop_loss < price < take_profit

        if signal == "SELL":
            return take_profit < price < stop_loss

        return False

# ==========================================================
# PART 4 — ORDER PREPARATION
# ==========================================================

    @staticmethod
    def _get_order_type(
        signal: str,
    ) -> int | None:
        """Convert strategy signal into MT5 order type."""

        if signal == "BUY":
            return mt5.ORDER_TYPE_BUY

        if signal == "SELL":
            return mt5.ORDER_TYPE_SELL

        return None


    def _prepare_order_request(
        self,
        symbol: str,
        signal: str,
        volume: float,
        price: float,
        stop_loss: float,
        take_profit: float,
    ) -> dict[str, Any] | None:
        """
        Build a validated MT5 market-order request.

        This PART only prepares the request.
        It does NOT send the order to MT5.
        """

        order_type = self._get_order_type(
            signal
        )

        if order_type is None:
            LOGGER.error(
                "Invalid trade signal: %s",
                signal,
            )
            return None

        if not symbol:
            LOGGER.error(
                "Trade symbol is empty."
            )
            return None

        if volume <= 0:
            LOGGER.error(
                "Invalid trade volume: %s",
                volume,
            )
            return None

        if price <= 0:
            LOGGER.error(
                "Invalid market price: %s",
                price,
            )
            return None

        if not self._is_sl_tp_valid(
            signal,
            price,
            stop_loss,
            take_profit,
        ):
            LOGGER.error(
                "Invalid SL/TP for %s: "
                "price=%s sl=%s tp=%s",
                signal,
                price,
                stop_loss,
                take_profit,
            )
            return None

        request: dict[str, Any] = {
            "action": mt5.TRADE_ACTION_DEAL,
            "symbol": symbol,
            "volume": float(volume),
            "type": order_type,
            "price": float(price),
            "sl": float(stop_loss),
            "tp": float(take_profit),
            "deviation": self.deviation,
            "magic": self.magic,
            "comment": self.comment,
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": mt5.ORDER_FILLING_IOC,
        }

        return request

# ==========================================================
# PART 5 — ORDER SENDING
# ==========================================================

    def _send_order(
        self,
        request: dict[str, Any],
    ) -> tuple[bool, int | None]:
        """
        Send a prepared market-order request to MetaTrader 5.

        This PART is responsible only for sending the request.
        It does not prepare or modify the order.
        """

        if not request:
            LOGGER.error(
                "Cannot send empty order request."
            )
            return False, None

        if not self.trading_enabled:
            LOGGER.info(
                "Trading disabled by configuration. "
                "Order not sent."
            )
            return False, None

        if not self.live_trading_enabled:
            LOGGER.info(
                "Live trading disabled. "
                "Dry-run mode active. Order not sent."
            )
            return False, None

        try:
            result = mt5.order_send(request)
        except Exception as error:
            LOGGER.exception(
                "Exception while sending MT5 order: %s",
                error,
            )
            return False, None

        if result is None:
            LOGGER.error(
                "MT5 order_send returned None."
            )
            return False, None

        success_codes = {
            mt5.TRADE_RETCODE_DONE,
            getattr(
                mt5,
                "TRADE_RETCODE_PLACED",
                None,
            ),
        }

        if result.retcode not in success_codes:
            LOGGER.error(
                "MT5 order failed: "
                "retcode=%s comment=%s",
                result.retcode,
                getattr(
                    result,
                    "comment",
                    "n/a",
                ),
            )
            return False, None

        ticket = getattr(
            result,
            "order",
            None,
        )

        if ticket is None:
            LOGGER.error(
                "MT5 order succeeded but "
                "no order ticket was returned."
            )
            return False, None

        LOGGER.info(
            "MT5 order sent successfully: "
            "ticket=%s retcode=%s",
            ticket,
            result.retcode,
        )

        return True, int(ticket)        

# ==========================================================
# PART 6 — ORDER VERIFICATION
# ==========================================================

    def _verify_order(
        self,
        ticket: int,
        symbol: str,
    ) -> bool:
        """
        Verify that an executed order has an
        associated open position.

        This PART only verifies the result.
        It does NOT send, modify, or close orders.
        """

        if ticket <= 0:
            return False

        if not symbol:
            return False

        try:
            positions = mt5.positions_get(
                symbol=symbol,
            )

        except Exception as error:
            LOGGER.warning(
                "Unable to verify position "
                "for %s: %s",
                symbol,
                error,
            )
            return False

        if positions is None:
            return False

        for position in positions:

            position_ticket = getattr(
                position,
                "ticket",
                None,
            )

            if position_ticket == ticket:

                LOGGER.info(
                    "Order verification successful: "
                    "ticket=%s symbol=%s",
                    ticket,
                    symbol,
                )

                return True

        LOGGER.warning(
            "Order verification failed: "
            "ticket=%s symbol=%s",
            ticket,
            symbol,
        )

        return False


# ==========================================================
# PART 7 — POSITION MANAGEMENT
# ==========================================================

    def has_open_position(
        self,
        symbol: str,
    ) -> bool:
        """
        Check whether the specified symbol
        currently has an open position.
        """

        if not symbol:
            return False

        try:
            positions = mt5.positions_get(
                symbol=symbol,
            )

        except Exception as error:
            LOGGER.warning(
                "Unable to query position "
                "for %s: %s",
                symbol,
                error,
            )
            return False

        if positions is None:
            return False

        return len(positions) > 0


    def count_open_positions(
        self,
    ) -> int:
        """
        Return the total number of open
        MT5 positions.
        """

        try:
            positions = mt5.positions_get()

        except Exception as error:
            LOGGER.warning(
                "Unable to query open positions: %s",
                error,
            )
            return 0

        if positions is None:
            return 0

        return len(positions)

# ==========================================================
# PART 8 — PUBLIC EXECUTION FLOW
# ==========================================================

    def execute_market_order(
        self,
        symbol: str,
        signal: str,
        volume: float,
        price: float,
        stop_loss: float,
        take_profit: float,
    ) -> tuple[bool, int | None]:
        """
        Execute the complete validated market-order flow.

        Flow:

            Validate
                ↓
            Prepare Request
                ↓
            Send Order
                ↓
            Verify Order
                ↓
            Return Result

        This method is the final execution interface
        for higher-level strategy / signal components.
        """

        if not symbol:
            LOGGER.error(
                "Execution rejected: empty symbol."
            )
            return False, None

        if signal not in {
            "BUY",
            "SELL",
        }:
            LOGGER.error(
                "Execution rejected: invalid signal=%s",
                signal,
            )
            return False, None

        if volume <= 0:
            LOGGER.error(
                "Execution rejected: invalid volume=%s",
                volume,
            )
            return False, None

        if price <= 0:
            LOGGER.error(
                "Execution rejected: invalid price=%s",
                price,
            )
            return False, None

        if not self._is_sl_tp_valid(
            signal,
            price,
            stop_loss,
            take_profit,
        ):
            LOGGER.error(
                "Execution rejected: invalid SL/TP."
            )
            return False, None

        request = self._prepare_order_request(
            symbol=symbol,
            signal=signal,
            volume=volume,
            price=price,
            stop_loss=stop_loss,
            take_profit=take_profit,
        )

        if request is None:
            LOGGER.error(
                "Execution rejected: "
                "order request preparation failed."
            )
            return False, None

        sent, ticket = self._send_order(
            request
        )

        if not sent:
            LOGGER.error(
                "Execution failed during order send."
            )
            return False, None

        if ticket is None:
            LOGGER.error(
                "Execution failed: "
                "missing order ticket."
            )
            return False, None

        if not self._verify_order(
            ticket=ticket,
            symbol=symbol,
        ):
            LOGGER.warning(
                "Order sent but position "
                "verification failed: "
                "ticket=%s symbol=%s",
                ticket,
                symbol,
            )
            return False, ticket

        LOGGER.info(
            "Market order execution completed: "
            "signal=%s symbol=%s volume=%s ticket=%s",
            signal,
            symbol,
            volume,
            ticket,
        )

        return True, ticket        