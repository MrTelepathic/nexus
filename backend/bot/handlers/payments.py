"""Telegram Stars payment flow — DB-backed with idempotency.

Complete payment lifecycle:
1. User triggers purchase → Bot sends invoice
2. Telegram sends pre_checkout_query → Bot confirms
3. Telegram sends successful_payment → Process + update DB
4. On dispute/refund → Handle refund via Telegram API

SECURITY: Idempotency enforced via idempotency_key in DB.
Each payment is processed exactly once via ON CONFLICT.
"""

import uuid

import structlog
from aiogram import F, Router
from aiogram.types import (
    ContentType,
    LabeledPrice,
    Message,
    PreCheckoutQuery,
    SuccessfulPayment,
)
from bot.config import get_settings
from bot.utils.formatters import escape_html, format_amount
from db.engine import get_session
from sqlalchemy import select, text

log = structlog.get_logger()
router = Router(name="payments")


# --- Price catalog (loaded from DB in production) ---
PRODUCT_CATALOG = {
    "starter_monthly": {
        "title": "Nexus Starter Plan",
        "description": "Monthly subscription — AI assistant + CRM + 100 products",
        "price": 100,
        "currency": "XTR",
        "period": "monthly",
    },
    "pro_monthly": {
        "title": "Nexus Pro Plan",
        "description": "Monthly subscription — Full AI + unlimited products + analytics",
        "price": 500,
        "currency": "XTR",
        "period": "monthly",
    },
    "pro_yearly": {
        "title": "Nexus Pro Plan (Yearly)",
        "description": "Yearly subscription — Save 20%! Full platform access",
        "price": 4800,
        "currency": "XTR",
        "period": "yearly",
    },
    "stars_100": {
        "title": "100 Nexus Stars",
        "description": "Premium currency for in-app purchases and rewards",
        "price": 100,
        "currency": "XTR",
        "period": None,
    },
}


@router.message(F.text == "/buy")
async def cmd_buy(message: Message, **kwargs) -> None:
    """Show available products for purchase."""
    from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=f"⭐ {item['title']} — {item['price']} Stars",
                    callback_data=f"buy:{product_id}",
                )
            ]
            for product_id, item in PRODUCT_CATALOG.items()
        ]
    )

    await message.answer(
        "<b>Nexus Store</b> 🛒\n\nChoose a product or subscription:",
        reply_markup=keyboard,
    )


@router.callback_query(F.data.startswith("buy:"))
async def handle_buy_callback(callback_query, **kwargs) -> None:
    """Initiate a Star invoice for the selected product."""
    product_id = callback_query.data.split(":", 1)[1]
    product = PRODUCT_CATALOG.get(product_id)

    if not product:
        await callback_query.answer("Product not found.", show_alert=True)
        return

    settings = get_settings()

    idempotency_key = str(uuid.uuid4())

    prices = [LabeledPrice(label=product["title"], amount=product["price"])]

    await callback_query.message.answer_invoice(
        title=product["title"],
        description=product["description"],
        payload=f"{product_id}:{idempotency_key}",
        provider_token=settings.stars_provider_token or "",
        currency=product["currency"],
        prices=prices,
        subscription_period=2592000 if product.get("period") == "monthly" else None,
        need_email=True,
        send_email_to_provider=True,
    )
    await callback_query.answer()


@router.pre_checkout_query()
async def handle_pre_checkout(pre_checkout_query: PreCheckoutQuery) -> None:
    """Validate BEFORE charging the user.

    SECURITY: Always answer within 10 seconds or Telegram auto-declines.
    """
    payload = pre_checkout_query.invoice_payload
    parts = payload.split(":", 1)
    product_id = parts[0]
    idempotency_key = parts[1] if len(parts) > 1 else None

    product = PRODUCT_CATALOG.get(product_id)

    if not product:
        await pre_checkout_query.answer(ok=False, error_message="Product not found.")
        return

    if pre_checkout_query.total_amount != product["price"]:
        log.warning(
            "price_mismatch",
            expected=product["price"],
            received=pre_checkout_query.total_amount,
        )
        await pre_checkout_query.answer(ok=False, error_message="Price mismatch.")
        return

    # Check idempotency — reject if already processed
    if idempotency_key:
        async with get_session() as session:
            result = await session.execute(
                select(text("1"))
                .select_from(text("payments"))
                .where(text(f"idempotency_key = '{idempotency_key}'"))
            )
            if result.scalar_one_or_none():
                log.warning("payment_already_processed", key=idempotency_key)
                await pre_checkout_query.answer(
                    ok=False, error_message="Payment already processed."
                )
                return

    log.info(
        "pre_checkout_approved",
        user_id=pre_checkout_query.from_user.id,
        product_id=product_id,
    )
    await pre_checkout_query.answer(ok=True)


