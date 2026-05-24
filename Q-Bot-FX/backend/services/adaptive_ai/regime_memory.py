"""Regime memory with safe file persistence."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


class AdaptiveMemoryStore:
    def __init__(self, file_path: Path | None = None) -> None:
        self.file_path = file_path or Path("data/adaptive_memory.json")

    def _ensure_file(self) -> None:
        self.file_path.parent.mkdir(parents=True, exist_ok=True)
        if not self.file_path.exists():
            self.file_path.write_text("{}", encoding="utf-8")

    def load(self) -> dict[str, Any]:
        self._ensure_file()
        raw = self.file_path.read_text(encoding="utf-8").strip()
        if not raw:
            self.file_path.write_text("{}", encoding="utf-8")
            return {}
        try:
            payload = json.loads(raw)
        except json.JSONDecodeError:
            self.file_path.write_text("{}", encoding="utf-8")
            return {}
        return payload if isinstance(payload, dict) else {}

    def save(self, data: dict[str, Any]) -> None:
        self._ensure_file()
        self.file_path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def summarize_regime_memory(learning_entries: list[dict[str, Any]]) -> dict[str, Any]:
    regime_stats: dict[str, dict[str, float]] = {}
    for row in learning_entries:
        regime = str(row.get("market_regime", "UNKNOWN"))
        pnl = float(row.get("pnl", 0) or 0)
        result = str(row.get("trade_result", "")).upper()
        if regime not in regime_stats:
            regime_stats[regime] = {"wins": 0.0, "losses": 0.0, "pnl": 0.0, "trades": 0.0}
        regime_stats[regime]["trades"] += 1
        regime_stats[regime]["pnl"] += pnl
        if result == "WIN":
            regime_stats[regime]["wins"] += 1
        if result == "LOSS":
            regime_stats[regime]["losses"] += 1

    if not regime_stats:
        return {"best_regime": "UNKNOWN", "dangerous_regime": "UNKNOWN", "regime_stats": {}}

    best_regime = max(regime_stats.items(), key=lambda x: x[1]["pnl"])[0]
    dangerous_regime = min(regime_stats.items(), key=lambda x: x[1]["pnl"])[0]
    return {
        "best_regime": best_regime,
        "dangerous_regime": dangerous_regime,
        "regime_stats": regime_stats,
    }
