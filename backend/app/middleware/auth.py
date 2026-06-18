"""Authentication middleware for Mini App API routes.

Validates initData on every request and sets request state.
"""

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse

from bot.config import get_settings
from bot.utils.crypto import validate_init_data


class AuthMiddleware(BaseHTTPMiddleware):
    """Middleware that validates Telegram Mini App initData.

    Applied to all /api/v1/* routes.
    Sets request.state.user_id and request.state.tenant_id
    if authentication succeeds.

    SECURITY: initData is HMAC-SHA-256 validated.
    """

    async def dispatch(self, request: Request, call_next):
        settings = get_settings()

        # Skip auth for health check and docs
        if request.url.path in ("/health", "/docs", "/redoc", "/openapi.json"):
            return await call_next(request)

        # Extract initData from header or cookie
        init_data = (
            request.headers.get("X-Init-Data")
            or request.cookies.get("init_data")
        )

        if not init_data:
            return JSONResponse(
                status_code=401,
                content={"detail": "Missing authentication data"},
            )

        import json
        redis = request.app.state.redis
        result = await validate_init_data(
            bot_token=settings.bot_token_str,
            init_data=init_data,
            redis=redis,
        )

        if not result:
            return JSONResponse(
                status_code=401,
                content={"detail": "Invalid or expired authentication"},
            )

        # Set user context in request state
        user_data = json.loads(result.get("user", "{}"))
        request.state.user_id = user_data.get("id")
        request.state.tenant_id = None  # Resolved from user record

        response = await call_next(request)
        return response
