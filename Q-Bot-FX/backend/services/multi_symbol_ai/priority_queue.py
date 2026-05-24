"""Priority queue builder for top trade setups."""

from __future__ import annotations


def pick_priority_symbol(ranking: list[dict[str, float]]) -> str | None:
    if not ranking:
        return None
    return str(ranking[0]["symbol"])


def rejected_symbols(ranking: list[dict[str, float]], threshold: float = 50.0) -> list[dict[str, str]]:
    out: list[dict[str, str]] = []
    for row in ranking:
        if float(row["opportunity_score"]) < threshold:
            reason = "volatility qua cao" if float(row["volatility"]) > 0.7 else "hieu suat lich su yeu"
            out.append({"symbol": str(row["symbol"]), "reason": reason})
    return out
