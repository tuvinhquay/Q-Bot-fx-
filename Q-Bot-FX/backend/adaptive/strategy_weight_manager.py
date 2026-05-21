from __future__ import annotations

import json
from pathlib import Path

WEIGHT_FILE = Path(__file__).resolve().parents[2] / "adaptive_weights.json"


class StrategyWeightManager:
    def __init__(self) -> None:
        self.weights = self.load_weights()

    def load_weights(self):
        if WEIGHT_FILE.exists():
            with open(WEIGHT_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        return {}

    def save_weights(self):
        with open(WEIGHT_FILE, "w", encoding="utf-8") as f:
            json.dump(self.weights, f, indent=2)

    def get_weight(self, key: str) -> float:
        return float(self.weights.get(key, 1.0))

    def update_weight(self, key: str, performance_stats):
        current = self.get_weight(key)
        winrate = float(performance_stats.get("winrate", 0.0))
        drawdown = float(performance_stats.get("max_drawdown", 0.0))
        pf = float(performance_stats.get("profit_factor", 0.0))

        delta = 0.0
        if winrate >= 0.6:
            delta += 0.08
        elif winrate < 0.45:
            delta -= 0.08

        if pf >= 1.5:
            delta += 0.08
        elif pf < 1.0:
            delta -= 0.08

        if drawdown > 100:
            delta -= 0.1
        elif drawdown < 30:
            delta += 0.04

        updated = min(2.0, max(0.2, current + delta))
        self.weights[key] = round(updated, 4)
        self.save_weights()
        return self.weights[key]
