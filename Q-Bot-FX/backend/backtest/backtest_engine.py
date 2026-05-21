from __future__ import annotations

from dataclasses import dataclass

import MetaTrader5 as mt5
import pandas as pd

from backend.analysis.confluence_engine import check as check_confluence
from backend.analysis.sl_tp_engine import calculate_stop_loss, calculate_take_profit
from backend.analysis.structure_detector import analyze as analyze_structure
from backend.analysis.trend_engine import detect_trend
from backend.backtest.equity_curve import generate_equity_curve
from backend.backtest.metrics import calculate_backtest_metrics
from backend.backtest.report_generator import generate_backtest_report


@dataclass
class SimTrade:
    symbol: str
    signal: str
    entry: float
    sl: float
    tp: float
    rr: float
    profit: float
    result: str


class BacktestEngine:
    def __init__(self) -> None:
        self.trades: list[dict] = []
        self.balance = 0.0
        self.equity_history: list[float] = []

    def _fetch_historical(self, symbol: str, timeframe: int, bars: int) -> pd.DataFrame:
        if not mt5.initialize():
            raise RuntimeError("MT5 initialize failed for backtest")

        rates = mt5.copy_rates_from_pos(symbol, timeframe, 0, bars)
        mt5.shutdown()

        if rates is None or len(rates) == 0:
            return pd.DataFrame()

        df = pd.DataFrame(rates)
        if "time" in df.columns:
            df["time"] = pd.to_datetime(df["time"], unit="s")
        return df

    @staticmethod
    def _simulate_trade(current_df: pd.DataFrame, signal: str, entry: float, sl: float, tp: float) -> tuple[float, str]:
        forward = current_df.iloc[-1:]
        if forward.empty:
            return 0.0, "OPEN"

        candle = forward.iloc[0]
        high = float(candle["high"])
        low = float(candle["low"])

        if signal == "BUY":
            if low <= sl:
                return entry - sl, "LOSS"
            if high >= tp:
                return tp - entry, "WIN"
        else:
            if high >= sl:
                return entry - sl, "LOSS"
            if low <= tp:
                return entry - tp, "WIN"

        return 0.0, "OPEN"

    def run_backtest(
        self,
        symbol: str,
        timeframe,
        bars: int = 2000,
        initial_balance: float = 1000.0,
    ):
        self.balance = initial_balance
        self.trades = []
        self.equity_history = [initial_balance]

        df = self._fetch_historical(symbol, timeframe, bars)
        if df.empty:
            raise RuntimeError("No historical data returned from MT5")

        # Replay candle by candle
        for i in range(300, len(df)):
            current_df = df.iloc[: i + 1].copy()

            # Multi-timeframe slices from same dataset for deterministic backtest
            d1_df = current_df.resample("1d", on="time").agg({"open": "first", "high": "max", "low": "min", "close": "last", "tick_volume": "sum"}).dropna()
            h4_df = current_df.resample("4h", on="time").agg({"open": "first", "high": "max", "low": "min", "close": "last", "tick_volume": "sum"}).dropna()
            h1_df = current_df

            trend = detect_trend(d1_df, h4_df)
            if trend.trend == "SIDEWAYS":
                continue

            structure = analyze_structure(h1_df)
            confl = check_confluence(h1_df, structure)
            if not confl.valid:
                continue

            signal = "BUY" if trend.trend == "BULLISH" else "SELL"
            entry = float(h1_df["close"].iloc[-1])

            sl_result = calculate_stop_loss(h1_df, signal, entry, self.balance)
            if not sl_result.valid:
                continue

            tp_result = calculate_take_profit(h1_df, signal, entry, sl_result.sl_price)
            rr = float(tp_result.rr_ratio)

            pnl_unit, result = self._simulate_trade(current_df, signal, entry, sl_result.sl_price, tp_result.tp_price)
            if result == "OPEN":
                continue

            # Simple position PnL model
            lot = 0.01
            profit = pnl_unit * 100000 * lot
            self.balance += profit
            self.equity_history.append(self.balance)

            self.trades.append(
                {
                    "symbol": symbol,
                    "signal": signal,
                    "entry": entry,
                    "sl": float(sl_result.sl_price),
                    "tp": float(tp_result.tp_price),
                    "rr": rr,
                    "profit": float(profit),
                    "result": result,
                }
            )

        metrics = calculate_backtest_metrics(self.trades)
        generate_equity_curve(metrics["equity_curve"], "backtest_equity.png")
        generate_backtest_report(metrics, symbol=symbol, timeframe=str(timeframe))
        return metrics
