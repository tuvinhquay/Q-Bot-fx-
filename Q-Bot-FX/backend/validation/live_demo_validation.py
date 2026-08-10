"""Safe live demo validation runner for Q-Bot-FX."""

from __future__ import annotations

import logging
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import MetaTrader5 as mt5

from backend.analysis.strategy_engine import generate_signal
from backend.execution.trade_executor import TradeExecutor
from backend.mt5.connector import MT5Connector
from backend.guards.market_guard import is_market_open
from backend.notifications.telegram_notifier import TelegramNotifier
from backend.services.deployment.runtime_checker import check_runtime_environment
from backend.services.mt5.auto_login_engine import MT5AutoLoginEngine
from config.settings import Settings

LOGGER = logging.getLogger(__name__)

PROJECT_ROOT = Path(__file__).resolve().parents[2]


@dataclass
class LiveDemoValidationResult:
    success: bool = False
    errors: list[str] = None
    warnings: list[str] = None
    runtime_status: dict[str, Any] | None = None
    mt5_connected: bool = False
    trade_allowed: bool = False
    account_login: int | None = None
    account_balance: float | None = None
    account_equity: float | None = None
    market_open: bool = False
    account_trade_allowed: bool | None = None
    symbol: str | None = None
    volume: float | None = None
    tick_ask: float | None = None
    tick_bid: float | None = None
    signal: str | None = None
    sl: float | None = None
    tp: float | None = None
    order_sent: bool = False
    order_ticket: int | None = None
    position_verified: bool = False
    position_info: dict[str, Any] | None = None
    telegram_message_id: int | None = None

    def __post_init__(self) -> None:
        self.errors = self.errors or []
        self.warnings = self.warnings or []


def _format_error(message: str) -> str:
    LOGGER.error(message)
    return message


def _format_warning(message: str) -> str:
    LOGGER.warning(message)
    return message


def _resolve_validation_symbol(settings: Settings) -> str:
    if settings.FORCE_SIGNAL_MODE and settings.FORCE_SIGNAL_SYMBOL:
        return settings.FORCE_SIGNAL_SYMBOL
    if settings.SYMBOLS:
        return settings.SYMBOLS[0]
    return "EURUSDm"


def _validate_mt5_environment(result: LiveDemoValidationResult, settings: Settings) -> bool:
    runtime_state = check_runtime_environment(PROJECT_ROOT)
    result.runtime_status = runtime_state
    if runtime_state.get("status") != "PASS":
        result.errors.append(
            _format_error(
                "Runtime environment validation failed. Review runtime_status before trading."
            )
        )
        return False

    login_result = MT5AutoLoginEngine().connect()
    if not login_result.success:
        result.errors.append(_format_error(f"MT5 connection failed: {login_result.error}"))
        return False

    result.mt5_connected = True
    result.account_login = login_result.account_login

    terminal_info = mt5.terminal_info()
    account_info = mt5.account_info()

    if terminal_info is None:
        result.errors.append(_format_error("MT5 terminal information not available."))
        return False

    result.trade_allowed = bool(getattr(terminal_info, "trade_allowed", False))
    if not result.trade_allowed:
        result.errors.append(_format_error("MT5 terminal auto trading is disabled. Enable AutoTrading in the terminal."))
        return False

    if account_info is not None:
        result.account_balance = float(getattr(account_info, "balance", 0.0) or 0.0)
        result.account_equity = float(getattr(account_info, "equity", 0.0) or 0.0)
        trade_allowed = getattr(account_info, "trade_allowed", None)
        if trade_allowed is None:
            result.account_trade_allowed = None
            result.warnings.append(
                _format_warning(
                    "MT5 account trade_allowed field unavailable."
                )
            )
        else:
            result.account_trade_allowed = bool(trade_allowed)
            if not result.account_trade_allowed:
                result.errors.append(
                    _format_error(
                        "MT5 account trade_allowed is disabled."
                    )
                )
                return False
    else:
        result.warnings.append(_format_warning("Could not read MT5 account information."))

    if not _validate_market_session(result):
        return False

    return True


def _validate_market_session(result: LiveDemoValidationResult) -> bool:
    result.market_open = is_market_open()
    if not result.market_open:
        result.errors.append(_format_error("Market is currently closed."))
        return False
    return True


def _validate_symbol(result: LiveDemoValidationResult, settings: Settings) -> bool:
    if result.symbol is None:
        result.errors.append(_format_error("No symbol available for validation."))
        return False

    symbol_info = mt5.symbol_info(result.symbol)
    if symbol_info is None:
        result.errors.append(_format_error(f"Symbol '{result.symbol}' is not available in the broker terminal."))
        return False

    if not mt5.symbol_select(result.symbol, True):
        result.errors.append(_format_error(f"Failed to select symbol '{result.symbol}' in MarketWatch."))
        return False

    if not _validate_volume(result, symbol_info):
        return False

    if not _validate_tick_data(result):
        return False

    return True


