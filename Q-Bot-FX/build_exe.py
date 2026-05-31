"""Build a self-contained Q-Bot-FX deployment folder."""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

from backend.services.deployment.backup_manager import BackupManager
from backend.services.deployment.runtime_checker import REQUIRED_ENV_KEYS

RUNTIME_DIRS = ["data", "logs", "backups", "charts", "runtime"]


def _read_env(path: Path) -> dict[str, str]:
    values: dict[str, str] = {}
    if not path.exists():
        return values
    for line in path.read_text(encoding="utf-8", errors="ignore").splitlines():
        if not line or line.strip().startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        values[key.strip()] = value.strip().strip('"').strip("'")
    return values


def _git_value(project_root: Path, args: list[str], default: str = "UNKNOWN") -> str:
    try:
        result = subprocess.run(
            ["git", *args],
            cwd=project_root,
            text=True,
            capture_output=True,
            check=False,
        )
    except OSError:
        return default
    value = result.stdout.strip()
    return value or default


def _prepare_dist(project_root: Path) -> Path:
    dist_dir = project_root / "dist"
    dist_dir.mkdir(exist_ok=True)
    for name in RUNTIME_DIRS:
        (dist_dir / name).mkdir(parents=True, exist_ok=True)

    env_source = project_root / ".env"
    if env_source.exists():
        shutil.copy2(env_source, dist_dir / ".env")
    else:
        print("[BUILD WARNING] .env file missing; dist/.env was not created.")

    env_values = _read_env(env_source)
    for key in REQUIRED_ENV_KEYS:
        if not env_values.get(key) and not os.environ.get(key):
            print(f"[BUILD WARNING] {key} is missing.")

    return dist_dir


def _write_report(project_root: Path, dist_dir: Path, build_status: str) -> None:
    exe_path = dist_dir / "QBotFX.exe"
    branch = _git_value(project_root, ["branch", "--show-current"])
    commit = _git_value(project_root, ["rev-parse", "--short", "HEAD"])
    exe_size = exe_path.stat().st_size if exe_path.exists() else 0
    report = (
        "Q-BOT FX BUILD REPORT\n"
        f"Build date: {datetime.now(timezone.utc).isoformat()}\n"
        f"Git branch: {branch}\n"
        f"Git commit: {commit}\n"
        f"Python version: {sys.version.split()[0]}\n"
        f"EXE size: {exe_size} bytes\n"
        f"Build status: {build_status}\n"
    )
    (dist_dir / "build_report.txt").write_text(report, encoding="utf-8")


def main() -> int:
    project_root = Path(__file__).resolve().parent
    dist_dir = _prepare_dist(project_root)
    BackupManager(project_root=project_root, backup_dir=dist_dir / "backups").backup_daily()

    entrypoint = project_root / "backend" / "main.py"
    command = [
        sys.executable,
        "-m",
        "PyInstaller",
        "--onefile",
        "--name",
        "QBotFX",
        str(entrypoint),
    ]
    print("Running:", " ".join(command))
    exit_code = subprocess.call(command, cwd=project_root)
    build_status = "SUCCESS" if exit_code == 0 and (dist_dir / "QBotFX.exe").exists() else "FAILED"
    _write_report(project_root, dist_dir, build_status)
    if build_status == "SUCCESS":
        print("[BUILD] Self-contained deployment ready at dist/")
    else:
        print("[BUILD WARNING] Build did not complete, but dist/ structure and build_report.txt were created.")
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
