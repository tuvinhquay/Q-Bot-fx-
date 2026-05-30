"""Runtime data recovery helpers."""

from __future__ import annotations

import json
from pathlib import Path

from backend.services.deployment.backup_manager import BackupManager, RUNTIME_FILES


class RecoveryManager:
    def __init__(self, backup_manager: BackupManager | None = None) -> None:
        self.backup_manager = backup_manager or BackupManager()

    def _is_valid_json(self, path: Path) -> bool:
        if not path.exists():
            return True
        if path.suffix.lower() != ".json":
            return True
        try:
            json.loads(path.read_text(encoding="utf-8") or "{}")
        except json.JSONDecodeError:
            return False
        return True

    def check_data_integrity(self) -> dict[str, object]:
        broken: list[str] = []
        for relative in RUNTIME_FILES:
            path = self.backup_manager.project_root / relative
            if not self._is_valid_json(path):
                broken.append(relative)
        if not broken:
            return {"healthy": True, "broken_files": [], "restored": False}
        restore = self.backup_manager.restore_latest()
        return {
            "healthy": False,
            "broken_files": broken,
            "restored": bool(restore.get("success")),
            "restore": restore,
        }
