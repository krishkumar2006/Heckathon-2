"""Server-Sent Events endpoint for real-time reminder notifications."""

import asyncio
import logging
from typing import AsyncGenerator

from fastapi import APIRouter, Request
from fastapi.responses import StreamingResponse

logger = logging.getLogger(__name__)
router = APIRouter(tags=["notifications"])

# In-memory notification queues per user (user_id -> asyncio.Queue)
_notification_queues: dict[str, asyncio.Queue] = {}


def get_user_queue(user_id: str) -> asyncio.Queue:
    """Get or create a notification queue for a user."""
    if user_id not in _notification_queues:
        _notification_queues[user_id] = asyncio.Queue()
    return _notification_queues[user_id]


async def push_notification(user_id: str, data: dict) -> None:
    """Push a notification to a user's SSE queue."""
    queue = get_user_queue(user_id)
    await queue.put(data)
    logger.info("Pushed notification to user %s", user_id)


async def _event_stream(
    user_id: str, request: Request
) -> AsyncGenerator[str, None]:
    """Generate SSE events for a user."""
    queue = get_user_queue(user_id)

    # Send initial connection confirmation
    yield f"event: connected\ndata: {{\"user_id\": \"{user_id}\"}}\n\n"

    try:
        while True:
            # Check if client disconnected
            if await request.is_disconnected():
                break

            try:
                # Wait for notification with timeout (for keepalive)
                notification = await asyncio.wait_for(queue.get(), timeout=30.0)

                import json

                yield f"event: reminder\ndata: {json.dumps(notification)}\n\n"
            except asyncio.TimeoutError:
                # Send keepalive ping
                yield ": keepalive\n\n"
    finally:
        # Clean up queue if empty
        if user_id in _notification_queues and _notification_queues[user_id].empty():
            del _notification_queues[user_id]


@router.get("/api/notifications/{user_id}/sse")
async def sse_notifications(user_id: str, request: Request):
    """
    SSE endpoint for real-time reminder notifications.

    Clients connect to this endpoint and receive reminder events as they fire.
    Sends keepalive pings every 30 seconds to maintain the connection.
    """
    return StreamingResponse(
        _event_stream(user_id, request),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )
