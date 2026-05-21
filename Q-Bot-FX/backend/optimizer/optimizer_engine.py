from __future__ import annotations

from dataclasses import dataclass

from backend.backtest.backtest_engine import BacktestEngine
from backend.backtest.equity_curve import generate_equity_curve
from backend.optimizer.export_results import export_results_to_csv
from backend.optimizer.ranking_engine import rank_strategies


@dataclass
class OptimizerRun:
    symbol: str
    timeframe: int
    metrics: dict


class BacktestOptimizer:
    def __init__(self) -> None:
        self.raw_results: list[dict] = []
        self.ranked_results: list[dict] = []
        self.run_records: list[OptimizerRun] = []

    @staticmethod
    def _tf_label(tf: int) -> str:
        mapping = {
            1: "M1",
            5: "M5",
            15: "M15",
            30: "M30",
            16385: "H1",
            16388: "H4",
            16408: "D1",
        }
        return mapping.get(tf, str(tf))

    def run_optimizer(
        self,
        symbols: list,
        timeframes: list,
        bars: int = 2000,
    ):
        self.raw_results = []
        self.ranked_results = []
        self.run_records = []

        for symbol in symbols:
            for timeframe in timeframes:
                engine = BacktestEngine()
                metrics = engine.run_backtest(symbol=symbol, timeframe=timeframe, bars=bars)
                self.run_records.append(OptimizerRun(symbol=symbol, timeframe=timeframe, metrics=metrics))

                row = {
                    "symbol": symbol,
                    "timeframe": self._tf_label(timeframe),
                    "total_trades": metrics.get("total_trades", 0),
                    "winrate": float(metrics.get("winrate", 0.0)) * 100.0,
                    "profit_factor": float(metrics.get("profit_factor", 0.0)),
                    "expectancy": float(metrics.get("expectancy", 0.0)),
                    "net_profit": float(metrics.get("net_profit", 0.0)),
                    "max_drawdown": float(metrics.get("max_drawdown", 0.0)),
                }
                self.raw_results.append(row)

        self.ranked_results = rank_strategies(self.raw_results)
        export_results_to_csv(self.ranked_results, "optimizer_results.csv")

        print("========================================")
        print("Q-BOT OPTIMIZER RESULTS")
        print("========================================")
        print("TOP STRATEGIES:")

        top3 = self.ranked_results[:3]
        for idx, item in enumerate(top3, start=1):
            print(f"\n{idx}.")
            print(f"{item['symbol']} {item['timeframe']}")
            print(f"Winrate: {item['winrate']:.0f}%")
            print(f"PF: {item['profit_factor']:.2f}")
            print(f"Score: {item['overall_score']:.0f}")

        print("\n========================================")

        if self.ranked_results:
            top = self.ranked_results[0]
            top_record = next(
                (
                    r for r in self.run_records
                    if r.symbol == top["symbol"] and self._tf_label(r.timeframe) == top["timeframe"]
                ),
                None,
            )
            if top_record is not None:
                generate_equity_curve(top_record.metrics.get("equity_curve", []), "top_strategy_equity.png")

        return self.ranked_results
