"""Market structure engine for Q-Bot-FX scalping.

PART 1  - Data validation & structure model
PART 2  - Swing high / swing low detection
PART 3  - Break of Structure (BOS)
PART 4  - Liquidity sweep detection
PART 5  - Order Block detection
PART 6  - Fair Value Gap (FVG) detection
PART 7  - Structure analysis & scoring

Designed for M5 / M15 / H1 scalping.
The module only analyzes market structure.
It does not execute trades.
"""

from __future__ import annotations

from dataclasses import dataclass

import pandas as pd


# ==========================================================
# PART 1 — DATA VALIDATION & STRUCTURE MODEL
# ==========================================================

REQUIRED_COLUMNS = {
    "open",
    "high",
    "low",
    "close",
}


@dataclass
class MarketStructure:
    """Complete market-structure analysis result."""

    bos: bool
    liquidity_sweep: bool
    order_block: bool
    fvg: bool

    # Direction of the detected structure.
    direction: str = "NEUTRAL"

    # Structure confidence score.
    score: int = 0

    # Number of valid structure conditions.
    confirmations: int = 0


def _valid_dataframe(df: pd.DataFrame | None, minimum_rows: int = 10) -> bool:
    """Validate candle dataframe before structure analysis."""

    if df is None:
        return False

    if df.empty:
        return False

    if len(df) < minimum_rows:
        return False

    if not REQUIRED_COLUMNS.issubset(df.columns):
        return False

    return True


# ==========================================================
# PART 2 — SWING HIGH / SWING LOW
# ==========================================================

def find_recent_swing_high_low(
    df: pd.DataFrame,
    lookback: int = 20,
) -> tuple[float | None, float | None]:
    """Return recent structural high and low."""

    if not _valid_dataframe(df, minimum_rows=3):
        return None, None

    lookback = max(int(lookback), 3)

    window = df.tail(lookback)

    swing_high = float(window["high"].max())
    swing_low = float(window["low"].min())

    return swing_high, swing_low


def detect_swing_direction(
    df: pd.DataFrame,
) -> str:
    """Detect basic short-term swing direction.

    Returns:
        BULLISH
        BEARISH
        NEUTRAL
    """

    if not _valid_dataframe(df, minimum_rows=6):
        return "NEUTRAL"

    recent = df.tail(6)

    first_high = float(recent["high"].iloc[0])
    last_high = float(recent["high"].iloc[-1])

    first_low = float(recent["low"].iloc[0])
    last_low = float(recent["low"].iloc[-1])

    if last_high > first_high and last_low > first_low:
        return "BULLISH"

    if last_high < first_high and last_low < first_low:
        return "BEARISH"

    return "NEUTRAL"


# ==========================================================
# PART 3 — BREAK OF STRUCTURE (BOS)
# ==========================================================

def detect_break_of_structure(
    df: pd.DataFrame,
    lookback: int = 20,
) -> bool:
    """Detect whether the latest candle breaks recent structure."""

    if not _valid_dataframe(df, minimum_rows=6):
        return False

    previous = df.iloc[:-1]

    recent_high, recent_low = find_recent_swing_high_low(
        previous,
        lookback=lookback,
    )

    if recent_high is None or recent_low is None:
        return False

    latest_close = float(df["close"].iloc[-1])

    bullish_break = latest_close > recent_high
    bearish_break = latest_close < recent_low

    return bullish_break or bearish_break


def detect_bos_direction(
    df: pd.DataFrame,
    lookback: int = 20,
) -> str:
    """Return BOS direction."""

    if not _valid_dataframe(df, minimum_rows=6):
        return "NEUTRAL"

    previous = df.iloc[:-1]

    recent_high, recent_low = find_recent_swing_high_low(
        previous,
        lookback=lookback,
    )

    if recent_high is None or recent_low is None:
        return "NEUTRAL"

    latest_close = float(df["close"].iloc[-1])

    if latest_close > recent_high:
        return "BULLISH"

    if latest_close < recent_low:
        return "BEARISH"

    return "NEUTRAL"


# ==========================================================
# PART 4 — LIQUIDITY SWEEP
# ==========================================================

def detect_liquidity_sweep(
    df: pd.DataFrame,
    lookback: int = 5,
) -> bool:
    """Detect liquidity grab above/below recent range.

    A sweep occurs when price breaks a recent extreme
    but closes back inside the previous range.
    """

    if not _valid_dataframe(df, minimum_rows=6):
        return False

    lookback = max(int(lookback), 3)

    previous = df.iloc[-(lookback + 1):-1]

    if previous.empty:
        return False

    previous_high = float(previous["high"].max())
    previous_low = float(previous["low"].min())

    latest = df.iloc[-1]

    latest_high = float(latest["high"])
    latest_low = float(latest["low"])
    latest_close = float(latest["close"])

    swept_high = (
        latest_high > previous_high
        and latest_close < previous_high
    )

    swept_low = (
        latest_low < previous_low
        and latest_close > previous_low
    )

    return swept_high or swept_low


