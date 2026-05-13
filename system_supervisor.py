"""
Q-Bot FX System Supervisor.

Auto start • Auto monitor • Auto restart • Telegram alert
"""

from __future__ import annotations

import os
import subprocess
import sys
import time
from pathlib import Path

from monitoring.telegram_alert import send_telegram_message

BASE_DIR = Path(__file__).resolve().parent
CHECK_INTERVAL = int(os.getenv("SUPERVISOR_CHECK_INTERVAL", "30"))
BOOT_WAIT_SECONDS = int(os.getenv("SUPERVISOR_BOOT_WAIT", "10"))

NODE_BACKEND_CMD = ["npm", "run", "dev"]
PYTHON_ENGINE_CMD = [
    sys.executable,
    "-m",
    "uvicorn",
    "backend.health_api:app",
    "--host",
    "0.0.0.0",
    "--port",
    "8000",
]
CI_MINI_CMD = [sys.executable, "ci-mini/ci_runner.py"]


# =========================================================
# TELEGRAM ALERTS
# =========================================================

def alert_supervisor_error(message: str) -> None:
    """Send a supervisor failure alert to Telegram when configured."""
    send_telegram_message(f"🚨 <b>Q-Bot FX Supervisor Alert</b>\n{message}")


# =========================================================
# PROCESS STARTERS
# =========================================================

def start_process(name: str, command: list[str], cwd: Path) -> subprocess.Popen | None:
    """Start a managed process and alert Telegram if startup fails."""
    try:
        print(f"🚀 Starting {name}...")
        return subprocess.Popen(command, cwd=cwd)
    except OSError as exc:
        error_message = f"Failed to start {name}: {exc}"
        print(f"🚨 {error_message}")
        alert_supervisor_error(error_message)
        return None


def start_node_backend() -> subprocess.Popen | None:
    """Start the Node backend that serves Telegram bot and health APIs."""
    return start_process("Node Backend", NODE_BACKEND_CMD, BASE_DIR / "backend")


def start_python_engine() -> subprocess.Popen | None:
    """Start the Python Trading Engine health API."""
    return start_process("Python Trading Engine", PYTHON_ENGINE_CMD, BASE_DIR / "Q-Bot-FX")


def run_ci_mini() -> int:
    """Run CI Mini health checks and return the exit status."""
    print("🧪 Running CI Mini health check...")
    return subprocess.call(CI_MINI_CMD, cwd=BASE_DIR)


# =========================================================
# AUTO RESTART
# =========================================================

def restart_if_crashed(
    name: str,
    process: subprocess.Popen | None,
    starter,
) -> subprocess.Popen | None:
    """Restart a managed process if it crashed or failed to start."""
    if process is not None and process.poll() is None:
        return process

    print(f"⚠️ {name} crashed or is not running → restarting")
    restarted_process = starter()
    if restarted_process is None:
        alert_supervisor_error(f"Restart failed for {name}")
    return restarted_process


def stop_process(process: subprocess.Popen | None, name: str) -> None:
    """Terminate a managed process during supervisor shutdown."""
    if process is None or process.poll() is not None:
        return

    print(f"🛑 Stopping {name}...")
    process.terminate()
    try:
        process.wait(timeout=10)
    except subprocess.TimeoutExpired:
        print(f"⚠️ {name} did not stop gracefully; killing")
        process.kill()


# =========================================================
# SUPERVISOR LOOP
# =========================================================

def main() -> None:
    """Start all services, monitor health, and auto-restart crashed services."""
    print("🧠 Q-Bot FX Supervisor started")

    node_process = start_node_backend()
    python_process = start_python_engine()

    time.sleep(BOOT_WAIT_SECONDS)

    try:
        while True:
            print("\n🔍 Checking system health...")
            ci_status = run_ci_mini()

            node_process = restart_if_crashed("Node Backend", node_process, start_node_backend)
            python_process = restart_if_crashed(
                "Python Trading Engine",
                python_process,
                start_python_engine,
            )

            if ci_status != 0:
                print("🚨 CI MINI DETECTED ERROR")
                alert_supervisor_error("CI Mini detected system health errors")

            time.sleep(CHECK_INTERVAL)
    except KeyboardInterrupt:
        print("\n🛑 Supervisor stopped by user")
    finally:
        stop_process(node_process, "Node Backend")
        stop_process(python_process, "Python Trading Engine")


if __name__ == "__main__":
    main()
