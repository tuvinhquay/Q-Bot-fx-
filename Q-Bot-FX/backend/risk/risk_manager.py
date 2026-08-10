
"""Quản lý rủi ro và tính khối lượng giao dịch cho Q-Bot-FX."""

from __future__ import annotations

import json
import os
from datetime import date
from pathlib import Path
from typing import Any


RISK_DIR = Path(__file__).resolve().parent
DEFAULT_DAILY_GUARD_PATH = RISK_DIR / "daily_guard.json"


class RiskManager:
    """Bộ quản lý rủi ro trung tâm của Q-Bot-FX."""

    def __init__(
        self,
        daily_guard_path: str | Path = DEFAULT_DAILY_GUARD_PATH,
    ) -> None:
        # Tỷ lệ rủi ro mặc định trên mỗi giao dịch.
        # Ví dụ 0.01 = 1%.
        self.risk_per_trade = self._get_float_env(
            "RISK_PER_TRADE",
            0.01,
        )

        # Số lượng vị thế tối đa được phép mở.
        self.max_open_trades = self._get_int_env(
            "MAX_OPEN_TRADES",
            3,
        )

        # Giới hạn drawdown trong ngày.
        self.max_daily_drawdown = self._get_float_env(
            "MAX_DAILY_DRAWDOWN",
            0.05,
        )

        # Balance dự phòng khi MT5 chưa cung cấp balance hợp lệ.
        self.account_balance = self._get_float_env(
            "ACCOUNT_BALANCE",
            1000.0,
        )

        # Giá trị mặc định chỉ dùng làm fallback.
        self.default_stop_loss_pips = self._get_float_env(
            "STOP_LOSS_PIPS",
            50.0,
        )

        self.daily_guard_path = Path(daily_guard_path)

    # ==========================================================
    # CẤU HÌNH
    # ==========================================================

    @staticmethod
    def _get_float_env(name: str, default: float) -> float:
        """Đọc một giá trị float từ biến môi trường."""
        value = os.getenv(name)

        if value is None:
            return default

        try:
            return float(value)
        except (TypeError, ValueError):
            return default

    @staticmethod
    def _get_int_env(name: str, default: int) -> int:
        """Đọc một giá trị integer từ biến môi trường."""
        value = os.getenv(name)

        if value is None:
            return default

        try:
            return int(value)
        except (TypeError, ValueError):
            return default

    # ==========================================================
    # POSITION SIZING
    # ==========================================================

    def calculate_lot_size(
        self,
        balance: float | None,
        stop_loss_pips: float,
        pip_value: float = 10.0,
    ) -> float:
        """
        Tính lot dựa trên:

        balance
        × risk_per_trade
        ÷
        (khoảng SL tính bằng pip × giá trị mỗi pip)

        Hàm này vẫn giữ tương thích với pipeline hiện tại.
        """

        safe_balance = (
            float(balance)
            if balance is not None and balance > 0
            else float(self.account_balance)
        )

        safe_stop_loss = (
            float(stop_loss_pips)
            if stop_loss_pips > 0
            else float(self.default_stop_loss_pips)
        )

        safe_pip_value = (
            float(pip_value)
            if pip_value > 0
            else 10.0
        )

        risk_money = safe_balance * self.risk_per_trade

        denominator = safe_stop_loss * safe_pip_value

        if denominator <= 0:
            return 0.01

        lot = risk_money / denominator

        # Không cho phép lot nhỏ hơn lot tối thiểu.
        lot = max(lot, 0.01)

        return round(lot, 2)

    def _get_symbol_pip_parameters(self, symbol: str) -> tuple[float, float]:
        try:
            import importlib

            mt5 = importlib.import_module("MetaTrader5")
        except Exception:
            return 0.0001, 10.0

        symbol_info = mt5.symbol_info(symbol)
        if symbol_info is None:
            return 0.0001, 10.0

        point = float(getattr(symbol_info, "point", 0.0) or 0.0)
        digits = int(getattr(symbol_info, "digits", 0) or 0)
        tick_size = float(
            getattr(symbol_info, "tick_size", point) or point or 0.0001
        )
        tick_value = float(
            getattr(symbol_info, "tick_value", 0.0)
            or getattr(symbol_info, "trade_tick_value", 0.0)
            or 0.0
        )
        if point <= 0:
            point = tick_size or 0.0001

        pip_size = point * 10 if digits >= 3 else point
        if pip_size <= 0:
            pip_size = 0.0001

        if tick_size > 0 and tick_value > 0:
            pip_value = tick_value * (pip_size / tick_size)
        else:
            pip_value = 10.0

        if pip_value <= 0:
            pip_value = 10.0

        return pip_size, pip_value

    def calculate_lot_size_from_price_distance(
        self,
        balance: float | None,
        entry_price: float,
        stop_loss_price: float,
        symbol: str | None = None,
        pip_size: float = 0.0001,
        pip_value: float = 10.0,
    ) -> float:
        """
        Tính lot trực tiếp từ khoảng cách Entry -> SL.

        Đây là hàm mới của PROMPT-35.1.

        Mục tiêu:
        Không còn phụ thuộc bắt buộc vào STOP_LOSS_PIPS cố định
        khi hệ thống đã có SL thực tế từ Strategy Engine.

        Ví dụ:

            Entry = 1.17000
            SL    = 1.16800

        Khoảng cách:

            0.00200 / 0.0001 = 20 pip
        """

        if entry_price <= 0:
            return 0.01

        if stop_loss_price <= 0:
            return self.calculate_lot_size(
                balance,
                self.default_stop_loss_pips,
                pip_value,
            )

        if symbol:
            symbol_pip_size, symbol_pip_value = self._get_symbol_pip_parameters(symbol)
            pip_size = symbol_pip_size or pip_size
            pip_value = symbol_pip_value or pip_value

        if pip_size <= 0:
            pip_size = 0.0001

        distance = abs(
            float(entry_price) - float(stop_loss_price)
        )

        stop_loss_pips = distance / pip_size

        if stop_loss_pips <= 0:
            stop_loss_pips = self.default_stop_loss_pips

        return self.calculate_lot_size(
            balance=balance,
            stop_loss_pips=stop_loss_pips,
            pip_value=pip_value,
        )

    # ==========================================================
    # OPEN POSITION GUARD
    # ==========================================================

    def can_open_new_trade(
        self,
        current_open_trades: int,
    ) -> bool:
        """Kiểm tra hệ thống còn được phép mở giao dịch mới hay không."""

        return current_open_trades < self.max_open_trades

    # ==========================================================
    # DAILY DRAWDOWN GUARD
    # ==========================================================

    def check_daily_drawdown(
        self,
        current_balance: float | None,
    ) -> bool:
        """
        Kiểm tra giới hạn drawdown trong ngày.

        Trả về:

            True  = được phép giao dịch
            False = đã chạm giới hạn rủi ro
        """

        safe_balance = (
            float(current_balance)
            if current_balance is not None and current_balance > 0
            else float(self.account_balance)
        )

        guard = self._load_or_reset_daily_guard(
            safe_balance
        )

        start_balance = float(
            guard.get("start_balance") or safe_balance
        )

        guard["current_balance"] = safe_balance

        self._save_daily_guard(guard)

        if start_balance <= 0:
            return True

        drawdown = (
            (start_balance - safe_balance)
            / start_balance
        )

        return drawdown < self.max_daily_drawdown

    def _load_or_reset_daily_guard(
        self,
        current_balance: float,
    ) -> dict[str, Any]:
        """Đọc daily guard hoặc tạo lại khi sang ngày mới."""

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
        """Đọc trạng thái daily guard."""

        if not self.daily_guard_path.exists():
            return {}

        try:
            with self.daily_guard_path.open(
                "r",
                encoding="utf-8",
            ) as guard_file:
                data = json.load(guard_file)

            if not isinstance(data, dict):
                return {}

            return data

        except (json.JSONDecodeError, OSError):
            return {}

    def _save_daily_guard(
        self,
        guard: dict[str, Any],
    ) -> None:
        """Lưu trạng thái daily guard."""

        self.daily_guard_path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        with self.daily_guard_path.open(
            "w",
            encoding="utf-8",
        ) as guard_file:
            json.dump(
                guard,
                guard_file,
                indent=2,
            )
            guard_file.write("\n")


# ==============================================================
# COMPATIBILITY HELPERS
# ==============================================================

def check_risk(signal: str) -> bool:
    """
    Kiểm tra tín hiệu có được phép chuyển sang execution hay không.

    BUY / SELL = cho phép.
    HOLD       = từ chối.
    """

    return signal in {"BUY", "SELL"}


def calculate_lot(
    balance: float | None,
    risk_percent: float = 1.0,
) -> float:
    """
    Hàm tương thích ngược với pipeline cũ.

    Không xóa hàm này trong PROMPT-35.1 vì có thể còn module
    khác đang sử dụng nó.
    """

    manager = RiskManager()

    manager.risk_per_trade = (
        float(risk_percent) / 100.0
    )

    return manager.calculate_lot_size(
        balance=balance,
        stop_loss_pips=manager.default_stop_loss_pips,
    )
