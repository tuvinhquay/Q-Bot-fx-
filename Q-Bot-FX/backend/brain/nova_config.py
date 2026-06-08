"""Nova Brain configuration for production deployment."""

from __future__ import annotations

import os
import shutil
from pathlib import Path


def _get_largest_free_drive() -> str:
    """Find drive with largest free space."""
    import psutil

    largest_drive = None
    largest_free = 0

    for partition in psutil.disk_partitions():
        try:
            usage = psutil.disk_usage(partition.mountpoint)
            if usage.free > largest_free:
                largest_free = usage.free
                largest_drive = partition.mountpoint
        except (OSError, PermissionError):
            pass

    return largest_drive or "C:\\"


def get_nova_brain_root() -> Path:
    """Get Nova Brain directory with priority logic.

    Priority:
    1. E drive NOVA_BRAIN (preferred external drive)
    2. D drive NOVA_BRAIN (secondary external drive)
    3. Largest free drive auto-detected
    """
    candidates = [
        Path("E:/NOVA_BRAIN"),
        Path("D:/NOVA_BRAIN"),
    ]

    for candidate in candidates:
        if candidate.drive:
            try:
                if os.path.exists(candidate.drive):
                    candidate.mkdir(parents=True, exist_ok=True)
                    return candidate
            except (OSError, PermissionError):
                pass

    largest_drive = _get_largest_free_drive()
    if largest_drive:
        brain_root = Path(largest_drive) / "NOVA_BRAIN"
        brain_root.mkdir(parents=True, exist_ok=True)
        return brain_root

    fallback = Path(__file__).resolve().parents[2] / "nova_brain"
    fallback.mkdir(parents=True, exist_ok=True)
    return fallback


def init_nova_brain_directories() -> dict[str, Path]:
    """Initialize Nova Brain directory structure."""
    brain_root = get_nova_brain_root()

    dirs = {
        "root": brain_root,
        "databases": brain_root / "databases",
        "logs": brain_root / "logs",
        "backups": brain_root / "backups",
        "exports": brain_root / "exports",
        "reports": brain_root / "reports",
        "config": brain_root / "config",
    }

    for dir_path in dirs.values():
        dir_path.mkdir(parents=True, exist_ok=True)

    return dirs


def get_disk_space_mb(path: Path) -> int:
    """Get free disk space in MB."""
    import shutil

    try:
        usage = shutil.disk_usage(path)
        return int(usage.free / (1024 * 1024))
    except Exception:
        return 0


NOVA_BRAIN_DIRS = init_nova_brain_directories()

NOVA_BRAIN_ROOT = NOVA_BRAIN_DIRS["root"]
NOVA_DATABASES_DIR = NOVA_BRAIN_DIRS["databases"]
NOVA_LOGS_DIR = NOVA_BRAIN_DIRS["logs"]
NOVA_BACKUPS_DIR = NOVA_BRAIN_DIRS["backups"]
NOVA_EXPORTS_DIR = NOVA_BRAIN_DIRS["exports"]
NOVA_REPORTS_DIR = NOVA_BRAIN_DIRS["reports"]
NOVA_CONFIG_DIR = NOVA_BRAIN_DIRS["config"]

DB_QBOT_BRAIN = NOVA_DATABASES_DIR / "qbot_brain.db"
DB_TRADE_JOURNAL = NOVA_DATABASES_DIR / "trade_journal.db"
DB_LEARNING = NOVA_DATABASES_DIR / "learning.db"
DB_ANALYTICS = NOVA_DATABASES_DIR / "analytics.db"
DB_SYSTEM_HEALTH = NOVA_DATABASES_DIR / "system_health.db"
