"""Adaptive intelligence engine."""

from __future__ import annotations

from typing import Any

from backend.services.adaptive_ai.confidence_adjuster import adjust_confidence
from backend.services.adaptive_ai.opportunity_ranker import rank_opportunity
from backend.services.adaptive_ai.regime_memory import AdaptiveMemoryStore, summarize_regime_memory
from backend.services.adaptive_ai.self_protection import evaluate_self_protection
from backend.services.adaptive_ai.symbol_behavior import analyze_symbol_behavior
from backend.services.learning.memory_store import MemoryStore


class AdaptiveIntelligenceEngine:
    """Central adaptive engine for Prompt 27."""

    def __init__(
        self,
        learning_store: MemoryStore | None = None,
        adaptive_store: AdaptiveMemoryStore | None = None,
    ) -> None:
        self.learning_store = learning_store or MemoryStore()
        self.adaptive_store = adaptive_store or AdaptiveMemoryStore()

    def evaluate(
        self,
        *,
        symbol: str,
        market_regime: str,
        base_confidence: float,
        capital_state: dict[str, Any],
        volatility_score: float,
    ) -> dict[str, Any]:
        learning_entries = self.learning_store.load()
        regime_insight = summarize_regime_memory(learning_entries)
        symbol_insight = analyze_symbol_behavior(learning_entries)

        loss_streak = int(capital_state.get("consecutive_losses", 0))
        in_best_regime = market_regime == regime_insight.get("best_regime")
        adaptive_conf = adjust_confidence(
            base_confidence=base_confidence,
            in_best_regime=in_best_regime,
            survival_mode=bool(capital_state.get("survival_mode", False)),
            loss_streak=loss_streak,
            volatility_score=volatility_score,
        )

        rank = rank_opportunity(
            symbol=symbol,
            market_regime=market_regime,
            symbol_insight=symbol_insight,
            regime_insight=regime_insight,
            adaptive_confidence=adaptive_conf,
        )
        protection = evaluate_self_protection(
            adaptive_confidence=adaptive_conf,
            market_danger_score=float(capital_state.get("market_danger_score", 50.0)),
            survival_mode=bool(capital_state.get("survival_mode", False)),
            loss_streak=loss_streak,
        )

        market_alignment = "GOOD" if in_best_regime else "BAD" if market_regime == regime_insight.get("dangerous_regime") else "NEUTRAL"
        allow_trade = (not bool(protection["should_block_trade"])) and rank["opportunity_score"] >= 45

        result = {
            "adaptive_confidence": adaptive_conf,
            "market_alignment": market_alignment,
            "strategy_strength": rank["strategy_strength"],
            "adaptive_status": str(protection["adaptive_status"]),
            "allow_trade": allow_trade,
            "risk_multiplier": float(protection["risk_multiplier"]),
            "dangerous_regime": regime_insight.get("dangerous_regime", "UNKNOWN"),
            "best_regime": regime_insight.get("best_regime", "UNKNOWN"),
            "strongest_symbol": symbol_insight.get("strongest_symbol", "UNKNOWN"),
            "weakest_symbol": symbol_insight.get("weakest_symbol", "UNKNOWN"),
            "opportunity_score": rank["opportunity_score"],
        }

        memory = self.adaptive_store.load()
        memory["last_state"] = result
        self.adaptive_store.save(memory)
        return result
