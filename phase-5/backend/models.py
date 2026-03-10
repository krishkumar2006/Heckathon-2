"""SQLModel models for Todo application with AI chatbot."""

from datetime import datetime
from enum import Enum
from uuid import uuid4
from sqlmodel import SQLModel, Field


class PriorityLevel(str, Enum):
    """Task priority levels."""

    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class RecurrencePattern(str, Enum):
    """Task recurrence patterns."""

    NONE = "none"
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"


class Task(SQLModel, table=True):
    """Task model for storing user todos."""

    id: int | None = Field(default=None, primary_key=True)
    user_id: str = Field(index=True)
    title: str = Field(max_length=200)
    description: str = Field(default="", max_length=1000)
    completed: bool = Field(default=False)
    priority: str = Field(default="medium", index=True)
    due_date: datetime | None = Field(default=None)
    reminder_offset_minutes: int | None = Field(default=None)
    recurrence: str = Field(default="none")
    is_recurring: bool = Field(default=False)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class TaskTag(SQLModel, table=True):
    """Many-to-many relationship between tasks and tags."""

    __tablename__ = "task_tag"

    id: int | None = Field(default=None, primary_key=True)
    task_id: int = Field(index=True, foreign_key="task.id")
    tag: str = Field(max_length=50, index=True)


class Conversation(SQLModel, table=True):
    """Conversation model for storing chat sessions."""

    id: str = Field(default_factory=lambda: str(uuid4()), primary_key=True)
    user_id: str = Field(index=True)
    title: str | None = Field(default=None, max_length=200)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class Message(SQLModel, table=True):
    """Message model for storing chat messages."""

    id: int | None = Field(default=None, primary_key=True)
    conversation_id: str = Field(index=True, foreign_key="conversation.id")
    role: str = Field(max_length=20)  # 'user' or 'assistant'
    content: str
    tool_calls: str | None = Field(default=None)  # JSON serialized
    created_at: datetime = Field(default_factory=datetime.utcnow)