@router.message(F.content_type == ContentType.SUCCESSFUL_PAYMENT)
async def handle_successful_payment(message: Message, **kwargs) -> None:
    """Process the completed transaction — idempotent.

    SECURITY: Same payment_id processed twice = no double-grant.
    """
    payment: SuccessfulPayment = message.successful_payment
    user = message.from_user
    tenant_id = kwargs.get("tenant_id")
    if not user:
        return

    payload = payment.invoice_payload
    parts = payload.split(":", 1)
    product_id = parts[0]
    idempotency_key = parts[1] if len(parts) > 1 else str(uuid.uuid4())

    product = PRODUCT_CATALOG.get(product_id)

    log.info(
        "payment_completed",
        user_id=user.id,
        product_id=product_id,
        amount=payment.total_amount,
        currency=payment.currency,
        telegram_payment_id=payment.telegram_payment_charge_id,
    )

    # --- Idempotent DB insert ---
    if tenant_id:
        async with get_session(str(tenant_id)) as session:
            # Use raw SQL for ON CONFLICT — the ORM doesn't handle this cleanly
            await session.execute(
                text("""
                    INSERT INTO payments (
                        id, tenant_id, user_id, amount, currency, method,
                        status, external_id, idempotency_key, provider_metadata
                    ) VALUES (
                        uuid_generate_v4(), :tenant_id, :user_id, :amount, :currency, 'stars',
                        'completed', :external_id, :idempotency_key, :metadata
                    )
                    ON CONFLICT (idempotency_key) DO NOTHING
                """),
                {
                    "tenant_id": str(tenant_id),
                    "user_id": user.id,
                    "amount": float(payment.total_amount),
                    "currency": payment.currency,
                    "external_id": payment.telegram_payment_charge_id,
                    "idempotency_key": idempotency_key,
                    "metadata": str(payment.model_dump_json()),
                },
            )
            await session.commit()

            # Update user LTV
            await session.execute(
                text("""
                    UPDATE users SET ltv = ltv + :amount
                    WHERE id = :user_id AND tenant_id = :tenant_id
                """),
                {
                    "amount": float(payment.total_amount),
                    "user_id": user.id,
                    "tenant_id": str(tenant_id),
                },
            )
            await session.commit()

    # --- Send receipt ---
    name = escape_html(user.first_name or "User")
    product_title = product["title"] if product else product_id
    await message.answer(
        f"✅ <b>Payment Successful!</b>\n\n"
        f"Thank you, {name}!\n\n"
        f"📦 <b>Product:</b> {escape_html(str(product_title))}\n"
        f"💰 <b>Amount:</b> {format_amount(payment.total_amount, payment.currency)}\n"
        f"🧾 <b>Payment ID:</b> <code>{payment.telegram_payment_charge_id}</code>\n\n"
        f"Your access has been activated. Enjoy Nexus! 🚀"
    )


@router.message(F.text.startswith("/refund"))
async def cmd_refund(message: Message) -> None:
    """Process a refund via Telegram Stars API."""
    parts = message.text.split()
    if len(parts) < 2:
        await message.answer("Usage: /refund <payment_charge_id>")
        return

    payment_charge_id = parts[1]
    bot = message.bot
    if not bot:
        return

    try:
        result = await bot.refund_star_payment(
            user_id=message.from_user.id,
            telegram_payment_charge_id=payment_charge_id,
        )

        if result:
            log.info(
                "refund_processed",
                user_id=message.from_user.id,
                payment_charge_id=payment_charge_id,
            )
            await message.answer(
                f"✅ Refund processed for payment <code>{payment_charge_id}</code>."
            )
        else:
            await message.answer("❌ Refund failed. Payment may not be eligible.")

    except Exception as e:
        log.error("refund_error", error=str(e))
        await message.answer(f"❌ Refund error: {escape_html(str(e))}")
