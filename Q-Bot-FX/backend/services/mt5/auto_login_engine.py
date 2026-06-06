"""MT5 auto login and reconnect engine."""

from __future__ import annotations

import os
import subprocess
import time
from dataclasses import dataclass
from pathlib import Path

import MetaTrader5 as mt5
from dotenv import load_dotenv

from backend.notifications.telegram_notifier import TelegramNotifier
from config.settings import Settings


@dataclass
class AutoLoginResult:
    success: bool
    attempts: int
    account_login: int | None = None
    trade_allowed: bool = False
    error: str | None = None


def _process_running(process_name: str = "terminal64.exe") -> bool:
    try:
        output = subprocess.run(
            ["tasklist", "/FI", f"IMAGENAME eq {process_name}"],
            capture_output=True,
            text=True,
            check=False,
        ).stdout
    except OSError:
        return False
    return process_name.lower() in output.lower()


class MT5AutoLoginEngine:
    """Start MT5 when needed and login with .env credentials."""

    def __init__(self, env_path: Path | None = None, max_retries: int = 5, retry_delay: float = 2.0) -> None:
        self.env_path = env_path or Path(".env")
        self.max_retries = max_retries
        self.retry_delay = retry_delay

    def _load_credentials(self) -> dict[str, str]:
        load_dotenv(self.env_path)
        return {
            "path": os.getenv("MT5_PATH", ""),
            "login": os.getenv("MT5_LOGIN", ""),
            "password": os.getenv("MT5_PASSWORD", ""),
            "server": os.getenv("MT5_SERVER", ""),
        }

    def _start_terminal_if_needed(self, mt5_path: str) -> None:
        if _process_running():
            return
        if mt5_path and Path(mt5_path).exists():
            subprocess.Popen([mt5_path], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            time.sleep(self.retry_delay)

    def connect(self, notify_on_failure: bool = True) -> AutoLoginResult:
        creds = self._load_credentials()
        if not all([creds["path"], creds["login"], creds["password"], creds["server"]]):
            return AutoLoginResult(False, 0, error="Missing MT5 credentials in .env")

        self._start_terminal_if_needed(creds["path"])
        last_error = None
        for attempt in range(1, self.max_retries + 1):
            initialized = mt5.initialize(
                path=creds["path"],
                login=int(creds["login"]),
                password=creds["password"],
                server=creds["server"],
            )
            if initialized:
                account = mt5.account_info()
                terminal = mt5.terminal_info()
                if account and terminal:
                    return AutoLoginResult(
                        True,
                        attempt,
                        account_login=int(getattr(account, "login", int(creds["login"]))),
                        trade_allowed=bool(getattr(terminal, "trade_allowed", False)),
                    )
            last_error = str(mt5.last_error())
            time.sleep(self.retry_delay)

        if notify_on_failure:
            try:
                TelegramNotifier(Settings()).send(f"CRITICAL\nMT5 login failed\nReason: {last_error}")
            except Exception:
                pass
        return AutoLoginResult(False, self.max_retries, error=last_error or "MT5 login failed")
