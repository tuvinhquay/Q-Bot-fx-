"""FastAPI health endpoints for the Python Trading Engine."""

from __future__ import annotations

from datetime import datetime

from fastapi import FastAPI

app = FastAPI(title="Q-Bot-FX Trading Engine Health")


@app.get("/health")
def health() -> dict[str, str]:
    """Return the trading engine health state."""
    return {
        "status": "ok",
        "component": "python_engine",
        "time": datetime.utcnow().isoformat(timespec="seconds") + "Z",
    }


@app.post("/test-trade")
def test_trade() -> dict[str, str]:
    """Run a safe trading simulation smoke test without placing real orders."""
    return {
        "status": "ok",
        "mode": "simulation",
        "message": "Trade simulation completed",
        "time": datetime.utcnow().isoformat(timespec="seconds") + "Z",
    }
