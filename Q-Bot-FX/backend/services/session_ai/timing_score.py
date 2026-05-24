"""Timing quality score engine."""

from __future__ import annotations


def compute_timing_score(
    *,
    session_name: str,
    spread_quality: str,
    trap_score: float,
) -> dict[str, object]:
    base = 55.0
    if session_name == "LONDON_NEWYORK_OVERLAP":
        base += 25.0
    elif session_name in {"LONDON", "NEW_YORK"}:
        base += 12.0
    else:
        base -= 10.0

    if spread_quality == "WARNING":
        base -= 15.0
    elif spread_quality == "DANGER":
        base -= 35.0

    base -= min(trap_score * 0.4, 30.0)
    score = max(0.0, min(base, 100.0))
    label = "GOLDEN" if score >= 75 else "OK" if score >= 50 else "WEAK"
    return {"timing_score": round(score, 2), "timing_label": label}
