"""Entry quality optimizer."""

from __future__ import annotations


def optimize_entry(
    *,
    entry: float,
    stop_loss: float,
    take_profit: float,
    trap_score: float,
) -> dict[str, object]:
    risk = abs(entry - stop_loss)
    reward = abs(take_profit - entry)
    rr = reward / max(risk, 1e-9)
    rr_score = min(max((rr / 3.0) * 100.0, 0.0), 100.0)
    chasing = "HIGH" if trap_score > 75 or rr < 1.2 else "MEDIUM" if rr < 1.8 else "LOW"
    quality = "GOOD" if rr >= 2.0 and trap_score < 60 else "OK" if rr >= 1.3 else "WEAK"
    optimized = entry if trap_score < 70 else entry * 0.999
    return {
        "optimized_entry": round(float(optimized), 5),
        "entry_quality": quality,
        "rr_score": round(float(rr_score), 2),
        "chasing_risk": chasing,
    }
