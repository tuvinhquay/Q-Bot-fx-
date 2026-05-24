"""Core signal pipeline for Q-Bot-FX trade execution."""

from __future__ import annotations

import logging
from datetime import datetime

import MetaTrader5 as mt5

from backend.adaptive.adaptive_engine import calculate_adaptive_score
from backend.adaptive.learning_memory import update_learning_memory
from backend.adaptive.market_regime_detector import detect_market_regime
from backend.adaptive.strategy_weight_manager import StrategyWeightManager
from backend.analysis.strategy_engine import generate_signal
from backend.chart.chart_generator import generate_chart
from backend.data.market_data import get_latest_market_data
from backend.execution.trade_executor import TradeExecutor
from backend.guards.market_guard import is_market_open
from backend.mt5.connector import MT5Connector
from backend.notifications.telegram_notifier import TelegramNotifier
from backend.performance.performance_engine import (
    calculate_performance,
    format_performance_report,
    mark_daily_report_sent,
    should_send_daily_report,
)
from backend.performance.trade_logger import log_trade
from backend.portfolio.portfolio_manager import PortfolioManager
from backend.risk.risk_manager import RiskManager, check_risk
from backend.services.telegram_service import TelegramService
from backend.services.telegram.formatter import build_telegram_caption
from backend.services.telegram.status_engine import classify_alert_status
from backend.services.learning.memory_engine import LearningMemoryEngine
from backend.services.capital.capital_manager import CapitalManager
from config.settings import FORCE_SIGNAL_MODE, FORCE_SIGNAL_SYMBOL, FORCE_SIGNAL_TYPE, Settings

LOGGER = logging.getLogger(__name__)


