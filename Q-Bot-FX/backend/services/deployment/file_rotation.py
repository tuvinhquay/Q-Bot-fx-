"""File rotation for generated artifacts."""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path


def rotate_files(directory: Path, keep_days: int = 30, max_files: int = 500) -> dict[str, int]:
    if not directory.exists():
        return {"removed": 0}
    files = [p for p in directory.iterdir() if p.is_file()]
    files.sort(key=lambda p: p.stat().st_mtime, reverse=True)
    now = datetime.now(timezone.utc).timestamp()
    max_age_seconds = keep_days * 24 * 60 * 60
    removed = 0
    for index, path in enumerate(files):
        too_old = now - path.stat().st_mtime > max_age_seconds
        too_many = index >= max_files
        if too_old or too_many:
            path.unlink(missing_ok=True)
            removed += 1
    return {"removed": removed}
