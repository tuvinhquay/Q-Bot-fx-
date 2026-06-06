"""System health checks for Q-Bot-FX infrastructure."""

from __future__ import annotations

import socket
from typing import Any

from backend.services.device.device_health import get_device_health


def _internet_ok() -> bool:
    try:
        socket.create_connection(("8.8.8.8", 53), timeout=2).close()
        return True
    except OSError:
        return False


def run_health_check(mt5_connected: bool = True, telegram_ok: bool = True) -> dict[str, Any]:
    device = get_device_health()
    issues: list[str] = []

    if not mt5_connected:
        issues.append("MT5 disconnected")
    if not _internet_ok():
        issues.append("Internet offline")
    if not telegram_ok:
        issues.append("Telegram unavailable")
    if device.disk_percent >= 90:
        issues.append("Disk usage critical")
    if device.ram_percent >= 90:
        issues.append("Memory usage critical")
    if device.cpu_percent >= 95:
        issues.append("CPU usage critical")

    if any("critical" in item.lower() or "disconnected" in item.lower() for item in issues):
        status = "FAIL"
    elif issues:
        status = "WARNING"
    else:
        status = "OK"

    return {
        "status": status,
        "issues": issues,
        "device": device.to_dict(),
    }
