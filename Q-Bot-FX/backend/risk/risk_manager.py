"""Risk management and position sizing for Q-Bot-FX."""

from __future__ import annotations

import json
import os
from datetime import date
from pathlib import Path
from typing import Any


RISK_DIR = Path(__file__).resolve().parent
DEFAULT_DAILY_GUARD_PATH = RISK_DIR / "daily_guard.json"


class RiskManager:
    """Protect the trading account with sizing and daily risk limits."""

    def __init__(self, daily_guard_path: str | Path = DEFAULT_DAILY_GUARD_PATH) -> None:
        self.risk_per_trade = self._get_float_env("RISK_PER_TRADE", 0.01)
        self.max_open_trades = self._get_int_env("MAX_OPEN_TRADES", 3)
        self.max_daily_drawdown = self._get_float_env("MAX_DAILY_DRAWDOWN", 0.05)
        self.account_balance = self._get_float_env("ACCOUNT_BALANCE", 1000.0)
        self.default_stop_loss_pips = self._get_float_env("STOP_LOSS_PIPS", 50.0)
        self.daily_guard_path = Path(daily_guard_path)

    @staticmethod
    def _get_float_env(name: str, default: float) -> float:
        value = os.getenv(name)
        if value is None:
            return default

        try:
            return float(value)
        except ValueError:
            return default

    @staticmethod
    def _get_int_env(name: str, default: int) -> int:
        value = os.getenv(name)
        if value is None:
            return default

        try:
            return int(value)
        except ValueError:
            return default

    def calculate_lot_size(
        self,
        balance: float | None,
        stop_loss_pips: float,
        pip_value: float = 10,
    ) -> float:
        """Calculate position size from balance, stop loss and configured risk."""
        safe_balance = balance if balance and balance > 0 else self.account_balance
        safe_stop_loss = stop_loss_pips if stop_loss_pips > 0 else self.default_stop_loss_pips
        safe_pip_value = pip_value if pip_value > 0 else 10

        risk_money = safe_balance * self.risk_per_trade
        lot = risk_money / (safe_stop_loss * safe_pip_value)
        return round(max(lot, 0.01), 2)

    def can_open_new_trade(self, current_open_trades: int) -> bool:
        """Return True when the account has room for another open trade."""
        return current_open_trades < self.max_open_trades

    def check_daily_drawdown(self, current_balance: float | None) -> bool:
        """Return False when the configured daily drawdown limit is reached."""
        safe_balance = current_balance if current_balance and current_balance > 0 else self.account_balance
        guard = self._load_or_reset_daily_guard(safe_balance)
        start_balance = float(guard.get("start_balance") or safe_balance)

        guard["current_balance"] = safe_balance
        self._save_daily_guard(guard)

        if start_balance <= 0:
            return True

        drawdown = (start_balance - safe_balance) / start_balance
        return drawdown < self.max_daily_drawdown

    def _load_or_reset_daily_guard(self, current_balance: float) -> dict[str, Any]:
        today = date.today().isoformat()
        guard = self._read_daily_guard()

        if guard.get("date") != today:
            guard = {
                "start_balance": current_balance,
                "current_balance": current_balance,
                "date": today,
            }
            self._save_daily_guard(guard)

        return guard

    def _read_daily_guard(self) -> dict[str, Any]:
        if not self.daily_guard_path.exists():
            return {}

        try:
            with self.daily_guard_path.open("r", encoding="utf-8") as guard_file:
                return json.load(guard_file)
        except (json.JSONDecodeError, OSError):
            return {}

    def _save_daily_guard(self, guard: dict[str, Any]) -> None:
        self.daily_guard_path.parent.mkdir(parents=True, exist_ok=True)
        with self.daily_guard_path.open("w", encoding="utf-8") as guard_file:
            json.dump(guard, guard_file, indent=2)
            guard_file.write("\n")



def check_risk(signal: str) -> bool:
    """Allow BUY/SELL and reject HOLD."""
    return signal in {"BUY", "SELL"}


def calculate_lot(balance: float | None, risk_percent: float = 1) -> float:
    """Backward-compatible lot helper for older pipeline code."""
    manager = RiskManager()
    manager.risk_per_trade = risk_percent / 100
    return manager.calculate_lot_size(balance, manager.default_stop_loss_pips)
