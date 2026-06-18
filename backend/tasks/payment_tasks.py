"""Payment-related async tasks."""

from realtime.celery_app import celery_app


@celery_app.task
def reconcile_payments():
    """Periodic task to reconcile payment records with provider APIs.

    Runs every 15 minutes to catch missed webhooks.
    """
    # TODO: Compare local payment records with Telegram/TON API
    return {"status": "ok"}


@celery_app.task
def process_ton_payment(tx_hash: str):
    """Verify and process a TON blockchain payment.

    SECURITY: Idempotency checked before processing.
    """
    # TODO: Query TON node RPC, verify tx, update payment record
    return {"status": "pending"}


@celery_app.task
def send_refund(user_id: int, payment_charge_id: str):
    """Process a refund via Telegram Stars API."""
    # TODO: Call refund_star_payment, update records
    return {"status": "pending"}
