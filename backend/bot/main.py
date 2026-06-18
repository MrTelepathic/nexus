"""Nexus Bot Service — aiogram 3 entry point.

Sets up:
- Dispatcher with FSM storage (Redis-backed)
- Middleware chain (tenant, rate-limit, logging)
- Router registration
- Webhook / polling lifecycle
"""

import asyncio
import logging
import sys
from os import getenv

import structlog
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.redis import RedisStorage
from bot.config import get_settings
from bot.handlers import admin, business, inline, payments, start
from bot.middleware.logging import LoggingMiddleware
from bot.middleware.rate_limit import RateLimitMiddleware
from bot.middleware.tenant import TenantMiddleware

log = structlog.get_logger()


async def create_bot() -> Bot:
    settings = get_settings()
    return Bot(
        token=settings.bot_token_str,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )


async def create_dispatcher(bot: Bot) -> Dispatcher:
    settings = get_settings()

    storage = RedisStorage.from_url(settings.redis_url)
    dp = Dispatcher(storage=storage)

    # --- Middleware (executed in reverse order of registration) ---
    dp.message.middleware(LoggingMiddleware())
    dp.message.middleware(RateLimitMiddleware(redis_url=settings.redis_url))
    dp.message.middleware(TenantMiddleware())

    dp.callback_query.middleware(LoggingMiddleware())
    dp.callback_query.middleware(RateLimitMiddleware(redis_url=settings.redis_url))
    dp.callback_query.middleware(TenantMiddleware())

    # --- Router registration ---
    dp.include_routers(
        start.router,
        payments.router,
        business.router,
        inline.router,
        admin.router,
    )

    return dp


async def on_startup(bot: Bot) -> None:
    """Run on bot startup: set commands, register webhook."""
    settings = get_settings()
    log.info("nexus_bot_starting", env=settings.app_env)

    from aiogram.types import BotCommand

    await bot.set_my_commands(
        [
            BotCommand(command="start", description="Start Nexus"),
            BotCommand(command="help", description="Get help"),
            BotCommand(command="dashboard", description="Open business dashboard"),
            BotCommand(command="settings", description="Bot settings"),
        ]
    )

    if settings.bot_webhook_url:
        await bot.set_webhook(
            url=f"{settings.bot_webhook_url}/bot/webhook",
            secret_token=settings.bot_webhook_secret_token,
            allowed_updates=[
                "message",
                "callback_query",
                "inline_query",
                "pre_checkout_query",
                "business_connection",
                "business_message",
            ],
        )
        log.info("webhook_set", url=settings.bot_webhook_url)
    else:
        log.info("running_in_polling_mode")


async def on_shutdown(bot: Bot) -> None:
    log.info("nexus_bot_shutting_down")
    await bot.delete_webhook()
    await bot.session.close()


async def main() -> None:
    logging.basicConfig(
        level=getenv("APP_LOG_LEVEL", "INFO"),
        format="%(message)s",
        stream=sys.stdout,
    )
    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.processors.add_log_level,
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.dev.ConsoleRenderer()
            if getenv("APP_ENV") != "production"
            else structlog.processors.JSONRenderer(),
        ],
    )

    bot = await create_bot()
    dp = await create_dispatcher(bot)

    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)

    try:
        if get_settings().bot_webhook_url:
            # Production: webhook mode (uvicorn serves the webhook endpoint)
            import uvicorn
            from app.main import create_fastapi_app

            app = create_fastapi_app(bot, dp)
            config = uvicorn.Config(
                app,
                host="0.0.0.0",
                port=8000,
                log_level=getenv("APP_LOG_LEVEL", "info").lower(),
            )
            server = uvicorn.Server(config)
            await server.serve()
        else:
            # Development: polling mode
            await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())
    finally:
        await on_shutdown(bot)


if __name__ == "__main__":
    asyncio.run(main())
