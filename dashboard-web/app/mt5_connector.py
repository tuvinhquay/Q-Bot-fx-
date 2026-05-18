from __future__ import annotations

from typing import Any, Optional

import MetaTrader5 as _mt5

# Treat MetaTrader5 as dynamic runtime API so Pylance doesn't flag missing attrs
# when local stubs or package metadata are incomplete.
mt5: Any = _mt5


class MT5Connector:
    def __init__(
        self,
        login: int,
        password: str,
        server: str,
        path: Optional[str] = None,
    ) -> None:
        self.login = login
        self.password = password
        self.server = server
        self.path = path

    def initialize(self) -> tuple[bool, str]:
        try:
            mt5.shutdown()

            if self.path:
                started = mt5.initialize(self.path)
            else:
                started = mt5.initialize()

            if not started:
                return False, f"Initialize failed: {mt5.last_error()}"

            authorized = mt5.login(
                login=self.login,
                password=self.password,
                server=self.server,
            )

            if not authorized:
                return False, f"Login failed: {mt5.last_error()}"

            terminal_info = mt5.terminal_info()
            if terminal_info is None:
                return False, "Terminal not ready"

            return True, "MT5 connected successfully"
        except Exception as e:
            return False, f"Exception: {str(e)}"

    def account_info(self) -> Optional[dict[str, Any]]:
        info = mt5.account_info()
        if info is None:
            return None

        return {
            "login": info.login,
            "balance": info.balance,
            "equity": info.equity,
            "margin": info.margin,
            "leverage": info.leverage,
            "company": info.company,
            "server": info.server,
            "currency": info.currency,
        }

    def shutdown(self) -> None:
        mt5.shutdown()
