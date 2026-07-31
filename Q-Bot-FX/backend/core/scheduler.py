"""Trading scheduler for continuous auto-trading loop."""

from __future__ import annotations

import logging
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

import MetaTrader5 as mt5

from backend.brain.brain_database import get_brain
from backend.core.signal_pipeline import run_signal_pipeline
from backend.notifications.telegram_notifier import TelegramNotifier
from backend.performance.performance_engine import calculate_performance, mark_daily_report_sent, should_send_daily_report
from backend.performance.performance_engine import load_trades
from backend.services.deployment.backup_manager import BackupManager
from backend.services.deployment.deployment_report import (
    build_daily_report,
    build_weekly_report,
    mark_weekly_report_sent,
    should_send_weekly_report,
)
from backend.services.deployment.log_rotation import rotate_logs
from backend.services.deployment.recovery_manager import RecoveryManager
from backend.services.device.device_health import get_device_health
from backend.services.heartbeat.heartbeat_engine import HeartbeatEngine
from backend.services.health.health_check import run_health_check
from backend.services.learning.memory_engine import LearningMemoryEngine
from backend.services.mt5.auto_login_engine import MT5AutoLoginEngine
from backend.services.recovery.crash_guard import CrashGuard
from backend.services.telegram.monitoring_center import build_live_dashboard
from config.settings import Settings

LOGGER = logging.getLogger(__name__)


def _project_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _get_account_snapshot() -> dict[str, float]:
    try:
        account_info = mt5.account_info()
        if account_info:
            balance = float(getattr(account_info, "balance", 0.0) or 0.0)
            equity = float(getattr(account_info, "equity", 0.0) or 0.0)
            return {
                "balance": balance,
                "equity": equity,
                "floating": equity - balance,
            }
    except Exception as error:
        LOGGER.warning("Failed to read account snapshot: %s", error)
    return {"balance": 0.0, "equity": 0.0, "floating": 0.0}


def _count_trades_today() -> dict[str, int]:
    trades = load_trades()
    today = datetime.now(timezone.utc).date().isoformat()
    today_trades = [trade for trade in trades if str(trade.get("timestamp", ""))[:10] == today]
    wins = sum(1 for trade in today_trades if float(trade.get("profit", 0) or 0) > 0)
    losses = len(today_trades) - wins
    return {"orders_today": len(today_trades), "win": wins, "loss": losses}


def _build_runtime_state(
    *,
    last_signal: str = "N/A",
    last_error: str = "N/A",
) -> dict[str, Any]:
    device = get_device_health()
    account = _get_account_snapshot()
    performance = calculate_performance() or {}
    learning_snapshot = LearningMemoryEngine().snapshot()
    brain = get_brain().get_brain_status()
    health = run_health_check(
        mt5_connected=bool(mt5.terminal_info()),
        telegram_ok=True,
    )
    trade_counts = _count_trades_today()

    runtime_state: dict[str, Any] = {
        "mt5": "CONNECTED" if mt5.terminal_info() else "DISCONNECTED",
        "internet": device.network_status,
        "heartbeat": "ACTIVE",
        "learning": "ACTIVE",
        "strategy": "ACTIVE",
        "risk": "READY",
        "trade_executor": "READY",
        "ai": "ACTIVE",
        "signal": "ACTIVE",
        "database": "OK" if brain.get("databases", 0) >= 4 else "WARNING",
        "cpu_percent": device.cpu_percent,
        "ram_percent": device.ram_percent,
        "disk_percent": device.disk_percent,
        "uptime_seconds": device.system_uptime_seconds,
        "balance": account["balance"],
        "equity": account["equity"],
        "floating": account["floating"],
        "orders_today": trade_counts["orders_today"],
        "win": trade_counts["win"],
        "loss": trade_counts["loss"],
        "win_rate": (performance.get("winrate", 0.0) or 0.0) * 100.0,
        "drawdown": performance.get("max_drawdown", 0.0) or 0.0,
        "last_signal": last_signal,
        "last_order": "N/A",
        "last_error": last_error,
        "updated_time": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC"),
        "performance": performance,
        "learning_snapshot": learning_snapshot,
        "health": {
            "status": health.get("status", "UNKNOWN"),
            "cpu_percent": device.cpu_percent,
            "ram_percent": device.ram_percent,
            "disk_percent": device.disk_percent,
            "internet": device.network_status,
            "mt5": "CONNECTED" if mt5.terminal_info() else "DISCONNECTED",
            "errors": len(health.get("issues", [])),
            "warnings": len(health.get("warnings", [])),
        },
        "heartbeat_status": "ACTIVE",
    }
    return runtime_state


