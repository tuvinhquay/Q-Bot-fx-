"""Brain configuration and directory management."""

from __future__ import annotations

import os
from pathlib import Path


def get_brain_root() -> Path:
    """Get brain directory with fallback logic.

    Priority:
    1. D:\QBOT_BRAIN
    2. E:\QBOT_BRAIN
    3. <project_root>\brain
    """
    candidates = [
        Path("D:\\QBOT_BRAIN"),
        Path("E:\\QBOT_BRAIN"),
    ]

    for candidate in candidates:
        if candidate.drive:
            try:
                if os.path.exists(candidate.drive):
                    candidate.mkdir(parents=True, exist_ok=True)
                    return candidate
            except (OSError, PermissionError):
                pass

    fallback = Path(__file__).resolve().parents[2] / "brain"
    fallback.mkdir(parents=True, exist_ok=True)
    return fallback


def init_brain_directories() -> dict[str, Path]:
    """Initialize all brain subdirectories."""
    brain_root = get_brain_root()

    dirs = {
        "root": brain_root,
        "databases": brain_root / "databases",
        "logs": brain_root / "logs",
        "backups": brain_root / "backups",
        "exports": brain_root / "exports",
        "config": brain_root / "config",
    }

    for dir_path in dirs.values():
        dir_path.mkdir(parents=True, exist_ok=True)

    return dirs


BRAIN_DIRS = init_brain_directories()

BRAIN_ROOT = BRAIN_DIRS["root"]
BRAIN_DATABASES_DIR = BRAIN_DIRS["databases"]
BRAIN_LOGS_DIR = BRAIN_DIRS["logs"]
BRAIN_BACKUPS_DIR = BRAIN_DIRS["backups"]
BRAIN_EXPORTS_DIR = BRAIN_DIRS["exports"]
BRAIN_CONFIG_DIR = BRAIN_DIRS["config"]

DB_QBOT_BRAIN = BRAIN_DATABASES_DIR / "qbot_brain.db"
DB_TRADE_JOURNAL = BRAIN_DATABASES_DIR / "trade_journal.db"
DB_LEARNING = BRAIN_DATABASES_DIR / "learning.db"
DB_ANALYTICS = BRAIN_DATABASES_DIR / "analytics.db"
