"""Local backup manager for AI runtime data."""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile

PROJECT_ROOT = Path(__file__).resolve().parents[3]

RUNTIME_FILES = [
    "learning_memory.json",
    "adaptive_memory.json",
    "trade_history.json",
    "capital_state.json",
    "session_memory.json",
    "data/learning_memory.json",
    "data/adaptive_memory.json",
    "data/trade_history.json",
    "data/capital_state.json",
    "data/session_memory.json",
]


class BackupManager:
    """Create and restore local recovery points without touching trading logic."""

    def __init__(self, project_root: Path | None = None, backup_dir: Path | None = None) -> None:
        self.project_root = project_root or PROJECT_ROOT
        self.backup_dir = backup_dir or (self.project_root / "backups")
        self.backup_dir.mkdir(parents=True, exist_ok=True)

    def _existing_targets(self) -> list[Path]:
        targets: list[Path] = []
        for relative in RUNTIME_FILES:
            path = self.project_root / relative
            if path.exists() and path.is_file():
                targets.append(path)
        return targets

    def backup_now(self) -> dict[str, object]:
        timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d_%H%M%S")
        archive_path = self.backup_dir / f"{timestamp}.zip"
        targets = self._existing_targets()
        with ZipFile(archive_path, "w", compression=ZIP_DEFLATED) as archive:
            for path in targets:
                archive.write(path, path.relative_to(self.project_root))
        return {
            "success": True,
            "archive": str(archive_path),
            "files_saved": len(targets),
        }

    def list_backups(self) -> list[Path]:
        return sorted(self.backup_dir.glob("*.zip"), key=lambda p: p.stat().st_mtime, reverse=True)

    def restore_latest(self) -> dict[str, object]:
        backups = self.list_backups()
        if not backups:
            return {"success": False, "reason": "No backup found"}
        latest = backups[0]
        with ZipFile(latest, "r") as archive:
            archive.extractall(self.project_root)
        return {"success": True, "archive": str(latest)}

    def cleanup_old_backups(self, keep_days: int = 30, keep_files: int = 30) -> dict[str, int]:
        now = datetime.now(timezone.utc).timestamp()
        max_age_seconds = keep_days * 24 * 60 * 60
        backups = self.list_backups()
        removed = 0
        for index, backup in enumerate(backups):
            too_old = now - backup.stat().st_mtime > max_age_seconds
            too_many = index >= keep_files
            if too_old or too_many:
                backup.unlink(missing_ok=True)
                removed += 1
        return {"removed": removed}
