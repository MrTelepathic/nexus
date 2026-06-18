"""AI-related async tasks."""

from realtime.celery_app import celery_app


@celery_app.task(bind=True, max_retries=3, default_retry_delay=60)
def process_ai_message(self, tenant_id: str, user_id: int, conversation_id: str, message: str):
    """Process a user message through the AI orchestrator.

    Runs asynchronously to avoid blocking the bot's webhook response.
    """
    import asyncio

    from ai.orchestrator import process_message

    loop = asyncio.new_event_loop()
    try:
        response = loop.run_until_complete(
            process_message(tenant_id, user_id, conversation_id, message)
        )
        # TODO: Send response back via bot.send_message
        return {"status": "ok", "response": response}
    except Exception as exc:
        self.retry(exc=exc)
    finally:
        loop.close()


@celery_app.task
def transcribe_voice(file_id: str, user_id: int):
    """Transcribe a voice note using Whisper."""
    # TODO: Download file, run Whisper, return transcription
    return {"status": "pending"}


@celery_app.task
def analyze_image(file_id: str, user_id: int):
    """Analyze an image using a vision model."""
    # TODO: Download file, run vision model, return description
    return {"status": "pending"}
