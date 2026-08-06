"""
Telegram Dashboard Updater
Q-Bot-FX
"""

from __future__ import annotations

import asyncio
import logging
from datetime import datetime, timezone
from typing import Any

from backend.services.telegram.monitoring_center import (
    build_live_dashboard,
)
from backend.services.telegram.telegram_service import (
    TelegramService,
)

LOGGER = logging.getLogger(__name__)


class DashboardUpdater:
    """
    Responsible for updating Telegram Live Dashboard.
    """

    def __init__(self) -> None:

        self.service: TelegramService | None = None

        self.running: bool = False

        self.interval: int = 5

        self.last_update: datetime | None = None

    # =====================================================
    # INITIALIZATION
    # =====================================================

    def initialize(
        self,
        service: TelegramService,
    ) -> None:

        self.service = service

        self.running = False

        self.last_update = None

    def is_initialized(self) -> bool:

        return self.service is not None

    def set_interval(
        self,
        seconds: int,
    ) -> None:

        self.interval = max(1, seconds)

    # =====================================================
    # STATUS
    # =====================================================

    def status(self) -> dict:

        return {
            "initialized": self.is_initialized(),
            "running": self.running,
            "interval": self.interval,
            "last_update": (
                self.last_update.isoformat()
                if self.last_update
                else None
            ),
        }

    def is_running(self) -> bool:

        return self.running

    # =====================================================
    # DASHBOARD BUILD
    # =====================================================

    def build_dashboard(
        self,
        context: dict[str, Any] | None = None,
    ) -> str:

        context = context or {}

        return build_live_dashboard(context)

    # =====================================================
    # UPDATE ONCE
    # =====================================================

    async def update_once(
        self,
        context: dict[str, Any] | None = None,
    ) -> bool:

        if not self.is_initialized():
            return False

        dashboard = self.build_dashboard(context)

        success = await self.service.update_dashboard(
            dashboard
        )

        if success:

            self.last_update = datetime.now(
                timezone.utc
            )

        return success

    # =====================================================
    # LOOP
    # =====================================================

    async def run(
        self,
        context: dict[str, Any] | None = None,
    ) -> None:

        self.running = True

        LOGGER.info(
            "DashboardUpdater started."
        )

        while self.running:

            try:

                await self.update_once(context)

            except Exception as error:

                LOGGER.warning(
                    "Dashboard update failed: %s",
                    error,
                )

            await asyncio.sleep(self.interval)

    async def start(
        self,
        context: dict[str, Any] | None = None,
    ) -> None:

        if self.running:
            return

        await self.run(context)

    def stop(self) -> None:

        self.running = False

        LOGGER.info(
            "DashboardUpdater stopped."
        )


# =====================================================
# SINGLETON
# =====================================================

_dashboard_updater = DashboardUpdater()


def get_dashboard_updater() -> DashboardUpdater:

    return _dashboard_updater


def dashboard_updater_status() -> dict:

    return _dashboard_updater.status()


def is_dashboard_running() -> bool:

    return _dashboard_updater.is_running()


def stop_dashboard_updater() -> None:

    _dashboard_updater.stop()