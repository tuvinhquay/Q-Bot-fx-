"""Smart capital distribution by ranking."""

from __future__ import annotations


def allocate_capital_weights(ranking: list[dict[str, float]]) -> dict[str, float]:
    if not ranking:
        return {}
    top = ranking[:3]
    total = sum(max(float(x["opportunity_score"]), 1.0) for x in top)
    return {str(x["symbol"]): round(max(float(x["opportunity_score"]), 1.0) / total, 4) for x in top}
