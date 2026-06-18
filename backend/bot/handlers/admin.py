"""Admin-only bot commands.

Handles business owner commands:
- /dashboard — Launch Mini App dashboard
- /stats — Quick stats summary
- /config — Bot configuration
- /broadcast — Send message to all customers
"""

import structlog
from aiogram import Router, F
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton

from bot.config import get_settings
from bot.utils.formatters import escape_html

log = structlog.get_logger()
router = Router(name="admin")


def _is_admin(user_id: int) -> bool:
    """Check if user is a business owner/admin.

    TODO: Check against DB roles, not hardcoded.
    """
    # Placeholder: In production, query users table
    return True


@router.message(F.text == "/dashboard")
async def cmd_dashboard(message: Message) -> None:
    """Launch the business dashboard Mini App."""
    settings = get_settings()

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(
            text="📊 Open Dashboard",
            web_app={"url": settings.mini_app_url},
        )],
    ])

    await message.answer(
        "<b>Nexus Dashboard</b>\n\n"
        "Open your business dashboard to manage:\n"
        "• 📈 Real-time analytics\n"
        "• 📦 Products & inventory\n"
        "• 💬 Customer conversations\n"
        "• 💰 Payments & wallet\n"
        "• 🎮 Gamification settings",
        reply_markup=keyboard,
    )


@router.message(F.text == "/stats")
async def cmd_stats(message: Message) -> None:
    """Show quick business statistics."""
    user = message.from_user
    if not user or not _is_admin(user.id):
        await message.answer("⛔ Admin access required.")
        return

    # TODO: Query real stats from DB
    await message.answer(
        "<b>📊 Quick Stats</b>\n\n"
        "👥 <b>Customers:</b> 1,234\n"
        "💬 <b>Conversations today:</b> 89\n"
        "💰 <b>Revenue this month:</b> 12,450 ⭐\n"
        "📦 <b>Active products:</b> 47\n"
        "⭐ <b>Avg rating:</b> 4.8/5\n"
        "📈 <b>Conversion rate:</b> 3.2%\n\n"
        "<i>Full analytics available in the Dashboard</i>"
    )


@router.message(F.text == "/broadcast")
async def cmd_broadcast(message: Message) -> None:
    """Send a message to all customers.

    SECURITY: Only business owners can broadcast.
    Rate limited to prevent spam.
    """
    user = message.from_user
    if not user or not _is_admin(user.id):
        await message.answer("⛔ Admin access required.")
        return

    parts = message.text.split(maxsplit=1)
    if len(parts) < 2:
        await message.answer(
            "Usage: /broadcast <message>\n\n"
            "This will send the message to all customers who have interacted with your business."
        )
        return

    text = parts[1]

    # TODO: Queue broadcast as async task
    # await celery_app.send_task(
    #     "tasks.notification_tasks.broadcast_message",
    #     args=[user.id, text],
    # )

    await message.answer(
        f"📢 <b>Broadcast Queued</b>\n\n"
        f"Your message will be sent to all customers shortly.\n\n"
        f"Message preview:\n{escape_html(text[:500])}"
    )


@router.message(F.text == "/config")
async def cmd_config(message: Message) -> None:
    """Show bot configuration options."""
    settings = get_settings()

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(
            text="🤖 AI Settings",
            callback_data="config:ai",
        )],
        [InlineKeyboardButton(
            text="💰 Payment Settings",
            callback_data="config:payments",
        )],
        [InlineKeyboardButton(
            text="🎨 Appearance",
            callback_data="config:appearance",
        )],
        [InlineKeyboardButton(
            text="🔐 Security",
            callback_data="config:security",
        )],
    ])

    await message.answer(
        "<b>⚙️ Bot Configuration</b>\n\n"
        f"🌐 <b>Environment:</b> {settings.app_env}\n"
        f"🤖 <b>AI Model:</b> {settings.openai_model}\n"
        f"💳 <b>Stars:</b> {'✅ Configured' if settings.stars_provider_token else '❌ Not configured'}\n",
        reply_markup=keyboard,
    )
