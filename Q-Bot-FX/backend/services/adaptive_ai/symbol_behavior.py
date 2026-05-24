"""Symbol behavior intelligence."""

from __future__ import annotations

from typing import Any


def analyze_symbol_behavior(learning_entries: list[dict[str, Any]]) -> dict[str, Any]:
    symbols: dict[str, dict[str, float]] = {}
    for row in learning_entries:
        symbol = str(row.get("symbol", "UNKNOWN"))
        pnl = float(row.get("pnl", 0) or 0)
        result = str(row.get("trade_result", "")).upper()
        if symbol not in symbols:
            symbols[symbol] = {"wins": 0.0, "losses": 0.0, "pnl": 0.0, "trades": 0.0}
        symbols[symbol]["trades"] += 1
        symbols[symbol]["pnl"] += pnl
        if result == "WIN":
            symbols[symbol]["wins"] += 1
        if result == "LOSS":
            symbols[symbol]["losses"] += 1

    if not symbols:
        return {"strongest_symbol": "UNKNOWN", "weakest_symbol": "UNKNOWN", "symbols": {}}

    for stat in symbols.values():
        trades = max(stat["trades"], 1.0)
        stat["winrate"] = stat["wins"] / trades
        stat["consistency"] = stat["winrate"] * 100.0 - (stat["losses"] / trades * 50.0)

    strongest_symbol = max(symbols.items(), key=lambda x: (x[1]["pnl"], x[1]["consistency"]))[0]
    weakest_symbol = min(symbols.items(), key=lambda x: (x[1]["pnl"], x[1]["consistency"]))[0]
    return {
        "strongest_symbol": strongest_symbol,
        "weakest_symbol": weakest_symbol,
        "symbols": symbols,
    }
