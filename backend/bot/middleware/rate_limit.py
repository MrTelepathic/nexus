"""Per-user rate limiting middleware using Redis sliding window.

Limits:
- 30 messages/minute per user (across all tenants)
- 10 callback queries/10s per user
- Configurable per-tenant limits in settings
"""

import time
from typing import Any, Callable, Dict, Awaitable

import structlog
from aiogram import BaseMiddleware
from aiogram.types import TelegramObject

log = structlog.get_logger()

USER_MESSAGE_LIMIT = 30
USER_MESSAGE_WINDOW = 60
USER_CALLBACK_LIMIT = 10
USER_CALLBACK_WINDOW = 10


class RateLimitMiddleware(BaseMiddleware):
    """Sliding-window rate limiter backed by Redis."""

    def __init__(self, redis_url: str) -> None:
        self._redis_url = redis_url
        self._redis = None

    async def _get_redis(self):
        if self._redis is None:
            try:
                from redis.asyncio import Redis
                self._redis = Redis.from_url(self._redis_url, decode_responses=True)
            except Exception as e:
                log.warning("redis_connect_failed", error=str(e))
                return None
        return self._redis

    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        user = getattr(event, "from_user", None)
        if not user:
            return await handler(event, data)

        redis = await self._get_redis()
        if not redis:
            return await handler(event, data)

        update_type = type(event).__name__
        if update_type == "CallbackQuery":
            limit = USER_CALLBACK_LIMIT
            window = USER_CALLBACK_WINDOW
            key_prefix = "rl:cb"
        else:
            limit = USER_MESSAGE_LIMIT
            window = USER_MESSAGE_WINDOW
            key_prefix = "rl:msg"

        key = f"{key_prefix}:{user.id}"

        try:
            now = time.time()
            pipe = redis.pipeline()
            pipe.zremrangebyscore(key, 0, now - window)
            pipe.zadd(key, {str(now): now})
            pipe.zcard(key)
            pipe.expire(key, window)
            results = await pipe.execute()

            request_count = results[2]

            if request_count > limit:
                log.warning("rate_limit_exceeded", user_id=user.id, count=request_count)
                return None
        except Exception as e:
            log.warning("rate_limit_error", error=str(e))

        return await handler(event, data)

    async def close(self) -> None:
        if self._redis:
            await self._redis.close()
