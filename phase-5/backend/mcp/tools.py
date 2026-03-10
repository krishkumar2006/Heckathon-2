"""MCP Tools for Todo task management.

These tools are used by the AI agent to manage user tasks through
natural language commands. Each tool follows MCP tool specification.
Extended in Phase 5 with priority, tags, due dates, reminders, and recurrence.
"""

from datetime import datetime
from typing import Any

from sqlmodel import Session, select, or_

from db import get_engine
from models import Task, TaskTag


def _get_session() -> Session:
    """Get a database session for tool operations."""
    return Session(get_engine())


def _get_task_tags(session: Session, task_id: int) -> list[str]:
    """Get all tags for a task."""
    statement = select(TaskTag).where(TaskTag.task_id == task_id)
    tags = session.exec(statement).all()
    return [t.tag for t in tags]


def _task_to_dict(task: Task, tags: list[str] | None = None) -> dict[str, Any]:
    """Convert a Task model to a response dict."""
    data: dict[str, Any] = {
        "id": task.id,
        "title": task.title,
        "description": task.description,
        "completed": task.completed,
        "priority": task.priority,
        "recurrence": task.recurrence,
        "is_recurring": task.is_recurring,
        "created_at": task.created_at.isoformat() if task.created_at else None,
    }
    if task.due_date:
        data["due_date"] = task.due_date.isoformat()
    if task.reminder_offset_minutes is not None:
        data["reminder_offset_minutes"] = task.reminder_offset_minutes
    if tags is not None:
        data["tags"] = tags
    return data


def add_task(
    user_id: str,
    title: str,
    description: str = "",
    priority: str = "medium",
    tags: list[str] | None = None,
    due_date: str | None = None,
    reminder_offset_minutes: int | None = None,
    recurrence: str = "none",
) -> dict[str, Any]:
    """
    Add a new task for the user.

    Args:
        user_id: The ID of the user creating the task
        title: The title of the task (required)
        description: Optional description of the task
        priority: Priority level (high, medium, low). Default: medium
        tags: Optional list of tags (e.g., ["work", "urgent"])
        due_date: Optional due date in ISO 8601 format
        reminder_offset_minutes: Minutes before due_date to send reminder
        recurrence: Recurrence pattern (none, daily, weekly, monthly)

    Returns:
        Dict with task details or error message
    """
    if not title or not title.strip():
        return {"success": False, "error": "Task title is required"}

    if len(title) > 200:
        return {"success": False, "error": "Task title must be 200 characters or less"}

    if priority not in ("high", "medium", "low"):
        return {"success": False, "error": "Priority must be high, medium, or low"}

    if recurrence not in ("none", "daily", "weekly", "monthly"):
        return {"success": False, "error": "Recurrence must be none, daily, weekly, or monthly"}

    parsed_due_date = None
    if due_date:
        try:
            parsed_due_date = datetime.fromisoformat(due_date.replace("Z", "+00:00"))
        except ValueError:
            return {"success": False, "error": "Invalid due_date format. Use ISO 8601."}

    if recurrence != "none" and not parsed_due_date:
        return {"success": False, "error": "Recurring tasks must have a due_date"}

    with _get_session() as session:
        task = Task(
            user_id=user_id,
            title=title.strip(),
            description=description.strip() if description else "",
            priority=priority,
            due_date=parsed_due_date,
            reminder_offset_minutes=reminder_offset_minutes,
            recurrence=recurrence,
            is_recurring=(recurrence != "none"),
        )
        session.add(task)
        session.commit()
        session.refresh(task)

        # Add tags
        task_tags: list[str] = []
        if tags:
            for tag in tags:
                clean_tag = tag.strip().lower()
                if clean_tag and len(clean_tag) <= 50:
                    task_tag = TaskTag(task_id=task.id, tag=clean_tag)
                    session.add(task_tag)
                    task_tags.append(clean_tag)
            session.commit()

        return {
            "success": True,
            "task": _task_to_dict(task, task_tags),
            "message": f"Task '{task.title}' has been added successfully.",
        }


