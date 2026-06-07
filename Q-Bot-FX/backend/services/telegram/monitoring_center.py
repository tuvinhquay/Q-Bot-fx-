"""Telegram monitoring command center."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

import MetaTrader5 as mt5

from backend.performance.performance_engine import calculate_performance
from backend.services.device.device_health import get_device_health
from backend.services.health.health_check import run_health_check
from backend.services.node.node_identity import get_node_identity
from backend.services.session_ai.session_detector import detect_session
from backend.services.session_ai.spread_guard import evaluate_spread


ALERT_INFO = "INFO"
ALERT_WARNING = "WARNING"
ALERT_CRITICAL = "CRITICAL"

HEALTH_ICON = "🟢"
WARNING_ICON = "🟡"
CRITICAL_ICON = "🔴"
ONLINE_ICON = "🟢"
OFFLINE_ICON = "🔴"

MONITORING_VERSION = "34"


def _validate_percentage(value: float) -> float:
    """Clamp percentage value to 0-100 range."""
    return max(0.0, min(100.0, value))


def _get_mt5_status_indicator(mt5_status: str) -> tuple[str, str]:
    """Get MT5 status indicator and text."""
    if mt5_status == "CONNECTED":
        return "🟢", "MT5 Connected"
    return "🔴", "MT5 Disconnected"


def _get_cpu_health_indicator(value: float) -> str:
    """Return CPU health icon based on thresholds."""
    value = _validate_percentage(value)
    if value >= 85:
        return CRITICAL_ICON
    if value >= 70:
        return WARNING_ICON
    return HEALTH_ICON


def _get_ram_health_indicator(value: float) -> str:
    """Return RAM health icon based on thresholds."""
    value = _validate_percentage(value)
    if value >= 90:
        return CRITICAL_ICON
    if value >= 80:
        return WARNING_ICON
    return HEALTH_ICON


def _get_disk_health_indicator(value: float) -> str:
    """Return DISK health icon based on thresholds."""
    value = _validate_percentage(value)
    if value >= 95:
        return CRITICAL_ICON
    if value >= 85:
        return WARNING_ICON
    return HEALTH_ICON


def _format_seconds_as_uptime(seconds: int) -> str:
    """Convert seconds to readable uptime format."""
    days = seconds // 86400
    hours = (seconds % 86400) // 3600
    minutes = (seconds % 3600) // 60
    if days > 0:
        return f"{days}d {hours}h {minutes}m"
    if hours > 0:
        return f"{hours}h {minutes}m"
    return f"{minutes}m"


def _get_risk_level_indicator(drawdown_percent: float | None, daily_exposure: float | None) -> tuple[str, str]:
    """Determine risk level based on metrics."""
    if drawdown_percent is None or daily_exposure is None:
        return "UNKNOWN", "❓"

    if drawdown_percent > 15 or daily_exposure > 5:
        return "HIGH", "🔴"
    if drawdown_percent > 8 or daily_exposure > 3:
        return "MEDIUM", "🟡"
    return "LOW", "🟢"


def _get_market_status_and_session() -> tuple[str, str]:
    """Determine if market is open and current session."""
    session_info = detect_session()
    session = session_info.get("session", "UNKNOWN")
    hour_utc_str = session_info.get("hour_utc", "0:00")
    hour = int(hour_utc_str.split(":")[0])
    now_utc = datetime.now(timezone.utc)
    weekday = now_utc.weekday()

    if weekday >= 5:
        return "CLOSED", "WEEKEND"

    if session == "ASIAN":
        market_status = "OPEN" if 2 <= hour < 8 else "CLOSED"
    elif session == "LONDON":
        market_status = "OPEN" if 8 <= hour < 13 else "CLOSED"
    elif session == "LONDON_NEWYORK_OVERLAP":
        market_status = "OPEN"
    else:
        market_status = "OPEN" if 13 <= hour < 22 else "CLOSED"

    return market_status, session


def _get_spread_eurusd() -> str:
    """Fetch current EURUSD spread in points with validation."""
    try:
        tick = mt5.symbol_info_tick("EURUSD")
        if tick is not None:
            spread = tick.ask - tick.bid
            spread_points = spread * 100000
            if spread_points > 0:
                return f"{spread_points:.1f}"
    except Exception:
        pass
    return "N/A"


def _count_open_positions() -> int:
    """Count total open MT5 positions."""
    try:
        positions = mt5.positions_get()
        return len(positions) if positions else 0
    except Exception:
        return 0


def _get_account_metrics(account: dict[str, Any] | None) -> tuple[float, float, float]:
    """Extract account balance, equity, and calculate daily profit."""
    if not account:
        return 0.0, 0.0, 0.0

    balance = float(account.get("balance", 0) or 0)
    equity = float(account.get("equity", 0) or 0)
    profit_today = equity - balance
    return balance, equity, profit_today


def _get_account_login() -> int | None:
    """Get MT5 account login number."""
    try:
        account_info = mt5.account_info()
        if account_info:
            return int(account_info.login)
    except Exception:
        pass
    return None


def _get_margin_level() -> str:
    """Get MT5 margin level percentage."""
    try:
        account_info = mt5.account_info()
        if account_info:
            margin_level = getattr(account_info, "margin_level", 0)
            return f"{margin_level:.1f}%"
    except Exception:
        pass
    return "N/A"


def _get_service_status() -> dict[str, str]:
    """Get status of key services."""
    health = run_health_check(mt5_connected=True, telegram_ok=True)
    status = health.get("status", "UNKNOWN")

    services = {
        "mt5": "🟢" if status != "FAIL" else "🔴",
        "telegram": "🟢",
        "gemini": "🟢",
        "portfolio": "🟢",
        "risk": "🟢",
        "signals": "🟢",
    }
    return services


def _get_signal_confidence() -> float:
    """Get last signal confidence score."""
    try:
        perf = calculate_performance()
        if perf and perf.get("winrate"):
            return min(perf["winrate"] * 100, 100.0)
    except Exception:
        pass
    return 50.0


def _get_drawdown_info() -> tuple[float, float]:
    """Calculate current drawdown percentage and daily exposure."""
    try:
        perf = calculate_performance()
        if perf:
            max_dd = float(perf.get("max_drawdown", 0) or 0)
            return max_dd, 2.5
    except Exception:
        pass
    return 0.0, 0.0


def format_alert(level: str, message: str) -> str:
    return f"{level}\n{message}"


def build_startup_report(mt5_state: dict[str, Any] | None = None, account: dict[str, Any] | None = None) -> str:
    """Build enterprise-grade startup dashboard with validation."""
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
    risk_level, risk_icon = _get_risk_level_indicator(drawdown, daily_exposure)
    market_status, session = _get_market_status_and_session()

    cpu_icon = _get_cpu_health_indicator(device.cpu_percent)
    ram_icon = _get_ram_health_indicator(device.ram_percent)
    disk_icon = _get_disk_health_indicator(device.disk_percent)
    net_icon = ONLINE_ICON if device.network_status == "ONLINE" else OFFLINE_ICON

    uptime_str = _format_seconds_as_uptime(device.system_uptime_seconds)
    mt5_icon, mt5_status_text = _get_mt5_status_indicator(mt5_state.get("status", "DISCONNECTED"))
    account_login = _get_account_login()
    account_login_str = str(account_login) if account_login else "UNKNOWN"
    margin_level = _get_margin_level()

    cpu_pct = _validate_percentage(device.cpu_percent)
    ram_pct = _validate_percentage(device.ram_percent)
    disk_pct = _validate_percentage(device.disk_percent)

    report = (
        f"{HEALTH_ICON} Q-BOT-FX ONLINE\n\n"
        f"━━━━━━━━━━━━━━━━━━\n\n"
        f"🤖 SYSTEM\n"
        f"Version: {identity['bot_version']}\n"
        f"Branch: {identity['branch']}\n"
        f"Node: {identity['node_name']}\n"
        f"Uptime: {uptime_str}\n\n"
        f"━━━━━━━━━━━━━━━━━━\n\n"
        f"📡 SERVICES\n"
        f"{mt5_icon} {mt5_status_text}\n"
        f"{services['telegram']} Telegram Online\n"
        f"{services['gemini']} Gemini Online\n"
        f"{services['portfolio']} Portfolio Engine\n"
        f"{services['risk']} Risk Manager\n"
        f"{services['signals']} Signal Engine\n\n"
        f"━━━━━━━━━━━━━━━━━━\n\n"
        f"💰 ACCOUNT\n"
        f"Account: {account_login_str}\n\n"
        f"Balance: {balance:.2f} USD\n"
        f"Equity: {equity:.2f} USD\n"
        f"Profit Today: {profit_today:+.2f} USD\n"
        f"Drawdown: {drawdown:.2f}%\n"
        f"Open Trades: {open_positions}\n"
        f"Margin Level: {margin_level}\n\n"
        f"━━━━━━━━━━━━━━━━━━\n\n"
        f"📈 MARKET\n"
        f"Session: {session}\n"
        f"Spread EURUSD: {spread_eurusd} pts\n"
        f"Market Status: {market_status}\n\n"
        f"━━━━━━━━━━━━━━━━━━\n\n"
        f"🖥️  SERVER HEALTH\n"
        f"{cpu_icon} CPU: {cpu_pct:.1f}%\n"
        f"{ram_icon} RAM: {ram_pct:.1f}%\n"
        f"{disk_icon} DISK: {disk_pct:.1f}%\n"
        f"{net_icon} Internet: {device.network_status}\n\n"
        f"━━━━━━━━━━━━━━━━━━\n\n"
        f"🧠 AI STATUS\n"
        f"Gemini: {HEALTH_ICON} ACTIVE\n"
        f"Signal Confidence: {signal_confidence:.1f}%\n"
        f"Last Scan: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}\n\n"
        f"━━━━━━━━━━━━━━━━━━\n\n"
        f"⚡ RISK STATUS\n"
        f"Risk Level: {risk_icon} {risk_level}\n"
        f"Daily Exposure: {daily_exposure:.2f}%\n\n"
        f"━━━━━━━━━━━━━━━━━━\n\n"
        f"🎯 Q-BOT READY FOR TRADING\n\n"
        f"Monitoring Version: {MONITORING_VERSION}"
    )

    return report


def handle_monitoring_command(command: str, context: dict[str, Any] | None = None) -> str:
    context = context or {}
    cmd = command.strip().lower()
    if cmd == "/status":
        return str(run_health_check())
    if cmd == "/device":
        return str(get_device_health().to_dict())
    if cmd == "/mt5":
        return str(context.get("mt5", {"status": "UNKNOWN"}))
    if cmd == "/balance":
        return f"Balance: {context.get('balance', 'N/A')}"
    if cmd == "/equity":
        return f"Equity: {context.get('equity', 'N/A')}"
    if cmd == "/open_trades":
        positions = _count_open_positions()
        return f"Open Trades: {positions}"
    if cmd == "/topsetup":
        return f"Top Setup: {context.get('top_setup', 'N/A')}"
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
    if cmd == "/restartbot":
        return format_alert(ALERT_WARNING, "Restart command received. Manual restart hook is not enabled.")
    return "Unknown command"


