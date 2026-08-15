"""Q-Bot-FX H1 Market Bias Engine.

PART 1 - DATA VALIDATION
PART 2 - TREND INDICATORS
PART 3 - MARKET STRUCTURE BIAS
PART 4 - MOMENTUM / TREND STRENGTH
PART 5 - H1 MARKET BIAS SCORING
PART 6 - FINAL BIAS DECISION

Vai trò duy nhất:
    Phân tích H1 để xác định MARKET BIAS cho các tầng M15/M5.

Không thực hiện:
    - Entry
    - Order execution
    - SL/TP
    - Position sizing
"""

from __future__ import annotations

from dataclasses import dataclass

import pandas as pd


# ============================================================
# PART 1 - DATA VALIDATION
# ============================================================

REQUIRED_COLUMNS = {
    "open",
    "high",
    "low",
    "close",
}


@dataclass
class TrendSignal:
    """Kết quả Market Bias của H1."""

    trend: str  # BULLISH | BEARISH | SIDEWAYS
    score: int = 0
    strength: str = "WEAK"


def _validate_dataframe(df: pd.DataFrame) -> bool:
    """Kiểm tra dữ liệu H1 trước khi phân tích."""

    if df is None:
        return False

    if df.empty:
        return False

    if len(df) < 50:
        return False

    if not REQUIRED_COLUMNS.issubset(df.columns):
        return False

    try:
        prices = df[["open", "high", "low", "close"]].tail(50)

        if prices.isnull().any().any():
            return False

        if (prices["high"] <= 0).any():
            return False

        if (prices["low"] <= 0).any():
            return False

        if (prices["close"] <= 0).any():
            return False

    except Exception:
        return False

    return True


# ============================================================
# PART 2 - TREND INDICATORS
# ============================================================

def _ema(series: pd.Series, period: int) -> pd.Series:
    """Tính EMA."""

    return series.ewm(
        span=period,
        adjust=False,
    ).mean()


def _ema_alignment(df: pd.DataFrame) -> str:
    """Xác định thứ tự EMA20 / EMA50 / EMA200."""

    close = df["close"]

    ema20 = _ema(close, 20).iloc[-1]
    ema50 = _ema(close, 50).iloc[-1]
    ema200 = _ema(close, 200).iloc[-1]

    if ema20 > ema50 > ema200:
        return "BULLISH"

    if ema20 < ema50 < ema200:
        return "BEARISH"

    return "MIXED"


def _ema_slope(df: pd.DataFrame) -> str:
    """Đánh giá hướng di chuyển của EMA50."""

    ema50 = _ema(df["close"], 50)

    if len(ema50) < 5:
        return "FLAT"

    current = float(ema50.iloc[-1])
    previous = float(ema50.iloc[-5])

    if current > previous:
        return "UP"

    if current < previous:
        return "DOWN"

    return "FLAT"


def _price_vs_ema200(df: pd.DataFrame) -> str:
    """Xác định vị trí giá so với EMA200."""

    ema200 = _ema(df["close"], 200).iloc[-1]
    close = float(df["close"].iloc[-1])

    if close > ema200:
        return "ABOVE"

    if close < ema200:
        return "BELOW"

    return "AT"


# ============================================================
# PART 3 - MARKET STRUCTURE BIAS
# ============================================================

def _has_higher_high_higher_low(
    df: pd.DataFrame,
) -> bool:
    """Kiểm tra cấu trúc tăng gần đây."""

    if len(df) < 8:
        return False

    recent = df.tail(8)

    first_high = float(recent["high"].iloc[:4].max())
    second_high = float(recent["high"].iloc[4:].max())

    first_low = float(recent["low"].iloc[:4].min())
    second_low = float(recent["low"].iloc[4:].min())

    return (
        second_high > first_high
        and second_low > first_low
    )


def _has_lower_high_lower_low(
    df: pd.DataFrame,
) -> bool:
    """Kiểm tra cấu trúc giảm gần đây."""

    if len(df) < 8:
        return False

    recent = df.tail(8)

    first_high = float(recent["high"].iloc[:4].max())
    second_high = float(recent["high"].iloc[4:].max())

    first_low = float(recent["low"].iloc[:4].min())
    second_low = float(recent["low"].iloc[4:].min())

    return (
        second_high < first_high
        and second_low < first_low
    )


