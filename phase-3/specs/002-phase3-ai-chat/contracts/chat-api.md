# API Contract: Chat Endpoint

**File**: `backend/routes/chat.py`
**Date**: 2026-03-01
**Status**: Draft — ready for implementation

---

## POST /api/{user_id}/chat

Send a message to the AI assistant and receive a response.

### Request

```
Method:   POST
Path:     /api/{user_id}/chat
Auth:     Bearer <JWT token>  (required)
Content:  application/json
```

**Path Parameters**:

| Parameter | Type | Description |
|-----------|------|-------------|
| user_id | string | Authenticated user's ID |

**Headers**:

| Header | Required | Value |
|--------|----------|-------|
| Authorization | YES | `Bearer <jwt_token>` |
| Content-Type | YES | `application/json` |

**Request Body** (`ChatRequest`):

```json
{
  "conversation_id": null,
  "message": "Add a task to buy groceries"
}
```

| Field | Type | Required | Constraints | Notes |
|-------|------|----------|-------------|-------|
| conversation_id | integer \| null | NO | Positive int or null | null = create new conversation |
| message | string | YES | 1-2000 chars | Cannot be empty or whitespace only |

### Response

**Success (200 OK)**:

```json
{
  "conversation_id": 42,
  "response": "Done! I've added 'Buy groceries' to your task list. ✅ Task ID: 15",
  "tool_calls": [
    {
      "tool": "add_task",
      "result": {
        "task_id": 15,
        "status": "created",
        "title": "Buy groceries"
      }
    }
  ]
}
```

| Field | Type | Notes |
|-------|------|-------|
| conversation_id | integer | ID of the conversation (new or existing) |
| response | string | AI assistant's reply text |
| tool_calls | array | List of tools called; empty `[]` if no tool used |

**Error Responses**:

| Status | When | Body |
|--------|------|------|
| 401 | Missing/invalid JWT | `{"detail": "Invalid or expired token"}` |
| 403 | URL user_id ≠ JWT user_id | `{"detail": "Access denied"}` |
| 404 | conversation_id not found | `{"detail": "Conversation not found"}` |
| 422 | Empty/whitespace message | `{"detail": "Message cannot be empty"}` |

**Note**: HTTP 500 is NEVER returned. If the AI agent fails, a `200` is returned with
an error message in the `response` field (friendly message, not a stack trace).

### Implementation: 10-Step Stateless Request Cycle

```
STEP 1: JWT verify + ownership check
  current_user = Depends(get_current_user)
  if current_user["sub"] != user_id → 403

STEP 2: Validate message
  if not body.message.strip() → 422

STEP 3: Handle conversation
  if body.conversation_id:
    load Conversation WHERE id = conversation_id
    if not found → 404
    if conversation.user_id != user_id → 403
  else:
    CREATE new Conversation(user_id, title=message[:100], now, now)
    db.add → db.commit → db.refresh

STEP 4: Load history (ASC order)
  messages = SELECT * FROM messages WHERE conversation_id = conversation.id
             ORDER BY created_at ASC
  history = [{"role": m.role, "content": m.content} for m in messages]

STEP 5: Save user message
  new_msg = Message(conversation_id, user_id, role="user", content=message, now)
  db.add → db.commit

STEP 6: Build agent input
  history.append({"role": "user", "content": body.message})

STEP 7: Call agent
  result = await run_agent(user_id, history)

STEP 8: Save assistant response
  asst_msg = Message(conversation_id, user_id, role="assistant",
                     content=result["response"],
                     tool_calls_json=json.dumps(result["tool_calls"]), now)
  db.add → db.commit

STEP 9: Update conversation timestamp
  conversation.updated_at = utc_now()
  db.add → db.commit

STEP 10: Return ChatResponse
  return ChatResponse(
    conversation_id=conversation.id,
    response=result["response"],
    tool_calls=result["tool_calls"]
  )
```

### Sample Interactions

**New conversation — task creation**:
```
Request:  {"conversation_id": null, "message": "Add a task to buy groceries"}
Response: {"conversation_id": 1, "response": "Done! Task 'Buy groceries' added ✅",
           "tool_calls": [{"tool": "add_task", "result": {"task_id": 5, "status": "created", "title": "Buy groceries"}}]}
```

**Continue conversation — list tasks**:
```
Request:  {"conversation_id": 1, "message": "Show all my tasks"}
Response: {"conversation_id": 1, "response": "Here are your tasks:\n1. Buy groceries ❌\n2. ...",
           "tool_calls": [{"tool": "list_tasks", "result": [...]}]}
```

**Simple greeting — no tool**:
```
Request:  {"conversation_id": null, "message": "Hello!"}
Response: {"conversation_id": 2, "response": "Hi! How can I help you today? 👋",
           "tool_calls": []}
```
