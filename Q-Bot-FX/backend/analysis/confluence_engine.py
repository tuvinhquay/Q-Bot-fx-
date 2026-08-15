"""Confluence engine for Q-Bot-FX scalping entry validation.

PART 1 — Foundation
PART 2 — Momentum

Architecture:

Market Data
    ↓
Indicator Layer
    ↓
Momentum Layer
    ↓
Confluence Engine
    ↓
Strategy Engine
"""

from __future__ import annotations

from dataclasses import dataclass

import pandas as pd

from .structure_detector import MarketStructure


# ==========================================================
# PART 1 — CONFLUENCE RESULT
# ==========================================================

@dataclass
class ConfluenceResult:
    """Result returned by the confluence validation engine."""

    score: int
    valid: bool

    direction: str = "NEUTRAL"
    confirmations: int = 0
    strength: str = "WEAK"
    reasons: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        self.score = max(0, int(self.score))
        self.confirmations = max(0, int(self.confirmations))

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


# ==========================================================
# PART 1 — SAFE DATA VALIDATION
# ==========================================================

_REQUIRED_COLUMNS = {
    "open",
    "high",
    "low",
    "close",
}


def _has_required_columns(df: pd.DataFrame) -> bool:
    """Check whether market data contains required OHLC columns."""

    if df is None or df.empty:
        return False

    return _REQUIRED_COLUMNS.issubset(df.columns)


def _is_valid_price(value: object) -> bool:
    """Return True when value represents a positive price."""

    try:
        price = float(value)
    except (TypeError, ValueError):
        return False

    return price > 0


# ==========================================================
# PART 1 — EMA PRIMITIVE
# ==========================================================

def _ema(
    series: pd.Series,
    period: int = 200,
) -> pd.Series:
    """Calculate exponential moving average safely."""

    if period <= 0:
        raise ValueError("EMA period must be greater than zero.")

    return series.astype(float).ewm(
        span=period,
        adjust=False,
    ).mean()


# ==========================================================
# PART 1 — RSI PRIMITIVE
# ==========================================================

def _rsi(
    series: pd.Series,
    period: int = 14,
) -> pd.Series:
    """Calculate RSI using a stable rolling-average implementation."""

    if period <= 0:
        raise ValueError("RSI period must be greater than zero.")

    close = series.astype(float)

    delta = close.diff()

    gains = delta.clip(lower=0)
    losses = -delta.clip(upper=0)

    average_gain = gains.rolling(
        period,
        min_periods=period,
    ).mean()

    average_loss = losses.rolling(
        period,
        min_periods=period,
    ).mean()

    rs = average_gain / average_loss.replace(
        0,
        1e-9,
    )

    return 100 - (
        100 / (1 + rs)
    )


# ==========================================================
# PART 2 — MOMENTUM RESULT
# ==========================================================

@dataclass
class MomentumResult:
    """Result returned by the momentum analysis layer."""

    direction: str = "NEUTRAL"
    score: int = 0
    confirmations: int = 0

    rsi: float = 50.0

    ema_fast: float = 0.0
    ema_slow: float = 0.0

    reasons: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        self.score = max(0, int(self.score))
        self.confirmations = max(0, int(self.confirmations))

        if self.direction not in {
            "BUY",
            "SELL",
            "NEUTRAL",
        }:
            self.direction = "NEUTRAL"


# ==========================================================
# PART 2 — MOMENTUM ANALYZER
# ==========================================================

