# ==========================================================
# PART 1
# IMPORTS
# ==========================================================

from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional

from telegram import Bot
from telegram.error import TelegramError

from backend.services.telegram.dashboard_manager import (
    get_dashboard_manager,
)

# ==========================================================
# PART 2
# TELEGRAM SERVICE
# ==========================================================

class TelegramService:
    """
    Telegram Bot Service.

    Responsible for:

    • Bot initialization
    • Send message
    • Edit message
    • Delete message
    • Dashboard lifecycle
    """

    def __init__(self) -> None:

        self.bot: Optional[Bot] = None

        self.token: Optional[str] = None

        self.started_at: Optional[datetime] = None

        self.dashboard = get_dashboard_manager()

# ==========================================================
# PART 3
# INITIALIZE
# ==========================================================

    def initialize(
        self,
        bot_token: str,
    ) -> None:
        """
        Initialize Telegram Bot.
        """

        self.token = bot_token

        self.bot = Bot(token=bot_token)

        self.started_at = datetime.now(
            timezone.utc
        )

    @property
    def initialized(
        self,
    ) -> bool:

        return self.bot is not None        

# ==========================================================
# PART 4
# SEND MESSAGE
# ==========================================================

    async def send_message(
        self,
        chat_id: int,
        text: str,
        parse_mode: str = "HTML",
    ):
        """
        Send a Telegram message.
        """

        if not self.initialized:
            raise RuntimeError(
                "TelegramService is not initialized."
            )

        return await self.bot.send_message(
            chat_id=chat_id,
            text=text,
            parse_mode=parse_mode,
            disable_web_page_preview=True,
        )

# ==========================================================
# PART 5
# EDIT MESSAGE
# ==========================================================

    async def edit_message(
        self,
        chat_id: int,
        message_id: int,
        text: str,
        parse_mode: str = "HTML",
    ):
        """
        Edit an existing Telegram message.
        """

        if not self.initialized:
            raise RuntimeError(
                "TelegramService is not initialized."
            )

        return await self.bot.edit_message_text(
            chat_id=chat_id,
            message_id=message_id,
            text=text,
            parse_mode=parse_mode,
            disable_web_page_preview=True,
        )

# ==========================================================
# PART 6
# INITIALIZE DASHBOARD
# ==========================================================

    def initialize_dashboard(
        self,
        chat_id: int,
    ) -> None:
        """
        Initialize Dashboard Manager.
        """

        self.dashboard.initialize(chat_id)


# ==========================================================
# PART 7
# CREATE DASHBOARD
# ==========================================================

    async def create_dashboard(
        self,
        chat_id: int,
        text: str,
    ) -> int:

        message = await self.send_message(
            chat_id,
            text,
        )

        self.dashboard.set_message(
            chat_id,
            message.message_id,
        )

        return message.message_id

# ==========================================================
# PART 8
# UPDATE DASHBOARD
# ==========================================================

    async def update_dashboard(
        self,
        text: str,
    ) -> bool:
        """
        Update current dashboard.
        """

        if not self.dashboard.is_ready():
            return False

        try:

            await self.edit_message(

                chat_id=self.dashboard.get_chat_id(),

                message_id=self.dashboard.get_message_id(),

                text=text,

            )

            self.dashboard.touch()

            return True

        except TelegramError:

            return False

# ==========================================================
# PART 9
# DELETE DASHBOARD
# ==========================================================

    async def delete_dashboard(
        self,
    ) -> bool:
        """
        Delete current dashboard.
        """

        if not self.dashboard.is_ready():
            return False

        try:

            await self.bot.delete_message(

                chat_id=self.dashboard.get_chat_id(),

                message_id=self.dashboard.get_message_id(),

            )

            self.dashboard.reset()

            return True

        except TelegramError:

            return False

# ==========================================================
# PART 10
# DASHBOARD ACCESSOR
# ==========================================================

def get_dashboard(self):

    return self.dashboard


def dashboard_info() -> dict:
    """
    Return dashboard information.
    """

    return get_dashboard_manager().to_dict()


def is_telegram_ready() -> bool:
    """
    Telegram ready?
    """

    return get_telegram_service().initialized

# ==========================================================
# PART 11
# GLOBAL SINGLETON
# ==========================================================

_telegram_service = TelegramService()


def get_telegram_service() -> TelegramService:
    """
    Return global TelegramService instance.
    """
    return _telegram_service


def initialize_telegram_service(
    token: str,
) -> TelegramService:
    """
    Initialize global TelegramService.
    """

    _telegram_service.initialize(token)

    return _telegram_service    
    
                        