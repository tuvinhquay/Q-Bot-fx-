"""Opportunity ranking based on symbol and regime intelligence."""

from __future__ import annotations

from typing import Any


def rank_opportunity(
    *,
    symbol: str,
    market_regime: str,
    symbol_insight: dict[str, Any],
    regime_insight: dict[str, Any],
    adaptive_confidence: float,
) -> dict[str, Any]:
    symbols = symbol_insight.get("symbols", {})
    stat = symbols.get(symbol, {})
    pnl = float(stat.get("pnl", 0.0))
    consistency = float(stat.get("consistency", 50.0))
    regime_bonus = 10.0 if market_regime == regime_insight.get("best_regime") else -10.0 if market_regime == regime_insight.get("dangerous_regime") else 0.0
    score = adaptive_confidence + (consistency * 0.3) + regime_bonus + (5.0 if pnl > 0 else -5.0 if pnl < 0 else 0.0)
    score = round(min(max(score, 0.0), 100.0), 2)
    strength = "STRONG" if score >= 75 else "MEDIUM" if score >= 50 else "WEAK"
    return {"opportunity_score": score, "strategy_strength": strength}
