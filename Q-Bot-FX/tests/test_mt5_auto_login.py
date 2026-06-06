"""CI mini tests for MT5 auto login infrastructure."""

from __future__ import annotations

from backend.services.mt5.connection_manager import MT5ConnectionState


def test_connection_state_shape():
    state = MT5ConnectionState(
        connected=False,
        error="offline"
    )

    assert state.connected is False
    assert state.error == "offline"


if __name__ == "__main__":
    test_connection_state_shape()
    print("PASS")