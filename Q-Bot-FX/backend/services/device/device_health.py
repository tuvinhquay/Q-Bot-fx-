"""Device health monitoring for a trading node."""

from __future__ import annotations

import socket
import time
from dataclasses import asdict, dataclass

try:
    import psutil
except ImportError:  # pragma: no cover - defensive fallback for minimal installs
    psutil = None


@dataclass
class DeviceHealthReport:
    cpu_percent: float
    ram_percent: float
    disk_percent: float
    network_status: str
    system_uptime_seconds: int
    battery_percent: float | None

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


def _network_status() -> str:
    try:
        socket.create_connection(("8.8.8.8", 53), timeout=2).close()
        return "ONLINE"
    except OSError:
        return "OFFLINE"


def get_device_health() -> DeviceHealthReport:
    if psutil is None:
        return DeviceHealthReport(0.0, 0.0, 0.0, _network_status(), 0, None)

    battery = psutil.sensors_battery()
    return DeviceHealthReport(
        cpu_percent=float(psutil.cpu_percent(interval=0.1)),
        ram_percent=float(psutil.virtual_memory().percent),
        disk_percent=float(psutil.disk_usage(".").percent),
        network_status=_network_status(),
        system_uptime_seconds=int(time.time() - psutil.boot_time()),
        battery_percent=float(battery.percent) if battery else None,
    )
