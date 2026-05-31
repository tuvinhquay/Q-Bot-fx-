"""Runtime environment checks for self-contained deployments."""

from __future__ import annotations

import os
from pathlib import Path


REQUIRED_FOLDERS = ["data", "logs", "backups"]
REQUIRED_ENV_KEYS = ["GEMINI_API_KEY", "TELEGRAM_BOT_TOKEN", "MT5_LOGIN"]


def _load_env_keys(env_path: Path) -> set[str]:
    keys: set[str] = set()
    if not env_path.exists():
        return keys
    for line in env_path.read_text(encoding="utf-8", errors="ignore").splitlines():
        if not line or line.strip().startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        if value.strip():
            keys.add(key.strip())
    return keys


def _mt5_terminal_exists() -> bool:
    candidates = [
        Path(os.environ.get("MT5_TERMINAL_PATH", "")),
        Path("C:/Program Files/MetaTrader 5/terminal64.exe"),
        Path("C:/Program Files/MetaTrader 5/terminal.exe"),
        Path("C:/Program Files (x86)/MetaTrader 5/terminal64.exe"),
        Path("C:/Program Files (x86)/MetaTrader 5/terminal.exe"),
    ]
    return any(path.exists() for path in candidates if str(path))


def check_runtime_environment(project_root: Path | str = ".") -> dict[str, object]:
    root = Path(project_root)
    issues: list[str] = []
    warnings: list[str] = []

    env_path = root / ".env"
    if not env_path.exists():
        issues.append(".env missing")
    else:
        keys = _load_env_keys(env_path)
        missing_keys = [key for key in REQUIRED_ENV_KEYS if key not in keys and not os.environ.get(key)]
        for key in missing_keys:
            warnings.append(f"{key} missing")

    for folder in REQUIRED_FOLDERS:
        if not (root / folder).exists():
            issues.append(f"{folder}/ missing")

    if not _mt5_terminal_exists():
        warnings.append("MT5 terminal not detected")

    if issues:
        status = "FAIL"
    elif warnings:
        status = "WARNING"
    else:
        status = "PASS"

    return {
        "title": "RUNTIME STATUS",
        "status": status,
        "issues": issues,
        "warnings": warnings,
    }


def format_runtime_report(state: dict[str, object]) -> str:
    lines = [str(state.get("title", "RUNTIME STATUS")), f"Status: {state.get('status', 'UNKNOWN')}"]
    for issue in state.get("issues", []):
        lines.append(f"FAIL: {issue}")
    for warning in state.get("warnings", []):
        lines.append(f"WARNING: {warning}")
    if len(lines) == 2:
        lines.append("All required runtime checks passed")
    return "\n".join(lines)