def _analyze_momentum(
    df: pd.DataFrame,
) -> MomentumResult:
    """Analyze short-term momentum.

    Components:

    1. EMA 9 / EMA 21 relationship
    2. EMA slope
    3. Price position
    4. RSI momentum

    This layer does not execute trades.
    """

    if df is None or df.empty:
        return MomentumResult()

    if not _has_required_columns(df):
        return MomentumResult()

    if len(df) < 30:
        return MomentumResult()

    close = df["close"].astype(float)

    ema_fast_series = _ema(close, 9)
    ema_slow_series = _ema(close, 21)

    rsi_series = _rsi(close, 14)

    latest_close = float(close.iloc[-1])

    fast = float(ema_fast_series.iloc[-1])
    slow = float(ema_slow_series.iloc[-1])

    previous_fast = float(ema_fast_series.iloc[-2])

    rsi_value = float(rsi_series.iloc[-1])

    if not _is_valid_price(latest_close):
        return MomentumResult()

    if pd.isna(rsi_value):
        return MomentumResult()

    score_buy = 0
    score_sell = 0

    confirmations_buy = 0
    confirmations_sell = 0

    reasons: list[str] = []

    # ------------------------------------------------------
    # EMA ALIGNMENT
    # ------------------------------------------------------

    if fast > slow:
        score_buy += 1
        confirmations_buy += 1
        reasons.append("EMA_BULLISH")

    elif fast < slow:
        score_sell += 1
        confirmations_sell += 1
        reasons.append("EMA_BEARISH")

    # ------------------------------------------------------
    # EMA SLOPE
    # ------------------------------------------------------

    if fast > previous_fast:
        score_buy += 1
        confirmations_buy += 1
        reasons.append("EMA_FAST_SLOPE_UP")

    elif fast < previous_fast:
        score_sell += 1
        confirmations_sell += 1
        reasons.append("EMA_FAST_SLOPE_DOWN")

    # ------------------------------------------------------
    # PRICE POSITION
    # ------------------------------------------------------

    if latest_close > fast and latest_close > slow:
        score_buy += 1
        confirmations_buy += 1
        reasons.append("PRICE_ABOVE_EMAS")

    elif latest_close < fast and latest_close < slow:
        score_sell += 1
        confirmations_sell += 1
        reasons.append("PRICE_BELOW_EMAS")

    # ------------------------------------------------------
    # RSI MOMENTUM
    # ------------------------------------------------------

    if 52 <= rsi_value < 70:
        score_buy += 1
        confirmations_buy += 1
        reasons.append("RSI_BULLISH")

    elif 30 < rsi_value <= 48:
        score_sell += 1
        confirmations_sell += 1
        reasons.append("RSI_BEARISH")

    # ------------------------------------------------------
    # FINAL MOMENTUM DIRECTION
    # ------------------------------------------------------

    if score_buy > score_sell and score_buy >= 2:
        direction = "BUY"
        score = score_buy
        confirmations = confirmations_buy

    elif score_sell > score_buy and score_sell >= 2:
        direction = "SELL"
        score = score_sell
        confirmations = confirmations_sell

    else:
        direction = "NEUTRAL"
        score = 0
        confirmations = 0

    return MomentumResult(
        direction=direction,
        score=score,
        confirmations=confirmations,
        rsi=rsi_value,
        ema_fast=fast,
        ema_slow=slow,
        reasons=tuple(reasons),
    )

# ==========================================================
# PART 3 — VOLATILITY / VOLUME
# ==========================================================

@dataclass
class VolatilityVolumeResult:
    """Volatility and volume analysis result."""

    direction: str = "NEUTRAL"
    score: int = 0
    confirmations: int = 0

    atr: float = 0.0
    atr_percent: float = 0.0

    volume_ratio: float = 0.0
    volume_confirmed: bool = False

    reasons: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        self.score = max(0, int(self.score))
        self.confirmations = max(0, int(self.confirmations))

        if self.direction not in {
            "BUY",
            "SELL",
            "NEUTRAL",
        }:
            self.direction = "NEUTRAL"


# ==========================================================
# PART 3 — ATR CALCULATION
# ==========================================================

def _atr(
    df: pd.DataFrame,
    period: int = 14,
) -> pd.Series:
    """Calculate Average True Range safely."""

    if period <= 0:
        raise ValueError(
            "ATR period must be greater than zero."
        )

    high = df["high"].astype(float)
    low = df["low"].astype(float)
    close = df["close"].astype(float)

    previous_close = close.shift(1)

    true_range = pd.concat(
        [
            high - low,
            (high - previous_close).abs(),
            (low - previous_close).abs(),
        ],
        axis=1,
    ).max(axis=1)

    return true_range.rolling(
        period,
        min_periods=period,
    ).mean()