def detect_liquidity_sweep_direction(
    df: pd.DataFrame,
    lookback: int = 5,
) -> str:
    """Return liquidity sweep direction."""

    if not _valid_dataframe(df, minimum_rows=6):
        return "NEUTRAL"

    lookback = max(int(lookback), 3)

    previous = df.iloc[-(lookback + 1):-1]

    if previous.empty:
        return "NEUTRAL"

    previous_high = float(previous["high"].max())
    previous_low = float(previous["low"].min())

    latest = df.iloc[-1]

    latest_high = float(latest["high"])
    latest_low = float(latest["low"])
    latest_close = float(latest["close"])

    # High liquidity sweep normally creates bearish rejection.
    if latest_high > previous_high and latest_close < previous_high:
        return "BEARISH"

    # Low liquidity sweep normally creates bullish rejection.
    if latest_low < previous_low and latest_close > previous_low:
        return "BULLISH"

    return "NEUTRAL"


# ==========================================================
# PART 5 — ORDER BLOCK
# ==========================================================

def detect_order_block(
    df: pd.DataFrame,
) -> bool:
    """Detect a simple impulsive order-block pattern."""

    if not _valid_dataframe(df, minimum_rows=3):
        return False

    previous = df.iloc[-2]
    latest = df.iloc[-1]

    previous_body = abs(
        float(previous["close"]) - float(previous["open"])
    )

    latest_body = abs(
        float(latest["close"]) - float(latest["open"])
    )

    if previous_body <= 0:
        previous_body = 1e-9

    bullish_impulse = (
        float(latest["close"]) > float(previous["high"])
        and latest_body > previous_body
    )

    bearish_impulse = (
        float(latest["close"]) < float(previous["low"])
        and latest_body > previous_body
    )

    return bullish_impulse or bearish_impulse


def detect_order_block_direction(
    df: pd.DataFrame,
) -> str:
    """Return detected order-block direction."""

    if not _valid_dataframe(df, minimum_rows=3):
        return "NEUTRAL"

    previous = df.iloc[-2]
    latest = df.iloc[-1]

    previous_body = abs(
        float(previous["close"]) - float(previous["open"])
    )

    latest_body = abs(
        float(latest["close"]) - float(latest["open"])
    )

    if previous_body <= 0:
        previous_body = 1e-9

    if (
        float(latest["close"]) > float(previous["high"])
        and latest_body > previous_body
    ):
        return "BULLISH"

    if (
        float(latest["close"]) < float(previous["low"])
        and latest_body > previous_body
    ):
        return "BEARISH"

    return "NEUTRAL"


# ==========================================================
# PART 6 — FAIR VALUE GAP (FVG)
# ==========================================================

def detect_fair_value_gap(
    df: pd.DataFrame,
) -> bool:
    """Detect three-candle Fair Value Gap."""

    if not _valid_dataframe(df, minimum_rows=3):
        return False

    first = df.iloc[-3]
    third = df.iloc[-1]

    bullish_gap = float(first["high"]) < float(third["low"])

    bearish_gap = float(first["low"]) > float(third["high"])

    return bullish_gap or bearish_gap


def detect_fvg_direction(
    df: pd.DataFrame,
) -> str:
    """Return FVG direction."""

    if not _valid_dataframe(df, minimum_rows=3):
        return "NEUTRAL"

    first = df.iloc[-3]
    third = df.iloc[-1]

    if float(first["high"]) < float(third["low"]):
        return "BULLISH"

    if float(first["low"]) > float(third["high"]):
        return "BEARISH"

    return "NEUTRAL"


# ==========================================================
# PART 7 — COMPLETE STRUCTURE ANALYSIS
# ==========================================================

def analyze(
    df: pd.DataFrame,
) -> MarketStructure:
    """Run complete market-structure analysis."""

    if not _valid_dataframe(df, minimum_rows=10):
        return MarketStructure(
            bos=False,
            liquidity_sweep=False,
            order_block=False,
            fvg=False,
            direction="NEUTRAL",
            score=0,
            confirmations=0,
        )

    bos = detect_break_of_structure(df)
    liquidity_sweep = detect_liquidity_sweep(df)
    order_block = detect_order_block(df)
    fvg = detect_fair_value_gap(df)

    bos_direction = detect_bos_direction(df)
    sweep_direction = detect_liquidity_sweep_direction(df)
    order_block_direction = detect_order_block_direction(df)
    fvg_direction = detect_fvg_direction(df)

    directions = [
        bos_direction,
        sweep_direction,
        order_block_direction,
        fvg_direction,
    ]

    bullish_count = directions.count("BULLISH")
    bearish_count = directions.count("BEARISH")

    if bullish_count > bearish_count:
        direction = "BULLISH"
    elif bearish_count > bullish_count:
        direction = "BEARISH"
    else:
        direction = detect_swing_direction(df)

    confirmations = sum(
        [
            int(bos),
            int(liquidity_sweep),
            int(order_block),
            int(fvg),
        ]
    )

    score = confirmations

    # Extra directional agreement.
    if direction in directions:
        score += 1

    return MarketStructure(
        bos=bos,
        liquidity_sweep=liquidity_sweep,
        order_block=order_block,
        fvg=fvg,
        direction=direction,
        score=score,
        confirmations=confirmations,
    )