# ==========================================================
# PART 1
# IMPORTS
# ==========================================================

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Optional

# ==========================================================
# PART 2
# DASHBOARD DATA MODEL
# ==========================================================

@dataclass
class DashboardState:

    chat_id: Optional[int] = None

    message_id: Optional[int] = None

    last_update: Optional[datetime] = None

    initialized: bool = False

# ==========================================================
# PART 3
# DASHBOARD MANAGER CLASS
# ==========================================================

class DashboardManager:

    def __init__(self):

        self.state = DashboardState()

# ==========================================================
# PART 4
# INITIALIZATION
# ==========================================================

    def initialize(self, chat_id: int) -> None:

        self.state.chat_id = chat_id

        self.state.initialized = True

        self.state.last_update = datetime.now(timezone.utc)


    def is_initialized(self) -> bool:

        return self.state.initialized


    def get_chat_id(self) -> Optional[int]:

        return self.state.chat_id

# ==========================================================
# PART 5
# MESSAGE STATE
# ==========================================================

    def set_message(
        self,
        chat_id: int,
        message_id: int,
    ) -> None:

        self.state.chat_id = chat_id

        self.state.message_id = message_id

        self.state.last_update = datetime.now(
            timezone.utc
        )


    def get_message_id(
        self,
    ) -> Optional[int]:

        return self.state.message_id


    def has_message(
        self,
    ) -> bool:

        return (
            self.state.chat_id is not None
            and self.state.message_id is not None
        )

# ==========================================================
# PART 6
# DASHBOARD RENDER
# ==========================================================

from backend.services.telegram.monitoring_center import (
    build_live_dashboard,
)


class DashboardManager(DashboardManager):

    def render_dashboard(
        self,
        context: dict | None = None,
    ) -> str:

        context = context or {}

        return build_live_dashboard(
            context
        )


# ==========================================================
# PART 7
# DASHBOARD INFO
# ==========================================================

    def get_dashboard_state(
        self,
    ) -> DashboardState:

        return self.state


    def reset(
        self,
    ) -> None:

        self.state = DashboardState()


    def update_timestamp(
        self,
    ) -> None:

        self.state.last_update = datetime.now(
            timezone.utc
        )


# ==========================================================
# PART 8
# DASHBOARD UPDATE
# ==========================================================

    def update_timestamp(self) -> None:
        """Update last dashboard refresh time."""
        self.state.last_update = datetime.now(timezone.utc)

    def get_last_update(self) -> Optional[datetime]:
        """Return last update timestamp."""
        return self.state.last_update

    def clear_message(self) -> None:
        """Reset current dashboard message."""
        self.state.message_id = None

    def reset(self) -> None:
        """Reset dashboard state."""
        self.state = DashboardState()


# ==========================================================
# PART 9
# DASHBOARD VALIDATION
# ==========================================================

    def is_ready(self) -> bool:
        """Dashboard ready for edit."""
        return (
            self.state.initialized
            and self.state.chat_id is not None
            and self.state.message_id is not None
        )

    def validate(self) -> bool:
        """Validate dashboard state."""
        return self.is_ready()

    def get_status(self) -> str:
        """Return dashboard status."""

        if not self.state.initialized:
            return "NOT_INITIALIZED"

        if self.state.message_id is None:
            return "WAITING_MESSAGE"

        return "READY"

# ==========================================================
# PART 10
# DASHBOARD EXPORT
# ==========================================================

    def to_dict(self) -> dict:
        """Export dashboard state."""

        return {
            "initialized": self.state.initialized,
            "chat_id": self.state.chat_id,
            "message_id": self.state.message_id,
            "last_update": (
                self.state.last_update.isoformat()
                if self.state.last_update
                else None
            ),
        }

    def __repr__(self) -> str:

        return (
            f"DashboardManager("
            f"chat_id={self.state.chat_id}, "
            f"message_id={self.state.message_id}, "
            f"initialized={self.state.initialized})"
        )


# ==========================================================
# PART 11
# DASHBOARD UTILITIES
# ==========================================================

    def clear(self) -> None:
        """Clear dashboard message only."""

        self.state.message_id = None

    def touch(self) -> None:
        """Refresh timestamp."""

        self.state.last_update = datetime.now(
            timezone.utc
        )

    def is_message_valid(self) -> bool:

        return (
            self.state.message_id is not None
        )


# ==========================================================
# PART 12
# SINGLETON
# ==========================================================

_dashboard_manager: DashboardManager | None = None


def get_dashboard_manager() -> DashboardManager:

    global _dashboard_manager

    if _dashboard_manager is None:

        _dashboard_manager = DashboardManager()

    return _dashboard_manager

# ==========================================================
# PART 13
# END OF FILE
# ==========================================================    