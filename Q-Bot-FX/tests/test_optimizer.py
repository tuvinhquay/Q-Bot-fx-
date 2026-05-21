from __future__ import annotations

import sys
from pathlib import Path

import MetaTrader5 as mt5

BASE_DIR = Path(__file__).resolve().parents[1]
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from backend.optimizer.optimizer_engine import BacktestOptimizer


if __name__ == "__main__":
    optimizer = BacktestOptimizer()

    symbols = [
        "EURUSDm",
        "GBPUSDm",
        "USDJPYm",
    ]

    timeframes = [
        mt5.TIMEFRAME_H1,
        mt5.TIMEFRAME_H4,
    ]

    ranked = optimizer.run_optimizer(
        symbols=symbols,
        timeframes=timeframes,
        bars=1000,
    )

    if ranked:
        top = ranked[0]
        print("TOP RESULT")
        print(f"strategy={top['symbol']} {top['timeframe']}")
        print(f"score={top['overall_score']:.2f}")
        print("csv=optimizer_results.csv")
        print("equity_chart=top_strategy_equity.png")
    else:
        print("No optimizer results produced")
