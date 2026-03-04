"""
backend/mcp_server.py — Phase 3 MCP Tool Server
9 stateless tool functions called by groq_agent.execute_tool().

Rules (Constitution Law XVII):
- Every tool opens its own DB session and closes after use.
- Every tool filters all queries by user_id.
- Every tool is wrapped in try/except → returns {"error": str(e)} on failure.
- user_id is NEVER in a tool's JSON schema — always injected by execute_tool().
"""

import json
from datetime import datetime, timezone

from sqlmodel import Session, select

from db import engine
from models import Conversation, EmailLog, Message, Task, UserActivity


# ---------------------------------------------------------------------------
# Task tools
# ---------------------------------------------------------------------------

def add_task(user_id: str, title: str, description: str | None = None) -> dict:
    """Create a new task for the user."""
    try:
        with Session(engine) as session:
            task = Task(user_id=user_id, title=title, description=description)
            session.add(task)
            session.commit()
            session.refresh(task)
            return {
                "task_id": task.id,
                "status": "created",
                "title": task.title,
            }
    except Exception as e:
        return {"error": str(e)}


def list_tasks(user_id: str, status: str = "all") -> list:
    """List the user's tasks with optional status filter."""
    try:
        with Session(engine) as session:
            statement = select(Task).where(Task.user_id == user_id)
            if status == "pending":
                statement = statement.where(Task.completed == False)  # noqa: E712
            elif status == "completed":
                statement = statement.where(Task.completed == True)  # noqa: E712
            tasks = session.exec(statement).all()
            return [
                {
                    "task_id": t.id,
                    "title": t.title,
                    "description": t.description,
                    "completed": t.completed,
                    "created_at": t.created_at.strftime("%Y-%m-%d"),
                }
                for t in tasks
            ]
    except Exception as e:
        return {"error": str(e)}  # type: ignore[return-value]


def complete_task(user_id: str, task_id: int) -> dict:
    """Mark a specific task as completed."""
    try:
        with Session(engine) as session:
            task = session.exec(
                select(Task).where(Task.id == task_id, Task.user_id == user_id)
            ).first()
            if task is None:
                return {"error": f"Task {task_id} not found"}
            task.completed = True
            task.updated_at = datetime.now(timezone.utc)
            session.add(task)
            session.commit()
            return {"task_id": task_id, "status": "completed", "title": task.title}
    except Exception as e:
        return {"error": str(e)}


def delete_task(user_id: str, task_id: int) -> dict:
    """Permanently delete a specific task."""
    try:
        with Session(engine) as session:
            task = session.exec(
                select(Task).where(Task.id == task_id, Task.user_id == user_id)
            ).first()
            if task is None:
                return {"error": f"Task {task_id} not found"}
            title = task.title
            session.delete(task)
            session.commit()
            return {"task_id": task_id, "status": "deleted", "title": title}
    except Exception as e:
        return {"error": str(e)}


def update_task(
    user_id: str,
    task_id: int,
    title: str | None = None,
    description: str | None = None,
) -> dict:
    """Update a task's title or description."""
    try:
        with Session(engine) as session:
            task = session.exec(
                select(Task).where(Task.id == task_id, Task.user_id == user_id)
            ).first()
            if task is None:
                return {"error": f"Task {task_id} not found"}
            if title is not None:
                task.title = title
            if description is not None:
                task.description = description
            task.updated_at = datetime.now(timezone.utc)
            session.add(task)
            session.commit()
            session.refresh(task)
            return {
                "task_id": task_id,
                "status": "updated",
                "title": task.title,
                "description": task.description,
            }
    except Exception as e:
        return {"error": str(e)}


# ---------------------------------------------------------------------------
# Email tool
# ---------------------------------------------------------------------------

def get_emails(user_id: str, limit: int = 10) -> list:
    """Get recent emails from the user's inbox."""
    try:
        limit = max(1, min(20, limit))
        with Session(engine) as session:
            emails = session.exec(
                select(EmailLog)
                .where(EmailLog.user_id == user_id)
                .order_by(EmailLog.received_at.desc())  # type: ignore[arg-type]
                .limit(limit)
            ).all()
            if not emails:
                return []
            return [
                {
                    "from": e.from_address,
                    "subject": e.subject,
                    "preview": e.preview,
                    "received_at": e.received_at.strftime("%a, %b %d"),
                    "is_read": e.is_read,
                }
                for e in emails
            ]
    except Exception as e:
        return {"error": str(e)}  # type: ignore[return-value]


# ---------------------------------------------------------------------------
# Activity tools
# ---------------------------------------------------------------------------

def get_login_activity(user_id: str, limit: int = 10) -> list:
    """Get recent login history for the user."""
    try:
        limit = max(1, min(20, limit))
        with Session(engine) as session:
            events = session.exec(
                select(UserActivity)
                .where(
                    UserActivity.user_id == user_id,
                    UserActivity.activity_type == "login",
                )
                .order_by(UserActivity.created_at.desc())  # type: ignore[arg-type]
                .limit(limit)
            ).all()
            if not events:
                return []
            return [
                {
                    "activity_type": e.activity_type,
                    "ip_address": e.ip_address or "Unknown",
                    "device": e.device or "Unknown device",
                    "when": e.created_at.strftime("%a, %b %d at %I:%M %p").replace(
                        " 0", " "
                    ),
                }
                for e in events
            ]
    except Exception as e:
        return {"error": str(e)}  # type: ignore[return-value]


def get_current_datetime() -> dict:
    """Get the current date and time."""
    try:
        now = datetime.now(timezone.utc)
        # Cross-platform formatting (no %-d which fails on Windows)
        day = str(now.day)
        hour_24 = now.hour
        hour_12 = hour_24 % 12 or 12
        am_pm = "AM" if hour_24 < 12 else "PM"
        minute = f"{now.minute:02d}"
        date_str = now.strftime(f"%A, %B {day}, %Y")
        time_str = f"{hour_12}:{minute} {am_pm} UTC"
        return {
            "date": date_str,
            "time": time_str,
            "iso": now.isoformat(),
        }
    except Exception as e:
        return {"error": str(e)}


def get_project_stats(user_id: str) -> dict:
    """Get a full overview of the user's project stats."""
    try:
        with Session(engine) as session:
            all_tasks = session.exec(
                select(Task).where(Task.user_id == user_id)
            ).all()
            total = len(all_tasks)
            completed = sum(1 for t in all_tasks if t.completed)
            pending = total - completed
            completion_rate = round((completed / total * 100) if total > 0 else 0)

            conversation_count = len(
                session.exec(
                    select(Conversation).where(Conversation.user_id == user_id)
                ).all()
            )

            last_login = session.exec(
                select(UserActivity)
                .where(
                    UserActivity.user_id == user_id,
                    UserActivity.activity_type == "login",
                )
                .order_by(UserActivity.created_at.desc())  # type: ignore[arg-type]
                .limit(1)
            ).first()

            last_login_str = "Never recorded"
            if last_login:
                d = last_login.created_at
                day = str(d.day)
                hour_24 = d.hour
                hour_12 = hour_24 % 12 or 12
                am_pm = "AM" if hour_24 < 12 else "PM"
                last_login_str = d.strftime(f"%B {day} at {hour_12}:{d.minute:02d} {am_pm}")

            return {
                "total_tasks": total,
                "completed_tasks": completed,
                "pending_tasks": pending,
                "completion_rate": f"{completion_rate}%",
                "conversation_count": conversation_count,
                "last_login": last_login_str,
            }
    except Exception as e:
        return {"error": str(e)}
