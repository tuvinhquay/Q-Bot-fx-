import json
import os
from datetime import datetime
from pathlib import Path
from typing import Any

TRADE_FILE = Path(__file__).resolve().parents[2] / "trade_history.json"


def _load_trades() -> list[dict[str, Any]]:
    if not os.path.exists(TRADE_FILE):
        return []
    with open(TRADE_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def _save_trades(trades: list[dict[str, Any]]) -> None:
    with open(TRADE_FILE, "w", encoding="utf-8") as f:
        json.dump(trades, f, indent=2)


def log_trade(symbol, signal, lot, entry, sl, tp, profit):
    trades = _load_trades()

    result = "WIN" if profit > 0 else "LOSS"

    trade = {
        "timestamp": datetime.utcnow().isoformat(),
        "symbol": symbol,
        "signal": signal,
        "lot": lot,
        "entry": entry,
        "sl": sl,
        "tp": tp,
        "profit": profit,
        "result": result,
    }

    trades.append(trade)
    _save_trades(trades)

    print(f"[TRADE LOGGER] Trade saved: {result} {profit}$")
