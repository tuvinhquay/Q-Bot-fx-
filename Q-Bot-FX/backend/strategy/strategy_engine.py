"""Q-Bot-FX Strategy Engine.

Vai trò:

    Market Data
        ↓
    Analysis / Confluence
        ↓
    Strategy Engine
        ↓
    BUY / SELL / HOLD
        ↓
    Risk Manager
        ↓
    Execution

Strategy Engine CHỈ tạo quyết định chiến lược.

Không thực hiện:
    - Gửi lệnh MT5
    - Tính lot
    - Đặt Stop Loss
    - Đặt Take Profit
    - Quản lý position
    - Quản lý tài khoản

Các nguồn tín hiệu:

    1. Momentum
    2. Volatility / Volume
    3. Market Structure
    4. Final Confluence

Direction nội bộ của Analysis:

    BUY
    SELL
    NEUTRAL

Direction của Trend Engine:

    BULLISH
    BEARISH
    SIDEWAYS

Direction cuối cùng của Strategy:

    BUY
    SELL
    HOLD
"""

from __future__ import annotations

from dataclasses import dataclass

from ..analysis.confluence_engine import (
    ConfluenceResult,
    MomentumResult,
    StructureAlignmentResult,
    VolatilityVolumeResult,
)


# ==========================================================
# STRATEGY RESULT
# ==========================================================


@dataclass
class StrategySignal:
    """Final strategy decision."""

    signal: str = "HOLD"

    direction: str = "NEUTRAL"

    score: int = 0

    confirmations: int = 0

    strength: str = "WEAK"

    valid: bool = False

    reasons: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        """Normalize strategy result safely."""

        self.score = max(0, int(self.score))

        self.confirmations = max(
            0,
            int(self.confirmations),
        )

        if self.signal not in {
            "BUY",
            "SELL",
            "HOLD",
        }:
            self.signal = "HOLD"

        if self.direction not in {
            "BUY",
            "SELL",
            "NEUTRAL",
        }:
            self.direction = "NEUTRAL"

        if self.strength not in {
            "WEAK",
            "MODERATE",
            "STRONG",
            "VERY_STRONG",
        }:
            self.strength = "WEAK"

        self.valid = bool(self.valid)


# ==========================================================
# SAFE EMPTY RESULT
# ==========================================================


def _empty_signal() -> StrategySignal:
    """Return a safe HOLD result."""

    return StrategySignal(
        signal="HOLD",
        direction="NEUTRAL",
        score=0,
        confirmations=0,
        strength="WEAK",
        valid=False,
        reasons=(),
    )


# ==========================================================
# DIRECTION NORMALIZATION
# ==========================================================


def _normalize_direction(value: object) -> str:
    """Normalize BUY/SELL and BULLISH/BEARISH directions."""

    if value is None:
        return "NEUTRAL"

    direction = str(value).upper().strip()

    if direction in {
        "BUY",
        "BULLISH",
    }:
        return "BUY"

    if direction in {
        "SELL",
        "BEARISH",
    }:
        return "SELL"

    return "NEUTRAL"


# ==========================================================
# DIRECTION AGREEMENT
# ==========================================================


def _count_direction_agreement(
    directions: list[str],
) -> tuple[int, int]:
    """Count BUY and SELL directional confirmations."""

    buy_count = sum(
        1
        for direction in directions
        if direction == "BUY"
    )

    sell_count = sum(
        1
        for direction in directions
        if direction == "SELL"
    )

    return buy_count, sell_count


# ==========================================================
# STRATEGY DECISION
# ==========================================================


