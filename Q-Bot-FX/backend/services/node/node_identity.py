"""Trading node identity."""

from __future__ import annotations

import os
import platform
import subprocess
import sys
from pathlib import Path


def _git_value(args: list[str], default: str = "UNKNOWN") -> str:
    try:
        result = subprocess.run(
            ["git", *args],
            cwd=Path(__file__).resolve().parents[3],
            capture_output=True,
            text=True,
            check=False,
        )
    except OSError:
        return default
    return result.stdout.strip() or default


def get_node_identity() -> dict[str, str]:
    return {
        "node_name": os.getenv("QBOT_NODE_NAME", platform.node() or "QBotNode"),
        "machine_name": platform.node(),
        "os": platform.platform(),
        "python_version": sys.version.split()[0],
        "bot_version": _git_value(["rev-parse", "--short", "HEAD"]),
        "branch": _git_value(["branch", "--show-current"]),
    }
