from datetime import datetime, timezone
from typing import Optional
from pydantic import BaseModel
from sqlmodel import Field, SQLModel, Index


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class Task(SQLModel, table=True):
    # Composite index on (user_id, completed) for efficient filtered queries
    __table_args__ = (
        Index("ix_task_user_id_completed", "user_id", "completed"),
    )

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: str = Field(index=True)
    title: str = Field(min_length=1, max_length=200)
    description: Optional[str] = Field(default=None, max_length=1000)
    completed: bool = Field(default=False, index=True)
    created_at: datetime = Field(default_factory=utc_now)
    updated_at: datetime = Field(default_factory=utc_now)


class TaskCreate(SQLModel):
    title: str = Field(min_length=1, max_length=200)
    description: Optional[str] = Field(default=None, max_length=1000)


class TaskUpdate(SQLModel):
    title: Optional[str] = Field(default=None, min_length=1, max_length=200)
    description: Optional[str] = Field(default=None, max_length=1000)


class TaskResponse(SQLModel):
    id: int
    user_id: str
    title: str
    description: Optional[str]
    completed: bool
    created_at: datetime
    updated_at: datetime


# ---------------------------------------------------------------------------
# Phase 3 Models (append-only — never modify Task model above)
# ---------------------------------------------------------------------------


class Conversation(SQLModel, table=True):
    __tablename__ = "conversations"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: str = Field(index=True)
    title: str = Field(max_length=100)
    created_at: datetime = Field(default_factory=utc_now)
    updated_at: datetime = Field(default_factory=utc_now)


class Message(SQLModel, table=True):
    __tablename__ = "messages"

    id: Optional[int] = Field(default=None, primary_key=True)
    conversation_id: int = Field(index=True)
    user_id: str = Field(index=True)
    role: str                            # "user" or "assistant"
    content: str
    tool_calls_json: Optional[str] = None
    created_at: datetime = Field(default_factory=utc_now)


class UserActivity(SQLModel, table=True):
    __tablename__ = "user_activity"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: str = Field(index=True)
    activity_type: str                   # "login", "logout", "signup"
    ip_address: Optional[str] = None
    device: Optional[str] = None
    created_at: datetime = Field(default_factory=utc_now)


class EmailLog(SQLModel, table=True):
    __tablename__ = "email_log"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: str = Field(index=True)
    from_address: str
    subject: str
    preview: str
    received_at: datetime
    is_read: bool = Field(default=False)


# Phase 3 Pydantic schemas

class ChatRequest(BaseModel):
    conversation_id: Optional[int] = None
    message: str = Field(min_length=1, max_length=2000)


class ChatResponse(BaseModel):
    conversation_id: int
    response: str
    tool_calls: list
