"""Adaptive AI report helpers."""

from __future__ import annotations

from typing import Any


def build_adaptive_report(state: dict[str, Any]) -> str:
    return (
        "🧠 ADAPTIVE AI\n\n"
        f"📊 Confidence: {state.get('adaptive_confidence', 0):.2f}\n"
        f"🌍 Best Regime: {state.get('best_regime', 'UNKNOWN')}\n"
        f"⚠️ Dangerous Regime: {state.get('dangerous_regime', 'UNKNOWN')}\n"
        f"💎 Strongest Symbol: {state.get('strongest_symbol', 'UNKNOWN')}\n"
        f"🔥 Weakest Symbol: {state.get('weakest_symbol', 'UNKNOWN')}\n\n"
        f"✅ Adaptive Status: {state.get('adaptive_status', 'UNKNOWN')}"
    )


def build_adaptive_summary_for_telegram(state: dict[str, Any]) -> dict[str, Any]:
    return {
        "adaptive_confidence": float(state.get("adaptive_confidence", 0.0)),
        "market_alignment": str(state.get("market_alignment", "UNKNOWN")),
        "strongest_symbol": str(state.get("strongest_symbol", "UNKNOWN")),
        "dangerous_regime": str(state.get("dangerous_regime", "UNKNOWN")),
        "adaptive_status": str(state.get("adaptive_status", "UNKNOWN")),
    }
