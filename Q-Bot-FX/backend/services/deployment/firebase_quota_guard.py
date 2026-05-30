"""Firebase free-tier quota guard."""

from __future__ import annotations


def evaluate_firebase_quota(
    *,
    storage_usage_percent: float,
    upload_count: int,
    download_count: int,
    upload_limit: int = 1000,
    download_limit: int = 5000,
) -> dict[str, object]:
    upload_usage = (upload_count / max(upload_limit, 1)) * 100.0
    download_usage = (download_count / max(download_limit, 1)) * 100.0
    peak = max(storage_usage_percent, upload_usage, download_usage)
    if peak >= 95:
        return {
            "level": "CRITICAL",
            "allow_image_upload": False,
            "allow_memory_upload": True,
            "message": "Firebase quota critical, upload memory only",
        }
    if peak >= 80:
        return {
            "level": "WARNING",
            "allow_image_upload": True,
            "allow_memory_upload": True,
            "message": "Firebase quota warning",
        }
    return {
        "level": "OK",
        "allow_image_upload": True,
        "allow_memory_upload": True,
        "message": "Firebase quota healthy",
    }
