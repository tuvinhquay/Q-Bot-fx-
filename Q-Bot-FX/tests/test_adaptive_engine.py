from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

BASE_DIR = Path(__file__).resolve().parents[1]
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from backend.adaptive.adaptive_engine import calculate_adaptive_score
from backend.adaptive.learning_memory import (
    load_learning_memory,
    save_learning_memory,
    update_learning_memory,
)
from backend.adaptive.market_regime_detector import detect_market_regime
from backend.adaptive.strategy_weight_manager import StrategyWeightManager


def _sample_df(rows: int = 400) -> pd.DataFrame:
    base = 1.10
    data = {
        "open": [],
        "high": [],
        "low": [],
        "close": [],
        "tick_volume": [],
    }
    for i in range(rows):
        o = base + (i * 0.0001)
        c = o + 0.00005
        h = c + 0.0002
        l = o - 0.0002
        data["open"].append(o)
        data["high"].append(h)
        data["low"].append(l)
        data["close"].append(c)
        data["tick_volume"].append(100 + (i % 20))
    return pd.DataFrame(data)


if __name__ == "__main__":
    df = _sample_df()
    regime = detect_market_regime(df)
    print(f"regime={regime['regime']}")

    stats = {
        "winrate": 0.62,
        "profit_factor": 1.7,
        "expectancy": 14.0,
        "max_drawdown": 20.0,
    }
    adaptive = calculate_adaptive_score("EURUSDm", "H1", stats, regime)
    print(f"adaptive_score={adaptive['adaptive_score']:.2f}")

    manager = StrategyWeightManager()
    new_weight = manager.update_weight("EURUSDm_H1", stats)
    print(f"weight={new_weight}")

    save_learning_memory({})
    update_learning_memory("EURUSDm_H1", regime["regime"], stats)
    mem = load_learning_memory()
    print(f"memory_keys={list(mem.keys())}")
