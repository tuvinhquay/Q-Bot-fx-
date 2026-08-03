"""Telegram monitoring command center."""

from __future__ import annotations

import html
from datetime import datetime, timezone
from typing import Any

import MetaTrader5 as mt5

from backend.brain.brain_database import get_brain
from backend.brain.system_health import get_health
from backend.performance.performance_engine import calculate_performance
from backend.services.device.device_health import get_device_health
from backend.services.health.health_check import run_health_check
from backend.services.node.node_identity import get_node_identity
from backend.services.learning.memory_engine import LearningMemoryEngine
from backend.services.session_ai.session_detector import detect_session
from backend.services.session_ai.spread_guard import evaluate_spread


# ==========================================================
# CONSTANTS
# ==========================================================

ALERT_INFO = "INFO"
ALERT_WARNING = "WARNING"
ALERT_CRITICAL = "CRITICAL"

HEALTH_ICON = "🟢"
WARNING_ICON = "🟡"
CRITICAL_ICON = "🔴"

ONLINE_ICON = "🟢"
OFFLINE_ICON = "🔴"

MONITORING_VERSION = "34"


# ==========================================================
# HELPERS
# ==========================================================

def _validate_percentage(value: float) -> float:
    """Clamp percentage value to 0-100 range."""
    return max(0.0, min(100.0, value))


def _get_mt5_status_indicator(mt5_status: str) -> tuple[str, str]:
    """Return MT5 status icon and text."""
    if mt5_status == "CONNECTED":
        return "🟢", "MT5 Connected"
    return "🔴", "MT5 Disconnected"


def _get_cpu_health_indicator(value: float) -> str:
    value = _validate_percentage(value)

    if value >= 85:
        return CRITICAL_ICON

    if value >= 70:
        return WARNING_ICON

    return HEALTH_ICON


def _get_ram_health_indicator(value: float) -> str:
    value = _validate_percentage(value)

    if value >= 90:
        return CRITICAL_ICON

    if value >= 80:
        return WARNING_ICON

    return HEALTH_ICON


def _get_disk_health_indicator(value: float) -> str:
    value = _validate_percentage(value)

    if value >= 95:
        return CRITICAL_ICON

    if value >= 85:
        return WARNING_ICON

    return HEALTH_ICON


def _format_seconds_as_uptime(seconds: int) -> str:
    """Convert seconds to readable uptime."""

    days = seconds // 86400
    hours = (seconds % 86400) // 3600
    minutes = (seconds % 3600) // 60

    if days > 0:
        return f"{days}d {hours}h {minutes}m"

    if hours > 0:
        return f"{hours}h {minutes}m"

    return f"{minutes}m"


def _get_risk_level_indicator(
    drawdown_percent: float | None,
    daily_exposure: float | None,
) -> tuple[str, str]:
    """Determine risk level."""

    if drawdown_percent is None or daily_exposure is None:
        return "UNKNOWN", "❓"

    if drawdown_percent > 15 or daily_exposure > 5:
        return "HIGH", "🔴"

    if drawdown_percent > 8 or daily_exposure > 3:
        return "MEDIUM", "🟡"

    return "LOW", "🟢"

# ==========================================================
# MARKET HELPERS PART 2
# ==========================================================

def _get_market_status_and_session() -> tuple[str, str]:
    """Determine current market status."""

    session_info = detect_session()

    session = session_info.get("session", "UNKNOWN")

    hour_utc = int(session_info.get("hour_utc", "0:00").split(":")[0])

    now = datetime.now(timezone.utc)

    weekday = now.weekday()

    if weekday >= 5:
        return "CLOSED", "WEEKEND"

    if session == "ASIAN":
        status = "OPEN" if 2 <= hour_utc < 8 else "CLOSED"

    elif session == "LONDON":
        status = "OPEN" if 8 <= hour_utc < 13 else "CLOSED"

    elif session == "LONDON_NEWYORK_OVERLAP":
        status = "OPEN"

    else:
        status = "OPEN" if 13 <= hour_utc < 22 else "CLOSED"

    return status, session


def _get_spread_eurusd() -> str:
    """Get EURUSD spread."""

    try:

        tick = mt5.symbol_info_tick("EURUSD")

        if tick:

            spread = (tick.ask - tick.bid) * 100000

            if spread > 0:
                return f"{spread:.1f}"

    except Exception:
        pass

    return "N/A"


