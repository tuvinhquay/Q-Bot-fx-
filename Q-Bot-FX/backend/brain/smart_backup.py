"""Smart backup system with disk space awareness."""

from __future__ import annotations

import logging
import zipfile
from datetime import datetime
from pathlib import Path

from backend.brain.nova_config import NOVA_BACKUPS_DIR, get_disk_space_mb

LOGGER = logging.getLogger(__name__)


class SmartBackupManager:
    """Intelligent backup with disk space awareness."""

    BACKUP_DIR = NOVA_BACKUPS_DIR
    MIN_FREE_SPACE_MB = 10 * 1024  # 10 GB minimum
    NORMAL_FREE_SPACE_MB = 20 * 1024  # 20 GB threshold

    @staticmethod
    def create_backup(db_files: list[Path]) -> Path | None:
        """Create backup with smart retention."""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_file = BACKUP_DIR / f"nova_backup_{timestamp}.zip"

            with zipfile.ZipFile(backup_file, "w", zipfile.ZIP_DEFLATED) as zipf:
                for db_file in db_files:
                    if db_file.exists():
                        zipf.write(db_file, db_file.name)

            LOGGER.info("Backup created: %s", backup_file)
            SmartBackupManager._cleanup_backups()
            return backup_file
        except Exception as e:
            LOGGER.error("Failed to create backup: %s", e)
            return None

    @staticmethod
    def _cleanup_backups() -> None:
        """Smart backup cleanup based on disk space."""
        try:
            backups = sorted(BACKUP_DIR.glob("nova_backup_*.zip"))
            disk_free_mb = get_disk_space_mb(BACKUP_DIR)

            if disk_free_mb < SmartBackupManager.MIN_FREE_SPACE_MB:
                if backups:
                    oldest = backups[0]
                    oldest.unlink()
                    LOGGER.warning("Removed oldest backup to free space: %s", oldest.name)
            elif disk_free_mb < SmartBackupManager.NORMAL_FREE_SPACE_MB:
                if len(backups) > 1:
                    for backup in backups[:-1]:
                        backup.unlink()
                        LOGGER.info("Removed backup: %s", backup.name)
        except Exception as e:
            LOGGER.error("Failed to cleanup backups: %s", e)

    @staticmethod
    def restore_backup(backup_file: Path, target_dir: Path) -> bool:
        """Restore from backup."""
        try:
            if not backup_file.exists():
                LOGGER.error("Backup file not found: %s", backup_file)
                return False

            with zipfile.ZipFile(backup_file, "r") as zipf:
                zipf.extractall(target_dir)

            LOGGER.info("Backup restored: %s", backup_file)
            return True
        except Exception as e:
            LOGGER.error("Failed to restore backup: %s", e)
            return False

    @staticmethod
    def get_backup_info() -> dict[str, any]:
        """Get backup information."""
        try:
            backups = list(BACKUP_DIR.glob("nova_backup_*.zip"))
            total_size_mb = sum(b.stat().st_size for b in backups) / (1024 * 1024)

            return {
                "count": len(backups),
                "total_size_mb": round(total_size_mb, 2),
                "latest": backups[-1].name if backups else "NONE",
                "disk_free_mb": get_disk_space_mb(BACKUP_DIR),
            }
        except Exception as e:
            LOGGER.error("Failed to get backup info: %s", e)
            return {}
