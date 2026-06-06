"""CI mini tests for device health."""

from __future__ import annotations

from backend.services.device.device_health import get_device_health
from backend.services.node.node_identity import get_node_identity


def test_device_health_report_shape():
    report = get_device_health()
    data = report.to_dict()

    assert "cpu_percent" in data
    assert "ram_percent" in data
    assert "disk_percent" in data
    assert data["network_status"] in {"ONLINE", "OFFLINE"}


def test_node_identity_shape():
    identity = get_node_identity()

    assert identity["node_name"]
    assert identity["python_version"]
    assert "branch" in identity


if __name__ == "__main__":
    test_device_health_report_shape()
    test_node_identity_shape()
