from datetime import datetime

from backend.notifications.telegram_notifier import TelegramNotifier


def send_startup_status(settings, balance=0.0, equity=0.0):
    notifier = TelegramNotifier(settings)

    message = (
        "🚀 Q-BOT FX STARTED\n"
        "━━━━━━━━━━━━━━\n\n"
        "🟢 MT5 Connected\n"
        "🟢 Gemini Online\n"
        "🟢 Telegram Online\n"
        "🟢 Trading Active\n\n"
        f"💰 Balance: {balance:.2f} USD\n"
        f"📈 Equity : {equity:.2f} USD\n\n"
        f"🕒 Time: {datetime.now():%Y-%m-%d %H:%M:%S}\n\n"
        "✅ SYSTEM READY"
    )

    notifier.send(message)


def send_heartbeat(settings, balance=0.0, equity=0.0):
    notifier = TelegramNotifier(settings)

    message = (
        "💓 Q-BOT FX HEARTBEAT\n"
        "━━━━━━━━━━━━━━\n\n"
        "🟢 MT5 Connected\n"
        "🟢 Trading Active\n\n"
        f"💰 Balance: {balance:.2f} USD\n"
        f"📈 Equity : {equity:.2f} USD\n\n"
        f"🕒 Time: {datetime.now():%Y-%m-%d %H:%M:%S}\n\n"
        "✅ NORMAL"
    )

    notifier.send(message)