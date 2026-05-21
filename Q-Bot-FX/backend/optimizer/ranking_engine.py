from __future__ import annotations


def rank_strategies(results):
    ranked = []
    for row in results:
        profit_factor = float(row.get("profit_factor", 0.0))
        winrate_pct = float(row.get("winrate", 0.0))
        expectancy = float(row.get("expectancy", 0.0))
        drawdown = float(row.get("max_drawdown", 0.0))

        overall_score = (
            (profit_factor * 0.4)
            + (winrate_pct * 0.3)
            + (expectancy * 0.2)
            - (drawdown * 0.1)
        )

        item = dict(row)
        item["overall_score"] = overall_score
        ranked.append(item)

    ranked.sort(key=lambda x: x["overall_score"], reverse=True)
    return ranked
