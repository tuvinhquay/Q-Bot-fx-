"""Prepare a PyInstaller build for Q-Bot-FX."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path


def main() -> int:
    project_root = Path(__file__).resolve().parent
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
    return subprocess.call(command, cwd=project_root)


if __name__ == "__main__":
    raise SystemExit(main())