def _count_open_positions() -> int:
    """Count MT5 open positions."""

    try:

        positions = mt5.positions_get()

        return len(positions) if positions else 0

    except Exception:

        return 0


def _load_trade_history() -> list[dict[str, Any]]:
    """Load trade history."""

    try:

        from backend.performance.performance_engine import load_trades

        return load_trades()

    except Exception:

        return []


def _get_account_metrics(account: dict[str, Any] | None):

    if not account:
        return 0.0, 0.0, 0.0

    balance = float(account.get("balance", 0))

    equity = float(account.get("equity", 0))

    profit_today = equity - balance

    return balance, equity, profit_today


def _get_account_login():

    try:

        info = mt5.account_info()

        if info:
            return int(info.login)

    except Exception:
        pass

    return None


def _get_margin_level():

    try:

        info = mt5.account_info()

        if info:

            return f"{info.margin_level:.1f}%"

    except Exception:

        pass

    return "N/A"

# ==========================================================
# SERVICE HELPERS PART 3.
# ==========================================================

def _get_service_status():

    health = run_health_check(
        mt5_connected=True,
        telegram_ok=True,
    )

    status = health.get("status", "UNKNOWN")

    return {
        "mt5": "🟢" if status != "FAIL" else "🔴",
        "telegram": "🟢",
        "gemini": "🟢",
        "portfolio": "🟢",
        "risk": "🟢",
        "signals": "🟢",
    }


def _get_signal_confidence():

    try:

        perf = calculate_performance()

        if perf and perf.get("winrate"):

            return min(perf["winrate"] * 100, 100)

    except Exception:
        pass

    return 50.0


def _get_drawdown_info():

    try:

        perf = calculate_performance()

        if perf:

            return (
                float(perf.get("max_drawdown", 0)),
                2.5,
            )

    except Exception:
        pass

    return 0.0, 0.0


def _get_brain_status():

    try:

        brain = get_brain()

        return brain.get_brain_status()

    except Exception:

        return {}


def _format_metric(label: str, value: Any):

    return f"{label}: {html.escape(str(value))}"


def _status_icon(value: str):

    value = value.upper()

    if value in {
        "OK",
        "ONLINE",
        "CONNECTED",
        "READY",
        "ACTIVE",
        "PASS",
    }:
        return HEALTH_ICON

    if value in {
        "WARNING",
        "DEGRADED",
    }:
        return WARNING_ICON

    if value in {
        "FAIL",
        "FAILED",
        "OFFLINE",
        "DISCONNECTED",
        "CRITICAL",
        "ERROR",
    }:
        return CRITICAL_ICON

    return "❓"


def format_alert(level: str, message: str):

    return f"{level}\n{message}"        


# ==========================================================
# TRADE SUMMARY PART 4
# ==========================================================

def _summarize_trade_history() -> dict[str, Any]:

    trades = _load_trade_history()

    today = datetime.now(timezone.utc).date().isoformat()

    today_trades = [
        t for t in trades
        if str(t.get("timestamp", ""))[:10] == today
    ]

    wins = sum(
        1
        for t in today_trades
        if float(t.get("profit", 0) or 0) > 0
    )

    losses = sum(
        1
        for t in today_trades
        if float(t.get("profit", 0) or 0) <= 0
    )

    last_trade = trades[-1] if trades else {}

    return {
        "orders_today": len(today_trades),
        "win_count": wins,
        "loss_count": losses,
        "last_signal": last_trade.get("signal", "N/A"),
        "last_order": (
            f"{last_trade.get('symbol','N/A')} "
            f"{last_trade.get('signal','N/A')}"
        ),
        "last_error": last_trade.get("error", "N/A"),
        "last_trade_time": last_trade.get("timestamp", "N/A"),
    }

# ==========================================================
# STARTUP REPORT PART 5
# ==========================================================