def generate_strategy_signal(
    confluence: ConfluenceResult,
    momentum: MomentumResult,
    volatility: VolatilityVolumeResult,
    structure: StructureAlignmentResult,
) -> StrategySignal:
    """Generate final BUY / SELL / HOLD strategy signal.

    The Strategy Engine does not calculate indicators.

    It only combines already calculated analysis results.

    Decision hierarchy:

        1. Validate analysis objects.
        2. Require valid final confluence.
        3. Normalize directions.
        4. Check directional agreement.
        5. Reject conflicting signals.
        6. Produce BUY / SELL / HOLD.
    """

    # ------------------------------------------------------
    # INPUT VALIDATION
    # ------------------------------------------------------

    if confluence is None:
        return _empty_signal()

    if momentum is None:
        return _empty_signal()

    if volatility is None:
        return _empty_signal()

    if structure is None:
        return _empty_signal()

    reasons: list[str] = [
        "ANALYSIS_DATA_VALID",
    ]

    # ------------------------------------------------------
    # CONFLUENCE VALIDATION
    # ------------------------------------------------------

    if not confluence.valid:
        reasons.append(
            "CONFLUENCE_INVALID"
        )

        return StrategySignal(
            signal="HOLD",
            direction="NEUTRAL",
            score=confluence.score,
            confirmations=confluence.confirmations,
            strength=confluence.strength,
            valid=False,
            reasons=tuple(reasons),
        )

    reasons.append(
        "CONFLUENCE_VALID"
    )

    # ------------------------------------------------------
    # NORMALIZE DIRECTIONS
    # ------------------------------------------------------

    confluence_direction = _normalize_direction(
        confluence.direction
    )

    momentum_direction = _normalize_direction(
        momentum.direction
    )

    volatility_direction = _normalize_direction(
        volatility.direction
    )

    structure_direction = _normalize_direction(
        structure.direction
    )

    directions = [
        confluence_direction,
        momentum_direction,
        volatility_direction,
        structure_direction,
    ]

    buy_count, sell_count = _count_direction_agreement(
        directions
    )

    # ------------------------------------------------------
    # CONFLUENCE DIRECTION MUST EXIST
    # ------------------------------------------------------

    if confluence_direction == "NEUTRAL":

        reasons.append(
            "CONFLUENCE_DIRECTION_NEUTRAL"
        )

        return StrategySignal(
            signal="HOLD",
            direction="NEUTRAL",
            score=confluence.score,
            confirmations=confluence.confirmations,
            strength=confluence.strength,
            valid=False,
            reasons=tuple(reasons),
        )

    # ------------------------------------------------------
    # MOMENTUM ALIGNMENT
    # ------------------------------------------------------

    if momentum_direction == confluence_direction:

        reasons.append(
            "MOMENTUM_ALIGNED"
        )

    else:

        reasons.append(
            "MOMENTUM_CONFLICT"
        )

    # ------------------------------------------------------
    # VOLATILITY / VOLUME ALIGNMENT
    # ------------------------------------------------------

    if volatility_direction == confluence_direction:

        reasons.append(
            "VOLATILITY_ALIGNED"
        )

    else:

        reasons.append(
            "VOLATILITY_CONFLICT"
        )

    # ------------------------------------------------------
    # STRUCTURE ALIGNMENT
    # ------------------------------------------------------

    if structure_direction == confluence_direction:

        reasons.append(
            "STRUCTURE_ALIGNED"
        )

    else:

        reasons.append(
            "STRUCTURE_CONFLICT"
        )

    # ------------------------------------------------------
    # HARD CONFLICT FILTER
    # ------------------------------------------------------
    #
    # Example:
    #
    # Confluence = BUY
    # Momentum = SELL
    # Structure = SELL
    #
    # Strategy must NOT buy.
    #
    # ------------------------------------------------------

    if (
        confluence_direction == "BUY"
        and sell_count >= 2
    ):

        reasons.append(
            "DIRECTIONAL_CONFLICT"
        )

        return StrategySignal(
            signal="HOLD",
            direction="NEUTRAL",
            score=confluence.score,
            confirmations=confluence.confirmations,
            strength="WEAK",
            valid=False,
            reasons=tuple(reasons),
        )

    if (
        confluence_direction == "SELL"
        and buy_count >= 2
    ):

        reasons.append(
            "DIRECTIONAL_CONFLICT"
        )

        return StrategySignal(
            signal="HOLD",
            direction="NEUTRAL",
            score=confluence.score,
            confirmations=confluence.confirmations,
            strength="WEAK",
            valid=False,
            reasons=tuple(reasons),
        )

    # ------------------------------------------------------
    # REQUIRE MINIMUM DIRECTIONAL AGREEMENT
    # ------------------------------------------------------

    target_count = (
        buy_count
        if confluence_direction == "BUY"
        else sell_count
    )

    if target_count < 2:

        reasons.append(
            "INSUFFICIENT_DIRECTIONAL_CONFIRMATION"
        )

        return StrategySignal(
            signal="HOLD",
            direction="NEUTRAL",
            score=confluence.score,
            confirmations=confluence.confirmations,
            strength="WEAK",
            valid=False,
            reasons=tuple(reasons),
        )

    # ------------------------------------------------------
    # FINAL BUY
    # ------------------------------------------------------

    if confluence_direction == "BUY":

        reasons.append(
            "STRATEGY_BUY_CONFIRMED"
        )

        return StrategySignal(
            signal="BUY",
            direction="BUY",
            score=confluence.score,
            confirmations=confluence.confirmations,
            strength=confluence.strength,
            valid=True,
            reasons=tuple(reasons),
        )

    # ------------------------------------------------------
    # FINAL SELL
    # ------------------------------------------------------

    if confluence_direction == "SELL":

        reasons.append(
            "STRATEGY_SELL_CONFIRMED"
        )

        return StrategySignal(
            signal="SELL",
            direction="SELL",
            score=confluence.score,
            confirmations=confluence.confirmations,
            strength=confluence.strength,
            valid=True,
            reasons=tuple(reasons),
        )

    # ------------------------------------------------------
    # SAFETY FALLBACK
    # ------------------------------------------------------

    reasons.append(
        "STRATEGY_FALLBACK_HOLD"
    )

    return StrategySignal(
        signal="HOLD",
        direction="NEUTRAL",
        score=0,
        confirmations=0,
        strength="WEAK",
        valid=False,
        reasons=tuple(reasons),
    )


# ==========================================================
# SIMPLE PUBLIC API
# ==========================================================


def generate_signal(
    confluence: ConfluenceResult,
    momentum: MomentumResult,
    volatility: VolatilityVolumeResult,
    structure: StructureAlignmentResult,
) -> StrategySignal:
    """Public Strategy Engine API."""

    return generate_strategy_signal(
        confluence=confluence,
        momentum=momentum,
        volatility=volatility,
        structure=structure,
    )