"""Single MT5 connection access point."""

from __future__ import annotations

import threading
from dataclasses import dataclass
from typing import Any

import MetaTrader5 as mt5


@dataclass
class MT5ConnectionState:
    connected: bool
    account: Any | None = None
    terminal: Any | None = None
    error: str | None = None


class ConnectionManager:
    """Keep MT5 initialization centralized for infrastructure modules."""

    _lock = threading.Lock()
    _state: MT5ConnectionState | None = None

    @classmethod
    def get_connection(cls) -> MT5ConnectionState:
        with cls._lock:
            if cls._state and cls._state.connected:
                return cls._state

            if not mt5.initialize():
                cls._state = MT5ConnectionState(False, error="MT5 initialize failed")
                return cls._state

            account = mt5.account_info()
            terminal = mt5.terminal_info()
            connected = account is not None and terminal is not None
            cls._state = MT5ConnectionState(
                connected=connected,
                account=account,
                terminal=terminal,
                error=None if connected else "MT5 account or terminal info unavailable",
            )
            return cls._state

    @classmethod
    def reset(cls) -> None:
        with cls._lock:
            cls._state = None
