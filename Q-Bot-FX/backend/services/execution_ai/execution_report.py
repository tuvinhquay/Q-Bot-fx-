"""Execution AI reporting."""

from __future__ import annotations

from typing import Any


def build_execution_report(state: dict[str, Any]) -> str:
    if not bool(state.get("allow_execution", False)):
        return (
            "🧠 EXECUTION AI\n"
            "━━━━━━━━━━━━━━\n"
            "⏳ AI dang cho candle confirm\n"
            f"⚠️ FOMO: {state.get('fomo_severity', 'N/A')}\n"
            f"📉 RR score: {state.get('rr_score', 0.0)}\n"
            f"🚫 Decision: {state.get('decision', 'WAIT')} - {state.get('reason', 'N/A')}"
        )
    return (
        "🧠 EXECUTION AI\n"
        "━━━━━━━━━━━━━━\n"
        "✅ Timing execution rat dep\n"
        f"🎯 RR score: {state.get('rr_score', 0.0)}\n"
        f"📈 Candle strength: {state.get('candle_strength', 'N/A')}\n"
        "🚀 AI cho phep vao lenh"
    )
