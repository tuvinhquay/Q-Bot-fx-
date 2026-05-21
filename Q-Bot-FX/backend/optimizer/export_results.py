from __future__ import annotations

import csv


COLUMNS = [
    "symbol",
    "timeframe",
    "total_trades",
    "winrate",
    "profit_factor",
    "expectancy",
    "net_profit",
    "max_drawdown",
    "overall_score",
]


def export_results_to_csv(results, output_file):
    with open(output_file, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=COLUMNS)
        writer.writeheader()
        for row in results:
            writer.writerow({k: row.get(k, "") for k in COLUMNS})
