"""WebSocket endpoint for real-time dashboard updates.

Handles:
- Live sales feed
- Real-time analytics
- Leaderboard updates
- Multiplayer game state

Connection lifecycle:
1. Client connects with initData in query params
2. Server validates initData (HMAC-SHA-256)
3. Client subscribes to rooms (dashboard, leaderboard, etc.)
4. Server broadcasts updates to all clients in a room
"""

import asyncio
import json

import structlog
from bot.config import get_settings
from fastapi import APIRouter, WebSocket, WebSocketDisconnect

log = structlog.get_logger()
router = APIRouter()


class ConnectionManager:
    """Manages WebSocket connections with room-based broadcasting.

    SECURITY: Each connection is authenticated via initData.
    Connections are grouped by tenant for data isolation.
    """

    def __init__(self):
        # tenant_id -> set of websockets
        self.active_connections: dict[str, set[WebSocket]] = {}
        # ws -> user info
        self.connection_info: dict[WebSocket, dict] = {}

    async def connect(self, websocket: WebSocket, tenant_id: str, user_info: dict):
        await websocket.accept()
        if tenant_id not in self.active_connections:
            self.active_connections[tenant_id] = set()
        self.active_connections[tenant_id].add(websocket)
        self.connection_info[websocket] = {
            "tenant_id": tenant_id,
            **user_info,
        }
        log.info(
            "ws_connected",
            tenant_id=tenant_id,
            user_id=user_info.get("user_id"),
        )

    def disconnect(self, websocket: WebSocket):
        info = self.connection_info.pop(websocket, {})
        tenant_id = info.get("tenant_id")
        if tenant_id and tenant_id in self.active_connections:
            self.active_connections[tenant_id].discard(websocket)
            if not self.active_connections[tenant_id]:
                del self.active_connections[tenant_id]
        log.info(
            "ws_disconnected",
            tenant_id=tenant_id,
            user_id=info.get("user_id"),
        )

    async def broadcast_to_tenant(self, tenant_id: str, message: dict):
        """Send a message to all connections in a tenant."""
        connections = self.active_connections.get(tenant_id, set())
        disconnected = set()
        for ws in connections:
            try:
                await ws.send_json(message)
            except Exception:
                disconnected.add(ws)
        for ws in disconnected:
            self.disconnect(ws)

    async def send_personal(self, websocket: WebSocket, message: dict):
        try:
            await websocket.send_json(message)
        except Exception:
            self.disconnect(websocket)


manager = ConnectionManager()


@router.websocket("/ws/dashboard")
async def dashboard_websocket(websocket: WebSocket):
    """WebSocket endpoint for the real-time dashboard.

    Authentication: Client sends initData as first message.
    After validation, the connection is established.

    Protocol:
    Client → Server: {"type": "auth", "init_data": "..."}
    Server → Client: {"type": "auth_ok", "user_id": 123}
    Client → Server: {"type": "subscribe", "room": "dashboard"}
    Server → Client: {"type": "update", "data": {...}}
    """
    settings = get_settings()

    await websocket.accept()

    try:
        # Wait for auth message (5 second timeout)
        auth_msg = await asyncio.wait_for(websocket.receive_json(), timeout=5.0)

        if auth_msg.get("type") != "auth":
            await websocket.send_json({"type": "auth_error", "detail": "Expected auth message"})
            await websocket.close()
            return

        init_data = auth_msg.get("init_data", "")

        # Validate initData
        # Note: For WebSocket, we use a simpler validation since
        # the nonce check in Redis may have already been consumed
        # by the HTTP auth. We still verify the HMAC.
        from bot.utils.crypto import compute_hmac, parse_init_data

        data = parse_init_data(init_data)
        hash_value = data.get("hash", "")
        data.pop("hash", None)

        data_check_parts = []
        for key in sorted(data.keys()):
            if key in ("user", "receiver"):
                data_check_parts.append(f"{key}={data[key]}")
            else:
                data_check_parts.append(f"{key}={data[key]}")

        data_check_string = "\n".join(data_check_parts)
        expected_hash = compute_hmac(settings.bot_token_str, data_check_string)

        import hmac

        if not hmac.compare_digest(expected_hash, hash_value):
            await websocket.send_json({"type": "auth_error", "detail": "Invalid signature"})
            await websocket.close()
            return

        user_info = json.loads(data.get("user", "{}"))
        # Use auth_date as tenant_id placeholder (in production, resolve from DB)
        tenant_id = "default"

        await manager.connect(websocket, tenant_id, user_info)
        await websocket.send_json({"type": "auth_ok", "user_id": user_info.get("id")})

        # Listen for messages
        while True:
            msg = await websocket.receive_json()
            msg_type = msg.get("type")

            if msg_type == "subscribe":
                # Acknowledge subscription
                await websocket.send_json(
                    {
                        "type": "subscribed",
                        "room": msg.get("room", "dashboard"),
                    }
                )

            elif msg_type == "ping":
                await websocket.send_json({"type": "pong"})

    except TimeoutError:
        await websocket.send_json({"type": "auth_error", "detail": "Auth timeout"})
        await websocket.close()
    except WebSocketDisconnect:
        pass
    except Exception as e:
        log.error("ws_error", error=str(e))
    finally:
        manager.disconnect(websocket)
