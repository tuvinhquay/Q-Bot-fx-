"""Tests for the local CI Mini runner."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
CI_MINI_DIR = REPO_ROOT / "ci-mini"
if str(CI_MINI_DIR) not in sys.path:
    sys.path.insert(0, str(CI_MINI_DIR))

import ci_runner


def test_run_tests_returns_true_on_success(monkeypatch, capsys) -> None:
    """run_tests should execute pytest and return True for a zero exit code."""

    def fake_run(command, capture_output, text):
        assert command == ["python", "-m", "pytest", "Q-Bot-FX"]
        assert capture_output is True
        assert text is True
        return subprocess.CompletedProcess(command, 0, stdout="passed", stderr="")

    monkeypatch.setattr(ci_runner.subprocess, "run", fake_run)

    assert ci_runner.run_tests() is True
    assert "🚀 Running CI MINI tests..." in capsys.readouterr().out


def test_run_tests_returns_false_on_failure(monkeypatch) -> None:
    """run_tests should return False when pytest exits non-zero."""

    def fake_run(command, capture_output, text):
        return subprocess.CompletedProcess(command, 1, stdout="failed", stderr="error")

    monkeypatch.setattr(ci_runner.subprocess, "run", fake_run)

    assert ci_runner.run_tests() is False


def test_notify_invokes_ci_notifier(monkeypatch) -> None:
    """notify should call the Telegram notifier script with the status."""
    calls = []

    def fake_run(command):
        calls.append(command)
        return subprocess.CompletedProcess(command, 0)

    monkeypatch.setattr(ci_runner.subprocess, "run", fake_run)

    ci_runner.notify("success")

    assert calls == [["python", "monitoring/ci_notifier.py", "success"]]
