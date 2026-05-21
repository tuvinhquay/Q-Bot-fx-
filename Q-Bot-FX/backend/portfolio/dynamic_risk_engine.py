from __future__ import annotations


def calculate_dynamic_risk(
    base_risk_percent: float,
    performance_stats,
    market_regime,
    equity_growth: float = 0.0,
):
    risk = base_risk_percent

    winrate = float(performance_stats.get("winrate", 0.5))
    drawdown = float(performance_stats.get("max_drawdown", 0.0))

    if winrate > 0.6:
        risk += 0.2
    elif winrate < 0.45:
        risk -= 0.2

    if drawdown > 50:
        risk -= 0.4
    elif drawdown > 20:
        risk -= 0.2

    regime = market_regime.get("regime", "RANGING")
    if regime == "VOLATILE":
        risk -= 0.2
    elif regime == "LOW_VOLATILITY":
        risk -= 0.1

    if equity_growth > 0:
        risk += min(0.2, equity_growth * 0.1)

    risk = max(0.6, min(2.0, risk))
    return round(risk, 3)
