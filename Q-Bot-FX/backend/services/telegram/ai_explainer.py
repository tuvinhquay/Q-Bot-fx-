"""AI explanation helpers for natural-language Telegram alerts."""

from __future__ import annotations


def explain_ai_signal(score: float) -> str:
    """Convert AI score to natural Vietnamese explanation."""
    if score < 40:
        return "AI đánh giá tín hiệu yếu"
    if score < 60:
        return "AI đánh giá tín hiệu trung bình"
    if score < 80:
        return "AI đánh giá tín hiệu tốt"
    return "AI đánh giá tín hiệu rất mạnh"


def explain_ai_confidence(score: float) -> str:
    """Human-readable confidence label from score."""
    if score < 40:
        return "Thấp"
    if score < 60:
        return "Trung bình"
    if score < 80:
        return "Tốt"
    return "Rất cao"
