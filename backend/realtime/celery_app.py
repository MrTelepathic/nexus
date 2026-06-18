"""Celery application for async task processing.

Handles:
- AI inference (LLM calls, RAG indexing)
- Payment reconciliation
- Scheduled notifications
- Analytics report generation
"""

from bot.config import get_settings
from celery import Celery

settings = get_settings()

celery_app = Celery(
    "nexus",
    broker=settings.rabbitmq_url,
    backend=settings.redis_url,
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_acks_late=True,  # Re-deliver on worker crash
    worker_prefetch_multiplier=1,  # Fair scheduling
    task_routes={
        "tasks.ai_tasks.*": {"queue": "ai"},
        "tasks.payment_tasks.*": {"queue": "payments"},
        "tasks.notification_tasks.*": {"queue": "notifications"},
        "tasks.analytics_tasks.*": {"queue": "analytics"},
    },
    task_default_queue="default",
)

celery_app.autodiscover_tasks(["tasks"])
