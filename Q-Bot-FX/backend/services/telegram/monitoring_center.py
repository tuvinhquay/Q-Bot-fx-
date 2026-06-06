"""Telegram monitoring command center."""

from __future__ import annotations

from typing import Any

from backend.performance.performance_engine import calculate_performance, format_performance_report
from backend.services.device.device_health import get_device_health
from backend.services.health.health_check import run_health_check
from backend.services.node.node_identity import get_node_identity


ALERT_INFO = "INFO"
ALERT_WARNING = "WARNING"
ALERT_CRITICAL = "CRITICAL"


def format_alert(level: str, message: str) -> str:
    return f"{level}\n{message}"


def build_startup_report(mt5_state: dict[str, Any] | None = None, account: dict[str, Any] | None = None) -> str:
    identity = get_node_identity()
    device = get_device_health()
    mt5_state = mt5_state or {}
    account = account or {}
    return (
        "Q-BOT-FX ONLINE\n\n"
        f"Version: {identity['bot_version']}\n"
        f"Branch: {identity['branch']}\n"
        f"Node: {identity['node_name']}\n"
        f"MT5 Status: {mt5_state.get('status', 'UNKNOWN')}\n"
        f"Balance: {account.get('balance', 'N/A')}\n"
        f"Equity: {account.get('equity', 'N/A')}\n"
        f"CPU: {device.cpu_percent:.2f}%\n"
        f"RAM: {device.ram_percent:.2f}%\n"
        f"Disk: {device.disk_percent:.2f}%\n"
        f"Internet: {device.network_status}\n"
        f"Uptime: {device.system_uptime_seconds}s"
    )


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
        return f"Open Trades: {context.get('open_trades', 'N/A')}"
    if cmd == "/topsetup":
        return f"Top Setup: {context.get('top_setup', 'N/A')}"
    if cmd == "/performance":
        return format_performance_report(calculate_performance())
    if cmd == "/restartbot":
        return format_alert(ALERT_WARNING, "Restart command received. Manual restart hook is not enabled.")
    return "Unknown command"
