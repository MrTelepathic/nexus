"""Message formatting utilities for Telegram bot."""

import html


def escape_html(text: str) -> str:
    """Escape HTML special characters for Telegram HTML parse mode."""
    return html.escape(text)


def format_amount(amount: float, currency: str = "XTR") -> str:
    """Format a monetary amount with currency symbol."""
    symbols = {"XTR": "⭐", "TON": "💎", "USD": "$", "IRR": "﷼"}
    symbol = symbols.get(currency, currency)
    if currency == "XTR":
        return f"{int(amount)} {symbol}"
    return f"{symbol}{amount:,.2f}"


def truncate(text: str, max_length: int = 4096) -> str:
    """Truncate text to Telegram's message length limit."""
    if len(text) <= max_length:
        return text
    return text[: max_length - 3] + "..."


def user_link(user_id: int, name: str | None = None) -> str:
    """Create a clickable t.me link for a user."""
    display = escape_html(name or str(user_id))
    return f'<a href="tg://user?id={user_id}">{display}</a>'
