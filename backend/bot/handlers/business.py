"""Business Connection handlers — real DB integration.

Handles:
- Auto-reply to customer messages on behalf of business owner
- Conversation state machine (idle → active → escalated)
- Message routing to AI orchestrator
- Sentiment tracking
"""

import uuid

import structlog
from aiogram import F, Router
from aiogram.types import BusinessConnection, Message
from db.engine import get_session
from db.models.conversation import Conversation
from db.models.conversation import Message as MessageModel
from sqlalchemy import select

log = structlog.get_logger()
router = Router(name="business")


@router.business_connection()
async def handle_business_connection(connection: BusinessConnection) -> None:
    """Called when a business owner connects/disconnects their account.

    Store the business_connection_id for later use.
    """
    log.info(
        "business_connection_update",
        connection_id=connection.id,
        is_enabled=connection.is_enabled,
    )

    # TODO: Store/update business connection in DB
    # This fires when a business owner links their account to the bot


async def get_or_create_conversation(
    tenant_id,
    user_id: int,
    chat_id: int,
    business_conn_id: str | None = None,
) -> Conversation:
    """Get existing conversation or create a new one."""
    async with get_session(str(tenant_id)) as session:
        result = await session.execute(
            select(Conversation)
            .where(
                Conversation.tenant_id == tenant_id,
                Conversation.user_id == user_id,
                Conversation.chat_id == chat_id,
            )
            .order_by(Conversation.created_at.desc())
            .limit(1)
        )
        conversation = result.scalar_one_or_none()

        if conversation and conversation.state == "closed":
            conversation = None  # Create new conversation

        if not conversation:
            conversation = Conversation(
                id=uuid.uuid4(),
                tenant_id=tenant_id,
                user_id=user_id,
                chat_id=chat_id,
                business_conn_id=uuid.UUID(business_conn_id) if business_conn_id else None,
                state="active",
            )
            session.add(conversation)
            await session.commit()

        return conversation


async def save_message(
    session,
    conversation_id: uuid.UUID,
    tenant_id,
    role: str,
    content: str,
) -> None:
    """Persist a message to the conversation history."""
    msg = MessageModel(
        id=uuid.uuid4(),
        conversation_id=conversation_id,
        tenant_id=tenant_id,
        role=role,
        content=content,
    )
    session.add(msg)
    await session.commit()


@router.business_message(F.text)
async def handle_business_message(message: Message, **kwargs) -> None:
    """Handle a customer message sent to a connected business.

    Flow:
    1. Resolve conversation state
    2. Save user message
    3. Route to AI orchestrator (or simple reply for MVP)
    4. Save assistant response
    5. Send response as business
    """
    if not message.business_connection_id:
        return

    user = message.from_user
    tenant_id = kwargs.get("tenant_id")
    if not user or not tenant_id:
        return

    log.info(
        "business_message_received",
        connection_id=message.business_connection_id,
        customer_id=user.id,
        text_preview=(message.text or "")[:100],
    )

    # Get or create conversation
    conversation = await get_or_create_conversation(
        tenant_id=tenant_id,
        user_id=user.id,
        chat_id=message.chat.id,
        business_conn_id=message.business_connection_id,
    )

    # Save user message
    async with get_session(str(tenant_id)) as session:
        await save_message(
            session,
            conversation.id,
            tenant_id,
            "user",
            message.text or "",
        )

        # Update conversation stats
        conversation.message_count += 1
        conversation.last_message_at = message.date
        conversation.state = "active"
        await session.commit()

    # --- Generate response ---
    # For MVP: simple auto-reply
    # In production: route through AI orchestrator
    response = _generate_reply(user.first_name, message.text or "")

    # Save assistant response
    async with get_session(str(tenant_id)) as session:
        await save_message(
            session,
            conversation.id,
            tenant_id,
            "assistant",
            response,
        )

    # Send response as the business (not as the bot)
    await message.bot.send_message(
        chat_id=message.chat.id,
        text=response,
        business_connection_id=message.business_connection_id,
    )


@router.business_message(F.photo | F.document | F.voice | F.video)
async def handle_business_media(message: Message, **kwargs) -> None:
    """Handle non-text business messages (photos, documents, voice notes)."""
    if not message.business_connection_id:
        return

    user = message.from_user
    tenant_id = kwargs.get("tenant_id")
    if not user or not tenant_id:
        return

    content_type = message.content_type
    log.info(
        "business_media_received",
        connection_id=message.business_connection_id,
        content_type=content_type,
    )

    # Get/create conversation and save the media message
    conversation = await get_or_create_conversation(
        tenant_id=tenant_id,
        user_id=user.id,
        chat_id=message.chat.id,
        business_conn_id=message.business_connection_id,
    )

    async with get_session(str(tenant_id)) as session:
        await save_message(
            session,
            conversation.id,
            tenant_id,
            "user",
            f"[{content_type}]",
        )
        conversation.message_count += 1
        conversation.last_message_at = message.date
        await session.commit()

    # Queue for AI processing (placeholder)
    if content_type == "voice":
        response = "🎤 Voice message received! Transcription coming soon..."
    elif content_type == "photo":
        response = "📸 Photo received! Our AI is analyzing it..."
    else:
        response = f"📎 {content_type.title()} received. Processing..."

    await message.bot.send_message(
        chat_id=message.chat.id,
        text=response,
        business_connection_id=message.business_connection_id,
    )


def _generate_reply(first_name: str | None, user_text: str) -> str:
    """Generate a reply. MVP: simple pattern matching.

    In production: replaced by AI orchestrator.
    """
    name = (first_name or "there").split()[0]
    text_lower = user_text.lower()

    # Simple intent detection
    if any(w in text_lower for w in ["price", "cost", "how much"]):
        return f"Hi {name}! Our pricing starts at 100 ⭐/month for the Starter plan. Would you like to see details?"

    if any(w in text_lower for w in ["help", "support", "issue", "problem"]):
        return f"I'm here to help, {name}! Could you describe the issue in more detail?"

    if any(w in text_lower for w in ["hello", "hi", "hey"]):
        return f"Hello {name}! 👋 How can I assist you today?"

    if any(w in text_lower for w in ["bye", "thanks", "thank you"]):
        return f"You're welcome, {name}! Feel free to reach out anytime. 😊"

    return f"Thanks for your message, {name}! Our team will review it shortly. Is there anything specific I can help with?"
