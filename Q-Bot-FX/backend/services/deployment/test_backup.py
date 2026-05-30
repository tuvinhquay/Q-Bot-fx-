"""Standalone deployment backup tests."""

from __future__ import annotations

import shutil
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[3]
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from backend.services.deployment.backup_manager import BackupManager
from backend.services.deployment.data_compressor import compress_json_file
from backend.services.deployment.deployment_report import build_deployment_report
from backend.services.deployment.file_rotation import rotate_files
from backend.services.deployment.firebase_backup import FirebaseBackup
from backend.services.deployment.firebase_quota_guard import evaluate_firebase_quota
from backend.services.deployment.recovery_manager import RecoveryManager
from backend.services.deployment.storage_guard import disk_usage


def main() -> None:
    sandbox = BASE_DIR / "tmp_deployment_test"
    if sandbox.exists():
        shutil.rmtree(sandbox)
    (sandbox / "data").mkdir(parents=True)
    (sandbox / "data" / "learning_memory.json").write_text("[]", encoding="utf-8")
    (sandbox / "data" / "adaptive_memory.json").write_text("{}", encoding="utf-8")
    (sandbox / "trade_history.json").write_text("[]", encoding="utf-8")

    manager = BackupManager(project_root=sandbox, backup_dir=sandbox / "backups")
    backup = manager.backup_now()
    backups = manager.list_backups()
    quota = evaluate_firebase_quota(storage_usage_percent=20, upload_count=5, download_count=8)
    firebase = FirebaseBackup().upload_backup(Path(str(backup["archive"])), quota)
    storage = disk_usage(sandbox)
    recovery = RecoveryManager(manager).check_data_integrity()
    compression = compress_json_file(sandbox / "trade_history.json")
    rotation = rotate_files(sandbox / "reports", keep_days=30, max_files=500)
    report = build_deployment_report(
        backup_ok=bool(backup["success"]),
        firebase_ok=bool(firebase["success"]),
        disk_percent=float(storage["percent"]),
        files_healthy=bool(recovery["healthy"]),
        recovery_ready=bool(backups),
    )

    print("[DEPLOYMENT] backup:", backup)
    print("[DEPLOYMENT] backups:", [p.name for p in backups])
    print("[DEPLOYMENT] quota:", quota)
    print("[DEPLOYMENT] firebase:", firebase)
    print("[DEPLOYMENT] storage:", storage)
    print("[DEPLOYMENT] recovery:", recovery)
    print("[DEPLOYMENT] compression:", compression)
    print("[DEPLOYMENT] rotation:", rotation)
    print("[DEPLOYMENT REPORT]\n" + report)

    if sandbox.exists():
        shutil.rmtree(sandbox)


if __name__ == "__main__":
    main()
