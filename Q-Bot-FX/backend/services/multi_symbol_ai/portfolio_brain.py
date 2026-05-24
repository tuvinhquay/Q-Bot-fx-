"""Portfolio-level AI brain orchestrator."""

from __future__ import annotations

from typing import Any

from backend.services.learning.memory_store import MemoryStore
from backend.services.multi_symbol_ai.capital_distribution import allocate_capital_weights
from backend.services.multi_symbol_ai.cross_market import infer_usd_strength
from backend.services.multi_symbol_ai.priority_queue import pick_priority_symbol, rejected_symbols
from backend.services.multi_symbol_ai.ranking_engine import build_market_ranking


class MultiSymbolPortfolioBrain:
    def __init__(self, memory_store: MemoryStore | None = None) -> None:
        self.memory_store = memory_store or MemoryStore()

    def evaluate(self, symbols: list[str], volatility_map: dict[str, float]) -> dict[str, Any]:
        entries = self.memory_store.load()
        ranking = build_market_ranking(symbols, entries, volatility_map)
        top_symbol = pick_priority_symbol(ranking)
        weights = allocate_capital_weights(ranking)
        rejected = rejected_symbols(ranking)
        return {
            "ranking": ranking,
            "top_symbol": top_symbol,
            "capital_weights": weights,
            "cross_market_insight": infer_usd_strength(symbols),
            "rejected": rejected,
        }
