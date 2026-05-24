"""Core orchestrator for AI learning memory."""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Any

from backend.services.learning.learning_analyzer import analyze_learning
from backend.services.learning.learning_report import build_learning_report
from backend.services.learning.memory_store import MemoryStore
from backend.services.learning.performance_tracker import calculate_performance_snapshot
from backend.services.learning.trade_journal import build_trade_journal_line

LOGGER = logging.getLogger(__name__)


class LearningMemoryEngine:
    """Persist and analyze trade memory for AI evolution."""

    def __init__(self, store: MemoryStore | None = None) -> None:
        self.store = store or MemoryStore()

    def record_trade(
        self,
        *,
        symbol: str,
        signal: str,
        market_regime: str,
        ai_score: float,
        risk_level: str,
        correlation_risk: str,
        directional_bias: str,
        trade_result: str,
        pnl: float,
        timeframe: str,
        timestamp: str | None = None,
    ) -> dict[str, Any]:
        LOGGER.info("[LEARNING] Recording trade memory...")
        entries = self.store.load()
        item = {
            "symbol": symbol,
            "signal": signal,
            "market_regime": market_regime,
            "ai_score": round(float(ai_score), 2),
            "risk_level": risk_level,
            "correlation_risk": correlation_risk,
            "directional_bias": directional_bias,
            "trade_result": trade_result,
            "pnl": round(float(pnl), 2),
            "timeframe": timeframe,
            "timestamp": timestamp or datetime.now(timezone.utc).isoformat(),
        }
        entries.append(item)
        self.store.save(entries)
        LOGGER.info("[AI MEMORY] Memory saved successfully.")
        LOGGER.info("[TRADE JOURNAL]\n%s", build_trade_journal_line(item))
        return item

    def snapshot(self) -> dict[str, Any]:
        entries = self.store.load()
        snapshot = calculate_performance_snapshot(entries)
        LOGGER.info(
            "[PERFORMANCE] total=%s win_rate=%.2f%% avg_pnl=%.2f",
            snapshot["total_trade"],
            snapshot["win_rate"],
            snapshot["avg_pnl"],
        )
        return snapshot

    def build_report(self) -> str:
        entries = self.store.load()
        snapshot = calculate_performance_snapshot(entries)
        analysis = analyze_learning(entries)
        report = build_learning_report(snapshot, analysis)
        LOGGER.info("[LEARNING REPORT] report generated.")
        return report
