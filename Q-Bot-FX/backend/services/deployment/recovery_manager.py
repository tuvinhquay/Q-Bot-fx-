"""Runtime data recovery helpers."""

from __future__ import annotations

import json
from pathlib import Path

from backend.services.deployment.backup_manager import BackupManager, RUNTIME_PATTERNS


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
        for pattern in RUNTIME_PATTERNS:
            for path in self.backup_manager.project_root.glob(pattern):
                if path.is_file() and path.suffix.lower() == ".json" and not self._is_valid_json(path):
                    broken.append(str(path.relative_to(self.backup_manager.project_root)))
        if not broken:
            return {"healthy": True, "broken_files": [], "restored": False}
        restore = self.backup_manager.restore_latest()
        return {
            "healthy": False,
            "broken_files": broken,
            "restored": bool(restore.get("success")),
            "restore": restore,
        }
