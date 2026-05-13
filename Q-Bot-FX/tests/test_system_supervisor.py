"""Tests for the Q-Bot FX system supervisor configuration."""

from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

import system_supervisor


class DummyProcess:
    def __init__(self, status: int | None) -> None:
        self.status = status

    def poll(self) -> int | None:
        return self.status


def test_supervisor_process_commands() -> None:
    """Supervisor should know how to start all managed commands."""
    assert system_supervisor.NODE_BACKEND_CMD == ["npm", "run", "dev"]
    assert system_supervisor.PYTHON_ENGINE_CMD[-5:] == [
        "backend.health_api:app",
        "--host",
        "0.0.0.0",
        "--port",
        "8000",
    ]
    assert system_supervisor.CI_MINI_CMD[-1] == "ci-mini/ci_runner.py"


def test_restart_if_crashed_keeps_running_process() -> None:
    """Running processes should not be restarted."""
    process = DummyProcess(None)
    restarted = False

    def starter():
        nonlocal restarted
        restarted = True
        return DummyProcess(None)

    assert system_supervisor.restart_if_crashed("Node Backend", process, starter) is process
    assert restarted is False


def test_restart_if_crashed_restarts_dead_process() -> None:
    """Dead processes should be restarted."""
    replacement = DummyProcess(None)

    def starter():
        return replacement

    assert system_supervisor.restart_if_crashed("Node Backend", DummyProcess(1), starter) is replacement
