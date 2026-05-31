"""Log rotation for deployed runtime folders."""

from __future__ import annotations

import shutil
from datetime import datetime, timezone
from pathlib import Path


def rotate_logs(log_dir: Path | str, max_size_mb: int = 10, max_files: int = 30) -> dict[str, int]:
    directory = Path(log_dir)
    directory.mkdir(parents=True, exist_ok=True)
    archive_dir = directory / "archive"
    archive_dir.mkdir(parents=True, exist_ok=True)

    archived = 0
    max_bytes = max_size_mb * 1024 * 1024
    for log_file in directory.glob("*.log"):
        if log_file.stat().st_size <= max_bytes:
            continue
        stamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        archive_path = archive_dir / f"{log_file.stem}_{stamp}.log"
        shutil.move(str(log_file), archive_path)
        log_file.touch()
        archived += 1

    files = sorted(archive_dir.glob("*.log"), key=lambda p: p.stat().st_mtime, reverse=True)
    removed = 0
    for old_file in files[max_files:]:
        old_file.unlink(missing_ok=True)
        removed += 1

    return {"archived": archived, "removed": removed}
