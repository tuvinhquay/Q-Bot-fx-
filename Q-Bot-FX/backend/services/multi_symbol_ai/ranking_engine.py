"""Multi-symbol opportunity ranking."""

from __future__ import annotations

from typing import Any


def _symbol_stats(entries: list[dict[str, Any]], symbol: str) -> dict[str, float]:
    rows = [x for x in entries if str(x.get("symbol", "")).upper() == symbol.upper()]
    if not rows:
        return {"winrate": 50.0, "pnl": 0.0, "consistency": 50.0}
    wins = sum(1 for r in rows if str(r.get("trade_result", "")).upper() == "WIN")
    losses = sum(1 for r in rows if str(r.get("trade_result", "")).upper() == "LOSS")
    total = max(len(rows), 1)
    pnl = sum(float(r.get("pnl", 0) or 0) for r in rows)
    winrate = (wins / total) * 100.0
    consistency = winrate - ((losses / total) * 35.0)
    return {"winrate": winrate, "pnl": pnl, "consistency": consistency}


def build_market_ranking(symbols: list[str], learning_entries: list[dict[str, Any]], volatility_map: dict[str, float]) -> list[dict[str, Any]]:
    ranking: list[dict[str, Any]] = []
    for sym in symbols:
        stat = _symbol_stats(learning_entries, sym)
        vol = float(volatility_map.get(sym, 0.5))
        vol_score = max(0.0, 100.0 - (vol * 100.0))
        score = 0.45 * stat["winrate"] + 0.35 * stat["consistency"] + 0.20 * vol_score
        if stat["pnl"] > 0:
            score += 5
        elif stat["pnl"] < 0:
            score -= 5
        ranking.append(
            {
                "symbol": sym,
                "opportunity_score": round(min(max(score, 0.0), 100.0), 2),
                "volatility": vol,
                "winrate": round(stat["winrate"], 2),
                "pnl": round(stat["pnl"], 2),
            }
        )
    ranking.sort(key=lambda x: x["opportunity_score"], reverse=True)
    return ranking