def _validate_volume(result: LiveDemoValidationResult, symbol_info: Any) -> bool:
    lot = 0.01
    result.volume = lot

    volume_min = float(getattr(symbol_info, "volume_min", 0.0) or 0.0)
    volume_max = float(getattr(symbol_info, "volume_max", 0.0) or 0.0)
    volume_step = float(getattr(symbol_info, "volume_step", 0.0) or 0.0)

    if volume_min > 0 and lot < volume_min:
        result.errors.append(
            _format_error(
                f"Lot size {lot} is below minimum {volume_min} for {result.symbol}."
            )
        )
        return False

    if volume_max > 0 and lot > volume_max:
        result.errors.append(
            _format_error(
                f"Lot size {lot} is above maximum {volume_max} for {result.symbol}."
            )
        )
        return False

    if volume_step > 0:
        normalized = round(lot / volume_step) * volume_step
        if abs(normalized - lot) > 1e-8:
            result.errors.append(
                _format_error(
                    f"Lot size {lot} does not match step {volume_step} for {result.symbol}."
                )
            )
            return False

    return True


def _validate_tick_data(result: LiveDemoValidationResult) -> bool:
    tick = mt5.symbol_info_tick(result.symbol)
    if tick is None:
        result.errors.append(_format_error(f"Failed to fetch tick data for {result.symbol}."))
        return False

    result.tick_ask = float(getattr(tick, "ask", 0.0) or 0.0)
    result.tick_bid = float(getattr(tick, "bid", 0.0) or 0.0)

    if result.tick_ask <= 0 or result.tick_bid <= 0:
        result.errors.append(
            _format_error(
                f"Invalid tick bid/ask for {result.symbol}: bid={result.tick_bid} ask={result.tick_ask}."
            )
        )
        return False

    return True


def _verify_order_position(result: LiveDemoValidationResult, ticket: int) -> bool:
    positions = mt5.positions_get(ticket=ticket)
    if positions is None or len(positions) == 0:
        result.errors.append(
            _format_error(
                f"Position verification failed for ticket {ticket}. No position found."
            )
        )
        return False

    position = positions[0]
    symbol = getattr(position, "symbol", None)
    volume = float(getattr(position, "volume", 0.0) or 0.0)
    position_type = int(getattr(position, "type", -1))
    price_open = float(getattr(position, "price_open", 0.0) or 0.0)
    sl = float(getattr(position, "sl", 0.0) or 0.0)
    tp = float(getattr(position, "tp", 0.0) or 0.0)

    if symbol != result.symbol:
        result.errors.append(_format_error(f"Position symbol mismatch: expected {result.symbol}, got {symbol}."))
        return False

    if result.volume is not None and abs(volume - result.volume) > 1e-8:
        result.errors.append(
            _format_error(
                f"Position volume mismatch: expected {result.volume}, got {volume}."
            )
        )
        return False

    direction = "BUY" if position_type == mt5.ORDER_TYPE_BUY else "SELL" if position_type == mt5.ORDER_TYPE_SELL else "UNKNOWN"
    if direction != result.signal:
        result.errors.append(
            _format_error(
                f"Position direction mismatch: expected {result.signal}, got {direction}."
            )
        )
        return False

    if sl <= 0 or tp <= 0:
        result.errors.append(
            _format_error(
                f"Position SL/TP invalid: sl={sl} tp={tp}."
            )
        )
        return False

    result.position_verified = True
    result.position_info = {
        "ticket": ticket,
        "symbol": symbol,
        "volume": volume,
        "direction": direction,
        "entry": price_open,
        "sl": sl,
        "tp": tp,
    }
    return True


def _build_telegram_message(result: LiveDemoValidationResult, settings: Settings) -> str:
    lines = ["Q-BOT-FX Live Demo Validation Report"]
    lines.append(f"Project root: {PROJECT_ROOT}")
    lines.append(f"MT5 connected: {result.mt5_connected}")
    lines.append(f"Trade allowed: {result.trade_allowed}")
    lines.append(f"Account: {result.account_login or 'UNKNOWN'}")
    if result.account_balance is not None:
        lines.append(f"Balance: {result.account_balance:.2f}")
    if result.account_equity is not None:
        lines.append(f"Equity: {result.account_equity:.2f}")
    lines.append(f"Symbol: {result.symbol}")
    lines.append(f"Signal: {result.signal or 'HOLD'}")
    if result.signal in {"BUY", "SELL"}:
        lines.append(f"SL: {result.sl:.5f}")
        lines.append(f"TP: {result.tp:.5f}")
    lines.append(f"Order sent: {result.order_sent}")
    if result.order_ticket is not None:
        lines.append(f"Order ticket: {result.order_ticket}")

    if result.errors:
        lines.append("Errors:")
        lines.extend(f"- {error}" for error in result.errors)
    if result.warnings:
        lines.append("Warnings:")
        lines.extend(f"- {warning}" for warning in result.warnings)

    return "\n".join(lines)


