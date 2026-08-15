"""Risk management engine for Q-Bot-FX.

Responsible for:
- validating strategy signals
- calculating safe position size
- validating stop loss / take profit
- enforcing maximum risk
- blocking unsafe trades

This module does NOT execute trades.
"""

from __future__ import annotations

from dataclasses import dataclass


# ==========================================================
# RISK RESULT
# ==========================================================

@dataclass
class RiskResult:
    """Result returned by the risk management engine."""

    approved: bool = False
    direction: str = "NEUTRAL"

    lot_size: float = 0.0

    risk_amount: float = 0.0
    stop_loss_distance: float = 0.0
    take_profit_distance: float = 0.0

    reason: str = "RISK_REJECTED"

    def __post_init__(self) -> None:
        self.lot_size = max(0.0, float(self.lot_size))
        self.risk_amount = max(0.0, float(self.risk_amount))
        self.stop_loss_distance = max(
            0.0,
            float(self.stop_loss_distance),
        )
        self.take_profit_distance = max(
            0.0,
            float(self.take_profit_distance),
        )

        if self.direction not in {
            "BUY",
            "SELL",
            "NEUTRAL",
        }:
            self.direction = "NEUTRAL"


# ==========================================================
# RISK CONFIGURATION
# ==========================================================

@dataclass
class RiskConfig:
    """Safe default risk configuration."""

    risk_percent: float = 1.0

    max_risk_percent: float = 2.0

    min_lot: float = 0.01

    max_lot: float = 1.0

    default_lot: float = 0.01

    reward_risk_ratio: float = 2.0

    def __post_init__(self) -> None:
        self.risk_percent = max(
            0.0,
            float(self.risk_percent),
        )

        self.max_risk_percent = max(
            0.0,
            float(self.max_risk_percent),
        )

        self.min_lot = max(
            0.0,
            float(self.min_lot),
        )

        self.max_lot = max(
            self.min_lot,
            float(self.max_lot),
        )

        self.default_lot = min(
            max(
                self.min_lot,
                float(self.default_lot),
            ),
            self.max_lot,
        )

        self.reward_risk_ratio = max(
            0.0,
            float(self.reward_risk_ratio),
        )


# ==========================================================
# SAFE VALUE VALIDATION
# ==========================================================

def _valid_positive(value: float) -> bool:
    """Return True when value is positive."""

    try:
        return float(value) > 0
    except (TypeError, ValueError):
        return False


# ==========================================================
# LOT SIZE CALCULATION
# ==========================================================

def calculate_lot_size(
    balance: float,
    stop_loss_distance: float,
    config: RiskConfig | None = None,
) -> float:
    """Calculate a conservative lot size.

    This is intentionally a simplified sizing model.

    Broker-specific contract specifications are handled later
    by the execution layer.
    """

    if config is None:
        config = RiskConfig()

    if not _valid_positive(balance):
        return 0.0

    if not _valid_positive(stop_loss_distance):
        return 0.0

    risk_amount = (
        float(balance)
        * config.risk_percent
        / 100.0
    )

    if risk_amount <= 0:
        return 0.0

    # Conservative normalized sizing.
    raw_lot = (
        risk_amount
        / max(stop_loss_distance * 100000.0, 1.0)
    )

    lot = min(
        max(raw_lot, config.min_lot),
        config.max_lot,
    )

    return round(lot, 2)


# ==========================================================
# RISK VALIDATION
# ==========================================================

def validate_risk(
    signal: object,
    balance: float,
    stop_loss_distance: float,
    config: RiskConfig | None = None,
) -> RiskResult:
    """Validate a strategy signal before execution."""

    if config is None:
        config = RiskConfig()

    if signal is None:
        return RiskResult(
            reason="SIGNAL_MISSING",
        )

    if not _valid_positive(balance):
        return RiskResult(
            reason="INVALID_BALANCE",
        )

    if not _valid_positive(stop_loss_distance):
        return RiskResult(
            reason="INVALID_STOP_LOSS",
        )

    direction = getattr(
        signal,
        "direction",
        "NEUTRAL",
    )

    signal_name = getattr(
        signal,
        "signal",
        "HOLD",
    )

    valid = bool(
        getattr(
            signal,
            "valid",
            False,
        )
    )

    if signal_name not in {
        "BUY",
        "SELL",
    }:
        return RiskResult(
            reason="SIGNAL_NOT_TRADEABLE",
        )

    if direction not in {
        "BUY",
        "SELL",
    }:
        return RiskResult(
            reason="DIRECTION_INVALID",
        )

    if not valid:
        return RiskResult(
            direction=direction,
            reason="STRATEGY_SIGNAL_INVALID",
        )

    if (
        config.risk_percent
        > config.max_risk_percent
    ):
        return RiskResult(
            direction=direction,
            reason="RISK_PERCENT_TOO_HIGH",
        )

    lot_size = calculate_lot_size(
        balance=balance,
        stop_loss_distance=stop_loss_distance,
        config=config,
    )

    if lot_size <= 0:
        return RiskResult(
            direction=direction,
            reason="LOT_SIZE_INVALID",
        )

    risk_amount = (
        float(balance)
        * config.risk_percent
        / 100.0
    )

    take_profit_distance = (
        stop_loss_distance
        * config.reward_risk_ratio
    )

    return RiskResult(
        approved=True,
        direction=direction,
        lot_size=lot_size,
        risk_amount=risk_amount,
        stop_loss_distance=stop_loss_distance,
        take_profit_distance=take_profit_distance,
        reason="RISK_APPROVED",
    )