"""CI mini tests for health check and crash guard."""

from __future__ import annotations

from backend.services.health.health_check import run_health_check
from backend.services.recovery.crash_guard import CrashGuard


def test_health_check_shape():
    state = run_health_check(mt5_connected=True, telegram_ok=True)

    assert state["status"] in {"OK", "WARNING", "FAIL"}
    assert "issues" in state
    assert "device" in state


def test_crash_guard_exception_result():
    result = CrashGuard().handle_exception(RuntimeError("boom"), recover=lambda: True)

    assert result["recovered"] is True
    assert "boom" in str(result["error"])
