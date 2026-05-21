import json
import os
from datetime import datetime
from pathlib import Path
from typing import Any

TRADE_FILE = Path(__file__).resolve().parents[2] / "trade_history.json"
STATE_FILE = Path(__file__).resolve().parents[2] / "performance_report_state.json"


def load_trades():
    if not os.path.exists(TRADE_FILE):
        return []
    with open(TRADE_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def calculate_performance():
    trades = load_trades()

    if len(trades) == 0:
        return None

    profits = [float(t["profit"]) for t in trades]
    wins = [p for p in profits if p > 0]
    losses = [p for p in profits if p <= 0]

    total_trades = len(profits)
    winrate = (len(wins) / total_trades) if total_trades else 0.0

    avg_win = (sum(wins) / len(wins)) if wins else 0.0
    avg_loss = abs(sum(losses) / len(losses)) if losses else 0.0

    loss_sum = abs(sum(losses))
    profit_factor = (sum(wins) / loss_sum) if loss_sum > 0 else 0.0
    expectancy = (winrate * avg_win) - ((1 - winrate) * avg_loss)

    rr_values = []
    for t in trades:
        entry = float(t.get("entry", 0) or 0)
        sl = float(t.get("sl", 0) or 0)
        tp = float(t.get("tp", 0) or 0)
        risk = abs(entry - sl)
        reward = abs(tp - entry)
        if risk > 0:
            rr_values.append(reward / risk)
    avg_rr = (sum(rr_values) / len(rr_values)) if rr_values else 0.0

    equity_curve = []
    running = 0.0
    for p in profits:
        running += p
        equity_curve.append(running)

    peak = []
    max_seen = float("-inf")
    for e in equity_curve:
        if e > max_seen:
            max_seen = e
        peak.append(max_seen)

    drawdown = [pk - eq for pk, eq in zip(peak, equity_curve)]
    max_dd = max(drawdown) if drawdown else 0.0

    return {
        "total_trades": total_trades,
        "winrate": winrate,
        "profit_factor": profit_factor,
        "expectancy": expectancy,
        "average_rr": avg_rr,
        "max_drawdown": max_dd,
        "equity_curve": equity_curve,
        "net_profit": sum(profits),
    }


def format_performance_report(stats: dict[str, Any] | None) -> str:
    if not stats:
        return "No trade performance data yet."
    return (
        "Q-Bot FX Performance Report\n\n"
        f"Total Trades: {stats['total_trades']}\n"
        f"Winrate: {stats['winrate'] * 100:.2f}%\n"
        f"Profit Factor: {stats['profit_factor']:.2f}\n"
        f"Expectancy: {stats['expectancy']:.2f}\n"
        f"Average RR: {stats['average_rr']:.2f}\n"
        f"Max Drawdown: {stats['max_drawdown']:.2f}\n"
        f"Net Profit: {stats['net_profit']:.2f}"
    )


def should_send_daily_report() -> bool:
    today = datetime.utcnow().date().isoformat()
    if not os.path.exists(STATE_FILE):
        return True
    with open(STATE_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data.get("last_sent_date") != today


def mark_daily_report_sent() -> None:
    today = datetime.utcnow().date().isoformat()
    with open(STATE_FILE, "w", encoding="utf-8") as f:
        json.dump({"last_sent_date": today}, f)
