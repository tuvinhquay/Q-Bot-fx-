"""Import bridge for the root-level ``ci-mini/ci_runner.py`` module."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
CI_MINI_DIR = REPO_ROOT / "ci-mini"
CI_RUNNER_PATH = CI_MINI_DIR / "ci_runner.py"

if str(CI_MINI_DIR) not in sys.path:
    sys.path.insert(0, str(CI_MINI_DIR))

_spec = importlib.util.spec_from_file_location("_qbot_ci_mini_ci_runner", CI_RUNNER_PATH)
if _spec is None or _spec.loader is None:
    raise ImportError(f"Unable to load CI Mini runner from {CI_RUNNER_PATH}")

_module = importlib.util.module_from_spec(_spec)
sys.modules[_spec.name] = _module
_spec.loader.exec_module(_module)


def __getattr__(name: str):
    return getattr(_module, name)


def __dir__() -> list[str]:
    return sorted(set(globals()) | set(dir(_module)))


build_report = _module.build_report
main = _module.main
load_config = _module.load_config
run_service_checks = _module.run_service_checks
send_telegram = _module.send_telegram
check_service = _module.check_service

__all__ = [
    "build_report",
    "main",
    "load_config",
    "run_service_checks",
    "send_telegram",
    "check_service",
]
