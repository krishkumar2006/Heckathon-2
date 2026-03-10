"""Event publisher service for Dapr Pub/Sub integration."""

import os
import logging
from datetime import datetime, timezone
from typing import Any

import httpx

logger = logging.getLogger(__name__)

DAPR_HTTP_PORT = os.getenv("DAPR_HTTP_PORT", "3500")
DAPR_BASE_URL = f"http://localhost:{DAPR_HTTP_PORT}"
PUBSUB_NAME = os.getenv("KAFKA_PUBSUB_NAME", "kafka-pubsub")


async def publish_event(
    topic: str,
    event_type: str,
    task_id: int,
    task_data: dict[str, Any],
    user_id: str,
) -> bool:
    """
    Publish an event to a Kafka topic via Dapr Pub/Sub.

    Args:
        topic: Kafka topic name (e.g., "task-events", "reminders")
        event_type: Event type (e.g., "task.created", "task.completed")
        task_id: The task ID related to this event
        task_data: Full task data snapshot
        user_id: The user who triggered the event

    Returns:
        True if published successfully, False otherwise
    """
    event_payload = {
        "event_type": event_type,
        "task_id": task_id,
        "task_data": task_data,
        "user_id": user_id,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }

    url = f"{DAPR_BASE_URL}/v1.0/publish/{PUBSUB_NAME}/{topic}"

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=event_payload)
            if response.status_code in (200, 204):
                logger.info(
                    "Published event %s to %s for task %d",
                    event_type, topic, task_id,
                )
                return True
            else:
                logger.warning(
                    "Failed to publish event %s: status %d, body %s",
                    event_type, response.status_code, response.text,
                )
                return False
    except httpx.ConnectError:
        logger.warning(
            "Dapr sidecar not available at %s. Event %s not published.",
            DAPR_BASE_URL, event_type,
        )
        return False
    except Exception as e:
        logger.error("Error publishing event %s: %s", event_type, str(e))
        return False


def task_to_event_data(task: Any) -> dict[str, Any]:
    """Convert a Task model instance to a serializable dict for events."""
    data: dict[str, Any] = {
        "id": task.id,
        "title": task.title,
        "description": task.description,
        "completed": task.completed,
        "priority": task.priority,
        "recurrence": task.recurrence,
        "is_recurring": task.is_recurring,
    }
    if task.due_date:
        data["due_date"] = task.due_date.isoformat()
    if task.reminder_offset_minutes is not None:
        data["reminder_offset_minutes"] = task.reminder_offset_minutes
    if hasattr(task, "created_at") and task.created_at:
        data["created_at"] = task.created_at.isoformat()
    return data
