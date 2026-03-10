"""Task CRUD routes for Todo API with priority, tags, and event publishing."""

from datetime import datetime
from typing import Annotated, Literal

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field
from sqlmodel import Session, select, or_

from db import get_session
from middleware.auth import CurrentUser
from models import Task, TaskTag
from services.event_publisher import publish_event, task_to_event_data
from services.reminder_service import schedule_reminder, cancel_reminder

router = APIRouter(prefix="/api/{user_id}/tasks", tags=["tasks"])


# --- Request/Response schemas ---

class TaskCreate(BaseModel):
    """Schema for creating a task."""

    title: str = Field(min_length=1, max_length=200)
    description: str = Field(default="", max_length=1000)
    priority: Literal["high", "medium", "low"] = Field(default="medium")
    due_date: datetime | None = Field(default=None)
    reminder_offset_minutes: int | None = Field(default=None)
    recurrence: Literal["none", "daily", "weekly", "monthly"] = Field(default="none")


class TaskUpdate(BaseModel):
    """Schema for updating a task."""

    title: str | None = Field(default=None, min_length=1, max_length=200)
    description: str | None = Field(default=None, max_length=1000)
    priority: Literal["high", "medium", "low"] | None = Field(default=None)
    due_date: datetime | None = Field(default=None)
    reminder_offset_minutes: int | None = Field(default=None)
    recurrence: Literal["none", "daily", "weekly", "monthly"] | None = Field(default=None)


class TagsRequest(BaseModel):
    """Schema for adding tags to a task."""

    tags: list[str] = Field(min_length=1)


class TaskResponse(BaseModel):
    """Schema for task response."""

    id: int
    user_id: str
    title: str
    description: str
    completed: bool
    priority: str
    due_date: datetime | None = None
    reminder_offset_minutes: int | None = None
    recurrence: str = "none"
    is_recurring: bool = False
    tags: list[str] = []
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


# --- Helpers ---

SessionDep = Annotated[Session, Depends(get_session)]


def verify_user_access(url_user_id: str, token_user_id: str) -> None:
    """Verify that URL user_id matches the authenticated user from JWT."""
    if url_user_id != token_user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied: user_id mismatch",
        )


def get_task_or_404(session: Session, user_id: str, task_id: int) -> Task:
    """Get task by id, ensuring it belongs to the user."""
    task = session.get(Task, task_id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found",
        )
    if task.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found",
        )
    return task


def _get_tags(session: Session, task_id: int) -> list[str]:
    """Fetch all tags for a given task."""
    stmt = select(TaskTag).where(TaskTag.task_id == task_id)
    return [t.tag for t in session.exec(stmt).all()]


def _build_task_response(task: Task, tags: list[str]) -> dict:
    """Build task response dict including tags."""
    data = {
        "id": task.id,
        "user_id": task.user_id,
        "title": task.title,
        "description": task.description,
        "completed": task.completed,
        "priority": task.priority,
        "due_date": task.due_date,
        "reminder_offset_minutes": task.reminder_offset_minutes,
        "recurrence": task.recurrence,
        "is_recurring": task.is_recurring,
        "tags": tags,
        "created_at": task.created_at,
        "updated_at": task.updated_at,
    }
    return data


# --- CRUD Endpoints ---

