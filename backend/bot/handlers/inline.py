"""Inline mode handler.

Allows users to search and share products/content in ANY chat
by typing @nexusbot <query> in the message input.

Features:
- Product search with instant results
- Article-style results with rich formatting
- Direct purchase links back to Mini App
"""

import structlog
from aiogram import Router
from aiogram.enums import InlineQueryResultType
from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    InlineQuery,
    InlineQueryResultArticle,
    InputTextMessageContent,
)
from bot.config import get_settings
from bot.utils.formatters import escape_html

log = structlog.get_logger()
router = Router(name="inline")


@router.inline_query()
async def handle_inline_query(inline_query: InlineQuery) -> None:
    """Handle @bot <query> inline searches.

    Search products by name/description and return inline results.
    Users can tap a result to send it to any chat.
    """
    query = inline_query.query.strip()
    user = inline_query.from_user
    if not user:
        return

    settings = get_settings()

    # TODO: Search products from DB
    # products = await search_products(query, limit=10)

    # Placeholder results for MVP
    results = []

    if not query:
        # Show featured/trending products when query is empty
        results.append(
            InlineQueryResultArticle(
                id="featured_1",
                type=InlineQueryResultType.ARTICLE,
                title="Nexus Starter Plan",
                description="AI business assistant — 100 Stars/month",
                input_message_content=InputTextMessageContent(
                    message_text=(
                        "🚀 <b>Nexus Starter Plan</b>\n\n"
                        "AI-powered business assistant for Telegram.\n"
                        "• Auto-reply to customers\n"
                        "• CRM & analytics\n"
                        "• 100 product listings\n\n"
                        "Just 100 ⭐/month!"
                    ),
                    parse_mode="HTML",
                ),
                reply_markup=InlineKeyboardMarkup(
                    inline_keyboard=[
                        [
                            InlineKeyboardButton(
                                text="🛒 Get Started",
                                web_app={
                                    "url": f"{settings.mini_app_url}/products/starter_monthly"
                                },
                            )
                        ],
                    ]
                ),
            )
        )
    else:
        # Search products by query
        # For MVP, return a search result
        results.append(
            InlineQueryResultArticle(
                id=f"search_{query[:20]}",
                type=InlineQueryResultType.ARTICLE,
                title=f"Search: {escape_html(query)}",
                description=f"Find '{escape_html(query)}' in Nexus marketplace",
                input_message_content=InputTextMessageContent(
                    message_text=f"🔍 Searching for <b>{escape_html(query)}</b> in Nexus...",
                    parse_mode="HTML",
                ),
                reply_markup=InlineKeyboardMarkup(
                    inline_keyboard=[
                        [
                            InlineKeyboardButton(
                                text="🔍 View Results",
                                web_app={"url": f"{settings.mini_app_url}/search?q={query}"},
                            )
                        ],
                    ]
                ),
            )
        )

    # Inline query has a 3-second timeout — return quickly
    await inline_query.answer(
        results=results[:10],  # Telegram allows max 50, we cap at 10
        cache_time=300,  # Cache results for 5 minutes
        is_personal=True,  # Results personalized per user
    )
