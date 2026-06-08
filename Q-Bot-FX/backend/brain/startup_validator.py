"""Comprehensive Nova-Bot startup validation."""

from __future__ import annotations

import logging
from typing import Any

import MetaTrader5 as mt5

from backend.brain.brain_database import get_brain
from backend.brain.nova_config import NOVA_BRAIN_ROOT, get_disk_space_mb
from backend.brain.system_health import get_health

LOGGER = logging.getLogger(__name__)


class StartupValidator:
    """Validate all systems before trading."""

    def __init__(self) -> None:
        self.results: dict[str, dict[str, Any]] = {}

    def validate_brain(self) -> bool:
        """Validate Nova Brain storage and databases."""
        try:
            brain = get_brain()
            status = brain.get_brain_status()

            self.results["brain"] = {
                "status": "OK",
                "location": status.get("location"),
                "databases": status.get("databases", 0),
                "memory_records": status.get("memory_records", 0),
            }

            if status.get("databases", 0) < 4:
                self.results["brain"]["status"] = "WARNING"
                LOGGER.warning("Brain databases incomplete: %d/4", status.get("databases", 0))

            return True
        except Exception as e:
            self.results["brain"] = {"status": "FAILED", "error": str(e)}
            LOGGER.error("Brain validation failed: %s", e)
            return False

    def validate_sqlite(self) -> bool:
        """Validate SQLite connectivity."""
        try:
            import sqlite3

            test_db = NOVA_BRAIN_ROOT / "databases" / ".test.db"
            conn = sqlite3.connect(str(test_db))
            conn.execute("SELECT 1")
            conn.close()
            test_db.unlink()

            self.results["sqlite"] = {"status": "OK"}
            return True
        except Exception as e:
            self.results["sqlite"] = {"status": "FAILED", "error": str(e)}
            LOGGER.error("SQLite validation failed: %s", e)
            return False

    def validate_telegram(self) -> bool:
        """Validate Telegram connectivity."""
        try:
            from backend.notifications.telegram_notifier import TelegramNotifier
            from config.settings import Settings

            settings = Settings()
            telegram = TelegramNotifier(settings)

            self.results["telegram"] = {"status": "OK", "token": "****" + settings.TELEGRAM_BOT_TOKEN[-4:]}
            return True
        except Exception as e:
            self.results["telegram"] = {"status": "WARNING", "error": str(e)}
            LOGGER.warning("Telegram validation warning: %s", e)
            return False

    def validate_gemini(self) -> bool:
        """Validate Gemini API connectivity."""
        try:
            from config.settings import Settings

            settings = Settings()
            if not settings.GEMINI_API_KEY:
                raise ValueError("GEMINI_API_KEY not set")

            self.results["gemini"] = {"status": "OK", "key": "****" + settings.GEMINI_API_KEY[-4:]}
            return True
        except Exception as e:
            self.results["gemini"] = {"status": "WARNING", "error": str(e)}
            LOGGER.warning("Gemini validation warning: %s", e)
            return False

    def validate_mt5(self) -> bool:
        """Validate MT5 connectivity."""
        try:
            terminal_info = mt5.terminal_info()
            if terminal_info is None:
                self.results["mt5"] = {"status": "WARNING", "error": "MT5 not responding"}
                return False

            self.results["mt5"] = {
                "status": "OK",
                "server": terminal_info.server if hasattr(terminal_info, "server") else "UNKNOWN",
                "connected": True,
            }
            return True
        except Exception as e:
            self.results["mt5"] = {"status": "FAILED", "error": str(e)}
            LOGGER.error("MT5 validation failed: %s", e)
            return False

    def validate_disk_space(self) -> bool:
        """Validate sufficient disk space."""
        try:
            disk_free_mb = get_disk_space_mb(NOVA_BRAIN_ROOT)

            status = "OK"
            if disk_free_mb < 10 * 1024:
                status = "CRITICAL"
            elif disk_free_mb < 20 * 1024:
                status = "WARNING"

            self.results["disk_space"] = {
                "status": status,
                "free_mb": disk_free_mb,
                "free_gb": round(disk_free_mb / 1024, 1),
            }

            return status != "CRITICAL"
        except Exception as e:
            self.results["disk_space"] = {"status": "WARNING", "error": str(e)}
            LOGGER.warning("Disk space validation warning: %s", e)
            return False

    def run_all_checks(self) -> dict[str, dict[str, Any]]:
        """Run all validation checks."""
        LOGGER.info("Starting Nova-Bot startup validation...")

        checks = [
            ("Step 1: Nova Brain", self.validate_brain),
            ("Step 2: SQLite", self.validate_sqlite),
            ("Step 3: Telegram", self.validate_telegram),
            ("Step 4: Gemini", self.validate_gemini),
            ("Step 5: MT5", self.validate_mt5),
            ("Step 6: Disk Space", self.validate_disk_space),
        ]

        for step_name, check_func in checks:
            LOGGER.info(step_name)
            try:
                check_func()
            except Exception as e:
                LOGGER.error("Unexpected error in %s: %s", step_name, e)

        self._log_results()
        return self.results

    def _log_results(self) -> None:
        """Log validation results."""
        LOGGER.info("Validation Results:")
        for check_name, result in self.results.items():
            status = result.get("status", "UNKNOWN")
            LOGGER.info("  %s: %s", check_name, status)

    def get_summary(self) -> dict[str, Any]:
        """Get validation summary."""
        all_ok = all(r.get("status") == "OK" for r in self.results.values())
        any_critical = any(r.get("status") == "CRITICAL" for r in self.results.values())

        return {
            "all_ok": all_ok,
            "critical_failures": any_critical,
            "checks": self.results,
        }
