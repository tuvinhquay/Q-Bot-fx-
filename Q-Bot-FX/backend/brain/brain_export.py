"""Brain export and import for portability."""

from __future__ import annotations

import json
import logging
import shutil
import zipfile
from datetime import datetime
from pathlib import Path

from backend.brain.brain_config import BRAIN_EXPORTS_DIR, BRAIN_ROOT

LOGGER = logging.getLogger(__name__)


def export_brain(export_name: str | None = None) -> Path | None:
    """Export entire brain to portable ZIP file."""
    try:
        if export_name is None:
            export_name = f"QBOT_BRAIN_EXPORT_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        export_file = BRAIN_EXPORTS_DIR / f"{export_name}.zip"

        with zipfile.ZipFile(export_file, "w", zipfile.ZIP_DEFLATED) as zipf:
            for item in BRAIN_ROOT.rglob("*"):
                if item.is_file():
                    arcname = item.relative_to(BRAIN_ROOT)
                    zipf.write(item, arcname)

        LOGGER.info("Brain exported: %s", export_file)
        return export_file
    except Exception as e:
        LOGGER.error("Failed to export brain: %s", e)
        return None


def import_brain(export_file: Path, overwrite: bool = False) -> bool:
    """Import brain from ZIP file."""
    try:
        if not export_file.exists():
            LOGGER.error("Export file not found: %s", export_file)
            return False

        if BRAIN_ROOT.exists() and not overwrite:
            LOGGER.warning("Brain directory exists. Set overwrite=True to replace.")
            return False

        if not BRAIN_ROOT.exists():
            BRAIN_ROOT.mkdir(parents=True, exist_ok=True)

        with zipfile.ZipFile(export_file, "r") as zipf:
            zipf.extractall(BRAIN_ROOT.parent)

        LOGGER.info("Brain imported: %s", export_file)
        return True
    except Exception as e:
        LOGGER.error("Failed to import brain: %s", e)
        return False


def export_brain_metadata() -> dict[str, any]:
    """Export brain metadata for verification."""
    try:
        metadata = {
            "timestamp": datetime.now().isoformat(),
            "brain_root": str(BRAIN_ROOT),
            "databases": {},
        }

        db_files = list(BRAIN_ROOT.glob("databases/*.db"))
        for db_file in db_files:
            metadata["databases"][db_file.name] = {
                "size_mb": round(db_file.stat().st_size / (1024 * 1024), 2),
                "modified": datetime.fromtimestamp(db_file.stat().st_mtime).isoformat(),
            }

        metadata_file = BRAIN_EXPORTS_DIR / "brain_metadata.json"
        with open(metadata_file, "w") as f:
            json.dump(metadata, f, indent=2)

        return metadata
    except Exception as e:
        LOGGER.error("Failed to export metadata: %s", e)
        return {}
