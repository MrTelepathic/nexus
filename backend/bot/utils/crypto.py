"""Telegram Mini App initData validation.

Security-critical module. Handles:
1. HMAC-SHA-256 signature verification
2. Replay-attack prevention (nonce store in Redis)
3. Timestamp freshness check (≤24h)

Reference: https://core.telegram.org/bots/webapps#validating-data-received-via-the-mini-app
"""

import hashlib
import hmac
import time
from urllib.parse import parse_qs

import structlog
from redis.asyncio import Redis

log = structlog.get_logger()

# Telegram Bot API 8.0: initData is validated with HMAC-SHA-256
# using the bot token as the secret key
REPLAY_NONCE_TTL = 86400  # 24 hours — nonce validity window
INIT_DATA_MAX_AGE = 86400  # 24 hours — max age of initData


def _build_data_check_string(
    user_id: int,
    auth_date: int,
    query_id: str | None = None,
    chat_instance: str | None = None,
    chat_type: str | None = None,
    start_param: str | None = None,
    can_send_after: int | None = None,
    received_at: int | None = None,
) -> str:
    """Build the data_check_string from initData fields.

    Per Telegram docs: sort all key=value pairs except hash, join with \\n.
    """
    pairs = []
    if auth_date:
        pairs.append(("auth_date", str(auth_date)))
    if can_send_after is not None:
        pairs.append(("can_send_after", str(can_send_after)))
    if chat_instance:
        pairs.append(("chat_instance", chat_instance))
    if chat_type:
        pairs.append(("chat_type", chat_type))
    if query_id:
        pairs.append(("query_id", query_id))
    if received_at is not None:
        pairs.append(("received_at", str(received_at)))
    if start_param:
        pairs.append(("start_param", start_param))

    # user and receiver objects are serialized as JSON and included as keys
    pairs.sort(key=lambda x: x[0])
    return "\n".join(f"{k}={v}" for k, v in pairs)


def compute_hmac(bot_token: str, data_check_string: str) -> str:
    """Compute HMAC-SHA-256 secret key is the bot token, upper-cased."""
    secret_key = hmac.new(b"WebAppData", bot_token.encode(), hashlib.sha256).digest()
    return hmac.new(secret_key, data_check_string.encode(), hashlib.sha256).hexdigest()


def parse_init_data(init_data: str) -> dict[str, str]:
    """Parse the initData query string into a dict.

    Format: key1=value1&key2=value2&...&hash=abc123
    """
    parsed = parse_qs(init_data, keep_blank_values=True)
    return {k: v[0] if len(v) == 1 else v for k, v in parsed.items()}


async def validate_init_data(
    bot_token: str,
    init_data: str,
    redis: Redis,
) -> dict[str, str] | None:
    """Validate Telegram Mini App initData.

    Returns parsed data dict on success, None on failure.

    Security checks:
    1. HMAC-SHA-256 signature matches
    2. auth_date is within 24 hours
    3. No replay (nonce check via Redis)

    SECURITY: This is the single source of truth for Mini App auth.
    Every API request must pass through this validation.
    """
    try:
        data = parse_init_data(init_data)

        # --- Check 1: Signature ---
        hash_value = data.pop("hash", None)
        if not hash_value:
            log.warning("init_data_missing_hash")
            return None

        # Build the data_check_string from sorted key=value pairs
        # Telegram docs say to serialize user/receiver as JSON
        data_check_parts = []
        for key in sorted(data.keys()):
            if key == "user" or key == "receiver":
                # These are JSON objects — include as-is per Telegram spec
                data_check_parts.append(f"{key}={data[key]}")
            else:
                data_check_parts.append(f"{key}={data[key]}")

        data_check_string = "\n".join(data_check_parts)
        expected_hash = compute_hmac(bot_token, data_check_string)

        if not hmac.compare_digest(expected_hash, hash_value):
            log.warning("init_data_invalid_hash")
            return None

        # --- Check 2: Timestamp freshness ---
        auth_date = int(data.get("auth_date", 0))
        now = int(time.time())
        if now - auth_date > INIT_DATA_MAX_AGE:
            log.warning("init_data_expired", age=now - auth_date)
            return None

        # --- Check 3: Replay prevention ---
        # Create a unique nonce from auth_date + user data
        user_data = data.get("user", "")
        nonce_key = (
            f"init_data:nonce:{auth_date}:{hashlib.sha256(user_data.encode()).hexdigest()[:16]}"
        )

        # SETNX: returns True only if key didn't exist (first use)
        is_new = await redis.set(nonce_key, "1", ex=REPLAY_NONCE_TTL, nx=True)
        if not is_new:
            log.warning("init_data_replay_detected", auth_date=auth_date)
            return None

        return data

    except Exception as e:
        log.error("init_data_validation_error", error=str(e))
        return None
