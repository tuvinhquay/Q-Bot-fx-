from __future__ import annotations

import MetaTrader5 as mt5

from backend.portfolio.correlation_engine import calculate_correlation_matrix
from backend.portfolio.dynamic_risk_engine import calculate_dynamic_risk
from backend.portfolio.exposure_manager import calculate_exposure


class PortfolioManager:
    def __init__(self, max_heat_percent: float = 6.0) -> None:
        self.max_heat_percent = max_heat_percent

    def _read_open_positions(self):
        positions = mt5.positions_get()
        if not positions:
            return []
        out = []
        for p in positions:
            typ = "BUY" if getattr(p, "type", 0) == getattr(mt5, "POSITION_TYPE_BUY", 0) else "SELL"
            out.append({
                "symbol": getattr(p, "symbol", ""),
                "signal": typ,
                "volume": float(getattr(p, "volume", 0.01)),
            })
        return out

    def get_total_open_risk(self, open_positions, risk_per_trade_percent: float) -> float:
        return float(len(open_positions)) * float(risk_per_trade_percent)

    def get_symbol_exposure(self, open_positions, symbol: str, signal: str):
        return calculate_exposure(open_positions, symbol, signal)

    def calculate_portfolio_heat(self, open_positions, planned_risk_percent: float) -> float:
        return self.get_total_open_risk(open_positions, planned_risk_percent) + planned_risk_percent

    def validate_trade(
        self,
        symbol: str,
        signal: str,
        symbol_data,
        performance_stats,
        market_regime,
        base_risk_percent: float = 1.0,
    ):
        open_positions = self._read_open_positions()

        dynamic_risk = calculate_dynamic_risk(
            base_risk_percent=base_risk_percent,
            performance_stats=performance_stats,
            market_regime=market_regime,
            equity_growth=float(performance_stats.get("net_profit", 0.0)) / 1000.0,
        )

        heat = self.calculate_portfolio_heat(open_positions, dynamic_risk)
        if heat > self.max_heat_percent:
            return {
                "allow_trade": False,
                "reason": "Portfolio heat too high",
                "portfolio_heat": heat,
                "dynamic_risk": dynamic_risk,
                "correlation_risk": "N/A",
                "directional_bias": "N/A",
            }

        exposure = self.get_symbol_exposure(open_positions, symbol, signal)
        if not exposure["allow_trade"]:
            return {
                "allow_trade": False,
                "reason": exposure["reason"],
                "portfolio_heat": heat,
                "dynamic_risk": dynamic_risk,
                "correlation_risk": "N/A",
                "directional_bias": exposure["directional_bias"],
            }

        corr = calculate_correlation_matrix(symbol_data)
        corr_risk = "LOW"
        for pair, val in corr.items():
            if symbol in pair and abs(val) > 0.85:
                corr_risk = "HIGH"
                return {
                    "allow_trade": False,
                    "reason": f"Correlation too high in {pair}",
                    "portfolio_heat": heat,
                    "dynamic_risk": dynamic_risk,
                    "correlation_risk": corr_risk,
                    "directional_bias": exposure["directional_bias"],
                }

        return {
            "allow_trade": True,
            "reason": "OK",
            "portfolio_heat": heat,
            "dynamic_risk": dynamic_risk,
            "correlation_risk": corr_risk,
            "directional_bias": exposure["directional_bias"],
        }
