"""Capital status report formatting for Telegram or logs."""

from __future__ import annotations

from typing import Any


def build_capital_report(capital_state: dict[str, Any]) -> str:
    if capital_state.get("survival_mode"):
        return (
            "🧠 CAPITAL STATUS\n"
            "━━━━━━━━━━━━━━\n"
            "💰 Account Protection: ACTIVE\n"
            "🛡️ Survival Mode: ON\n"
            f"📉 Drawdown: {capital_state.get('daily_drawdown_pct', 0.0):.2f}%\n"
            f"⚠️ Risk reduced to {capital_state.get('allocated_risk_percent', 0.0):.2f}%\n"
            "🤖 AI confidence lowered"
        )
    return (
        "🚀 CAPITAL STATUS\n"
        "━━━━━━━━━━━━━━\n"
        "✅ Market stable\n"
        "📈 Win streak healthy\n"
        f"💰 Risk optimized: {capital_state.get('allocated_risk_percent', 0.0):.2f}%\n"
        f"🤖 AI confidence strong: {capital_state.get('confidence_score', 0.0):.2f}"
    )
