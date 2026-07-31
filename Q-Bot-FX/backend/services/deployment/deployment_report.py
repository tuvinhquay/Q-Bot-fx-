"""Deployment status report formatter."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

WEEKLY_REPORT_STATE_FILE = Path(__file__).resolve().parents[3] / "weekly_report_state.json"


def build_deployment_report(
    *,
    backup_ok: bool,
    firebase_ok: bool,
    disk_percent: float,
    files_healthy: bool,
    recovery_ready: bool,
) -> str:
    backup = "OK" if backup_ok else "FAILED"
    firebase = "OK" if firebase_ok else "LOCAL ONLY"
    files = "Healthy" if files_healthy else "Needs recovery"
    recovery = "Ready" if recovery_ready else "Unavailable"
    return (
        "Q-BOT DEPLOYMENT STATUS\n"
        f"Backup: {backup}\n"
        f"Firebase: {firebase}\n"
        f"Storage: {disk_percent:.2f}%\n"
        f"Files: {files}\n"
        f"Recovery: {recovery}"
    )


def build_backup_telegram_message(files_saved: int, firebase_synced: bool, disk_percent: float) -> str:
    firebase = "Firebase synced" if firebase_synced else "Local backup created"
    return (
        "CLOUD BACKUP SUCCESS\n\n"
        f"Files saved: {files_saved}\n"
        f"{firebase}\n"
        f"Disk usage: {disk_percent:.2f}%\n\n"
        "Recovery point created"
    )


def _safe_block(title: str, value: Any, default: str = "N/A") -> str:
    if value is None:
        return f"{title}: {default}"
    if isinstance(value, (dict, list)):
        return f"{title}: {json.dumps(value, ensure_ascii=False)}"
    return f"{title}: {value}"


def build_daily_report(state: dict[str, Any] | None = None) -> str:
    state = state or {}
    performance = state.get("performance", {})
    learning = state.get("learning_snapshot", state.get("learning", {}))
    health = state.get("health", {})
    heartbeat = state.get("heartbeat", {})

    win_rate_text = f"{float(performance.get('winrate', 0.0) or 0.0) * 100.0:.2f}%"
    profit_factor_text = f"{float(performance.get('profit_factor', 0.0) or 0.0):.2f}"
    net_profit_text = f"{float(performance.get('net_profit', 0.0) or 0.0):.2f}"
    drawdown_value = performance.get("max_drawdown", state.get("drawdown", 0.0))

    return (
        "Q-BOT-FX DAILY REPORT\n"
        f"Date: {datetime.now(timezone.utc).strftime('%Y-%m-%d')}\n\n"
        "TRADING\n"
        f"{_safe_block('Orders Today', state.get('orders_today', 0))}\n"
        f"{_safe_block('Win', state.get('win', 0))}\n"
        f"{_safe_block('Loss', state.get('loss', 0))}\n"
        f"{_safe_block('Balance', state.get('balance', 0.0))}\n"
        f"{_safe_block('Equity', state.get('equity', 0.0))}\n"
        f"{_safe_block('Floating', state.get('floating', 0.0))}\n"
        f"{_safe_block('Drawdown', drawdown_value)}\n\n"
        "PERFORMANCE\n"
        f"{_safe_block('Total Trades', performance.get('total_trades', 0))}\n"
        f"{_safe_block('Win Rate', win_rate_text)}\n"
        f"{_safe_block('Profit Factor', profit_factor_text)}\n"
        f"{_safe_block('Net Profit', net_profit_text)}\n\n"
        "LEARNING\n"
        f"{_safe_block('Total Memory', learning.get('total_trade', 0))}\n"
        f"{_safe_block('Best Symbol', learning.get('best_symbol', 'N/A'))}\n"
        f"{_safe_block('Worst Symbol', learning.get('worst_symbol', 'N/A'))}\n"
        f"{_safe_block('Best Regime', learning.get('best_regime', 'N/A'))}\n"
        f"{_safe_block('Dangerous Regime', learning.get('dangerous_regime', 'N/A'))}\n\n"
        "HEALTH\n"
        f"{_safe_block('CPU', health.get('cpu_percent', 'N/A'))}\n"
        f"{_safe_block('RAM', health.get('ram_percent', 'N/A'))}\n"
        f"{_safe_block('Disk', health.get('disk_percent', 'N/A'))}\n"
        f"{_safe_block('Internet', health.get('internet', 'N/A'))}\n"
        f"{_safe_block('MT5', health.get('mt5', 'N/A'))}\n"
        f"{_safe_block('Errors', health.get('errors', 0))}\n"
        f"{_safe_block('Warnings', health.get('warnings', 0))}\n\n"
        "HEARTBEAT\n"
        f"{_safe_block('Heartbeat Status', heartbeat.get('status', 'ACTIVE'))}\n"
        f"{_safe_block('Updated', heartbeat.get('updated_time', datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')))}"
    )


def build_weekly_report(state: dict[str, Any] | None = None) -> str:
    state = state or {}
    performance = state.get("performance", {})
    learning = state.get("learning_snapshot", state.get("learning", {}))
    health = state.get("health", {})

    win_rate_text = f"{float(performance.get('winrate', 0.0) or 0.0) * 100.0:.2f}%"
    drawdown_value = performance.get("max_drawdown", state.get("drawdown", 0.0))
    net_profit_text = f"{float(performance.get('net_profit', 0.0) or 0.0):.2f}"

    return (
        "Q-BOT-FX WEEKLY REPORT\n"
        f"Week Ending: {datetime.now(timezone.utc).strftime('%Y-%m-%d')}\n\n"
        "SUMMARY\n"
        f"{_safe_block('Orders', state.get('orders_today', 0))}\n"
        f"{_safe_block('Win Rate', win_rate_text)}\n"
        f"{_safe_block('Drawdown', drawdown_value)}\n"
        f"{_safe_block('Net Profit', net_profit_text)}\n\n"
        "LEARNING TREND\n"
        f"{_safe_block('Best Symbol', learning.get('best_symbol', 'N/A'))}\n"
        f"{_safe_block('Worst Symbol', learning.get('worst_symbol', 'N/A'))}\n"
        f"{_safe_block('Best Regime', learning.get('best_regime', 'N/A'))}\n"
        f"{_safe_block('Dangerous Regime', learning.get('dangerous_regime', 'N/A'))}\n\n"
        "OPERATIONAL HEALTH\n"
        f"{_safe_block('CPU', health.get('cpu_percent', 'N/A'))}\n"
        f"{_safe_block('RAM', health.get('ram_percent', 'N/A'))}\n"
        f"{_safe_block('Disk', health.get('disk_percent', 'N/A'))}\n"
        f"{_safe_block('Internet', health.get('internet', 'N/A'))}\n"
        f"{_safe_block('MT5', health.get('mt5', 'N/A'))}\n"
        "\nPrompt 35 readiness: collect this week's live metrics and stabilize the data pipeline."
    )


def should_send_weekly_report() -> bool:
    today = datetime.now(timezone.utc).date()
    week_key = f"{today.isocalendar().year}-{today.isocalendar().week}"
    if not WEEKLY_REPORT_STATE_FILE.exists():
        return True
    try:
        data = json.loads(WEEKLY_REPORT_STATE_FILE.read_text(encoding="utf-8"))
    except Exception:
        return True
    return data.get("last_week") != week_key


def mark_weekly_report_sent() -> None:
    today = datetime.now(timezone.utc).date()
    week_key = f"{today.isocalendar().year}-{today.isocalendar().week}"
    WEEKLY_REPORT_STATE_FILE.write_text(
        json.dumps({"last_week": week_key}, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
