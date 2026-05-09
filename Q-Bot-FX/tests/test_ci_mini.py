"""Pytest smoke tests for the CI Mini configuration."""

from __future__ import annotations

import json
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
CI_MINI_DIR = REPO_ROOT / "ci-mini"


def test_ci_mini_config_has_required_services() -> None:
    """CI Mini should monitor the core Q-Bot-FX services."""
    config = json.loads((CI_MINI_DIR / "config.json").read_text(encoding="utf-8"))

    assert set(config["services"]) == {
        "telegram_bot",
        "backend_api",
        "python_engine",
    }
    assert config["services"]["telegram_bot"]["health_url"] == "http://localhost:3000/health"
    assert config["services"]["backend_api"]["health_url"] == "http://localhost:3000/api/health"
    assert config["services"]["python_engine"]["health_url"] == "http://localhost:8000/health"


def test_ci_mini_trade_simulation_is_configured() -> None:
    """CI Mini should include the safe trading smoke-test endpoint."""
    config = json.loads((CI_MINI_DIR / "config.json").read_text(encoding="utf-8"))

    assert config["tests"]["trade_simulation"] == {
        "name": "Trading Simulation",
        "url": "http://localhost:8000/test-trade",
    }