def _maybe_reconnect_mt5(notifier: TelegramNotifier, crash_guard: CrashGuard) -> None:
    if mt5.terminal_info():
        return
    reconnect = MT5AutoLoginEngine().connect(notify_on_failure=False)
    if reconnect.success:
        notifier.send("MT5 reconnected successfully.")
        return
    crash_guard.handle_mt5_disconnect()


def _publish_dashboard(
    notifier: TelegramNotifier,
    heartbeat: HeartbeatEngine,
    dashboard_message_id: int | None,
    runtime_state: dict[str, Any],
) -> int | None:
    message = heartbeat.build_message(runtime_state)
    if dashboard_message_id is None:
        return notifier.send_dashboard_message(message)
    if notifier.edit_dashboard_message(dashboard_message_id, message):
        return dashboard_message_id
    return notifier.send_dashboard_message(message)


def start_trading_loop(settings: Settings, run_once: bool = False) -> None:
    """Start continuous trading loop with five-second production heartbeat."""
    print("QBOT Trading Engine Started")
    print(f"Run interval: {settings.TRADE_INTERVAL_MINUTES} minutes")

    notifier = TelegramNotifier(settings)
    heartbeat = HeartbeatEngine()
    crash_guard = CrashGuard(notifier)
    project_root = _project_root()
    backup_manager = BackupManager(project_root=project_root, backup_dir=project_root / "backups")
    recovery_manager = RecoveryManager(backup_manager)
    dashboard_message_id: int | None = None

    startup_recovery = recovery_manager.check_data_integrity()
    if not startup_recovery.get("healthy", True):
        LOGGER.warning("Startup recovery triggered for: %s", startup_recovery.get("broken_files", []))

    while True:
        cycle_started = datetime.now(timezone.utc)
        last_signal = "N/A"
        last_error = "N/A"

        try:
            result = run_signal_pipeline(settings)
            if isinstance(result, str) and result in {"BUY", "SELL"}:
                last_signal = result
            elif isinstance(result, str) and result:
                last_error = result
        except Exception as error:
            last_error = str(error)
            crash_guard.handle_exception(error)

        if run_once:
            print("Test cycle finished. Exiting.")
            break

        next_cycle = cycle_started + timedelta(minutes=settings.TRADE_INTERVAL_MINUTES)
        while datetime.now(timezone.utc) < next_cycle:
            runtime_state = _build_runtime_state(last_signal=last_signal, last_error=last_error)
            dashboard_message_id = _publish_dashboard(notifier, heartbeat, dashboard_message_id, runtime_state)

            if should_send_daily_report():
                notifier.send(build_daily_report(runtime_state))
                mark_daily_report_sent()
                backup_manager.backup_daily()
                rotate_logs(project_root / "logs", max_size_mb=10, max_files=30)

            if should_send_weekly_report() and datetime.now(timezone.utc).weekday() == 6:
                notifier.send(build_weekly_report(runtime_state))
                mark_weekly_report_sent()

            _maybe_reconnect_mt5(notifier, crash_guard)
            time.sleep(heartbeat.interval.total_seconds())

        runtime_state = _build_runtime_state(last_signal=last_signal, last_error=last_error)
        dashboard_message_id = _publish_dashboard(notifier, heartbeat, dashboard_message_id, runtime_state)

    print("Q-Bot stopped safely.")
