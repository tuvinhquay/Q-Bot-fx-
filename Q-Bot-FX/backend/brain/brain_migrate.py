"""Migrate legacy JSON memory to SQLite brain."""

from __future__ import annotations

import json
import logging
from pathlib import Path

from backend.brain.brain_database import get_brain

LOGGER = logging.getLogger(__name__)


def migrate_legacy_json() -> dict[str, int]:
    """Auto-migrate old JSON files to SQLite."""
    stats = {
        "adaptive_memory": 0,
        "learning_memory": 0,
        "daily_guard": 0,
        "trade_history": 0,
        "errors": 0,
    }

    brain = get_brain()

    old_files = [
        ("adaptive_memory.json", "adaptive"),
        ("./data/adaptive_memory.json", "adaptive"),
        ("learning_memory.json", "learning"),
        ("./data/learning_memory.json", "learning"),
        ("./backend/risk/daily_guard.json", "risk"),
        ("trade_history.json", "trades"),
    ]

    for file_path, memory_type in old_files:
        legacy_file = Path(file_path)
        if legacy_file.exists():
            try:
                with open(legacy_file, "r") as f:
                    data = json.load(f)

                if memory_type == "adaptive":
                    brain.save_memory("adaptive_ai", "weights", data)
                    stats["adaptive_memory"] += 1
                elif memory_type == "learning":
                    brain.save_memory("learning_ai", "lessons", data)
                    stats["learning_memory"] += 1
                elif memory_type == "risk":
                    brain.save_memory("risk_management", "daily_guard", data)
                    stats["daily_guard"] += 1
                elif memory_type == "trades":
                    if isinstance(data, list):
                        for trade in data:
                            brain.add_trade(trade)
                            stats["trade_history"] += 1

                LOGGER.info("Migrated: %s -> %s (%d records)", file_path, memory_type, stats[memory_type])
            except Exception as e:
                LOGGER.error("Failed to migrate %s: %s", file_path, e)
                stats["errors"] += 1

    return stats
