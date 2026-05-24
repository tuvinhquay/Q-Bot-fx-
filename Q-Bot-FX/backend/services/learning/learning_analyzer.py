"""Analyzer that converts memory data into warnings and suggestions."""

from __future__ import annotations

from collections import defaultdict
from typing import Any


def analyze_learning(entries: list[dict[str, Any]]) -> dict[str, Any]:
    symbol_stats: dict[str, dict[str, int]] = defaultdict(lambda: {"win": 0, "loss": 0})
    regime_pnl: dict[str, float] = defaultdict(float)

    for item in entries:
        symbol = str(item.get("symbol", "UNKNOWN"))
        regime = str(item.get("market_regime", "UNKNOWN"))
        result = str(item.get("trade_result", "UNKNOWN")).upper()
        pnl = float(item.get("pnl", 0) or 0)

        if result == "WIN":
            symbol_stats[symbol]["win"] += 1
        elif result == "LOSS":
            symbol_stats[symbol]["loss"] += 1
        regime_pnl[regime] += pnl

    warnings: list[str] = []
    suggestions: list[str] = []

    for symbol, stat in symbol_stats.items():
        if stat["loss"] >= 3 and stat["loss"] > stat["win"]:
            warnings.append(f"{symbol} dang thua lien tuc")
            suggestions.append(f"Giam tan suat giao dich {symbol} hoac ha risk tam thoi")

    if regime_pnl:
        worst_regime, worst_value = min(regime_pnl.items(), key=lambda x: x[1])
        best_regime, best_value = max(regime_pnl.items(), key=lambda x: x[1])
        if worst_value < 0:
            warnings.append(f"{worst_regime} dang gay drawdown dang ke")
            suggestions.append(f"Can nhac loc tin hieu chat hon khi thi truong {worst_regime}")
        if best_value > 0:
            suggestions.append(f"{best_regime} dang hoat dong tot, co the uu tien")

    sample = len(entries)
    confidence = "Thấp" if sample < 10 else "Trung bình" if sample < 30 else "Cao"
    insight = f"Muc tin cay hoc may hien tai: {confidence} (mau: {sample} lenh)"

    return {
        "warnings": warnings,
        "suggestions": suggestions,
        "confidence_insight": insight,
    }
