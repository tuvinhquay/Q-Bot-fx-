from __future__ import annotations

from backend.adaptive.strategy_weight_manager import StrategyWeightManager


def calculate_adaptive_score(
    symbol,
    timeframe,
    performance_stats,
    market_regime,
):
    key = f"{symbol}_{timeframe}"
    manager = StrategyWeightManager()
    weight = manager.get_weight(key)

    winrate = float(performance_stats.get("winrate", 0.0)) * 100.0
    pf = float(performance_stats.get("profit_factor", 0.0))
    drawdown = float(performance_stats.get("max_drawdown", 0.0))
    expectancy = float(performance_stats.get("expectancy", 0.0))

    regime = market_regime.get("regime", "RANGING")
    regime_bonus = {
        "TRENDING": 8.0,
        "RANGING": 3.0,
        "VOLATILE": -4.0,
        "LOW_VOLATILITY": -2.0,
    }.get(regime, 0.0)

    score = (
        (winrate * 0.5)
        + (pf * 15.0)
        + (expectancy * 0.3)
        + regime_bonus
        + (weight * 10.0)
        - (drawdown * 0.1)
    )

    allow_trading = score >= 35.0

    return {
        "adaptive_score": score,
        "weight": weight,
        "allow_trading": allow_trading,
    }
