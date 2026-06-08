"""System health monitoring and crash recovery database."""

from __future__ import annotations

import logging
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Any

from backend.brain.nova_config import DB_SYSTEM_HEALTH

LOGGER = logging.getLogger(__name__)


class SystemHealthManager:
    """Track crashes, exceptions, and system warnings."""

    def __init__(self) -> None:
        self._init_database()

    def _init_database(self) -> None:
        """Initialize system_health.db with event tables."""
        conn = sqlite3.connect(str(DB_SYSTEM_HEALTH))
        conn.execute("""
            CREATE TABLE IF NOT EXISTS events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                event_type TEXT NOT NULL,
                severity TEXT NOT NULL,
                component TEXT,
                message TEXT,
                stack_trace TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                resolved BOOLEAN DEFAULT FALSE
            )
        """)

        conn.execute("""
            CREATE TABLE IF NOT EXISTS warnings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                warning_type TEXT NOT NULL,
                metric_name TEXT,
                current_value REAL,
                threshold REAL,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        conn.execute("""
            CREATE TABLE IF NOT EXISTS startup_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                startup_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                mt5_status TEXT,
                telegram_status TEXT,
                gemini_status TEXT,
                brain_status TEXT,
                disk_free_mb INTEGER
            )
        """)

        conn.commit()
        conn.close()

    def log_crash(self, component: str, message: str, stack_trace: str = "") -> None:
        """Log application crash."""
        try:
            conn = sqlite3.connect(str(DB_SYSTEM_HEALTH))
            conn.execute(
                """
                INSERT INTO events (event_type, severity, component, message, stack_trace)
                VALUES (?, ?, ?, ?, ?)
                """,
                ("crash", "CRITICAL", component, message, stack_trace),
            )
            conn.commit()
            conn.close()
            LOGGER.error("Crash logged: %s - %s", component, message)
        except Exception as e:
            LOGGER.error("Failed to log crash: %s", e)

    def log_exception(self, component: str, exception: Exception) -> None:
        """Log exception."""
        try:
            import traceback

            stack_trace = traceback.format_exc()
            conn = sqlite3.connect(str(DB_SYSTEM_HEALTH))
            conn.execute(
                """
                INSERT INTO events (event_type, severity, component, message, stack_trace)
                VALUES (?, ?, ?, ?, ?)
                """,
                ("exception", "ERROR", component, str(exception), stack_trace),
            )
            conn.commit()
            conn.close()
        except Exception as e:
            LOGGER.error("Failed to log exception: %s", e)

    def log_memory_warning(self, current_percent: float, threshold: float = 90.0) -> None:
        """Log memory usage warning."""
        try:
            if current_percent >= threshold:
                conn = sqlite3.connect(str(DB_SYSTEM_HEALTH))
                conn.execute(
                    """
                    INSERT INTO warnings (warning_type, metric_name, current_value, threshold)
                    VALUES (?, ?, ?, ?)
                    """,
                    ("memory", "RAM_PERCENT", current_percent, threshold),
                )
                conn.commit()
                conn.close()
        except Exception as e:
            LOGGER.error("Failed to log memory warning: %s", e)

    def log_cpu_warning(self, current_percent: float, threshold: float = 95.0) -> None:
        """Log CPU usage warning."""
        try:
            if current_percent >= threshold:
                conn = sqlite3.connect(str(DB_SYSTEM_HEALTH))
                conn.execute(
                    """
                    INSERT INTO warnings (warning_type, metric_name, current_value, threshold)
                    VALUES (?, ?, ?, ?)
                    """,
                    ("cpu", "CPU_PERCENT", current_percent, threshold),
                )
                conn.commit()
                conn.close()
        except Exception as e:
            LOGGER.error("Failed to log CPU warning: %s", e)

    def log_mt5_disconnect(self, reason: str = "") -> None:
        """Log MT5 disconnection."""
        try:
            conn = sqlite3.connect(str(DB_SYSTEM_HEALTH))
            conn.execute(
                """
                INSERT INTO events (event_type, severity, component, message)
                VALUES (?, ?, ?, ?)
                """,
                ("disconnect", "WARNING", "MT5", f"MT5 disconnected: {reason}"),
            )
            conn.commit()
            conn.close()
        except Exception as e:
            LOGGER.error("Failed to log MT5 disconnect: %s", e)

    def log_telegram_failure(self, reason: str = "") -> None:
        """Log Telegram failure."""
        try:
            conn = sqlite3.connect(str(DB_SYSTEM_HEALTH))
            conn.execute(
                """
                INSERT INTO events (event_type, severity, component, message)
                VALUES (?, ?, ?, ?)
                """,
                ("failure", "WARNING", "Telegram", f"Telegram failed: {reason}"),
            )
            conn.commit()
            conn.close()
        except Exception as e:
            LOGGER.error("Failed to log Telegram failure: %s", e)

    def log_gemini_failure(self, reason: str = "") -> None:
        """Log Gemini API failure."""
        try:
            conn = sqlite3.connect(str(DB_SYSTEM_HEALTH))
            conn.execute(
                """
                INSERT INTO events (event_type, severity, component, message)
                VALUES (?, ?, ?, ?)
                """,
                ("failure", "WARNING", "Gemini", f"Gemini failed: {reason}"),
            )
            conn.commit()
            conn.close()
        except Exception as e:
            LOGGER.error("Failed to log Gemini failure: %s", e)

    def log_startup(self, mt5_status: str, telegram_status: str, gemini_status: str, brain_status: str) -> None:
        """Log startup attempt."""
        try:
            from backend.brain.nova_config import get_disk_space_mb

            disk_free = get_disk_space_mb(DB_SYSTEM_HEALTH.parent)
            conn = sqlite3.connect(str(DB_SYSTEM_HEALTH))
            conn.execute(
                """
                INSERT INTO startup_history (mt5_status, telegram_status, gemini_status, brain_status, disk_free_mb)
                VALUES (?, ?, ?, ?, ?)
                """,
                (mt5_status, telegram_status, gemini_status, brain_status, disk_free),
            )
            conn.commit()
            conn.close()
        except Exception as e:
            LOGGER.error("Failed to log startup: %s", e)

    def get_recent_errors(self, limit: int = 10) -> list[dict[str, Any]]:
        """Get recent errors."""
        try:
            conn = sqlite3.connect(str(DB_SYSTEM_HEALTH))
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(
                "SELECT * FROM events WHERE severity IN ('ERROR', 'CRITICAL') ORDER BY timestamp DESC LIMIT ?",
                (limit,),
            )
            return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            LOGGER.error("Failed to get errors: %s", e)
            return []

    def get_recent_warnings(self, limit: int = 20) -> list[dict[str, Any]]:
        """Get recent warnings."""
        try:
            conn = sqlite3.connect(str(DB_SYSTEM_HEALTH))
            conn.row_factory = sqlite3.Row
            cursor = conn.execute("SELECT * FROM warnings ORDER BY timestamp DESC LIMIT ?", (limit,))
            return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            LOGGER.error("Failed to get warnings: %s", e)
            return []


_health_manager: SystemHealthManager | None = None


def get_health() -> SystemHealthManager:
    """Get or create singleton health manager."""
    global _health_manager
    if _health_manager is None:
        _health_manager = SystemHealthManager()
    return _health_manager