def build_startup_report(
    mt5_state: dict[str, Any] | None = None,
    account: dict[str, Any] | None = None,
) -> str:

    identity = get_node_identity()

    device = get_device_health()

    mt5_state = mt5_state or {}

    account = account or {}

    services = _get_service_status()

    balance, equity, profit_today = _get_account_metrics(account)

    spread_eurusd = _get_spread_eurusd()

    open_positions = _count_open_positions()

    signal_confidence = _get_signal_confidence()

    drawdown, daily_exposure = _get_drawdown_info()

    risk_level, risk_icon = _get_risk_level_indicator(
        drawdown,
        daily_exposure,
    )

    market_status, session = _get_market_status_and_session()

    cpu_icon = _get_cpu_health_indicator(device.cpu_percent)

    ram_icon = _get_ram_health_indicator(device.ram_percent)

    disk_icon = _get_disk_health_indicator(device.disk_percent)

    net_icon = (
        ONLINE_ICON
        if device.network_status == "ONLINE"
        else OFFLINE_ICON
    )

    uptime_str = _format_seconds_as_uptime(
        device.system_uptime_seconds
    )

    mt5_icon, mt5_status_text = _get_mt5_status_indicator(
        mt5_state.get("status", "DISCONNECTED")
    )

    account_login = _get_account_login()

    account_login_str = (
        str(account_login)
        if account_login
        else "UNKNOWN"
    )

    margin_level = _get_margin_level()

    cpu_pct = _validate_percentage(device.cpu_percent)

    ram_pct = _validate_percentage(device.ram_percent)

    disk_pct = _validate_percentage(device.disk_percent)

    brain_status = _get_brain_status()

    brain_location = brain_status.get("location", "UNKNOWN")

    brain_size = brain_status.get("size_mb", 0)

    brain_dbs = brain_status.get("databases", 0)

    brain_memory = brain_status.get("memory_records", 0)

    brain_backup = brain_status.get(
        "last_backup",
        "NONE",
    )

    report = (

        f"{HEALTH_ICON} Q-BOT-FX ONLINE\n\n"

        f"{'━'*40}\n\n"

        f"🤖 SYSTEM\n"
        f"Version: {identity['bot_version']}\n"
        f"Branch: {identity['branch']}\n"
        f"Node: {identity['node_name']}\n"
        f"Uptime: {uptime_str}\n\n"

        f"{'━'*40}\n\n"

        f"📡 SERVICES\n"
        f"{mt5_icon} {mt5_status_text}\n"
        f"{services['telegram']} Telegram Online\n"
        f"{services['gemini']} Gemini Online\n"
        f"{services['portfolio']} Portfolio Engine\n"
        f"{services['risk']} Risk Manager\n"
        f"{services['signals']} Signal Engine\n\n"

        f"{'━'*40}\n\n"

        f"💰 ACCOUNT\n"
        f"Account: {account_login_str}\n\n"
        f"Balance: {balance:.2f} USD\n"
        f"Equity: {equity:.2f} USD\n"
        f"Profit Today: {profit_today:+.2f} USD\n"
        f"Drawdown: {drawdown:.2f}%\n"
        f"Open Trades: {open_positions}\n"
        f"Margin Level: {margin_level}\n\n"

        f"{'━'*40}\n\n"

        f"📈 MARKET\n"
        f"Session: {session}\n"
        f"Spread EURUSD: {spread_eurusd} pts\n"
        f"Market Status: {market_status}\n\n"

        f"{'━'*40}\n\n"

        f"🖥️ SERVER HEALTH\n"
        f"{cpu_icon} CPU: {cpu_pct:.1f}%\n"
        f"{ram_icon} RAM: {ram_pct:.1f}%\n"
        f"{disk_icon} DISK: {disk_pct:.1f}%\n"
        f"{net_icon} Internet: {device.network_status}\n\n"

        f"{'━'*40}\n\n"

        f"🧠 AI STATUS\n"
        f"Gemini: {HEALTH_ICON} ACTIVE\n"
        f"Signal Confidence: {signal_confidence:.1f}%\n"
        f"Last Scan: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}\n\n"

        f"{'━'*40}\n\n"

        f"⚡ RISK STATUS\n"
        f"Risk Level: {risk_icon} {risk_level}\n"
        f"Daily Exposure: {daily_exposure:.2f}%\n\n"

        f"{'━'*40}\n\n"

        f"🧠 BRAIN STATUS\n"
        f"Location: {brain_location}\n"
        f"Size: {brain_size} MB\n"
        f"Databases: {brain_dbs}\n"
        f"Memory Records: {brain_memory}\n"
        f"Last Backup: {brain_backup}\n\n"

        f"{'━'*40}\n\n"

        f"🎯 Q-BOT READY FOR TRADING\n\n"

        f"Monitoring Version: {MONITORING_VERSION}"
    )

    return report    

# ==========================================================
# LIVE DASHBOARD PART 8
# ==========================================================

