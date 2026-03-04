# API Contract: Activity & Conversations Endpoints

**File**: `backend/routes/activity.py`
**Date**: 2026-03-01
**Status**: Draft — ready for implementation

---

## GET /api/{user_id}/activity

Return recent login activity for the authenticated user.

### Request

```
Method:   GET
Path:     /api/{user_id}/activity
Auth:     Bearer <JWT token>  (required)
```

**Path Parameters**:

| Parameter | Type | Description |
|-----------|------|-------------|
| user_id | string | Authenticated user's ID |

**Headers**:

| Header | Required | Value |
|--------|----------|-------|
| Authorization | YES | `Bearer <jwt_token>` |

### Response

**Success (200 OK)**:

```json
[
  {
    "activity_type": "login",
    "ip_address": "192.168.1.1",
    "device": "Chrome on Windows",
    "created_at": "Sunday, March 1 at 10:30 AM"
  },
  {
    "activity_type": "login",
    "ip_address": "Unknown",
    "device": "Unknown device",
    "created_at": "Saturday, February 28 at 9:15 AM"
  }
]
```

| Field | Type | Notes |
|-------|------|-------|
| activity_type | string | Always "login" for this endpoint |
| ip_address | string | IP or "Unknown" |
| device | string | "Browser on OS" or "Unknown device" |
| created_at | string | Human-readable datetime format |

**Empty result**: Returns `[]` (not an error)

**Error Responses**:

| Status | When |
|--------|------|
| 401 | Missing/invalid JWT |
| 403 | URL user_id ≠ JWT user_id |

### Query Logic

```sql
SELECT * FROM user_activity
WHERE user_id = :user_id
  AND activity_type = 'login'
ORDER BY created_at DESC
LIMIT 20
```

---

## GET /api/{user_id}/conversations

Return list of past conversations for the authenticated user.

### Request

```
Method:   GET
Path:     /api/{user_id}/conversations
Auth:     Bearer <JWT token>  (required)
```

**Path Parameters**:

| Parameter | Type | Description |
|-----------|------|-------------|
| user_id | string | Authenticated user's ID |

**Headers**:

| Header | Required | Value |
|--------|----------|-------|
| Authorization | YES | `Bearer <jwt_token>` |

### Response

**Success (200 OK)**:

```json
[
  {
    "id": 42,
    "title": "Add a task to buy groceries",
    "created_at": "2026-03-01T10:30:00",
    "updated_at": "2026-03-01T10:45:00"
  },
  {
    "id": 41,
    "title": "Show all my tasks",
    "created_at": "2026-02-28T09:15:00",
    "updated_at": "2026-02-28T09:20:00"
  }
]
```

| Field | Type | Notes |
|-------|------|-------|
| id | integer | Conversation ID |
| title | string | First message[:100] |
| created_at | string | ISO datetime |
| updated_at | string | ISO datetime; updated on each new message |

**Empty result**: Returns `[]` (not an error)

**Error Responses**:

| Status | When |
|--------|------|
| 401 | Missing/invalid JWT |
| 403 | URL user_id ≠ JWT user_id |

### Query Logic

```sql
SELECT * FROM conversations
WHERE user_id = :user_id
ORDER BY updated_at DESC
LIMIT 20
```

---

## MCP Tools Contract (Internal — called by Groq agent)

These are NOT HTTP endpoints. They are Python functions called server-side by `execute_tool()`.

### Contract Rules (Constitution Law XVII)

1. Every tool accepts `user_id` as first argument (injected by `execute_tool()`)
2. `user_id` is NEVER in the tool's JSON schema (only in the Python function signature)
3. Every tool opens its own DB session and closes it after use
4. Every tool is wrapped in `try/except` and returns `{"error": str(e)}` on failure
5. Every tool returns a `dict` or `list` (never raises exceptions)

### Tool Schemas (GROQ_TOOLS — for Groq API)

```python
[
  {
    "type": "function",
    "function": {
      "name": "add_task",
      "description": "Create a new task for the user",
      "parameters": {
        "type": "object",
        "properties": {
          "title": {"type": "string", "description": "Task title (required, 1-200 chars)"},
          "description": {"type": "string", "description": "Optional task description"}
        },
        "required": ["title"]
      }
    }
  },
  {
    "type": "function",
    "function": {
      "name": "list_tasks",
      "description": "List the user's tasks with optional status filter",
      "parameters": {
        "type": "object",
        "properties": {
          "status": {
            "type": "string",
            "enum": ["all", "pending", "completed"],
            "description": "Filter by task status. Default: all"
          }
        },
        "required": []
      }
    }
  },
  {
    "type": "function",
    "function": {
      "name": "complete_task",
      "description": "Mark a specific task as completed",
      "parameters": {
        "type": "object",
        "properties": {
          "task_id": {"type": "integer", "description": "The ID of the task to complete"}
        },
        "required": ["task_id"]
      }
    }
  },
  {
    "type": "function",
    "function": {
      "name": "delete_task",
      "description": "Permanently delete a specific task",
      "parameters": {
        "type": "object",
        "properties": {
          "task_id": {"type": "integer", "description": "The ID of the task to delete"}
        },
        "required": ["task_id"]
      }
    }
  },
  {
    "type": "function",
    "function": {
      "name": "update_task",
      "description": "Update a task's title or description",
      "parameters": {
        "type": "object",
        "properties": {
          "task_id": {"type": "integer", "description": "The ID of the task to update"},
          "title": {"type": "string", "description": "New title (optional)"},
          "description": {"type": "string", "description": "New description (optional)"}
        },
        "required": ["task_id"]
      }
    }
  },
  {
    "type": "function",
    "function": {
      "name": "get_emails",
      "description": "Get recent emails from the user's inbox",
      "parameters": {
        "type": "object",
        "properties": {
          "limit": {"type": "integer", "description": "Number of emails to return (1-20, default 10)"}
        },
        "required": []
      }
    }
  },
  {
    "type": "function",
    "function": {
      "name": "get_login_activity",
      "description": "Get recent login history for the user",
      "parameters": {
        "type": "object",
        "properties": {
          "limit": {"type": "integer", "description": "Number of login events to return (default 10)"}
        },
        "required": []
      }
    }
  },
  {
    "type": "function",
    "function": {
      "name": "get_current_datetime",
      "description": "Get the current date and time",
      "parameters": {
        "type": "object",
        "properties": {},
        "required": []
      }
    }
  },
  {
    "type": "function",
    "function": {
      "name": "get_project_stats",
      "description": "Get a full overview of the user's project: task counts, conversations, last login",
      "parameters": {
        "type": "object",
        "properties": {},
        "required": []
      }
    }
  }
]
```

### execute_tool() Contract

```python
def execute_tool(tool_name: str, arguments: dict, user_id: str) -> dict | list:
    """
    Dispatches to the correct MCP tool, injecting user_id.
    Returns the tool result or {"error": "Unknown tool: <name>"}.
    """
```

**Mapping**:
| tool_name | Calls |
|-----------|-------|
| `add_task` | `add_task(user_id, **arguments)` |
| `list_tasks` | `list_tasks(user_id, **arguments)` |
| `complete_task` | `complete_task(user_id, **arguments)` |
| `delete_task` | `delete_task(user_id, **arguments)` |
| `update_task` | `update_task(user_id, **arguments)` |
| `get_emails` | `get_emails(user_id, **arguments)` |
| `get_login_activity` | `get_login_activity(user_id, **arguments)` |
| `get_current_datetime` | `get_current_datetime()` |
| `get_project_stats` | `get_project_stats(user_id)` |
| unknown | `{"error": "Unknown tool: <name>"}` |
