# Data Model: Todo App

**Date**: 2026-02-27
**Branch**: `001-todo-app`

---

## Entities

### Task

The primary data entity. Each task belongs to exactly one user and can never be transferred.

| Field | Type | Constraints | Notes |
|-------|------|-------------|-------|
| `id` | Integer | Primary key, auto-increment | Row identity |
| `user_id` | String | Not null, indexed | Foreign key to auth user (UUID string from Better Auth) |
| `title` | String | Not null, min 1 char, max 200 chars | Required task name |
| `description` | String (nullable) | Optional, max 1000 chars | Additional detail |
| `completed` | Boolean | Not null, default `False`, indexed | Task status flag |
| `created_at` | DateTime | Not null, default UTC now | Immutable after creation |
| `updated_at` | DateTime | Not null, default UTC now, updates on save | Last modification timestamp |

**Indexes**:
- `idx_task_user_id` on `user_id` — supports "all tasks for user" queries
- `idx_task_completed` on `completed` — supports status filter queries
- `idx_task_user_completed` composite on `(user_id, completed)` — supports "user's pending/completed" queries

**State Machine**:
```
PENDING ──[toggle]──→ COMPLETED
COMPLETED ──[toggle]──→ PENDING
```
Toggling is idempotent in pairs; calling toggle twice returns to original state.

---

### User (managed by Better Auth)

Users are managed entirely by Better Auth; the Todo backend does NOT own the user table.
The backend only receives a user ID (UUID string) from the verified JWT token.

| Field | Source | Usage in Todo Backend |
|-------|--------|----------------------|
| `id` (UUID) | JWT `sub` field | Used as `user_id` in every Task query |
| `email` | JWT payload | Returned in user dict for display |
| `name` | JWT payload (optional) | Displayed in Navbar |

---

## Validation Rules

### Task Title
- MUST be present (non-empty string)
- Minimum length: 1 character
- Maximum length: 200 characters
- Validated at: API request boundary (Pydantic schema), UI form (client-side)

### Task Description
- OPTIONAL — may be null or empty
- Maximum length: 1000 characters
- Validated at: API request boundary (Pydantic schema), UI form (client-side)

### User ID (in URL path)
- MUST match `current_user["sub"]` from verified JWT token
- Mismatch → 403 Forbidden (ownership violation)
- Validated at: every route handler before any DB query

---

## Pydantic Schemas (Backend)

### TaskCreate (POST body)
```python
class TaskCreate(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    description: Optional[str] = Field(default=None, max_length=1000)
```

### TaskUpdate (PUT body)
```python
class TaskUpdate(BaseModel):
    title: Optional[str] = Field(default=None, min_length=1, max_length=200)
    description: Optional[str] = Field(default=None, max_length=1000)
```

### TaskResponse (all responses)
```python
class TaskResponse(BaseModel):
    id: int
    user_id: str
    title: str
    description: Optional[str]
    completed: bool
    created_at: datetime
    updated_at: datetime
```

---

## TypeScript Interfaces (Frontend)

```typescript
// frontend/types/task.ts

interface Task {
  id: number
  user_id: string
  title: string
  description: string | null
  completed: boolean
  created_at: string   // ISO 8601 datetime string
  updated_at: string   // ISO 8601 datetime string
}

interface CreateTaskInput {
  title: string         // required, 1-200 chars
  description?: string  // optional, max 1000 chars
}

interface UpdateTaskInput {
  title?: string        // optional, 1-200 chars if provided
  description?: string  // optional, max 1000 chars if provided
}

interface ApiResponse<T> {
  data: T
  error?: string
}

interface User {
  id: string
  email: string
  name: string
}
```

---

## Entity Relationships

```
User (Better Auth)
  │
  │ 1
  │
  ▼ N
Task
  - id (PK)
  - user_id (FK → User.id, indexed)
  - title
  - description
  - completed (indexed)
  - created_at
  - updated_at
```

One user owns many tasks. Tasks are never shared. Deleting a user would cascade-delete
their tasks (out of scope for hackathon; Better Auth handles user lifecycle).
