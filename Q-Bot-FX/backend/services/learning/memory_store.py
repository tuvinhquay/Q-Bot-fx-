"""Safe JSON store for learning memory."""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any

LOGGER = logging.getLogger(__name__)


class MemoryStore:
    """Read/write learning memory with corruption tolerance."""

    def __init__(self, file_path: Path | None = None) -> None:
        self.file_path = file_path or Path("data/learning_memory.json")

    def _ensure_file(self) -> None:
        self.file_path.parent.mkdir(parents=True, exist_ok=True)
        if not self.file_path.exists():
            self.file_path.write_text("[]", encoding="utf-8")

    def load(self) -> list[dict[str, Any]]:
        self._ensure_file()
        raw = self.file_path.read_text(encoding="utf-8").strip()
        if not raw:
            LOGGER.warning("[AI MEMORY] learning memory file is empty, resetting.")
            self.file_path.write_text("[]", encoding="utf-8")
            return []
        try:
            payload = json.loads(raw)
        except json.JSONDecodeError:
            LOGGER.warning("[AI MEMORY] learning memory file is corrupted, resetting.")
            self.file_path.write_text("[]", encoding="utf-8")
            return []

        if not isinstance(payload, list):
            LOGGER.warning("[AI MEMORY] invalid learning memory format, resetting.")
            self.file_path.write_text("[]", encoding="utf-8")
            return []
        return [item for item in payload if isinstance(item, dict)]

    def save(self, entries: list[dict[str, Any]]) -> None:
        self._ensure_file()
        self.file_path.write_text(
            json.dumps(entries, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
