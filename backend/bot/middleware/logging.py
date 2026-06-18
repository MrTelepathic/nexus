"""Structured logging middleware for aiogram.

Logs every incoming update with user ID, chat ID, message type, and latency.
"""

import time
from collections.abc import Awaitable, Callable
from typing import Any

import structlog
from aiogram import BaseMiddleware
from aiogram.types import TelegramObject

log = structlog.get_logger()


class LoggingMiddleware(BaseMiddleware):
    """Logs all incoming updates with structured context."""

    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        start = time.perf_counter()
        user = getattr(event, "from_user", None)
        chat = getattr(event, "chat", None)

        structlog.contextvars.clear_contextvars()
        if user:
            structlog.contextvars.bind_contextvars(user_id=user.id)
            if user.username:
                structlog.contextvars.bind_contextvars(username=user.username)
        if chat:
            structlog.contextvars.bind_contextvars(chat_id=chat.id)

        structlog.contextvars.bind_contextvars(update_type=type(event).__name__)

        try:
            result = await handler(event, data)
            elapsed_ms = round((time.perf_counter() - start) * 1000, 2)
            log.info(
                "update_handled",
                elapsed_ms=elapsed_ms,
                handler=getattr(handler, "__name__", "unknown"),
            )
            return result
        except Exception:
            elapsed_ms = round((time.perf_counter() - start) * 1000, 2)
            log.error("update_handler_error", elapsed_ms=elapsed_ms, exc_info=True)
            raise
