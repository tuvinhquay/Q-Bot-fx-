"""FastAPI health endpoints for the Python Trading Engine."""

from __future__ import annotations

from datetime import datetime
<<<<<<< Updated upstream

from fastapi import FastAPI
=======
import importlib
import os

# ⭐ ADD: load .env
from dotenv import load_dotenv

# Load .env from project root
load_dotenv()

from backend.mt5_gateway.mt5_health import check_mt5_health


# Fallback FastAPI when running tests without FastAPI installed
if importlib.util.find_spec("fastapi") is not None:
    FastAPI = importlib.import_module("fastapi").FastAPI
else:
    class FastAPI:  # type: ignore
        def __init__(self, *args, **kwargs) -> None:
            pass

        def get(self, *args, **kwargs):
            def decorator(func):
                return func
            return decorator

        def post(self, *args, **kwargs):
            def decorator(func):
                return func
            return decorator
>>>>>>> Stashed changes


app = FastAPI(title="Q-Bot-FX Trading Engine Health")


# ==============================
# CORE ENGINE HEALTH
# ==============================
@app.get("/health")
def health() -> dict[str, str]:
    return {
        "status": "ok",
        "component": "python_engine",
        "time": datetime.utcnow().isoformat(timespec="seconds") + "Z",
    }


# ==============================
# SAFE TEST TRADE (SIMULATION)
# ==============================
@app.post("/test-trade")
def test_trade() -> dict[str, str]:
    return {
        "status": "ok",
        "mode": "simulation",
        "message": "Trade simulation completed",
        "time": datetime.utcnow().isoformat(timespec="seconds") + "Z",
    }
<<<<<<< Updated upstream
=======


# ==============================
# MT5 HEALTH CHECK
# ==============================
@app.get("/mt5/health")
def mt5_health() -> dict[str, str]:
    ok = check_mt5_health()

    return {
        "status": "ok" if ok else "error",
        "component": "mt5_gateway",
        "time": datetime.utcnow().isoformat(timespec="seconds") + "Z",
    }
>>>>>>> Stashed changes
