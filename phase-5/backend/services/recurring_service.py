"""Recurring task service - spawns next occurrence when a recurring task completes."""

import logging
from datetime import datetime, timedelta, timezone
from typing import Any

from sqlmodel import Session

from db import get_engine
from models import Task, TaskTag

logger = logging.getLogger(__name__)

# Recurrence intervals
_INTERVALS = {
    "daily": timedelta(days=1),
    "weekly": timedelta(weeks=1),
    "monthly": timedelta(days=30),  # Approximation
}


async def spawn_next_occurrence(
    task_data: dict[str, Any], user_id: str
) -> int | None:
    """
    Create the next occurrence of a recurring task.

    Called when a recurring task is completed. Copies the task with
    a new due_date shifted by the recurrence interval.

    Args:
        task_data: The completed task's data
        user_id: The user who owns the task

    Returns:
        New task ID if created, None otherwise
    """
    recurrence = task_data.get("recurrence", "none")
    if recurrence == "none" or recurrence not in _INTERVALS:
        return None

    due_date_str = task_data.get("due_date")
    if not due_date_str:
        logger.warning("Recurring task has no due_date, cannot spawn next.")
        return None

    try:
        old_due_date = datetime.fromisoformat(due_date_str)
    except (ValueError, TypeError):
        logger.error("Invalid due_date format: %s", due_date_str)
        return None

    new_due_date = old_due_date + _INTERVALS[recurrence]

    # Ensure new due date is in the future
    now = datetime.now(timezone.utc)
    while new_due_date <= now:
        new_due_date += _INTERVALS[recurrence]

    with Session(get_engine()) as session:
        new_task = Task(
            user_id=user_id,
            title=task_data.get("title", "Recurring task"),
            description=task_data.get("description", ""),
            completed=False,
            priority=task_data.get("priority", "medium"),
            due_date=new_due_date,
            reminder_offset_minutes=task_data.get("reminder_offset_minutes"),
            recurrence=recurrence,
            is_recurring=True,
        )
        session.add(new_task)
        session.commit()
        session.refresh(new_task)

        logger.info(
            "Spawned recurring task %d (next due: %s) from completed task",
            new_task.id,
            new_due_date.isoformat(),
        )

        return new_task.id
