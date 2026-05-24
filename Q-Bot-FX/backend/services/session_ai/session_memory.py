"""Session-time learning memory built on top of learning records."""

from __future__ import annotations

from collections import defaultdict
from typing import Any


def infer_best_worst_session(learning_entries: list[dict[str, Any]]) -> dict[str, str]:
    session_pnl: dict[str, float] = defaultdict(float)
    for row in learning_entries:
        session = str(row.get("session", "UNKNOWN"))
        pnl = float(row.get("pnl", 0) or 0)
        session_pnl[session] += pnl
    if not session_pnl:
        return {"best_session": "UNKNOWN", "worst_session": "UNKNOWN"}
    best = max(session_pnl.items(), key=lambda x: x[1])[0]
    worst = min(session_pnl.items(), key=lambda x: x[1])[0]
    return {"best_session": best, "worst_session": worst}
