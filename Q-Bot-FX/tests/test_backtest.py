from __future__ import annotations

import sys
from pathlib import Path

import MetaTrader5 as mt5

BASE_DIR = Path(__file__).resolve().parents[1]
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from backend.backtest.backtest_engine import BacktestEngine


if __name__ == "__main__":
    engine = BacktestEngine()
    metrics = engine.run_backtest(
        symbol="EURUSDm",
        timeframe=mt5.TIMEFRAME_H1,
        bars=1000,
    )
    print("BACKTEST SUMMARY")
    print(f"total_trades={metrics['total_trades']}")
    print(f"winrate={metrics['winrate'] * 100:.2f}%")
    print(f"net_profit={metrics['net_profit']:.2f}")
    print("equity_chart=backtest_equity.png")
