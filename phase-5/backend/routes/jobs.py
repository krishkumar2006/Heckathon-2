"""Dapr Jobs API callback handler for scheduled reminders."""

import logging
from typing import Any

from fastapi import APIRouter, Request

from services.event_publisher import publish_event

logger = logging.getLogger(__name__)
router = APIRouter(tags=["jobs"])


@router.post("/api/jobs/trigger")
async def handle_job_trigger(request: Request) -> dict[str, Any]:
    """
    Dapr Jobs API callback endpoint.

    Dapr calls this at the exact scheduled time for reminder jobs.
    The handler publishes a reminder event to the reminders topic.
    """
    job_data = await request.json()
    data = job_data.get("data", {})

    if data.get("type") == "reminder":
        task_id = data.get("task_id")
        user_id = data.get("user_id")

        logger.info(
            "Reminder job fired for task_id=%s, user_id=%s", task_id, user_id
        )

        # Publish reminder event to reminders topic
        await publish_event(
            topic="reminders",
            event_type="reminder.due",
            task_id=task_id,
            task_data=data,
            user_id=user_id,
        )

        return {"status": "SUCCESS"}

    logger.warning("Unknown job type received: %s", data.get("type"))
    return {"status": "SUCCESS"}
