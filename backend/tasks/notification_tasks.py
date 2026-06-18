"""Notification and scheduling tasks."""

from realtime.celery_app import celery_app


@celery_app.task
def broadcast_message(tenant_id: str, text: str, target: str = "all"):
    """Broadcast a message to all customers of a business.

    Targets: "all", "active" (interacted in last 30 days), "paying"
    """
    # TODO: Query users by target, send in batches
    return {"status": "ok"}


@celery_app.task
def send_scheduled_message(user_id: int, text: str):
    """Send a pre-scheduled message to a user."""
    # TODO: Send via bot.send_message
    return {"status": "ok"}


@celery_app.task
def check_unhappy_customers(tenant_id: str):
    """Detect unhappy customers via sentiment analysis and escalate.

    Runs periodically to catch negative sentiment before churn.
    """
    # TODO: Query conversations with low sentiment scores
    return {"status": "ok"}
