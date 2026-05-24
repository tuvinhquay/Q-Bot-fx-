"""Smart capital manager orchestrator."""

from __future__ import annotations

import logging
from typing import Any

from backend.services.capital.capital_report import build_capital_report
from backend.services.capital.confidence_engine import compute_confidence_scores
from backend.services.capital.drawdown_guard import classify_drawdown
from backend.services.capital.recovery_engine import recovery_risk_step
from backend.services.capital.smart_risk_allocator import allocate_smart_risk
from backend.services.capital.survival_mode import resolve_survival_mode
from backend.services.learning.memory_store import MemoryStore

LOGGER = logging.getLogger(__name__)


class CapitalManager:
    """Compute survival-aware capital control from memory and market context."""

    def __init__(self, memory_store: MemoryStore | None = None) -> None:
        self.memory_store = memory_store or MemoryStore()

    def evaluate(
        self,
        *,
        base_risk_percent: float,
        market_regime: str,
        volatility_score: float,
        daily_drawdown_pct: float,
        weekly_drawdown_pct: float,
        floating_drawdown_pct: float,
    ) -> dict[str, Any]:
        entries = self.memory_store.load()
        recent = entries[-50:]
        consecutive_losses = 0
        for row in reversed(recent):
            if str(row.get("trade_result", "")).upper() == "LOSS":
                consecutive_losses += 1
            else:
                break

        drawdown = classify_drawdown(
            daily_drawdown_pct=daily_drawdown_pct,
            weekly_drawdown_pct=weekly_drawdown_pct,
            floating_drawdown_pct=floating_drawdown_pct,
        )
        LOGGER.info("[DRAWDOWN] level=%s message=%s", drawdown.level, drawdown.message)

        survival_mode, survival_reason = resolve_survival_mode(
            drawdown_level=drawdown.level,
            consecutive_losses=consecutive_losses,
            volatility_score=volatility_score,
        )
        LOGGER.info("[SURVIVAL MODE] active=%s reason=%s", survival_mode, survival_reason)

        confidence = compute_confidence_scores(
            recent_entries=recent,
            regime=market_regime,
            volatility_score=volatility_score,
        )
        LOGGER.info(
            "[CONFIDENCE] confidence=%.2f emotional=%.2f danger=%.2f",
            confidence["confidence_score"],
            confidence["emotional_risk_score"],
            confidence["market_danger_score"],
        )

        recovery_risk = recovery_risk_step(consecutive_losses)
        LOGGER.info("[RECOVERY] loss_streak=%s recovery_risk=%.2f%%", consecutive_losses, recovery_risk)

        allocated_risk = allocate_smart_risk(
            base_risk_percent=base_risk_percent,
            confidence_score=confidence["confidence_score"],
            market_danger_score=confidence["market_danger_score"],
            survival_mode=survival_mode,
            recovery_risk_percent=recovery_risk,
            hard_cap_percent=max(base_risk_percent, 1.5),
        )
        LOGGER.info("[SMART RISK] allocated risk=%.2f%%", allocated_risk)

        payload: dict[str, Any] = {
            "drawdown_level": drawdown.level,
            "drawdown_message": drawdown.message,
            "survival_mode": survival_mode,
            "survival_reason": survival_reason,
            "consecutive_losses": consecutive_losses,
            "allocated_risk_percent": allocated_risk,
            "daily_drawdown_pct": daily_drawdown_pct,
            "weekly_drawdown_pct": weekly_drawdown_pct,
            "floating_drawdown_pct": floating_drawdown_pct,
            **confidence,
        }
        payload["capital_report"] = build_capital_report(payload)
        LOGGER.info("[CAPITAL] capital decision completed.")
        return payload