# ==========================================================
# PART 3 — VOLATILITY / VOLUME ANALYZER
# ==========================================================

def _analyze_volatility_volume(
    df: pd.DataFrame,
) -> VolatilityVolumeResult:
    """
    Analyze volatility and volume conditions.

    Components:

        1. ATR volatility
        2. ATR relative to price
        3. Tick-volume expansion
        4. Current price direction

    This layer does NOT execute trades.
    """

    if df is None or df.empty:
        return VolatilityVolumeResult()

    if not _has_required_columns(df):
        return VolatilityVolumeResult()

    if len(df) < 30:
        return VolatilityVolumeResult()

    close = df["close"].astype(float)

    latest_close = float(close.iloc[-1])

    if not _is_valid_price(latest_close):
        return VolatilityVolumeResult()

    # ------------------------------------------------------
    # ATR
    # ------------------------------------------------------

    atr_series = _atr(df, 14)

    if atr_series.empty:
        return VolatilityVolumeResult()

    latest_atr = float(atr_series.iloc[-1])

    if pd.isna(latest_atr) or latest_atr <= 0:
        return VolatilityVolumeResult()

    atr_percent = (
        latest_atr
        / max(abs(latest_close), 1e-9)
    ) * 100.0

    score_buy = 0
    score_sell = 0

    confirmations_buy = 0
    confirmations_sell = 0

    reasons: list[str] = []

    # ------------------------------------------------------
    # ATR VOLATILITY STATE
    # ------------------------------------------------------

    if atr_percent > 0.02:

        reasons.append("ATR_ACTIVE")

    elif atr_percent > 0:

        reasons.append("ATR_LOW")

    # ------------------------------------------------------
    # TICK VOLUME
    # ------------------------------------------------------

    volume_ratio = 0.0
    volume_confirmed = False

    if "tick_volume" in df.columns:

        volume = df["tick_volume"].astype(float)

        if len(volume) >= 21:

            average_volume = float(
                volume.iloc[-21:-1].mean()
            )

            latest_volume = float(
                volume.iloc[-1]
            )

            if average_volume > 0:

                volume_ratio = (
                    latest_volume
                    / average_volume
                )

                # ------------------------------------------
                # VOLUME EXPANSION
                # ------------------------------------------

                if volume_ratio >= 1.20:

                    volume_confirmed = True

                    reasons.append(
                        "VOLUME_EXPANSION"
                    )

                    previous_close = float(
                        close.iloc[-2]
                    )

                    if latest_close > previous_close:

                        score_buy += 1
                        confirmations_buy += 1

                        reasons.append(
                            "VOLUME_BUY_CONFIRMATION"
                        )

                    elif latest_close < previous_close:

                        score_sell += 1
                        confirmations_sell += 1

                        reasons.append(
                            "VOLUME_SELL_CONFIRMATION"
                        )

                # ------------------------------------------
                # NORMAL VOLUME
                # ------------------------------------------

                elif volume_ratio >= 0.80:

                    reasons.append(
                        "VOLUME_NORMAL"
                    )

                # ------------------------------------------
                # LOW VOLUME
                # ------------------------------------------

                else:

                    reasons.append(
                        "VOLUME_LOW"
                    )

    # ------------------------------------------------------
    # PRICE DIRECTION
    # ------------------------------------------------------

    if len(close) >= 3:

        previous_close = float(
            close.iloc[-2]
        )

        previous_previous_close = float(
            close.iloc[-3]
        )

        current_move = (
            latest_close
            - previous_close
        )

        previous_move = (
            previous_close
            - previous_previous_close
        )

        # ----------------------------------------------
        # BULLISH CONTINUATION
        # ----------------------------------------------

        if (
            current_move > 0
            and previous_move >= 0
        ):

            score_buy += 1
            confirmations_buy += 1

            reasons.append(
                "VOLATILITY_BULLISH"
            )

        # ----------------------------------------------
        # BEARISH CONTINUATION
        # ----------------------------------------------

        elif (
            current_move < 0
            and previous_move <= 0
        ):

            score_sell += 1
            confirmations_sell += 1

            reasons.append(
                "VOLATILITY_BEARISH"
            )

    # ------------------------------------------------------
    # FINAL PART 3 DIRECTION
    # ------------------------------------------------------

    if (
        score_buy > score_sell
        and score_buy >= 1
    ):

        direction = "BUY"
        score = score_buy
        confirmations = confirmations_buy

    elif (
        score_sell > score_buy
        and score_sell >= 1
    ):

        direction = "SELL"
        score = score_sell
        confirmations = confirmations_sell

    else:

        direction = "NEUTRAL"
        score = 0
        confirmations = 0

    # ------------------------------------------------------
    # RETURN PART 3 RESULT
    # ------------------------------------------------------

    return VolatilityVolumeResult(
        direction=direction,
        score=score,
        confirmations=confirmations,
        atr=latest_atr,
        atr_percent=atr_percent,
        volume_ratio=volume_ratio,
        volume_confirmed=volume_confirmed,
        reasons=tuple(reasons),
    )