@router.get("", response_model=list[TaskResponse])
def list_tasks(
    user_id: str,
    user: CurrentUser,
    session: SessionDep,
    search: str | None = Query(default=None, description="Search in title and description"),
    priority: Literal["high", "medium", "low"] | None = Query(default=None),
    tag: str | None = Query(default=None, description="Filter by tag"),
    status_filter: Literal["all", "pending", "completed"] | None = Query(
        default=None, alias="status"
    ),
    sort: Literal["due_date", "priority", "title", "created_at"] | None = Query(default=None),
    order: Literal["asc", "desc"] | None = Query(default=None),
    due_from: datetime | None = Query(default=None),
    due_to: datetime | None = Query(default=None),
) -> list[dict]:
    """List all tasks for a user with optional search, filter, and sort."""
    verify_user_access(user_id, user.user_id)

    statement = select(Task).where(Task.user_id == user_id)

    # Status filter
    if status_filter == "completed":
        statement = statement.where(Task.completed == True)  # noqa: E712
    elif status_filter == "pending":
        statement = statement.where(Task.completed == False)  # noqa: E712

    # Priority filter
    if priority:
        statement = statement.where(Task.priority == priority)

    # Search
    if search and search.strip():
        term = f"%{search.strip()}%"
        statement = statement.where(
            or_(Task.title.ilike(term), Task.description.ilike(term))
        )

    # Tag filter via join
    if tag and tag.strip():
        statement = statement.join(TaskTag).where(TaskTag.tag == tag.strip().lower())

    # Due date range
    if due_from:
        statement = statement.where(Task.due_date >= due_from)
    if due_to:
        statement = statement.where(Task.due_date <= due_to)

    # Sort
    if sort == "due_date":
        col = Task.due_date.asc() if order != "desc" else Task.due_date.desc()
        statement = statement.order_by(col)
    elif sort == "priority":
        from sqlalchemy import case

        priority_order = case(
            (Task.priority == "high", 1),
            (Task.priority == "medium", 2),
            (Task.priority == "low", 3),
            else_=4,
        )
        if order == "desc":
            statement = statement.order_by(priority_order.desc())
        else:
            statement = statement.order_by(priority_order)
    elif sort == "title":
        col = Task.title.asc() if order != "desc" else Task.title.desc()
        statement = statement.order_by(col)
    else:
        statement = statement.order_by(Task.created_at.desc())

    tasks = session.exec(statement).all()
    result = []
    for task in tasks:
        tags = _get_tags(session, task.id)
        result.append(_build_task_response(task, tags))
    return result