def _market_structure_bias(
    df: pd.DataFrame,
) -> str:
    """Xác định bias từ cấu trúc giá."""

    bullish = _has_higher_high_higher_low(df)
    bearish = _has_lower_high_lower_low(df)

    if bullish and not bearish:
        return "BULLISH"

    if bearish and not bullish:
        return "BEARISH"

    return "SIDEWAYS"


# ============================================================
# PART 4 - MOMENTUM / TREND STRENGTH
# ============================================================

def _momentum_bias(
    df: pd.DataFrame,
) -> str:
    """Đánh giá động lượng dựa trên thay đổi giá."""

    if len(df) < 10:
        return "NEUTRAL"

    close = df["close"]

    current = float(close.iloc[-1])
    previous = float(close.iloc[-6])

    if current > previous:
        return "BULLISH"

    if current < previous:
        return "BEARISH"

    return "NEUTRAL"


def _candle_strength(
    df: pd.DataFrame,
) -> str:
    """Đánh giá sức mạnh nến gần nhất."""

    last = df.iloc[-1]

    candle_range = float(last["high"]) - float(last["low"])

    if candle_range <= 0:
        return "WEAK"

    body = abs(
        float(last["close"]) - float(last["open"])
    )

    body_ratio = body / candle_range

    if body_ratio >= 0.65:
        return "STRONG"

    if body_ratio >= 0.40:
        return "NORMAL"

    return "WEAK"


# ============================================================
# PART 5 - H1 MARKET BIAS SCORING
# ============================================================

def _calculate_bias_score(
    df: pd.DataFrame,
) -> tuple[str, int]:
    """Tính điểm tổng hợp cho H1 Market Bias."""

    score_bullish = 0
    score_bearish = 0

    # --------------------------------------------------------
    # EMA ALIGNMENT
    # --------------------------------------------------------

    alignment = _ema_alignment(df)

    if alignment == "BULLISH":
        score_bullish += 2

    elif alignment == "BEARISH":
        score_bearish += 2

    # --------------------------------------------------------
    # EMA SLOPE
    # --------------------------------------------------------

    slope = _ema_slope(df)

    if slope == "UP":
        score_bullish += 1

    elif slope == "DOWN":
        score_bearish += 1

    # --------------------------------------------------------
    # PRICE VS EMA200
    # --------------------------------------------------------

    price_position = _price_vs_ema200(df)

    if price_position == "ABOVE":
        score_bullish += 1

    elif price_position == "BELOW":
        score_bearish += 1

    # --------------------------------------------------------
    # MARKET STRUCTURE
    # --------------------------------------------------------

    structure = _market_structure_bias(df)

    if structure == "BULLISH":
        score_bullish += 2

    elif structure == "BEARISH":
        score_bearish += 2

    # --------------------------------------------------------
    # MOMENTUM
    # --------------------------------------------------------

    momentum = _momentum_bias(df)

    if momentum == "BULLISH":
        score_bullish += 1

    elif momentum == "BEARISH":
        score_bearish += 1

    # --------------------------------------------------------
    # FINAL SCORE
    # --------------------------------------------------------

    if score_bullish > score_bearish:
        return "BULLISH", score_bullish

    if score_bearish > score_bullish:
        return "BEARISH", score_bearish

    return "SIDEWAYS", 0


# ============================================================
# PART 6 - FINAL BIAS DECISION
# ============================================================

def detect_trend(
    h1_df: pd.DataFrame,
) -> TrendSignal:
    """Phân tích H1 và trả về Market Bias."""

    if not _validate_dataframe(h1_df):
        return TrendSignal(
            trend="SIDEWAYS",
            score=0,
            strength="WEAK",
        )

    trend, score = _calculate_bias_score(h1_df)

    candle_strength = _candle_strength(h1_df)

    # --------------------------------------------------------
    # BIAS CONFIDENCE FILTER
    # --------------------------------------------------------

    # Điểm tối thiểu để H1 được xem là có bias.
    MIN_BIAS_SCORE = 5

    if score < MIN_BIAS_SCORE:
        return TrendSignal(
            trend="SIDEWAYS",
            score=score,
            strength="WEAK",
        )

    # --------------------------------------------------------
    # STRENGTH
    # --------------------------------------------------------

    if score >= 7 and candle_strength == "STRONG":
        strength = "STRONG"

    elif score >= 6:
        strength = "MODERATE"

    else:
        strength = "WEAK"

    return TrendSignal(
        trend=trend,
        score=score,
        strength=strength,
    )