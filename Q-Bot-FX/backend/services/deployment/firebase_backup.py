"""Firebase backup adapter.

This module is intentionally dependency-light. A real Firebase client can be
injected later without coupling deployment safety to the trading engine.
"""

from __future__ import annotations

from pathlib import Path
from typing import Protocol

from backend.services.deployment.firebase_quota_guard import evaluate_firebase_quota


class FirebaseClient(Protocol):
    def upload(self, local_path: Path, remote_name: str) -> bool: ...

    def download(self, remote_name: str, local_path: Path) -> bool: ...

    def exists(self, remote_name: str) -> bool: ...


class FirebaseBackup:
    def __init__(self, client: FirebaseClient | None = None) -> None:
        self.client = client

    def upload_backup(self, archive_path: Path, quota_state: dict[str, object] | None = None) -> dict[str, object]:
        quota = quota_state or evaluate_firebase_quota(storage_usage_percent=0, upload_count=0, download_count=0)
        if not quota["allow_memory_upload"]:
            return {"success": False, "reason": "Firebase quota blocked memory upload"}
        if self.client is None:
            return {"success": True, "mode": "local-only", "reason": "Firebase client not configured"}
        ok = self.client.upload(archive_path, archive_path.name)
        return {"success": ok, "mode": "firebase"}

    def download_backup(self, remote_name: str, local_path: Path) -> dict[str, object]:
        if self.client is None:
            return {"success": False, "reason": "Firebase client not configured"}
        return {"success": self.client.download(remote_name, local_path)}

    def verify_backup(self, remote_name: str) -> dict[str, object]:
        if self.client is None:
            return {"success": True, "mode": "local-only", "reason": "Firebase client not configured"}
        return {"success": self.client.exists(remote_name)}
