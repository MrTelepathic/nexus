"""LLM response streaming via progressive message editing.

Telegram doesn't support SSE, so we simulate streaming by:
1. Send initial message with "typing..." indicator
2. Edit the message every ~500ms with accumulated text
3. Final edit with complete response

This gives users the illusion of real-time streaming.
"""

import asyncio
from typing import AsyncGenerator

import structlog

log = structlog.get_logger()

# Telegram API limits
MAX_MESSAGE_LENGTH = 4096
EDIT_THROTTLE_MS = 500  # Minimum ms between edits


async def stream_response(
    bot,
    chat_id: int,
    message_id: int | None,
    response_gen: AsyncGenerator[str, None],
) -> str:
    """Stream an LLM response by progressively editing a Telegram message.

    Args:
        bot: aiogram Bot instance
        chat_id: Target chat
        message_id: Existing message to edit (or None to create new)
        response_gen: Async generator yielding text chunks

    Returns:
        The complete response text.
    """
    accumulated = ""
    last_edit_time = 0

    # Send initial message if no message_id provided
    if message_id is None:
        msg = await bot.send_message(chat_id=chat_id, text="...")
        message_id = msg.message_id

    try:
        async for chunk in response_gen:
            accumulated += chunk

            # Throttle edits to avoid Telegram rate limits
            now = asyncio.get_event_loop().time() * 1000
            if now - last_edit_time < EDIT_THROTTLE_MS:
                continue

            # Truncate for display
            display_text = accumulated[:MAX_MESSAGE_LENGTH]
            if len(accumulated) > MAX_MESSAGE_LENGTH:
                display_text += "..."

            try:
                await bot.edit_message_text(
                    chat_id=chat_id,
                    message_id=message_id,
                    text=display_text,
                )
                last_edit_time = now
            except Exception as e:
                # Message might not have changed, or rate limited
                log.debug("edit_throttled", error=str(e))

    except Exception as e:
        log.error("stream_error", error=str(e))

    # Final edit with complete response
    final_text = accumulated[:MAX_MESSAGE_LENGTH]
    if len(accumulated) > MAX_MESSAGE_LENGTH:
        final_text += "\n\n_(response truncated)_"

    try:
        await bot.edit_message_text(
            chat_id=chat_id,
            message_id=message_id,
            text=final_text,
        )
    except Exception:
        pass

    return accumulated
