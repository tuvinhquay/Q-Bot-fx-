"""Telegram/terminal reporting for Prompt 28."""

from __future__ import annotations

from typing import Any


def build_top_setup_report(brain_state: dict[str, Any]) -> str:
    ranking = brain_state.get("ranking", [])
    top = ranking[:3]
    lines = ["🏆 TOP SETUP HOM NAY"]
    for idx, row in enumerate(top, start=1):
        lines.append(f"{idx}. {row['symbol']} -> {row['opportunity_score']} diem")
    if not top:
        lines.append("Khong co setup noi bat")
    rej = brain_state.get("rejected", [])
    if rej:
        lines.append(f"⚠️ {rej[0]['symbol']} bi AI loai bo")
        lines.append(f"Ly do: {rej[0]['reason']}")
    lines.append(f"🌐 Cross-Market: {brain_state.get('cross_market_insight', 'N/A')}")
    return "\n".join(lines)
