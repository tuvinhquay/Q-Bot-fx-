"""Risk explanation helpers for Telegram alerts."""

from __future__ import annotations


def explain_portfolio_heat(heat_percent: float) -> str:
    if heat_percent > 5:
        return "Danh mục đang khá nóng"
    if heat_percent > 3:
        return "Danh mục có nhiệt độ trung bình"
    return "Danh mục đang ổn định"


def explain_dynamic_risk(dynamic_risk: float) -> str:
    if dynamic_risk > 3:
        return "AI đang tăng mức rủi ro"
    if dynamic_risk > 2:
        return "Mức rủi ro đang nhích lên"
    return "Rủi ro động đang trong ngưỡng an toàn"


def explain_correlation_risk(correlation_risk: str) -> str:
    normalized = str(correlation_risk).strip().upper()
    if normalized == "HIGH":
        return "Có rủi ro trùng hướng với lệnh khác"
    if normalized == "MEDIUM":
        return "Có mức tương quan trung bình với lệnh khác"
    return "Tương quan với lệnh khác đang thấp"


def explain_directional_bias(directional_bias: str) -> str:
    normalized = str(directional_bias).strip().upper()
    if normalized == "LONG_HEAVY":
        return "Danh mục đang nghiêng về phía BUY"
    if normalized == "SHORT_HEAVY":
        return "Danh mục đang nghiêng về phía SELL"
    return "Danh mục đang cân bằng hướng lệnh"