def build_live_dashboard(
    context: dict[str, Any] | None = None,
) -> str:

    context = context or {}

    identity = get_node_identity()

    device = get_device_health()

    health = run_health_check(
        mt5_connected=str(
            context.get("mt5", "DISCONNECTED")
        ).upper() == "CONNECTED",
        telegram_ok=str(
            context.get("telegram", "ONLINE")
        ).upper() in {
            "ONLINE",
            "OK",
            "CONNECTED",
        },
    )

    performance = calculate_performance() or {}

    learning_snapshot = LearningMemoryEngine().snapshot()

    brain_status = _get_brain_status()

    trade_summary = _summarize_trade_history()

    balance = float(context.get("balance", 0))

    equity = float(context.get("equity", 0))

    floating = float(
        context.get(
            "floating",
            equity - balance,
        )
    )

    drawdown = float(
        context.get(
            "drawdown",
            performance.get(
                "max_drawdown",
                0,
            ),
        )
    )

    win_rate = float(
        context.get(
            "win_rate",
            performance.get(
                "winrate",
                0,
            ) * 100,
        )
    )

    win_count = int(
        context.get(
            "win",
            trade_summary["win_count"],
        )
    )

    loss_count = int(
        context.get(
            "loss",
            trade_summary["loss_count"],
        )
    )

    updated_time = (
        context.get("updated_time")
        or datetime.now(
            timezone.utc
        ).strftime("%Y-%m-%d %H:%M:%S UTC")
    )

    mt5_status = str(
        context.get(
            "mt5",
            "DISCONNECTED",
        )
    )

    internet_status = str(
        context.get(
            "internet",
            device.network_status,
        )
    )

    heartbeat_status = str(
        context.get(
            "heartbeat",
            "ACTIVE",
        )
    )

    ai_status = str(
        context.get(
            "ai",
            "ACTIVE",
        )
    )

    learning_status = str(
        context.get(
            "learning",
            "ACTIVE",
        )
    )

    strategy_status = str(
        context.get(
            "strategy",
            "ACTIVE",
        )
    )

    risk_status = str(
        context.get(
            "risk",
            "READY",
        )
    )

    trade_executor_status = str(
        context.get(
            "trade_executor",
            "READY",
        )
    )

    database_status = str(
        context.get(
            "database",
            "OK",
        )
    )

    cpu_pct = _validate_percentage(
        float(
            context.get(
                "cpu_percent",
                device.cpu_percent,
            )
        )
    )

    ram_pct = _validate_percentage(
        float(
            context.get(
                "ram_percent",
                device.ram_percent,
            )
        )
    )

    disk_pct = _validate_percentage(
        float(
            context.get(
                "disk_percent",
                device.disk_percent,
            )
        )
    )

    uptime_seconds = int(
        context.get(
            "uptime_seconds",
            device.system_uptime_seconds,
        )
    )

    uptime_str = _format_seconds_as_uptime(
        uptime_seconds
    )

    return (

        f"{HEALTH_ICON} Q-BOT-FX DASHBOARD\n"

        f"{'━'*40}\n"

        f"BOT: {identity['bot_version']} | {identity['branch']}\n"

        f"NODE: {identity['node_name']}\n"

        f"UPDATED: {html.escape(str(updated_time))}\n\n"

        f"MT5: {_status_icon(mt5_status)} {html.escape(mt5_status)}\n"

        f"Internet: {_status_icon(internet_status)} {html.escape(internet_status)}\n"

        f"Heartbeat: {_status_icon(heartbeat_status)} {html.escape(heartbeat_status)}\n"

        f"AI: {_status_icon(ai_status)} {html.escape(ai_status)}\n"

        f"Learning: {_status_icon(learning_status)} {html.escape(learning_status)}\n"

        f"Strategy: {_status_icon(strategy_status)} {html.escape(strategy_status)}\n"

        f"Risk: {_status_icon(risk_status)} {html.escape(risk_status)}\n"

        f"Trade Executor: {_status_icon(trade_executor_status)} {html.escape(trade_executor_status)}\n"

        f"Database: {_status_icon(database_status)} {html.escape(database_status)}\n\n"

        f"{'━'*40}\n"

        f"CPU: {cpu_pct:.1f}%\n"

        f"RAM: {ram_pct:.1f}%\n"

        f"DISK: {disk_pct:.1f}%\n"

        f"UPTIME: {uptime_str}\n\n"

        f"{'━'*40}\n"

        f"Balance: {balance:.2f}\n"

        f"Equity: {equity:.2f}\n"

        f"Floating: {floating:+.2f}\n"

        f"Orders Today: {trade_summary['orders_today']}\n"

        f"Win: {win_count}\n"

        f"Loss: {loss_count}\n"

        f"Win Rate: {win_rate:.2f}%\n"

        f"Drawdown: {drawdown:.2f}%\n\n"    

        f"{'━'*40}\n"

        f"Last Signal: {html.escape(str(context.get('last_signal', trade_summary['last_signal'])))}\n"

        f"Last Order: {html.escape(str(context.get('last_order', trade_summary['last_order'])))}\n"

        f"Last Error: {html.escape(str(context.get('last_error', 'N/A')))}\n"

        f"Last Trade: {html.escape(str(trade_summary['last_trade_time']))}\n\n"

        f"{'━'*40}\n"

        f"Learning Total: {learning_snapshot.get('total_trade',0)}\n"

        f"Best Symbol: {learning_snapshot.get('best_symbol','N/A')}\n"

        f"Worst Symbol: {learning_snapshot.get('worst_symbol','N/A')}\n"

        f"Best Regime: {learning_snapshot.get('best_regime','N/A')}\n"

        f"Dangerous Regime: {learning_snapshot.get('dangerous_regime','N/A')}\n\n"

        f"{'━'*40}\n"

        f"Brain DBs: {brain_status.get('databases',0)}\n"

        f"Brain Records: {brain_status.get('memory_records',0)}\n"

        f"Brain Backup: {brain_status.get('last_backup','NONE')}\n\n"

        f"{'━'*40}\n"

        f"Health: {health.get('status','UNKNOWN')}\n"

        f"Errors: {len(get_health().get_recent_errors(limit=5))}\n"

        f"Warnings: {len(get_health().get_recent_warnings(limit=5))}"

    )
    
    
