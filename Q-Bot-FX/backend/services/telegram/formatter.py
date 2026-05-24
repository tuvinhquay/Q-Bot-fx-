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
    adaptive_ai: dict[str, Any] | None = None,
    execution_ai: dict[str, Any] | None = None,
) -> str:
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

    adaptive_section = ""
    if adaptive_ai:
        adaptive_section = (
            f"\n\n{AI_ICON} AI THICH NGHI\n"
            f"{SEPARATOR}\n"
            f"{CHECK_ICON} Adaptive Confidence: {float(adaptive_ai.get('adaptive_confidence', 0.0)):.2f}/100\n"
            f"🌍 Market Alignment: {adaptive_ai.get('market_alignment', 'UNKNOWN')}\n"
            f"💎 Strongest Symbol: {adaptive_ai.get('strongest_symbol', 'UNKNOWN')}\n"
            f"⚠️ Dangerous Regime: {adaptive_ai.get('dangerous_regime', 'UNKNOWN')}\n"
            f"✅ Adaptive Status: {adaptive_ai.get('adaptive_status', 'UNKNOWN')}"
        )

    execution_section = ""
    if execution_ai:
        execution_section = (
            f"\n\n{AI_ICON} EXECUTION AI\n"
            f"{SEPARATOR}\n"
            f"⏳ Patience score: {float(execution_ai.get('patience_score', 0.0)):.2f}\n"
            f"🎯 RR score: {float(execution_ai.get('rr_score', 0.0)):.2f}\n"
            f"⚠️ FOMO: {execution_ai.get('fomo_severity', 'N/A')}\n"
            f"📈 Candle: {execution_ai.get('candle_strength', 'N/A')}\n"
            f"✅ Decision: {execution_ai.get('decision', 'WAIT')} ({execution_ai.get('reason', 'N/A')})"
        )

    return (
        f"{HEADER_TEMPLATE.format(fire=FIRE_ICON)}\n\n"
        f"{RISK_ICON} Cap tien: {symbol}\n"
        f"{TREND_ICON} Xu huong: {signal}\n\n"
        f"{MONEY_ICON} Entry: {trade_levels.get('entry', 0.0):.5f}\n"
        f"🛑 Cat lo: {trade_levels.get('stop_loss', 0.0):.5f}\n"
        f"🎯 Chot loi: {trade_levels.get('take_profit', 0.0):.5f}\n\n"
        f"{AI_ICON} DANH GIA AI\n"
        f"{SEPARATOR}\n"
        f"{CHECK_ICON} Diem AI: {ai_score:.2f}/100\n"
        f"⚖️ Do tu tin AI: {ai_confidence}\n"
        f"🌍 Trang thai thi truong: {regime}\n"
        f"{BRAIN_ICON} {ai_signal_text}\n\n"
        f"{WARNING_ICON} RUI RO\n"
        f"{SEPARATOR}\n"
        f"{FIRE_ICON} Nhiet danh muc: {portfolio_heat:.2f}%\n"
        f"{MONEY_ICON} Rui ro dong: {dynamic_risk:.2f}%\n"
        f"🔗 Tuong quan lenh: {correlation_risk}\n"
        f"📦 Trang thai danh muc: {directional_bias}\n"
        f"• {heat_explain}\n"
        f"• {dynamic_explain}\n"
        f"• {corr_explain}\n"
        f"• {bias_explain}\n\n"
        f"{status_icon} KET LUAN\n"
        f"{SEPARATOR}\n"
        f"{BRAIN_ICON} {status.reason}\n"
        f"{status_icon} Muc canh bao: {status.level}\n"
        f"{TIME_ICON} Khung thoi gian: H1"
        f"{adaptive_section}"
        f"{execution_section}"
    )
