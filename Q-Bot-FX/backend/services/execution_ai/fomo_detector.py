"""Detect FOMO-like execution conditions."""

from __future__ import annotations


def detect_fomo(
    *,
    current_price: float,
    suggested_entry: float,
    spread_quality: str,
    trap_score: float,
) -> dict[str, object]:
    distance_pct = abs(current_price - suggested_entry) / max(abs(suggested_entry), 1e-9) * 100.0
    fomo = distance_pct > 0.12 or trap_score > 65.0
    severity = "HIGH" if distance_pct > 0.25 or (spread_quality == "DANGER" and trap_score > 60) else "MEDIUM" if fomo else "LOW"
    reason = "Entry qua xa breakout zone" if distance_pct > 0.12 else "Volatility panic" if trap_score > 65 else "Gia on dinh"
    return {"fomo_detected": fomo, "severity": severity, "reason": reason}