# ==========================================================
# PART 4 — STRUCTURE ALIGNMENT
# ==========================================================

@dataclass
class StructureAlignmentResult:
    """Market structure alignment result."""

    direction: str = "NEUTRAL"
    score: int = 0
    confirmations: int = 0

    bos: bool = False
    liquidity_sweep: bool = False
    order_block: bool = False
    fvg: bool = False

    reasons: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        self.score = max(0, int(self.score))
        self.confirmations = max(0, int(self.confirmations))

        if self.direction not in {
            "BUY",
            "SELL",
            "NEUTRAL",
        }:
            self.direction = "NEUTRAL"


# ==========================================================
# PART 4 — STRUCTURE ANALYZER
# ==========================================================

def _analyze_structure_alignment(
    structure: MarketStructure,
) -> StructureAlignmentResult:
    """
    Analyze market structure confirmation.

    Components:

        1. Break of Structure (BOS)
        2. Liquidity Sweep
        3. Order Block
        4. Fair Value Gap

    This layer does NOT execute trades.

    It converts the structure detector output
    into directional confirmation data.
    """

    if structure is None:
        return StructureAlignmentResult()

    bos = bool(structure.bos)
    liquidity_sweep = bool(
        structure.liquidity_sweep
    )
    order_block = bool(
        structure.order_block
    )
    fvg = bool(structure.fvg)

    # ------------------------------------------------------
    # STRUCTURE DIRECTION
    # ------------------------------------------------------

    structure_direction = getattr(
        structure,
        "direction",
        "NEUTRAL",
    )

    if structure_direction not in {
        "BUY",
        "SELL",
        "NEUTRAL",
    }:
        structure_direction = "NEUTRAL"

    score = 0
    confirmations = 0

    reasons: list[str] = []

    # ------------------------------------------------------
    # BOS
    # ------------------------------------------------------

    if bos:
        score += 1
        confirmations += 1
        reasons.append(
            "BOS_CONFIRMED"
        )

    # ------------------------------------------------------
    # LIQUIDITY SWEEP
    # ------------------------------------------------------

    if liquidity_sweep:
        score += 1
        confirmations += 1
        reasons.append(
            "LIQUIDITY_SWEEP_CONFIRMED"
        )

    # ------------------------------------------------------
    # ORDER BLOCK
    # ------------------------------------------------------

    if order_block:
        score += 1
        confirmations += 1
        reasons.append(
            "ORDER_BLOCK_CONFIRMED"
        )

    # ------------------------------------------------------
    # FAIR VALUE GAP
    # ------------------------------------------------------

    if fvg:
        score += 1
        confirmations += 1
        reasons.append(
            "FVG_CONFIRMED"
        )

    # ------------------------------------------------------
    # STRUCTURE DIRECTION REASON
    # ------------------------------------------------------

    if structure_direction == "BUY":

        reasons.append(
            "STRUCTURE_BULLISH"
        )

    elif structure_direction == "SELL":

        reasons.append(
            "STRUCTURE_BEARISH"
        )

    else:

        reasons.append(
            "STRUCTURE_NEUTRAL"
        )

    # ------------------------------------------------------
    # FINAL STRUCTURE DIRECTION
    # ------------------------------------------------------
    #
    # Direction comes from MarketStructure.
    #
    # PART 4 does not independently invent BUY/SELL.
    # PART 5 will compare this direction against:
    #
    #   Momentum
    #   Volatility / Volume
    #   Structure
    #
    # before producing the final entry decision.
    # ------------------------------------------------------

    direction = structure_direction

    return StructureAlignmentResult(
        direction=direction,
        score=score,
        confirmations=confirmations,
        bos=bos,
        liquidity_sweep=liquidity_sweep,
        order_block=order_block,
        fvg=fvg,
        reasons=tuple(reasons),
    )    

