"""Trade journal rendering for AI learning memory."""

from __future__ import annotations

from typing import Any


def build_trade_journal_line(entry: dict[str, Any]) -> str:
    symbol = entry.get("symbol", "UNKNOWN")
    signal = entry.get("signal", "UNKNOWN")
    regime = entry.get("market_regime", "UNKNOWN")
    ai_score = entry.get("ai_score", 0)
    trade_result = entry.get("trade_result", "UNKNOWN")
    pnl = entry.get("pnl", 0)
    pnl_prefix = "+" if isinstance(pnl, (float, int)) and pnl > 0 else ""
    return (
        "[AI JOURNAL]\n"
        f"{symbol} {signal}\n"
        f"Market: {regime}\n"
        f"AI Score: {ai_score}\n"
        f"Result: {trade_result}\n"
        f"PnL: {pnl_prefix}{pnl}"
    )
