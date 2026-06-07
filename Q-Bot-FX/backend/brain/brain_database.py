"""Brain Database Manager - Core SQLite foundation."""

from __future__ import annotations

import json
import logging
import sqlite3
import threading
import zipfile
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

from backend.brain.brain_config import BRAIN_BACKUPS_DIR
from backend.brain.brain_config import DB_ANALYTICS
from backend.brain.brain_config import DB_LEARNING
from backend.brain.brain_config import DB_QBOT_BRAIN
from backend.brain.brain_config import DB_TRADE_JOURNAL

LOGGER = logging.getLogger(__name__)


class BrainDatabaseManager:
    """Centralized brain database management."""

    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._connections: dict[str, sqlite3.Connection] = {}
        self._init_all_databases()

    def _get_connection(self, db_path: Path) -> sqlite3.Connection:
        """Get or create database connection with thread safety."""
        db_key = str(db_path)

        if db_key in self._connections:
            try:
                self._connections[db_key].execute("SELECT 1")
                return self._connections[db_key]
            except sqlite3.OperationalError:
                del self._connections[db_key]

        conn = sqlite3.connect(str(db_path), check_same_thread=False)
        conn.row_factory = sqlite3.Row
        self._connections[db_key] = conn
        return conn

    def _init_all_databases(self) -> None:
        """Initialize all database schemas."""
        self._init_qbot_brain()
        self._init_trade_journal()
        self._init_learning()
        self._init_analytics()
        LOGGER.info("All brain databases initialized")

    def _init_qbot_brain(self) -> None:
        """Initialize qbot_brain.db with system_memory table."""
        conn = self._get_connection(DB_QBOT_BRAIN)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS system_memory (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                memory_type TEXT NOT NULL,
                key TEXT NOT NULL UNIQUE,
                value TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()

    def _init_trade_journal(self) -> None:
        """Initialize trade_journal.db with trades table."""
        conn = self._get_connection(DB_TRADE_JOURNAL)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS trades (
                trade_id INTEGER PRIMARY KEY AUTOINCREMENT,
                symbol TEXT NOT NULL,
                direction TEXT NOT NULL,
                entry_price REAL NOT NULL,
                exit_price REAL,
                profit REAL,
                session TEXT,
                strategy TEXT,
                result TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()

    def _init_learning(self) -> None:
        """Initialize learning.db with lessons table."""
        conn = self._get_connection(DB_LEARNING)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS lessons (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                category TEXT NOT NULL,
                event TEXT NOT NULL,
                decision TEXT NOT NULL,
                outcome TEXT NOT NULL,
                confidence REAL DEFAULT 0.5,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()

    def _init_analytics(self) -> None:
        """Initialize analytics.db with performance table."""
        conn = self._get_connection(DB_ANALYTICS)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS performance (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date DATE NOT NULL,
                symbol TEXT,
                winrate REAL,
                profit_factor REAL,
                drawdown REAL,
                trades_count INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()

    def save_memory(self, memory_type: str, key: str, value: Any) -> bool:
        """Save data to system_memory."""
        try:
            with self._lock:
                conn = self._get_connection(DB_QBOT_BRAIN)
                value_json = json.dumps(value) if not isinstance(value, str) else value
                conn.execute(
                    """
                    INSERT OR REPLACE INTO system_memory (memory_type, key, value, updated_at)
                    VALUES (?, ?, ?, CURRENT_TIMESTAMP)
                    """,
                    (memory_type, key, value_json),
                )
                conn.commit()
            return True
        except Exception as e:
            LOGGER.error("Failed to save memory: %s", e)
            return False

    def load_memory(self, memory_type: str, key: str) -> Any | None:
        """Load data from system_memory."""
        try:
            with self._lock:
                conn = self._get_connection(DB_QBOT_BRAIN)
                cursor = conn.execute(
                    "SELECT value FROM system_memory WHERE memory_type = ? AND key = ?",
                    (memory_type, key),
                )
                row = cursor.fetchone()
                if row:
                    try:
                        return json.loads(row[0])
                    except json.JSONDecodeError:
                        return row[0]
            return None
        except Exception as e:
            LOGGER.error("Failed to load memory: %s", e)
            return None

    def add_trade(self, trade_data: dict[str, Any]) -> int | None:
        """Add trade to journal."""
        try:
            with self._lock:
                conn = self._get_connection(DB_TRADE_JOURNAL)
                cursor = conn.execute(
                    """
                    INSERT INTO trades
                    (symbol, direction, entry_price, exit_price, profit, session, strategy, result)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        trade_data.get("symbol"),
                        trade_data.get("direction"),
                        trade_data.get("entry_price"),
                        trade_data.get("exit_price"),
                        trade_data.get("profit"),
                        trade_data.get("session"),
                        trade_data.get("strategy"),
                        trade_data.get("result"),
                    ),
                )
                conn.commit()
                return cursor.lastrowid
        except Exception as e:
            LOGGER.error("Failed to add trade: %s", e)
            return None

    def get_trades(self, symbol: str | None = None, limit: int = 100) -> list[dict[str, Any]]:
        """Get trades from journal."""
        try:
            with self._lock:
                conn = self._get_connection(DB_TRADE_JOURNAL)
                if symbol:
                    cursor = conn.execute(
                        "SELECT * FROM trades WHERE symbol = ? ORDER BY timestamp DESC LIMIT ?",
                        (symbol, limit),
                    )
                else:
                    cursor = conn.execute("SELECT * FROM trades ORDER BY timestamp DESC LIMIT ?", (limit,))
                return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            LOGGER.error("Failed to get trades: %s", e)
            return []

    def add_lesson(self, lesson_data: dict[str, Any]) -> int | None:
        """Add lesson to learning database."""
        try:
            with self._lock:
                conn = self._get_connection(DB_LEARNING)
                cursor = conn.execute(
                    """
                    INSERT INTO lessons (category, event, decision, outcome, confidence)
                    VALUES (?, ?, ?, ?, ?)
                    """,
                    (
                        lesson_data.get("category"),
                        lesson_data.get("event"),
                        lesson_data.get("decision"),
                        lesson_data.get("outcome"),
                        lesson_data.get("confidence", 0.5),
                    ),
                )
                conn.commit()
                return cursor.lastrowid
        except Exception as e:
            LOGGER.error("Failed to add lesson: %s", e)
            return None

    def get_lessons(self, category: str | None = None) -> list[dict[str, Any]]:
        """Get lessons from learning database."""
        try:
            with self._lock:
                conn = self._get_connection(DB_LEARNING)
                if category:
                    cursor = conn.execute("SELECT * FROM lessons WHERE category = ?", (category,))
                else:
                    cursor = conn.execute("SELECT * FROM lessons")
                return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            LOGGER.error("Failed to get lessons: %s", e)
            return []

    def save_performance(self, perf_data: dict[str, Any]) -> bool:
        """Save performance metrics."""
        try:
            with self._lock:
                conn = self._get_connection(DB_ANALYTICS)
                conn.execute(
                    """
                    INSERT INTO performance (date, symbol, winrate, profit_factor, drawdown, trades_count)
                    VALUES (?, ?, ?, ?, ?, ?)
                    """,
                    (
                        perf_data.get("date"),
                        perf_data.get("symbol"),
                        perf_data.get("winrate"),
                        perf_data.get("profit_factor"),
                        perf_data.get("drawdown"),
                        perf_data.get("trades_count"),
                    ),
                )
                conn.commit()
                return True
        except Exception as e:
            LOGGER.error("Failed to save performance: %s", e)
            return False

    def get_performance(self, symbol: str | None = None) -> list[dict[str, Any]]:
        """Get performance analytics."""
        try:
            with self._lock:
                conn = self._get_connection(DB_ANALYTICS)
                if symbol:
                    cursor = conn.execute("SELECT * FROM performance WHERE symbol = ?", (symbol,))
                else:
                    cursor = conn.execute("SELECT * FROM performance")
                return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            LOGGER.error("Failed to get performance: %s", e)
            return []

    def create_backup(self) -> Path | None:
        """Create daily backup of all databases."""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_file = BRAIN_BACKUPS_DIR / f"brain_backup_{timestamp}.zip"

            with zipfile.ZipFile(backup_file, "w", zipfile.ZIP_DEFLATED) as zipf:
                for db_file in [DB_QBOT_BRAIN, DB_TRADE_JOURNAL, DB_LEARNING, DB_ANALYTICS]:
                    if db_file.exists():
                        zipf.write(db_file, db_file.name)

            LOGGER.info("Brain backup created: %s", backup_file)
            self._cleanup_old_backups()
            return backup_file
        except Exception as e:
            LOGGER.error("Failed to create backup: %s", e)
            return None

    def _cleanup_old_backups(self, keep_count: int = 30) -> None:
        """Keep only recent backups."""
        try:
            backups = sorted(BRAIN_BACKUPS_DIR.glob("brain_backup_*.zip"))
            if len(backups) > keep_count:
                for backup in backups[:-keep_count]:
                    backup.unlink()
                    LOGGER.info("Removed old backup: %s", backup.name)
        except Exception as e:
            LOGGER.error("Failed to cleanup backups: %s", e)

    def get_brain_status(self) -> dict[str, Any]:
        """Get brain status for reporting."""
        try:
            total_size = 0
            db_count = 0

            for db_file in [DB_QBOT_BRAIN, DB_TRADE_JOURNAL, DB_LEARNING, DB_ANALYTICS]:
                if db_file.exists():
                    total_size += db_file.stat().st_size
                    db_count += 1

            with self._lock:
                conn = self._get_connection(DB_QBOT_BRAIN)
                cursor = conn.execute("SELECT COUNT(*) FROM system_memory")
                memory_records = cursor.fetchone()[0]

            recent_backup = None
            backups = list(BRAIN_BACKUPS_DIR.glob("brain_backup_*.zip"))
            if backups:
                recent_backup = max(backups, key=lambda p: p.stat().st_mtime).name

            return {
                "location": str(DB_QBOT_BRAIN.parent),
                "size_mb": round(total_size / (1024 * 1024), 2),
                "databases": db_count,
                "memory_records": memory_records,
                "last_backup": recent_backup,
            }
        except Exception as e:
            LOGGER.error("Failed to get brain status: %s", e)
            return {}

    def close(self) -> None:
        """Close all database connections."""
        with self._lock:
            for conn in self._connections.values():
                try:
                    conn.close()
                except Exception:
                    pass
            self._connections.clear()


_brain_manager: BrainDatabaseManager | None = None


def get_brain() -> BrainDatabaseManager:
    """Get or create singleton brain manager."""
    global _brain_manager
    if _brain_manager is None:
        _brain_manager = BrainDatabaseManager()
    return _brain_manager
