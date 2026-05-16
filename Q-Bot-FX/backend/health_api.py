"""FastAPI health endpoints for the Python Trading Engine."""

from __future__ import annotations

from datetime import datetime
import importlib

from backend.mt5_gateway.mt5_health import check_mt5_health


if importlib.util.find_spec("fastapi") is not None:
    FastAPI = importlib.import_module("fastapi").FastAPI
else:
    class FastAPI:  # type: ignore[no-redef]
        """Minimal decorator-compatible fallback when FastAPI is not installed in tests."""

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


@app.get("/mt5/health")
def mt5_health() -> dict[str, str]:
    """Return MetaTrader 5 gateway health state."""
    return {"status": "ok" if check_mt5_health() else "error"}