@router.post("", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
async def create_task(
    user_id: str, task_data: TaskCreate, user: CurrentUser, session: SessionDep
) -> dict:
    """Create a new task."""
    verify_user_access(user_id, user.user_id)

    is_recurring = task_data.recurrence != "none"

    task = Task(
        user_id=user_id,
        title=task_data.title,
        description=task_data.description,
        priority=task_data.priority,
        due_date=task_data.due_date,
        reminder_offset_minutes=task_data.reminder_offset_minutes,
        recurrence=task_data.recurrence,
        is_recurring=is_recurring,
    )
    session.add(task)
    session.commit()
    session.refresh(task)

    # Schedule reminder if due_date and reminder_offset are set
    if task.due_date and task.reminder_offset_minutes:
        await schedule_reminder(
            task_id=task.id,
            user_id=user_id,
            due_date=task.due_date,
            offset_minutes=task.reminder_offset_minutes,
        )

    # Publish task.created event
    await publish_event(
        topic="task-events",
        event_type="task.created",
        task_id=task.id,
        task_data=task_to_event_data(task),
        user_id=user_id,
    )

    return _build_task_response(task, [])


@router.get("/{task_id}", response_model=TaskResponse)
def get_task(
    user_id: str, task_id: int, user: CurrentUser, session: SessionDep
) -> dict:
    """Get a single task by id."""
    verify_user_access(user_id, user.user_id)
    task = get_task_or_404(session, user_id, task_id)
    tags = _get_tags(session, task.id)
    return _build_task_response(task, tags)


@router.put("/{task_id}", response_model=TaskResponse)
async def update_task(
    user_id: str,
    task_id: int,
    task_data: TaskUpdate,
    user: CurrentUser,
    session: SessionDep,
) -> dict:
    """Update a task."""
    verify_user_access(user_id, user.user_id)
    task = get_task_or_404(session, user_id, task_id)

    if task_data.title is not None:
        task.title = task_data.title
    if task_data.description is not None:
        task.description = task_data.description
    if task_data.priority is not None:
        task.priority = task_data.priority
    if task_data.due_date is not None:
        task.due_date = task_data.due_date
    if task_data.reminder_offset_minutes is not None:
        task.reminder_offset_minutes = task_data.reminder_offset_minutes
    if task_data.recurrence is not None:
        task.recurrence = task_data.recurrence
        task.is_recurring = task_data.recurrence != "none"

    task.updated_at = datetime.utcnow()
    session.add(task)
    session.commit()
    session.refresh(task)

    tags = _get_tags(session, task.id)

    # Reschedule reminder if due_date or offset changed
    if task.due_date and task.reminder_offset_minutes:
        await cancel_reminder(task.id)
        await schedule_reminder(
            task_id=task.id,
            user_id=user_id,
            due_date=task.due_date,
            offset_minutes=task.reminder_offset_minutes,
        )
    elif not task.due_date or not task.reminder_offset_minutes:
        await cancel_reminder(task.id)

    # Publish task.updated event
    await publish_event(
        topic="task-events",
        event_type="task.updated",
        task_id=task.id,
        task_data=task_to_event_data(task),
        user_id=user_id,
    )

    return _build_task_response(task, tags)


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(
    user_id: str, task_id: int, user: CurrentUser, session: SessionDep
) -> None:
    """Delete a task."""
    verify_user_access(user_id, user.user_id)
    task = get_task_or_404(session, user_id, task_id)

    deleted_task_data = task_to_event_data(task)
    deleted_task_id = task.id

    # Cancel any scheduled reminder
    await cancel_reminder(task.id)

    # Delete associated tags first
    tag_stmt = select(TaskTag).where(TaskTag.task_id == task_id)
    for t in session.exec(tag_stmt).all():
        session.delete(t)

    session.delete(task)
    session.commit()

    # Publish task.deleted event
    await publish_event(
        topic="task-events",
        event_type="task.deleted",
        task_id=deleted_task_id,
        task_data=deleted_task_data,
        user_id=user_id,
    )


@router.patch("/{task_id}/complete", response_model=TaskResponse)
async def toggle_complete(
    user_id: str, task_id: int, user: CurrentUser, session: SessionDep
) -> dict:
    """Toggle task completion status."""
    verify_user_access(user_id, user.user_id)
    task = get_task_or_404(session, user_id, task_id)
    task.completed = not task.completed
    task.updated_at = datetime.utcnow()
    session.add(task)
    session.commit()
    session.refresh(task)

    tags = _get_tags(session, task.id)

    event_type = "task.completed" if task.completed else "task.updated"
    await publish_event(
        topic="task-events",
        event_type=event_type,
        task_id=task.id,
        task_data=task_to_event_data(task),
        user_id=user_id,
    )

    return _build_task_response(task, tags)


# --- Tag Management Endpoints ---

@router.post("/{task_id}/tags", response_model=TaskResponse)
def add_tags(
    user_id: str,
    task_id: int,
    body: TagsRequest,
    user: CurrentUser,
    session: SessionDep,
) -> dict:
    """Add tags to a task."""
    verify_user_access(user_id, user.user_id)
    task = get_task_or_404(session, user_id, task_id)

    existing = set(_get_tags(session, task.id))
    for tag in body.tags:
        clean = tag.strip().lower()
        if clean and len(clean) <= 50 and clean not in existing:
            session.add(TaskTag(task_id=task.id, tag=clean))
            existing.add(clean)

    session.commit()

    tags = _get_tags(session, task.id)
    return _build_task_response(task, tags)


@router.delete("/{task_id}/tags/{tag}", response_model=TaskResponse)
def remove_tag(
    user_id: str,
    task_id: int,
    tag: str,
    user: CurrentUser,
    session: SessionDep,
) -> dict:
    """Remove a tag from a task."""
    verify_user_access(user_id, user.user_id)
    task = get_task_or_404(session, user_id, task_id)

    clean_tag = tag.strip().lower()
    stmt = select(TaskTag).where(
        TaskTag.task_id == task.id, TaskTag.tag == clean_tag
    )
    tag_record = session.exec(stmt).first()
    if tag_record:
        session.delete(tag_record)
        session.commit()

    tags = _get_tags(session, task.id)
    return _build_task_response(task, tags)
