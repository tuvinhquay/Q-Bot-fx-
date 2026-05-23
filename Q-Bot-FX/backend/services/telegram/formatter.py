"""Natural-language Telegram caption formatter."""

from __future__ import annotations

from typing import Any

from backend.services.telegram.ai_explainer import explain_ai_confidence, explain_ai_signal
from backend.services.telegram.icons import (
    AI_ICON,
    BRAIN_ICON,
    CHECK_ICON,
    DANGER_ICON,
    FIRE_ICON,
    MONEY_ICON,
    RISK_ICON,
    SUCCESS_ICON,
    TIME_ICON,
    TREND_ICON,
    WARNING_ICON,
)
from backend.services.telegram.risk_explainer import (
    explain_correlation_risk,
    explain_directional_bias,
    explain_dynamic_risk,
    explain_portfolio_heat,
)
from backend.services.telegram.status_engine import classify_alert_status
from backend.services.telegram.templates import HEADER_TEMPLATE, SEPARATOR


def _as_float(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def build_telegram_caption(
    signal: str,
    symbol: str,
    trade_levels: dict[str, float],
    adaptive: dict[str, Any],
    market_regime: dict[str, Any],
    portfolio_result: dict[str, Any],
) -> str:
    """Build natural-language Vietnamese caption for Telegram chart alerts."""
    ai_score = _as_float(adaptive.get("adaptive_score"))
    dynamic_risk = _as_float(portfolio_result.get("dynamic_risk"))
    portfolio_heat = _as_float(portfolio_result.get("portfolio_heat"))
    correlation_risk = str(portfolio_result.get("correlation_risk", "LOW")).upper()
    directional_bias = str(portfolio_result.get("directional_bias", "NEUTRAL"))
    regime = str(market_regime.get("regime", "UNKNOWN"))

    status = classify_alert_status(
        ai_score=ai_score,
        dynamic_risk=dynamic_risk,
        portfolio_heat=portfolio_heat,
        correlation_risk=correlation_risk,
    )
    status_icon = SUCCESS_ICON if status.level == "SAFE" else WARNING_ICON if status.level == "WARNING" else DANGER_ICON

    ai_signal_text = explain_ai_signal(ai_score)
    ai_confidence = explain_ai_confidence(ai_score)
    heat_explain = explain_portfolio_heat(portfolio_heat)
    dynamic_explain = explain_dynamic_risk(dynamic_risk)
    corr_explain = explain_correlation_risk(correlation_risk)
    bias_explain = explain_directional_bias(directional_bias)

    return (
        f"{HEADER_TEMPLATE.format(fire=FIRE_ICON)}\n\n"
        f"{RISK_ICON} Cặp tiền: {symbol}\n"
        f"{TREND_ICON} Xu hướng: {signal}\n\n"
        f"{MONEY_ICON} Entry: {trade_levels.get('entry', 0.0):.5f}\n"
        f"🛑 Cắt lỗ: {trade_levels.get('stop_loss', 0.0):.5f}\n"
        f"🎯 Chốt lời: {trade_levels.get('take_profit', 0.0):.5f}\n\n"
        f"{AI_ICON} ĐÁNH GIÁ AI\n"
        f"{SEPARATOR}\n"
        f"{CHECK_ICON} Điểm AI: {ai_score:.2f}/100\n"
        f"⚖️ Độ tự tin AI: {ai_confidence}\n"
        f"🌍 Trạng thái thị trường: {regime}\n"
        f"{BRAIN_ICON} {ai_signal_text}\n\n"
        f"{WARNING_ICON} RỦI RO\n"
        f"{SEPARATOR}\n"
        f"{FIRE_ICON} Nhiệt danh mục: {portfolio_heat:.2f}%\n"
        f"{MONEY_ICON} Rủi ro động: {dynamic_risk:.2f}%\n"
        f"🔗 Tương quan lệnh: {correlation_risk}\n"
        f"📦 Trạng thái danh mục: {directional_bias}\n"
        f"• {heat_explain}\n"
        f"• {dynamic_explain}\n"
        f"• {corr_explain}\n"
        f"• {bias_explain}\n\n"
        f"{status_icon} KẾT LUẬN\n"
        f"{SEPARATOR}\n"
        f"{BRAIN_ICON} {status.reason}\n"
        f"{status_icon} Mức cảnh báo: {status.level}\n"
        f"{TIME_ICON} Khung thời gian: H1"
    )