# ==========================================================
# PART 5 — FINAL ENTRY QUALITY
# ==========================================================

def _calculate_final_confluence(
    momentum: MomentumResult,
    volatility: VolatilityVolumeResult,
    structure: StructureAlignmentResult,
) -> ConfluenceResult:
    """
    Combine Momentum, Volatility/Volume and Structure.

    This function does NOT execute trades.

    It only produces the final confluence assessment.

    Scoring model:

        Momentum          → maximum 4 points
        Volatility/Volume → maximum 2 points
        Structure         → maximum 4 points

    Maximum theoretical score = 10.
    """

    if momentum is None:
        return _empty_result()

    if volatility is None:
        return _empty_result()

    if structure is None:
        return _empty_result()

    reasons: list[str] = [
        "BASE_DATA_VALID"
    ]

    # ------------------------------------------------------
    # DIRECTION VOTES
    # ------------------------------------------------------

    buy_votes = 0
    sell_votes = 0

    # ------------------------------------------------------
    # MOMENTUM
    # ------------------------------------------------------

    momentum_score = min(
        max(int(momentum.score), 0),
        4,
    )

    if momentum.direction == "BUY":

        buy_votes += 1

        reasons.extend(
            momentum.reasons
        )

        reasons.append(
            "MOMENTUM_BUY_CONFIRMED"
        )

    elif momentum.direction == "SELL":

        sell_votes += 1

        reasons.extend(
            momentum.reasons
        )

        reasons.append(
            "MOMENTUM_SELL_CONFIRMED"
        )

    # ------------------------------------------------------
    # VOLATILITY / VOLUME
    # ------------------------------------------------------

    volatility_score = min(
        max(int(volatility.score), 0),
        2,
    )

    if volatility.direction == "BUY":

        buy_votes += 1

        reasons.extend(
            volatility.reasons
        )

        reasons.append(
            "VOLATILITY_BUY_CONFIRMED"
        )

    elif volatility.direction == "SELL":

        sell_votes += 1

        reasons.extend(
            volatility.reasons
        )

        reasons.append(
            "VOLATILITY_SELL_CONFIRMED"
        )

    # ------------------------------------------------------
    # STRUCTURE
    # ------------------------------------------------------

    structure_score = min(
        max(int(structure.score), 0),
        4,
    )

    if structure.direction == "BUY":

        buy_votes += 1

        reasons.extend(
            structure.reasons
        )

        reasons.append(
            "STRUCTURE_BUY_CONFIRMED"
        )

    elif structure.direction == "SELL":

        sell_votes += 1

        reasons.extend(
            structure.reasons
        )

        reasons.append(
            "STRUCTURE_SELL_CONFIRMED"
        )

    # ------------------------------------------------------
    # FINAL DIRECTION
    # ------------------------------------------------------

    if buy_votes >= 2 and buy_votes > sell_votes:

        direction = "BUY"

    elif sell_votes >= 2 and sell_votes > buy_votes:

        direction = "SELL"

    else:

        direction = "NEUTRAL"

    # ------------------------------------------------------
    # FINAL SCORE
    # ------------------------------------------------------

    if direction == "BUY":

        score = (
            momentum_score
            + volatility_score
            + structure_score
        )

    elif direction == "SELL":

        score = (
            momentum_score
            + volatility_score
            + structure_score
        )

    else:

        score = 0

    # ------------------------------------------------------
    # CONFIRMATIONS
    # ------------------------------------------------------

    confirmations = 0

    if momentum.direction == direction:
        confirmations += momentum.confirmations

    if volatility.direction == direction:
        confirmations += volatility.confirmations

    if structure.direction == direction:
        confirmations += structure.confirmations

    # ------------------------------------------------------
    # STRENGTH
    # ------------------------------------------------------

    if score >= 8:

        strength = "VERY_STRONG"

    elif score >= 6:

        strength = "STRONG"

    elif score >= 4:

        strength = "MODERATE"

    else:

        strength = "WEAK"

    # ------------------------------------------------------
    # VALID ENTRY
    # ------------------------------------------------------
    #
    # A signal becomes valid only when:
    #
    #   1. Direction is confirmed
    #   2. At least two independent layers agree
    #   3. Final score reaches minimum threshold
    #
    # This prevents a single indicator from
    # creating an entry signal.
    # ------------------------------------------------------

    valid = (
        direction in {
            "BUY",
            "SELL",
        }
        and (
            buy_votes >= 2
            or sell_votes >= 2
        )
        and score >= 4
    )

    # ------------------------------------------------------
    # FINAL REASON
    # ------------------------------------------------------

    if direction == "BUY":

        reasons.append(
            "FINAL_DIRECTION_BUY"
        )

    elif direction == "SELL":

        reasons.append(
            "FINAL_DIRECTION_SELL"
        )

    else:

        reasons.append(
            "FINAL_DIRECTION_NEUTRAL"
        )

    if valid:

        reasons.append(
            "ENTRY_CONFLUENCE_VALID"
        )

    else:

        reasons.append(
            "ENTRY_CONFLUENCE_INVALID"
        )

    return ConfluenceResult(
        score=score,
        valid=valid,
        direction=direction,
        confirmations=confirmations,
        strength=strength,
        reasons=tuple(reasons),
    )

    
