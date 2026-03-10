"""Reminder service using Dapr Jobs API for scheduling reminders."""

import os
import logging
from datetime import datetime, timezone, timedelta
from typing import Any

import httpx

logger = logging.getLogger(__name__)

DAPR_HTTP_PORT = os.getenv("DAPR_HTTP_PORT", "3500")
DAPR_BASE_URL = f"http://localhost:{DAPR_HTTP_PORT}"


async def schedule_reminder(
    task_id: int,
    user_id: str,
    due_date: datetime,
    offset_minutes: int,
) -> bool:
    """
    Schedule a reminder via Dapr Jobs API.

    The reminder fires at (due_date - offset_minutes). Dapr calls back
    to POST /api/jobs/trigger at the scheduled time.

    Args:
        task_id: The task to remind about
        user_id: The user to notify
        due_date: When the task is due
        offset_minutes: Minutes before due_date to fire reminder

    Returns:
        True if scheduled successfully, False otherwise
    """
    reminder_time = due_date - timedelta(minutes=offset_minutes)

    # If reminder time is in the past, skip scheduling
    if reminder_time <= datetime.now(timezone.utc):
        logger.warning(
            "Reminder time for task %d is in the past, skipping.", task_id
        )
        return False

    job_name = f"reminder-task-{task_id}"
    url = f"{DAPR_BASE_URL}/v1.0-alpha1/jobs/{job_name}"

    job_payload: dict[str, Any] = {
        "schedule": f"@at {reminder_time.isoformat()}",
        "data": {
            "type": "reminder",
            "task_id": task_id,
            "user_id": user_id,
            "due_date": due_date.isoformat(),
            "title": "",
        },
    }

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=job_payload, timeout=5.0)
            if response.status_code in (200, 204):
                logger.info(
                    "Scheduled reminder for task %d at %s",
                    task_id,
                    reminder_time.isoformat(),
                )
                return True
            else:
                logger.warning(
                    "Failed to schedule reminder: status %d, body %s",
                    response.status_code,
                    response.text,
                )
                return False
    except httpx.ConnectError:
        logger.warning(
            "Dapr sidecar not available at %s. Reminder not scheduled.",
            DAPR_BASE_URL,
        )
        return False
    except Exception as e:
        logger.error("Error scheduling reminder for task %d: %s", task_id, str(e))
        return False


async def cancel_reminder(task_id: int) -> bool:
    """
    Cancel a scheduled reminder via Dapr Jobs API.

    Args:
        task_id: The task whose reminder to cancel

    Returns:
        True if cancelled successfully (or already gone), False on error
    """
    job_name = f"reminder-task-{task_id}"
    url = f"{DAPR_BASE_URL}/v1.0-alpha1/jobs/{job_name}"

    try:
        async with httpx.AsyncClient() as client:
            response = await client.delete(url, timeout=5.0)
            if response.status_code in (200, 204, 404):
                logger.info("Cancelled reminder for task %d", task_id)
                return True
            else:
                logger.warning(
                    "Failed to cancel reminder: status %d", response.status_code
                )
                return False
    except httpx.ConnectError:
        logger.warning("Dapr sidecar not available. Cannot cancel reminder.")
        return False
    except Exception as e:
        logger.error("Error cancelling reminder for task %d: %s", task_id, str(e))
        return False
