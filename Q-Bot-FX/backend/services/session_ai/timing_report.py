"""Session and timing report for terminal/Telegram."""

from __future__ import annotations

from typing import Any


def build_session_report(state: dict[str, Any]) -> str:
    return (
        "🕒 SESSION TIMING AI\n"
        "━━━━━━━━━━━━━━\n"
        f"🧭 Session: {state.get('session', 'UNKNOWN')}\n"
        f"⏰ UTC: {state.get('hour_utc', '00:00')}\n"
        f"📊 Timing score: {state.get('timing_score', 0.0)} ({state.get('timing_label', 'N/A')})\n"
        f"💱 Spread: {state.get('spread_quality', 'N/A')}\n"
        f"🌪 Trap score: {state.get('trap_score', 0.0)}\n"
        f"✅ Best session hoc duoc: {state.get('best_session', 'UNKNOWN')}\n"
        f"⚠️ Session de thua: {state.get('worst_session', 'UNKNOWN')}\n"
        f"🗒️ Note: {state.get('note', 'N/A')}"
    )