# ==========================================================
# PART 1 — EMPTY RESULT
# ==========================================================

def _empty_result() -> ConfluenceResult:
    """Return a safe neutral confluence result."""

    return ConfluenceResult(
        score=0,
        valid=False,
        direction="NEUTRAL",
        confirmations=0,
        strength="WEAK",
        reasons=(),
    )


# ==========================================================
# PART 2 — PUBLIC ENTRY POINT
# ==========================================================

def check(
    df_h1: pd.DataFrame,
    structure: MarketStructure,
) -> ConfluenceResult:
    """Run confluence analysis.

    PART 1:
        Safe market-data validation.

    PART 2:
        Momentum analysis.

    Later parts:
        PART 3 → Volatility / Volume
        PART 4 → Structure Alignment
        PART 5 → Final Entry Quality
    """

    if not _has_required_columns(df_h1):
        return _empty_result()

    if len(df_h1) < 30:
        return _empty_result()

    if structure is None:
        return _empty_result()

    latest_close = df_h1["close"].iloc[-1]

    if not _is_valid_price(latest_close):
        return _empty_result()

    momentum = _analyze_momentum(df_h1)

    reasons = (
        "BASE_DATA_VALID",
        *momentum.reasons,
    )

    strength = "WEAK"

    if momentum.score >= 4:
        strength = "STRONG"

    elif momentum.score >= 3:
        strength = "MODERATE"

    return ConfluenceResult(
        score=momentum.score,
        valid=False,
        direction=momentum.direction,
        confirmations=momentum.confirmations,
        strength=strength,
        reasons=reasons,
    )