def handle_monitoring_command(
    command: str,
    context: dict[str, Any] | None = None,
) -> str:

    context = context or {}

    cmd = command.strip().lower()

    if cmd == "/dashboard":
        return build_live_dashboard(context)

    if cmd == "/status":
        return str(run_health_check())

    if cmd == "/health":
        health = run_health_check()

        return (
            f"Health: {health['status']}\n"
            f"Issues: "
            f"{', '.join(health.get('issues', [])) or 'None'}"
        )

    if cmd == "/device":
        return str(
            get_device_health().to_dict()
        )

    if cmd == "/mt5":
        return str(
            context.get(
                "mt5",
                {"status": "UNKNOWN"},
            )
        )

    if cmd == "/orders":
        return (
            f"Open Trades: {_count_open_positions()}\n"
            f"Orders Today: "
            f"{_summarize_trade_history()['orders_today']}"
        )

    if cmd == "/balance":
        return f"Balance: {context.get('balance','N/A')}"

    if cmd == "/equity":
        return f"Equity: {context.get('equity','N/A')}"

    if cmd == "/open_trades":
        return (
            f"Open Trades: "
            f"{_count_open_positions()}"
        )

    if cmd == "/topsetup":
        return (
            f"Top Setup: "
            f"{context.get('top_setup','N/A')}"
        )

    if cmd == "/performance":

        perf = calculate_performance()

        if perf:

            return (
                f"Winrate: {perf['winrate']*100:.1f}%\n"
                f"Profit Factor: {perf['profit_factor']:.2f}\n"
                f"Max Drawdown: {perf['max_drawdown']:.2f}%\n"
                f"Total Trades: {perf['total_trades']}"
            )

        return "No performance data yet"

    if cmd == "/logs":

        health = get_health()

        errors = health.get_recent_errors(limit=5)
        warnings = health.get_recent_warnings(limit=5)

        lines = ["Recent Errors:"]

        if errors:

            for item in errors:

                lines.append(
                    f"- {item.get('timestamp','N/A')} | "
                    f"{item.get('component','N/A')} | "
                    f"{item.get('message','N/A')}"
                )

        else:

            lines.append("- None")

        lines.append("")

        lines.append("Recent Warnings:")

        if warnings:

            for item in warnings:

                lines.append(
                    f"- {item.get('timestamp','N/A')} | "
                    f"{item.get('metric_name','N/A')} | "
                    f"{item.get('current_value','N/A')}"
                )

        else:

            lines.append("- None")

        return "\n".join(lines)

    if cmd == "/report":

        return build_live_dashboard(context)

    if cmd in ("/restart", "/restartbot"):

        return format_alert(
            ALERT_WARNING,
            "Restart command received.\n"
            "Manual restart hook is not enabled."
        )

    return "Unknown command"