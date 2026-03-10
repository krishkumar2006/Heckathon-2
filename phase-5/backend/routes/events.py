"""Dapr event subscription handlers for task and reminder events."""

import logging
from typing import Any

from fastapi import APIRouter, Request

logger = logging.getLogger(__name__)
router = APIRouter(tags=["events"])


@router.get("/dapr/subscribe")
async def dapr_subscribe():
    """
    Dapr subscription endpoint.
    Dapr calls this to discover which topics this service subscribes to.
    """
    return [
        {
            "pubsubname": "kafka-pubsub",
            "topic": "task-events",
            "route": "/api/events/task",
        },
        {
            "pubsubname": "kafka-pubsub",
            "topic": "reminders",
            "route": "/api/events/reminder",
        },
    ]


@router.post("/api/events/task")
async def handle_task_event(request: Request) -> dict[str, Any]:
    """
    Handle task lifecycle events from Kafka via Dapr Pub/Sub.

    Processes: task.created, task.updated, task.completed, task.deleted
    Used for: audit logging, recurring task processing
    """
    event = await request.json()
    event_type = event.get("event_type", "unknown")
    task_id = event.get("task_id")
    user_id = event.get("user_id")

    logger.info(
        "Received task event: type=%s, task_id=%s, user_id=%s",
        event_type, task_id, user_id,
    )

    # Process recurring tasks on completion
    if event_type == "task.completed":
        task_data = event.get("task_data", {})
        if task_data.get("is_recurring") and task_data.get("recurrence") != "none":
            logger.info(
                "Recurring task %s completed. Spawning next occurrence.", task_id
            )
            from services.recurring_service import spawn_next_occurrence

            new_task_id = await spawn_next_occurrence(task_data, user_id)
            if new_task_id:
                logger.info("Spawned new recurring task %d", new_task_id)

    return {"status": "SUCCESS"}


@router.post("/api/events/reminder")
async def handle_reminder_event(request: Request) -> dict[str, Any]:
    """
    Handle reminder events from Kafka via Dapr Pub/Sub.

    Fired when a scheduled reminder is due. Notifies the user.
    """
    event = await request.json()
    task_id = event.get("task_id")
    user_id = event.get("user_id")
    title = event.get("title", "")

    logger.info(
        "Received reminder event: task_id=%s, user_id=%s, title=%s",
        task_id, user_id, title,
    )

    # Push notification to user's SSE stream
    if user_id:
        from routes.notifications import push_notification

        await push_notification(user_id, {
            "type": "reminder",
            "task_id": task_id,
            "title": title or "Task reminder",
            "message": f"Reminder: {title or 'Your task'} is due soon!",
        })

    return {"status": "SUCCESS"}
