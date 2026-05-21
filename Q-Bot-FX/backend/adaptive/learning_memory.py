from __future__ import annotations

import json
from pathlib import Path

MEMORY_FILE = Path(__file__).resolve().parents[2] / "learning_memory.json"


def load_learning_memory():
    if MEMORY_FILE.exists():
        with open(MEMORY_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def save_learning_memory(memory):
    with open(MEMORY_FILE, "w", encoding="utf-8") as f:
        json.dump(memory, f, indent=2)


def update_learning_memory(key: str, regime: str, stats):
    memory = load_learning_memory()
    memory[key] = {
        "best_regime": regime,
        "winrate": float(stats.get("winrate", 0.0)) * 100.0,
        "profit_factor": float(stats.get("profit_factor", 0.0)),
    }
    save_learning_memory(memory)
    return memory[key]
