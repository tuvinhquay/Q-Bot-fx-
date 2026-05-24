"""Performance tracker for AI learning memory."""

from __future__ import annotations

from collections import defaultdict
from typing import Any


def _safe_float(value: Any) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return 0.0


def calculate_performance_snapshot(entries: list[dict[str, Any]]) -> dict[str, Any]:
    total = len(entries)
    if total == 0:
        return {
            "total_trade": 0,
            "win_rate": 0.0,
            "loss_rate": 0.0,
            "avg_pnl": 0.0,
            "best_symbol": "N/A",
            "worst_symbol": "N/A",
            "best_regime": "N/A",
            "dangerous_regime": "N/A",
        }

    win_count = sum(1 for x in entries if str(x.get("trade_result", "")).upper() == "WIN")
    loss_count = sum(1 for x in entries if str(x.get("trade_result", "")).upper() == "LOSS")
    pnl_values = [_safe_float(x.get("pnl")) for x in entries]

    symbol_pnl: dict[str, float] = defaultdict(float)
    regime_pnl: dict[str, float] = defaultdict(float)
    for row, pnl in zip(entries, pnl_values):
        symbol_pnl[str(row.get("symbol", "UNKNOWN"))] += pnl
        regime_pnl[str(row.get("market_regime", "UNKNOWN"))] += pnl

    best_symbol = max(symbol_pnl.items(), key=lambda item: item[1])[0] if symbol_pnl else "N/A"
    worst_symbol = min(symbol_pnl.items(), key=lambda item: item[1])[0] if symbol_pnl else "N/A"
    best_regime = max(regime_pnl.items(), key=lambda item: item[1])[0] if regime_pnl else "N/A"
    dangerous_regime = min(regime_pnl.items(), key=lambda item: item[1])[0] if regime_pnl else "N/A"

    return {
        "total_trade": total,
        "win_rate": (win_count / total) * 100.0,
        "loss_rate": (loss_count / total) * 100.0,
        "avg_pnl": sum(pnl_values) / total,
        "best_symbol": best_symbol,
        "worst_symbol": worst_symbol,
        "best_regime": best_regime,
        "dangerous_regime": dangerous_regime,
    }
