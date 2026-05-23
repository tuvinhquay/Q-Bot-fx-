"""Standalone Telegram alert test for Prompt 24 layer."""

from __future__ import annotations

import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[3]
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from backend.notifications.telegram_notifier import TelegramNotifier
from backend.services.telegram.formatter import build_telegram_caption
from config.settings import Settings


def main() -> None:
    settings = Settings()
    notifier = TelegramNotifier(settings)

    caption = build_telegram_caption(
        signal="BUY",
        symbol="EURUSDm",
        trade_levels={
            "entry": 1.16020,
            "stop_loss": 1.15780,
            "take_profit": 1.16480,
        },
        adaptive={
            "adaptive_score": 63.75,
            "weight": 1.05,
            "allow_trading": True,
        },
        market_regime={"regime": "LOW VOLATILITY"},
        portfolio_result={
            "portfolio_heat": 2.20,
            "dynamic_risk": 1.10,
            "correlation_risk": "HIGH",
            "directional_bias": "NEUTRAL",
            "allow_trade": True,
            "reason": "ok",
        },
    )

    chart_candidate = Path("backtest_equity.png")
    if chart_candidate.exists():
        notifier.send_photo(str(chart_candidate), caption)
    else:
        notifier.send(caption)


if __name__ == "__main__":
    main()
