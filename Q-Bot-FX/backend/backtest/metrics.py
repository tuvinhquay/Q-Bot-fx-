from __future__ import annotations

from typing import Any


def _streaks(results: list[str]) -> tuple[int, int]:
    max_win = 0
    max_loss = 0
    cur_win = 0
    cur_loss = 0

    for r in results:
        if r == "WIN":
            cur_win += 1
            cur_loss = 0
            max_win = max(max_win, cur_win)
        else:
            cur_loss += 1
            cur_win = 0
            max_loss = max(max_loss, cur_loss)

    return max_win, max_loss


def calculate_backtest_metrics(trades: list[dict[str, Any]]) -> dict[str, float | int | list[float]]:
    if not trades:
        return {
            "total_trades": 0,
            "wins": 0,
            "losses": 0,
            "winrate": 0.0,
            "net_profit": 0.0,
            "gross_profit": 0.0,
            "gross_loss": 0.0,
            "profit_factor": 0.0,
            "expectancy": 0.0,
            "average_rr": 0.0,
            "max_drawdown": 0.0,
            "longest_win_streak": 0,
            "longest_loss_streak": 0,
            "equity_curve": [],
        }

    profits = [float(t["profit"]) for t in trades]
    wins = [p for p in profits if p > 0]
    losses = [p for p in profits if p <= 0]

    total_trades = len(trades)
    win_count = len(wins)
    loss_count = len(losses)
    winrate = win_count / total_trades if total_trades else 0.0

    gross_profit = sum(wins)
    gross_loss = sum(losses)
    net_profit = sum(profits)

    profit_factor = (gross_profit / abs(gross_loss)) if gross_loss < 0 else 0.0
    avg_win = gross_profit / win_count if win_count else 0.0
    avg_loss = abs(gross_loss / loss_count) if loss_count else 0.0
    expectancy = (winrate * avg_win) - ((1 - winrate) * avg_loss)

    rrs = [float(t.get("rr", 0.0)) for t in trades if float(t.get("rr", 0.0)) > 0]
    average_rr = sum(rrs) / len(rrs) if rrs else 0.0

    equity_curve = []
    eq = 0.0
    for p in profits:
        eq += p
        equity_curve.append(eq)

    peak = float("-inf")
    drawdowns = []
    for eq in equity_curve:
        peak = max(peak, eq)
        drawdowns.append(peak - eq)
    max_drawdown = max(drawdowns) if drawdowns else 0.0

    results = [str(t.get("result", "LOSS")) for t in trades]
    longest_win_streak, longest_loss_streak = _streaks(results)

    return {
        "total_trades": total_trades,
        "wins": win_count,
        "losses": loss_count,
        "winrate": winrate,
        "net_profit": net_profit,
        "gross_profit": gross_profit,
        "gross_loss": gross_loss,
        "profit_factor": profit_factor,
        "expectancy": expectancy,
        "average_rr": average_rr,
        "max_drawdown": max_drawdown,
        "longest_win_streak": longest_win_streak,
        "longest_loss_streak": longest_loss_streak,
        "equity_curve": equity_curve,
    }
