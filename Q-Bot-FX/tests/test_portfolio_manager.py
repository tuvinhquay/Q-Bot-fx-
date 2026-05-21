from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

BASE_DIR = Path(__file__).resolve().parents[1]
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from backend.portfolio.correlation_engine import calculate_correlation_matrix
from backend.portfolio.dynamic_risk_engine import calculate_dynamic_risk
from backend.portfolio.exposure_manager import calculate_exposure
from backend.portfolio.portfolio_manager import PortfolioManager


def _df(seed: float):
    close = [seed + (i * 0.001) for i in range(250)]
    return pd.DataFrame({"close": close})


if __name__ == "__main__":
    symbol_data = {
        "EURUSDm": _df(1.1),
        "GBPUSDm": _df(1.2),
        "USDJPYm": _df(150.0),
    }
    corr = calculate_correlation_matrix(symbol_data)
    print(f"corr_pairs={len(corr)}")

    open_trades = [
        {"symbol": "EURUSDm", "signal": "BUY", "volume": 0.01},
        {"symbol": "GBPUSDm", "signal": "BUY", "volume": 0.01},
    ]
    exposure = calculate_exposure(open_trades, "EURUSDm", "BUY", max_abs_exposure=2)
    print(f"exposure_allow={exposure['allow_trade']}")

    stats = {"winrate": 0.62, "max_drawdown": 15.0, "profit_factor": 1.8, "net_profit": 120.0}
    regime = {"regime": "TRENDING"}
    dynamic = calculate_dynamic_risk(1.0, stats, regime, equity_growth=0.2)
    print(f"dynamic_risk={dynamic}")

    manager = PortfolioManager(max_heat_percent=2.0)
    heat = manager.calculate_portfolio_heat(open_trades, planned_risk_percent=1.0)
    print(f"heat={heat}")

    # Monkeypatch open positions reader for deterministic test
    manager._read_open_positions = lambda: open_trades  # type: ignore[method-assign]
    blocked = manager.validate_trade(
        symbol="GBPUSDm",
        signal="BUY",
        symbol_data=symbol_data,
        performance_stats=stats,
        market_regime=regime,
        base_risk_percent=1.0,
    )
    print(f"blocked={not blocked['allow_trade']}")