def list_tasks(
    user_id: str,
    include_completed: bool = True,
    limit: int = 50,
    priority: str | None = None,
    tag: str | None = None,
    search: str | None = None,
    sort: str | None = None,
    status: str | None = None,
) -> dict[str, Any]:
    """
    List tasks for a user with optional search, filter, and sort.

    Args:
        user_id: The ID of the user
        include_completed: Whether to include completed tasks
        limit: Maximum number of tasks to return
        priority: Filter by priority (high, medium, low)
        tag: Filter by tag
        search: Search keyword in title and description
        sort: Sort by (due_date, priority, title, created_at)
        status: Filter by status (all, pending, completed)

    Returns:
        Dict with list of tasks or error message
    """
    with _get_session() as session:
        statement = select(Task).where(Task.user_id == user_id)

        # Status filter
        if status == "completed":
            statement = statement.where(Task.completed == True)  # noqa: E712
        elif status == "pending":
            statement = statement.where(Task.completed == False)  # noqa: E712
        elif not include_completed:
            statement = statement.where(Task.completed == False)  # noqa: E712

        # Priority filter
        if priority and priority in ("high", "medium", "low"):
            statement = statement.where(Task.priority == priority)

        # Search
        if search and search.strip():
            search_term = f"%{search.strip()}%"
            statement = statement.where(
                or_(
                    Task.title.ilike(search_term),
                    Task.description.ilike(search_term),
                )
            )

        # Tag filter (join with TaskTag)
        if tag and tag.strip():
            statement = statement.join(TaskTag).where(
                TaskTag.tag == tag.strip().lower()
            )

        # Sort
        if sort == "due_date":
            statement = statement.order_by(Task.due_date.asc())
        elif sort == "priority":
            # Custom ordering: high=1, medium=2, low=3
            from sqlalchemy import case
            priority_order = case(
                (Task.priority == "high", 1),
                (Task.priority == "medium", 2),
                (Task.priority == "low", 3),
                else_=4,
            )
            statement = statement.order_by(priority_order)
        elif sort == "title":
            statement = statement.order_by(Task.title.asc())
        else:
            statement = statement.order_by(Task.created_at.desc())

        statement = statement.limit(limit)
        tasks = session.exec(statement).all()

        task_list = []
        for task in tasks:
            tags = _get_task_tags(session, task.id)
            task_list.append(_task_to_dict(task, tags))

        pending_count = sum(1 for t in task_list if not t["completed"])
        completed_count = sum(1 for t in task_list if t["completed"])

        return {
            "success": True,
            "tasks": task_list,
            "total": len(task_list),
            "pending": pending_count,
            "completed": completed_count,
            "message": f"Found {len(task_list)} task(s): {pending_count} pending, {completed_count} completed.",
        }


def complete_task(user_id: str, task_id: int) -> dict[str, Any]:
    """
    Mark a task as completed.

    Args:
        user_id: The ID of the user
        task_id: The ID of the task to complete

    Returns:
        Dict with updated task or error message
    """
    with _get_session() as session:
        task = session.get(Task, task_id)

        if not task:
            return {"success": False, "error": f"Task with ID {task_id} not found"}

        if task.user_id != user_id:
            return {"success": False, "error": "Task not found"}

        if task.completed:
            tags = _get_task_tags(session, task.id)
            return {
                "success": True,
                "task": _task_to_dict(task, tags),
                "message": f"Task '{task.title}' was already completed.",
            }

        task.completed = True
        task.updated_at = datetime.utcnow()
        session.add(task)
        session.commit()
        session.refresh(task)

        tags = _get_task_tags(session, task.id)
        return {
            "success": True,
            "task": _task_to_dict(task, tags),
            "message": f"Task '{task.title}' has been marked as completed.",
        }


def delete_task(user_id: str, task_id: int) -> dict[str, Any]:
    """
    Delete a task.

    Args:
        user_id: The ID of the user
        task_id: The ID of the task to delete

    Returns:
        Dict with success status or error message
    """
    with _get_session() as session:
        task = session.get(Task, task_id)

        if not task:
            return {"success": False, "error": f"Task with ID {task_id} not found"}

        if task.user_id != user_id:
            return {"success": False, "error": "Task not found"}

        task_title = task.title

        # Delete associated tags
        tag_statement = select(TaskTag).where(TaskTag.task_id == task_id)
        tags = session.exec(tag_statement).all()
        for tag in tags:
            session.delete(tag)

        session.delete(task)
        session.commit()

        return {
            "success": True,
            "deleted_task_id": task_id,
            "message": f"Task '{task_title}' has been deleted.",
        }


def update_task(
    user_id: str,
    task_id: int,
    title: str | None = None,
    description: str | None = None,
    priority: str | None = None,
    tags: list[str] | None = None,
    due_date: str | None = None,
    reminder_offset_minutes: int | None = None,
    recurrence: str | None = None,
) -> dict[str, Any]:
    """
    Update a task's fields.

    Args:
        user_id: The ID of the user
        task_id: The ID of the task to update
        title: New title (optional)
        description: New description (optional)
        priority: New priority (optional)
        tags: New tags list - replaces existing (optional)
        due_date: New due date in ISO 8601 (optional)
        reminder_offset_minutes: New reminder offset (optional)
        recurrence: New recurrence pattern (optional)

    Returns:
        Dict with updated task or error message
    """
    if all(v is None for v in [title, description, priority, tags, due_date, reminder_offset_minutes, recurrence]):
        return {"success": False, "error": "At least one field must be provided"}

    with _get_session() as session:
        task = session.get(Task, task_id)

        if not task:
            return {"success": False, "error": f"Task with ID {task_id} not found"}

        if task.user_id != user_id:
            return {"success": False, "error": "Task not found"}

        if title is not None:
            if len(title) > 200:
                return {"success": False, "error": "Title must be 200 characters or less"}
            task.title = title.strip()
        if description is not None:
            task.description = description.strip()
        if priority is not None:
            if priority not in ("high", "medium", "low"):
                return {"success": False, "error": "Priority must be high, medium, or low"}
            task.priority = priority
        if due_date is not None:
            try:
                task.due_date = datetime.fromisoformat(due_date.replace("Z", "+00:00"))
            except ValueError:
                return {"success": False, "error": "Invalid due_date format"}
        if reminder_offset_minutes is not None:
            task.reminder_offset_minutes = reminder_offset_minutes
        if recurrence is not None:
            if recurrence not in ("none", "daily", "weekly", "monthly"):
                return {"success": False, "error": "Invalid recurrence value"}
            task.recurrence = recurrence
            task.is_recurring = (recurrence != "none")

        # Replace tags if provided
        if tags is not None:
            existing = session.exec(
                select(TaskTag).where(TaskTag.task_id == task_id)
            ).all()
            for t in existing:
                session.delete(t)
            for tag in tags:
                clean = tag.strip().lower()
                if clean and len(clean) <= 50:
                    session.add(TaskTag(task_id=task_id, tag=clean))

        task.updated_at = datetime.utcnow()
        session.add(task)
        session.commit()
        session.refresh(task)

        final_tags = _get_task_tags(session, task.id)
        return {
            "success": True,
            "task": _task_to_dict(task, final_tags),
            "message": f"Task '{task.title}' has been updated.",
        }


