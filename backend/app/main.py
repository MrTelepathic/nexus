"""FastAPI Mini App Backend.

Serves:
- REST API for the Mini App (products, orders, dashboard, wallet)
- WebSocket endpoint for real-time dashboard updates
- Webhook endpoint for Telegram bot updates

Separate from the bot service for independent scaling.
The bot service can run in polling mode (dev) or share this
uvicorn process (prod) via the webhook endpoint.
"""

import time
from contextlib import asynccontextmanager

import structlog
from bot.config import get_settings
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

log = structlog.get_logger()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application startup/shutdown lifecycle."""
    settings = get_settings()
    log.info("fastapi_starting", env=settings.app_env)

    # Initialize database
    from db.engine import close_db, init_db

    await init_db()

    # Initialize Redis
    import redis.asyncio as aioredis

    app.state.redis = aioredis.from_url(settings.redis_url, decode_responses=True)

    log.info("fastapi_ready")
    yield

    # Shutdown
    await close_db()
    await app.state.redis.close()
    log.info("fastapi_shutdown")


def create_fastapi_app(bot=None, dispatcher=None) -> FastAPI:
    """Create and configure the FastAPI application.

    Args:
        bot: aiogram Bot instance (optional, for shared-process mode)
        dispatcher: aiogram Dispatcher (optional, for shared-process mode)
    """
    settings = get_settings()

    app = FastAPI(
        title="Nexus API",
        description="Nexus Platform — Mini App Backend",
        version="0.1.0",
        docs_url="/docs" if not settings.is_production else None,
        redoc_url="/redoc" if not settings.is_production else None,
        lifespan=lifespan,
    )

    # --- CORS ---
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[
            "https://*.telegram.org",  # Telegram Mini Apps
            settings.mini_app_url,
        ],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # --- Request timing middleware ---
    @app.middleware("http")
    async def timing_middleware(request: Request, call_next):
        start = time.perf_counter()
        response = await call_next(request)
        elapsed_ms = round((time.perf_counter() - start) * 1000, 2)
        response.headers["X-Process-Time"] = str(elapsed_ms)
        log.info(
            "api_request",
            method=request.method,
            path=request.url.path,
            status=response.status_code,
            elapsed_ms=elapsed_ms,
        )
        return response

    # --- Global exception handler ---
    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception):
        log.error("unhandled_exception", path=request.url.path, exc_info=True)
        return JSONResponse(
            status_code=500,
            content={"detail": "Internal server error"},
        )

    # --- Health check ---
    @app.get("/health")
    async def health_check():
        return {"status": "ok", "service": "nexus-api"}

    # --- Import and register API routers ---
    from app.api.v1.router import api_router

    app.include_router(api_router, prefix="/api/v1")

    # --- WebSocket for real-time dashboard ---
    from app.api.ws.dashboard import router as ws_router

    app.include_router(ws_router)

    # --- Telegram webhook endpoint (shared-process mode) ---
    if bot and dispatcher:

        async def webhook_handler(request: Request):
            """Handle incoming Telegram updates via webhook."""
            data = await request.json()
            # Manually dispatch through aiogram
            from aiogram import types

            update = types.Update.model_validate(data)
            await dispatcher.feed_update(bot, update)
            return JSONResponse({"ok": True})

        app.add_api_route(
            "/bot/webhook",
            webhook_handler,
            methods=["POST"],
            include_in_schema=False,
        )

    return app


# --- Standalone entry point (for uvicorn) ---
app = create_fastapi_app()
