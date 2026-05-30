"""Compress old JSON data files."""

from __future__ import annotations

from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile


def compress_json_file(path: Path, remove_original: bool = False) -> dict[str, object]:
    if not path.exists() or path.suffix.lower() != ".json":
        return {"success": False, "reason": "JSON file not found"}
    archive_path = path.with_suffix(".zip")
    with ZipFile(archive_path, "w", compression=ZIP_DEFLATED) as archive:
        archive.write(path, path.name)
    if remove_original:
        path.unlink(missing_ok=True)
    return {"success": True, "archive": str(archive_path)}
