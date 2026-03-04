# Data Model: Phase 3 — AI Chat Assistant

**Feature**: `002-phase3-ai-chat`
**Date**: 2026-03-01
**File**: `backend/models.py` (append-only — never modify existing `Task` model)

---

## Existing Model (FROZEN — do not touch)

```python
class Task(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: str = Field(index=True)
    title: str = Field(min_length=1, max_length=200)
    description: Optional[str] = Field(default=None, max_length=1000)
    completed: bool = Field(default=False, index=True)
    created_at: datetime = Field(default_factory=utc_now)
    updated_at: datetime = Field(default_factory=utc_now)
```

---

## New Models (ADD at bottom of models.py)

### Model 1: Conversation

Represents one chat session between user and AI.
Title is set from the first message (first 100 characters).
Never updated after creation.

```
Table: conversations
```

| Field | Type | Constraints | Notes |
|-------|------|-------------|-------|
| id | int | PK, auto-increment | |
| user_id | str | NOT NULL, INDEX | User who owns this conversation |
| title | str | NOT NULL, max 100 chars | First message[:100] |
| created_at | datetime | NOT NULL, default UTC now | When created |
| updated_at | datetime | NOT NULL, default UTC now | Updated on each new message |

**Relationships**:
- One conversation → many messages (via `conversation_id`)
- One conversation → one user (via `user_id`)

**Indexes**: `user_id` (for fast per-user conversation listing)

```python
class Conversation(SQLModel, table=True):
    __tablename__ = "conversations"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: str = Field(index=True)
    title: str = Field(max_length=100)
    created_at: datetime = Field(default_factory=utc_now)
    updated_at: datetime = Field(default_factory=utc_now)
```

---

### Model 2: Message

Stores every message in every conversation.
Always loaded in ASC order (chronological) for AI history.

```
Table: messages
```

| Field | Type | Constraints | Notes |
|-------|------|-------------|-------|
| id | int | PK, auto-increment | |
| conversation_id | int | NOT NULL, INDEX | FK → conversations.id |
| user_id | str | NOT NULL, INDEX | For efficient user-scoped queries |
| role | str | NOT NULL | "user" or "assistant" |
| content | str | NOT NULL | Full message text |
| tool_calls_json | Optional[str] | NULL allowed | JSON array of tools called; null for user messages |
| created_at | datetime | NOT NULL, default UTC now | For ASC ordering |

**Roles**:
- `"user"` — message from the human
- `"assistant"` — message from the AI

**tool_calls_json format** (for assistant messages with tool calls):
```json
[
  {"tool": "add_task", "result": {"task_id": 1, "status": "created", "title": "Buy milk"}}
]
```

**Query order**: Always `ORDER BY created_at ASC` when loading history.

```python
class Message(SQLModel, table=True):
    __tablename__ = "messages"

    id: Optional[int] = Field(default=None, primary_key=True)
    conversation_id: int = Field(index=True)
    user_id: str = Field(index=True)
    role: str                           # "user" or "assistant"
    content: str
    tool_calls_json: Optional[str] = None
    created_at: datetime = Field(default_factory=utc_now)
```

---

### Model 3: UserActivity

Audit log for user login/logout/signup events.
Captures IP and device for the activity display tool.

```
Table: user_activity
```

| Field | Type | Constraints | Notes |
|-------|------|-------------|-------|
| id | int | PK, auto-increment | |
| user_id | str | NOT NULL, INDEX | User who performed activity |
| activity_type | str | NOT NULL | "login", "logout", or "signup" |
| ip_address | Optional[str] | NULL allowed | From `request.client.host` |
| device | Optional[str] | NULL allowed | "Chrome on Windows" format |
| created_at | datetime | NOT NULL, default UTC now | When activity occurred |

**activity_type values**:
- `"login"` — tracked via HTTP middleware on successful sign-in
- `"logout"` — future use
- `"signup"` — future use

**Populated by**: HTTP middleware in `main.py` tracking `/api/auth/sign-in` responses.

```python
class UserActivity(SQLModel, table=True):
    __tablename__ = "user_activity"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: str = Field(index=True)
    activity_type: str               # "login", "logout", "signup"
    ip_address: Optional[str] = None
    device: Optional[str] = None
    created_at: datetime = Field(default_factory=utc_now)
```

---

### Model 4: EmailLog

Simulated email records for the `get_emails` AI tool.
Populated by `seed_emails.py`. Used for demo purposes only.

```
Table: email_log
```

| Field | Type | Constraints | Notes |
|-------|------|-------------|-------|
| id | int | PK, auto-increment | |
| user_id | str | NOT NULL, INDEX | User who owns this email |
| from_address | str | NOT NULL | Sender email address |
| subject | str | NOT NULL | Email subject line |
| preview | str | NOT NULL | First 200 chars of body |
| received_at | datetime | NOT NULL | When email was received |
| is_read | bool | NOT NULL, default False | Read status |

**Populated by**: `python seed_emails.py --user_id <id>` (8 sample emails).

```python
class EmailLog(SQLModel, table=True):
    __tablename__ = "email_log"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: str = Field(index=True)
    from_address: str
    subject: str
    preview: str
    received_at: datetime
    is_read: bool = Field(default=False)
```

---

## New Pydantic Schemas (ADD after EmailLog model)

### ChatRequest

```python
class ChatRequest(BaseModel):
    conversation_id: Optional[int] = None   # None = create new conversation
    message: str = Field(min_length=1, max_length=2000)
```

| Field | Type | Rules |
|-------|------|-------|
| conversation_id | Optional[int] | None → create new; int → continue existing |
| message | str | Required; 1-2000 chars |

### ChatResponse

```python
class ChatResponse(BaseModel):
    conversation_id: int
    response: str
    tool_calls: list
```

| Field | Type | Notes |
|-------|------|-------|
| conversation_id | int | The conversation this message belongs to |
| response | str | AI assistant's reply text |
| tool_calls | list | Tools called: `[{"tool": str, "result": dict}]` |

---

## Entity Relationships

```
users (Better Auth)
  │
  ├── tasks (Phase 2)          user_id → users.id
  │
  ├── conversations             user_id → users.id
  │     └── messages            conversation_id → conversations.id
  │                             user_id → users.id (denormalized for fast queries)
  │
  ├── user_activity             user_id → users.id
  │
  └── email_log                 user_id → users.id
```

Note: Foreign key constraints are NOT enforced at the SQLModel level for Neon
compatibility. `user_id` is a string matching Better Auth's user ID format.

---

## Migration Plan

After adding models to `models.py`, run:

```python
from db import engine
from models import SQLModel, Conversation, Message, UserActivity, EmailLog
SQLModel.metadata.create_all(engine)
print("New tables created successfully!")
```

This creates all 4 new tables without touching the existing `tasks` table.
Neon's serverless PostgreSQL handles the DDL safely.

**Verification**: Check Neon dashboard for:
- `conversations` table
- `messages` table
- `user_activity` table
- `email_log` table

---

## State Transitions

### Conversation Lifecycle
```
POST /chat (no conversation_id)
  → CREATE new Conversation (title = message[:100])
  → conversation.id returned in response

POST /chat (with conversation_id)
  → LOAD existing Conversation
  → Verify user_id ownership → 403 if mismatch
  → UPDATE conversation.updated_at on each message
```

### Message Lifecycle
```
User sends message
  → SAVE Message (role="user", tool_calls_json=null)
  → CALL Groq agent
  → SAVE Message (role="assistant", tool_calls_json=JSON or null)
  → RETURN response with tool_calls list
```