def run_signal_pipeline(settings: Settings) -> str | None:
    # ===== MARKET GUARD =====
    if not is_market_open():
        print("Skip trading cycle: market is closed.")
        return "Market closed"

    connector = MT5Connector(settings)
    connected = connector.connect()
    if not connected:
        LOGGER.error("MT5 init failed")
        raise RuntimeError("MT5 connection failed")

    print("MT5 connected")
    LOGGER.info("MT5 connected: OK")

    candles = get_latest_market_data(connector)
    LOGGER.info("Fetched candles: %s", len(candles))

    symbol = settings.SYMBOLS[0]
    if FORCE_SIGNAL_MODE and symbol == FORCE_SIGNAL_SYMBOL:
        LOGGER.warning("FORCE SIGNAL MODE ENABLED")
        signal = FORCE_SIGNAL_TYPE
        confidence = 0.99
        fake_entry = float(candles["close"].iloc[-1]) if not candles.empty else 0.0
        signal_sl = fake_entry * (0.998 if signal == "BUY" else 1.002)
        signal_tp = fake_entry * (1.004 if signal == "BUY" else 0.996)
        LOGGER.warning("[FORCED SIGNAL] %s %s", FORCE_SIGNAL_TYPE, symbol)
    else:
        signal_data = generate_signal(symbol)
        signal = signal_data.action
        confidence = signal_data.confidence
        signal_sl = signal_data.sl
        signal_tp = signal_data.tp

    LOGGER.info("Signal: %s (confidence=%.2f)", signal, confidence)

    perf_stats = calculate_performance() or {
        "winrate": 0.5,
        "profit_factor": 1.0,
        "expectancy": 0.0,
        "max_drawdown": 0.0,
    }
    market_regime = detect_market_regime(candles)
    adaptive = calculate_adaptive_score(
        symbol=symbol,
        timeframe="H1",
        performance_stats=perf_stats,
        market_regime=market_regime,
    )
    LOGGER.info("[MARKET REGIME] %s", market_regime["regime"])
    LOGGER.info("[ADAPTIVE SCORE] %.2f", adaptive["adaptive_score"])
    LOGGER.info("[AI WEIGHT] %.2f", adaptive["weight"])
    if adaptive["allow_trading"]:
        LOGGER.info("[AI DECISION] Trading Allowed")
    else:
        LOGGER.info("[AI DECISION] Market filtered out")
        signal = "HOLD"

    symbol_data = {}
    for s in settings.SYMBOLS[: min(4, len(settings.SYMBOLS))]:
        symbol_data[s] = connector.get_rates(symbol=s, timeframe=mt5.TIMEFRAME_H1, n=200)

    portfolio_manager = PortfolioManager(max_heat_percent=6.0)
    portfolio_result = portfolio_manager.validate_trade(
        symbol=symbol,
        signal=signal if signal in ["BUY", "SELL"] else "BUY",
        symbol_data=symbol_data,
        performance_stats=perf_stats,
        market_regime=market_regime,
        base_risk_percent=1.0,
    )
    LOGGER.info("[PORTFOLIO HEAT] %.2f%%", portfolio_result["portfolio_heat"])
    if not portfolio_result["allow_trade"]:
        if "Correlation" in portfolio_result["reason"]:
            LOGGER.info("[CORRELATION FILTER] blocked %s", symbol)
        if "exposure" in portfolio_result["reason"]:
            LOGGER.info("[EXPOSURE FILTER] %s", portfolio_result["reason"])
        LOGGER.info("[AI DECISION] Market filtered out")
        signal = "HOLD"
    LOGGER.info("[DYNAMIC RISK] adjusted risk=%.2f%%", portfolio_result["dynamic_risk"])

    # ===== SEND TELEGRAM ALERT =====
    if signal in ["BUY", "SELL"]:
        notifier = TelegramNotifier(settings)
        trade_levels = {
            "entry": float(candles["close"].iloc[-1]) if not candles.empty else 0.0,
            "stop_loss": signal_sl,
            "take_profit": signal_tp,
        }

        chart_df = connector.get_rates(
            symbol=symbol,
            timeframe=mt5.TIMEFRAME_H1,
            n=settings.CANDLES_H1,
        )

        chart_path = generate_chart(
            chart_df,
            symbol=symbol,
            entry=trade_levels["entry"],
            sl=trade_levels["stop_loss"],
            tp=trade_levels["take_profit"],
        )

        LOGGER.info("[TELEGRAM] Sending AI alert...")
        caption = build_telegram_caption(
            signal=signal,
            symbol=symbol,
            trade_levels=trade_levels,
            adaptive=adaptive,
            market_regime=market_regime,
            portfolio_result=portfolio_result,
        )
        LOGGER.info("[TELEGRAM] Caption built successfully")

        notifier.send_photo(chart_path, caption)
        LOGGER.info("[TELEGRAM] Photo sent successfully")

    if signal == "HOLD" and not FORCE_SIGNAL_MODE:
        LOGGER.info("No trade signal, stopping pipeline.")
        return

    if not check_risk(signal):
        LOGGER.info("Risk check failed, stopping pipeline.")
        return

    executor = TradeExecutor()
    risk = RiskManager()

    current_open_trades = executor.count_open_positions()
    if not risk.can_open_new_trade(current_open_trades):
        LOGGER.info("Too many open trades: %s", current_open_trades)
        return "Too many open trades"

    if executor.has_open_position(symbol):
        LOGGER.info("Existing open position for %s, skipping new order.", symbol)
        return

    account_info = connector.get_account_info()
    balance = account_info.get("balance") or risk.account_balance
    LOGGER.info("Account balance: %s", balance)

    if not risk.check_daily_drawdown(balance):
        LOGGER.warning("Daily loss limit reached, stopping trading for today.")
        return "Daily loss limit reached"

    reference_balance = float(getattr(risk, "account_balance", balance) or balance)
    daily_drawdown_pct = ((float(balance) - reference_balance) / reference_balance * 100.0) if reference_balance else 0.0
    capital_manager = CapitalManager()
    capital_state = capital_manager.evaluate(
        base_risk_percent=float(portfolio_result["dynamic_risk"]),
        market_regime=str(market_regime.get("regime", "UNKNOWN")),
        volatility_score=float(market_regime.get("volatility_score", 0.5) or 0.5),
        daily_drawdown_pct=daily_drawdown_pct,
        weekly_drawdown_pct=daily_drawdown_pct,
        floating_drawdown_pct=daily_drawdown_pct,
    )
    risk.risk_per_trade = capital_state["allocated_risk_percent"] / 100.0
    LOGGER.info(
        "[CAPITAL] survival=%s allocated_risk=%.2f%%",
        capital_state["survival_mode"],
        capital_state["allocated_risk_percent"],
    )
    lot = risk.calculate_lot_size(balance, risk.default_stop_loss_pips)
    LOGGER.info("Calculated lot size: %s", lot)

    success, ticket = executor.open_market_order(symbol, signal, lot)
    if not success:
        LOGGER.warning("Order was not placed.")
        return

    LOGGER.info("ORDER SENT SUCCESS: ticket=%s", ticket)

    entry_price = float(candles["close"].iloc[-1]) if not candles.empty else 0.0
    # Estimated profit at TP for journaling stats in live signal testing flow.
    expected_profit = abs(signal_tp - entry_price) * float(lot) * 100000
    log_trade(symbol, signal, lot, entry_price, signal_sl, signal_tp, expected_profit)

    stats = calculate_performance()
    report = format_performance_report(stats)
    LOGGER.info("[PERFORMANCE]\n%s", report)
    if stats:
        key = f"{symbol}_H1"
        manager = StrategyWeightManager()
        manager.update_weight(key, stats)
        update_learning_memory(key, market_regime["regime"], stats)

    learning_status = classify_alert_status(
        ai_score=float(adaptive.get("adaptive_score", 0.0)),
        dynamic_risk=float(portfolio_result.get("dynamic_risk", 0.0)),
        portfolio_heat=float(portfolio_result.get("portfolio_heat", 0.0)),
        correlation_risk=str(portfolio_result.get("correlation_risk", "LOW")),
    )
    learning_engine = LearningMemoryEngine()
    learning_engine.record_trade(
        symbol=symbol,
        signal=signal,
        market_regime=str(market_regime.get("regime", "UNKNOWN")),
        ai_score=float(adaptive.get("adaptive_score", 0.0)),
        risk_level=learning_status.level,
        correlation_risk=str(portfolio_result.get("correlation_risk", "LOW")),
        directional_bias=str(portfolio_result.get("directional_bias", "NEUTRAL")),
        trade_result="OPEN",
        pnl=expected_profit,
        timeframe="H1",
    )
    LOGGER.info("[LEARNING REPORT]\n%s", learning_engine.build_report())

    telegram = TelegramService(settings.TELEGRAM_BOT_TOKEN, settings.TELEGRAM_CHAT_ID)
    message = (
        "Q-Bot-FX OPEN TRADE\n\n"
        f"Symbol: {symbol}\n"
        f"Signal: {signal}\n"
        f"Lot: {lot}\n"
        f"Time: {datetime.utcnow():%Y-%m-%d %H:%M}\n"
        f"Ticket: {ticket}"
    )
    if not telegram.send_message(message):
        LOGGER.warning("Telegram notification failed.")

    if should_send_daily_report():
        notifier = TelegramNotifier(settings)
        notifier.send(report)
        mark_daily_report_sent()

    notifier = TelegramNotifier(settings)
    notifier.send(capital_state["capital_report"])
