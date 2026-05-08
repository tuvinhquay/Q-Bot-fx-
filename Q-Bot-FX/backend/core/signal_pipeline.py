"""Core signal pipeline for Q-Bot-FX trade execution."""

from __future__ import annotations

import logging
from datetime import datetime

from backend.data.market_data import get_latest_market_data
from backend.execution.trade_executor import TradeExecutor
from backend.mt5.connector import MT5Connector
from backend.risk.risk_manager import calculate_lot, check_risk
from backend.services.telegram_service import TelegramService
from backend.strategy.demo_strategy import generate_signal
from config.settings import Settings

LOGGER = logging.getLogger(__name__)


def run_signal_pipeline(settings: Settings) -> None:
    connector = MT5Connector(settings)
    connected = connector.connect()
    LOGGER.info("MT5 connected: %s", "OK" if connected else "WARNING")
    if not connected:
        LOGGER.warning("MT5 connection failed, stopping pipeline.")
        return

    candles = get_latest_market_data(connector)
    LOGGER.info("Fetched candles: %s", len(candles))

    signal_data = generate_signal(candles)
    signal = signal_data.get("signal", "HOLD")
    LOGGER.info("Signal: %s", signal)

    if signal == "HOLD":
        LOGGER.info("No trade signal, stopping pipeline.")
        return

    if not check_risk(signal):
        LOGGER.info("Risk check failed, stopping pipeline.")
        return

    symbol = settings.SYMBOLS[0]
    executor = TradeExecutor()
    if executor.has_open_position(symbol):
        LOGGER.info("Existing open position for %s, skipping new order.", symbol)
        return

    account_info = connector.get_account_info()
    balance = account_info.get("balance")
    LOGGER.info("Account balance: %s", balance)

    lot = calculate_lot(balance, settings.RISK_PERCENT)
    LOGGER.info("Calculated lot size: %s", lot)

    success, ticket = executor.open_market_order(symbol, signal, lot)
    if not success:
        LOGGER.warning("Order was not placed.")
        return

    LOGGER.info("ORDER SENT SUCCESS: ticket=%s", ticket)

    telegram = TelegramService(settings.TELEGRAM_BOT_TOKEN, settings.TELEGRAM_CHAT_ID)
    message = (
        "🚀 Q-Bot-FX OPEN TRADE\n\n"
        f"Symbol: {symbol}\n"
        f"Signal: {signal}\n"
        f"Lot: {lot}\n"
        f"Time: {datetime.utcnow():%Y-%m-%d %H:%M}\n"
        f"Ticket: {ticket}"
    )
    if not telegram.send_message(message):
        LOGGER.warning("Telegram notification failed.")
