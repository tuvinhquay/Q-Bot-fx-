"""Disk storage guard for deployment safety."""

from __future__ import annotations

import shutil
from pathlib import Path


def disk_usage(path: Path | str = ".") -> dict[str, object]:
    usage = shutil.disk_usage(path)
    percent = (usage.used / max(usage.total, 1)) * 100.0
    if percent >= 90:
        status = "DANGER"
    elif percent >= 80:
        status = "WARNING"
    else:
        status = "OK"
    return {
        "total": usage.total,
        "used": usage.used,
        "free": usage.free,
        "percent": round(percent, 2),
        "status": status,
        "should_cleanup": percent >= 90,
    }
