"""Deployment status report formatter."""

from __future__ import annotations


def build_deployment_report(
    *,
    backup_ok: bool,
    firebase_ok: bool,
    disk_percent: float,
    files_healthy: bool,
    recovery_ready: bool,
) -> str:
    backup = "OK" if backup_ok else "FAILED"
    firebase = "OK" if firebase_ok else "LOCAL ONLY"
    files = "Healthy" if files_healthy else "Needs recovery"
    recovery = "Ready" if recovery_ready else "Unavailable"
    return (
        "Q-BOT DEPLOYMENT STATUS\n"
        f"Backup: {backup}\n"
        f"Firebase: {firebase}\n"
        f"Storage: {disk_percent:.2f}%\n"
        f"Files: {files}\n"
        f"Recovery: {recovery}"
    )


def build_backup_telegram_message(files_saved: int, firebase_synced: bool, disk_percent: float) -> str:
    firebase = "Firebase synced" if firebase_synced else "Local backup created"
    return (
        "CLOUD BACKUP SUCCESS\n\n"
        f"Files saved: {files_saved}\n"
        f"{firebase}\n"
        f"Disk usage: {disk_percent:.2f}%\n\n"
        "Recovery point created"
    )