def run_live_demo_validation(
    execute_demo_order: bool = False,
    notify_telegram: bool = False,
) -> LiveDemoValidationResult:
    settings = Settings()
    result = LiveDemoValidationResult()
    result.symbol = _resolve_validation_symbol(settings)

    if not _validate_mt5_environment(result, settings):
        result.success = False
        if notify_telegram:
            TelegramNotifier(settings).send(_build_telegram_message(result, settings))
        return result

    if not _validate_symbol(result, settings):
        result.success = False
        if notify_telegram:
            TelegramNotifier(settings).send(_build_telegram_message(result, settings))
        return result

    connector = MT5Connector(settings)
    if not connector.connect():
        result.errors.append(_format_error("MT5 connector failed to connect for market data."))
        result.success = False
        if notify_telegram:
            TelegramNotifier(settings).send(_build_telegram_message(result, settings))
        return result

    result.market_data = connector.get_rates(symbol=result.symbol, timeframe=mt5.TIMEFRAME_H1, n=50)
    if result.market_data is None or result.market_data.empty:
        result.errors.append(_format_error("Insufficient market data for symbol validation."))
        result.success = False
        if notify_telegram:
            TelegramNotifier(settings).send(_build_telegram_message(result, settings))
        return result

    signal_data = generate_signal(result.symbol)
    result.signal = signal_data.action
    result.sl = float(signal_data.sl or 0.0)
    result.tp = float(signal_data.tp or 0.0)

    if result.signal not in {"BUY", "SELL"}:
        result.warnings.append(_format_warning("Signal generator returned HOLD or no valid trade signal."))
        result.success = True
        if notify_telegram:
            TelegramNotifier(settings).send(_build_telegram_message(result, settings))
        return result

    if result.tick_ask is None or result.tick_bid is None:
        result.errors.append(_format_error("Tick prices unavailable for SL/TP validation."))
        result.success = False
        if notify_telegram:
            TelegramNotifier(settings).send(_build_telegram_message(result, settings))
        return result

    current_price = result.tick_ask if result.signal == "BUY" else result.tick_bid
    if not TradeExecutor()._is_sl_tp_valid(result.signal, current_price, result.sl, result.tp):
        result.errors.append(_format_error("Generated SL/TP levels are invalid for the current market price."))
        result.success = False
        if notify_telegram:
            TelegramNotifier(settings).send(_build_telegram_message(result, settings))
        return result

    if execute_demo_order:
        if not settings.LIVE_TRADING_ENABLED:
            result.errors.append(_format_error("Live trading is disabled in settings. Set LIVE_TRADING_ENABLED=true to send a demo order."))
            result.success = False
            if notify_telegram:
                TelegramNotifier(settings).send(_build_telegram_message(result, settings))
            return result

        executor = TradeExecutor()
        sent, ticket = executor.open_market_order(
            symbol=result.symbol,
            signal=result.signal,
            lot=result.volume or 0.01,
            stop_loss=result.sl,
            take_profit=result.tp,
        )
        result.order_sent = sent
        result.order_ticket = ticket
        result.success = sent

        if not sent:
            result.errors.append(_format_error("Demo order execution failed during order send."))
            if notify_telegram:
                TelegramNotifier(settings).send(_build_telegram_message(result, settings))
            return result

        if ticket is None:
            result.errors.append(_format_error("Order returned success without ticket."))
            result.success = False
            if notify_telegram:
                TelegramNotifier(settings).send(_build_telegram_message(result, settings))
            return result

        if not _verify_order_position(result, ticket):
            result.success = False
            if notify_telegram:
                TelegramNotifier(settings).send(_build_telegram_message(result, settings))
            return result

        result.warnings.append(_format_warning("Demo order executed and position verified successfully."))
    else:
        result.success = True

    if notify_telegram:
        notification_result = TelegramNotifier(settings).send(_build_telegram_message(result, settings))
        if isinstance(notification_result, dict):
            message = notification_result.get("result") or {}
            if isinstance(message, dict) and isinstance(message.get("message_id"), int):
                result.telegram_message_id = int(message["message_id"])

    return result


def main() -> int:
    execute = "--execute" in sys.argv or "--send-order" in sys.argv
    notify = "--notify" in sys.argv
    result = run_live_demo_validation(execute_demo_order=execute, notify_telegram=notify)
    print(_build_telegram_message(result, Settings()))
    return 0 if result.success else 1


if __name__ == "__main__":
    raise SystemExit(main())