def get_all_tools() -> list[dict[str, Any]]:
    """
    Get the list of all available MCP tools with their specifications.

    Returns:
        List of tool specifications for OpenAI function calling
    """
    return [
        {
            "type": "function",
            "function": {
                "name": "add_task",
                "description": "Add a new task to the user's todo list. Use this when the user wants to create, add, or make a new task. Supports priority, tags, due dates, reminders, and recurrence.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "title": {
                            "type": "string",
                            "description": "The title or name of the task to add",
                        },
                        "description": {
                            "type": "string",
                            "description": "Optional detailed description of the task",
                        },
                        "priority": {
                            "type": "string",
                            "enum": ["high", "medium", "low"],
                            "description": "Priority level. Default: medium",
                        },
                        "tags": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Optional list of tags (e.g., ['work', 'urgent'])",
                        },
                        "due_date": {
                            "type": "string",
                            "description": "Optional due date in ISO 8601 format (e.g., 2026-02-10T14:00:00Z)",
                        },
                        "reminder_offset_minutes": {
                            "type": "integer",
                            "description": "Minutes before due_date to send a reminder (e.g., 30 for 30 min before)",
                        },
                        "recurrence": {
                            "type": "string",
                            "enum": ["none", "daily", "weekly", "monthly"],
                            "description": "Recurrence pattern. Default: none. Requires due_date.",
                        },
                    },
                    "required": ["title"],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "list_tasks",
                "description": "List tasks for the user with optional search, filter, and sort. Use when the user wants to see, view, show, search, or filter their tasks.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "include_completed": {
                            "type": "boolean",
                            "description": "Whether to include completed tasks. Default: true.",
                        },
                        "limit": {
                            "type": "integer",
                            "description": "Maximum number of tasks to return. Default: 50.",
                        },
                        "priority": {
                            "type": "string",
                            "enum": ["high", "medium", "low"],
                            "description": "Filter by priority level.",
                        },
                        "tag": {
                            "type": "string",
                            "description": "Filter by tag (e.g., 'work').",
                        },
                        "search": {
                            "type": "string",
                            "description": "Search keyword in task title and description.",
                        },
                        "sort": {
                            "type": "string",
                            "enum": ["due_date", "priority", "title", "created_at"],
                            "description": "Sort results by this field.",
                        },
                        "status": {
                            "type": "string",
                            "enum": ["all", "pending", "completed"],
                            "description": "Filter by task status.",
                        },
                    },
                    "required": [],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "complete_task",
                "description": "Mark a task as completed. Use this when the user wants to complete, finish, check off, or mark a task as done.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "task_id": {
                            "type": "integer",
                            "description": "The ID of the task to mark as completed",
                        },
                    },
                    "required": ["task_id"],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "delete_task",
                "description": "Delete a task from the todo list. Use this when the user wants to remove, delete, or get rid of a task.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "task_id": {
                            "type": "integer",
                            "description": "The ID of the task to delete",
                        },
                    },
                    "required": ["task_id"],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "update_task",
                "description": "Update a task's fields including title, description, priority, tags, due date, reminder, or recurrence. Use when the user wants to edit, modify, change, or rename a task.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "task_id": {
                            "type": "integer",
                            "description": "The ID of the task to update",
                        },
                        "title": {
                            "type": "string",
                            "description": "The new title for the task",
                        },
                        "description": {
                            "type": "string",
                            "description": "The new description for the task",
                        },
                        "priority": {
                            "type": "string",
                            "enum": ["high", "medium", "low"],
                            "description": "New priority level",
                        },
                        "tags": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "New tags (replaces existing tags)",
                        },
                        "due_date": {
                            "type": "string",
                            "description": "New due date in ISO 8601 format",
                        },
                        "reminder_offset_minutes": {
                            "type": "integer",
                            "description": "Minutes before due_date to send reminder",
                        },
                        "recurrence": {
                            "type": "string",
                            "enum": ["none", "daily", "weekly", "monthly"],
                            "description": "New recurrence pattern",
                        },
                    },
                    "required": ["task_id"],
                },
            },
        },
    ]
