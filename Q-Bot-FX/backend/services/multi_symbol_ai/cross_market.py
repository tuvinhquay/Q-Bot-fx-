"""Cross-market awareness helpers."""

from __future__ import annotations


def infer_usd_strength(symbols: list[str]) -> str:
    usd_related = [s for s in symbols if "USD" in s.upper()]
    if len(usd_related) >= max(1, int(len(symbols) * 0.6)):
        return "USD manh tren toan market"
    return "USD khong chiem uu the ro rang"
