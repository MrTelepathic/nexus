"""Start command and onboarding flow.

Handles:
- /start with deep link parameters (referral codes, product links)
- First-time user registration (handled by TenantMiddleware)
- Mini App launch button
"""

from aiogram import Router, F
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import CommandStart, Command

from bot.config import get_settings
from bot.utils.formatters import escape_html

router = Router(name="start")


@router.message(CommandStart())
async def cmd_start(message: Message, **kwargs) -> None:
    """Handle /start command with optional deep link payload."""
    settings = get_settings()
    user = message.from_user
    if not user:
        return

    # Parse deep link payload (referral code, product ID, etc.)
    payload = message.text.split(maxsplit=1)[1] if " " in message.text else None

    # If payload starts with "ref_", process referral
    if payload and payload.startswith("ref_"):
        referral_code = payload[4:]
        # TODO: Look up referrer by code, create referral record
        from structlog import get_logger
        get_logger().info("referral_link_opened", code=referral_code, user_id=user.id)

    name = escape_html(user.first_name or "there")

    # Build Mini App keyboard
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(
            text="🚀 Open Nexus Dashboard",
            web_app={"url": f"{settings.mini_app_url}?start={payload or 'main'}"},
        )],
        [InlineKeyboardButton(
            text="📖 Help",
            callback_data="help",
        )],
    ])

    await message.answer(
        f"Welcome to <b>Nexus</b>, {name}! 🌐\n\n"
        "Your AI-powered business platform inside Telegram.\n\n"
        "• 📊 <b>Dashboard</b> — Manage your business in real-time\n"
        "• 🤖 <b>AI Assistant</b> — Automate sales & support\n"
        "• 💳 <b>Payments</b> — Stars, crypto & fiat\n"
        "• 🎮 <b>Gamification</b> — Engage your customers\n\n"
        "Tap below to get started:",
        reply_markup=keyboard,
    )


@router.message(Command("help"))
async def cmd_help(message: Message, **kwargs) -> None:
    """Show help information."""
    await message.answer(
        "<b>Nexus Bot Commands</b>\n\n"
        "/start — Launch Nexus\n"
        "/dashboard — Open business dashboard\n"
        "/buy — Browse products & subscriptions\n"
        "/settings — Bot configuration\n"
        "/help — Show this message\n\n"
        "<b>For Business Owners:</b>\n"
        "Connect your business to auto-reply to customers using AI.\n\n"
        "<b>For Customers:</b>\n"
        "Shop, earn rewards, and interact with businesses.",
    )


@router.callback_query(F.data == "help")
async def callback_help(callback_query, **kwargs) -> None:
    """Handle help button callback."""
    await callback_query.message.answer(
        "<b>Nexus Help</b>\n\n"
        "Use /start to relaunch the bot.\n"
        "Use /buy to browse products.\n"
        "Open the Dashboard to manage your business."
    )
    await callback_query.answer()
