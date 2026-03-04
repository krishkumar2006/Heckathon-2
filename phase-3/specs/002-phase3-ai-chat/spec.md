# Feature Specification: Phase 3 — AI Chat Assistant

> **This spec follows the Constitution v1.1.0 Phase 3 laws. Read it before implementing.**

**Feature Branch**: `002-phase3-ai-chat`
**Created**: 2026-03-01
**Status**: Draft
**Constitution**: `.specify/memory/constitution.md` (v1.1.0)

---

## User Scenarios & Testing *(mandatory)*

### User Story 1 — AI Task Management via Chat (Priority: P1)

A logged-in user opens the Chat page and types natural language commands to manage their
tasks. The AI understands intent and takes action without the user knowing any commands.
The user sees confirmation of every action with friendly messages.

**Why this priority**: Core feature proving AI utility for hackathon demo. Without task
management via chat, the feature has no primary value.

**Independent Test**: User signs in, navigates to `/chat`, types "Add a task to buy
groceries", and sees the task appear in the chat reply AND in the dashboard task list.

**Acceptance Scenarios**:

1. **Given** a logged-in user on the chat page, **When** they type "Add a task to buy
   groceries" and send, **Then** the AI creates the task and responds with confirmation
   including the task ID.

2. **Given** a user with existing tasks, **When** they type "Show all my tasks",
   **Then** the AI lists all tasks with IDs, titles, and completion status.

3. **Given** a user with task #1, **When** they type "Mark task 1 as done",
   **Then** the AI marks it complete and confirms with a friendly message.

4. **Given** a user with task #2, **When** they type "Delete task 2",
   **Then** the AI deletes it and confirms the deletion.

5. **Given** a user, **When** they type "Change task 1 title to Call mom tonight",
   **Then** the AI updates the title and shows the updated task.

6. **Given** a user, **When** they type "What's still pending?",
   **Then** the AI shows only incomplete tasks.

7. **Given** a user referencing task 999, **When** they type "Mark task 999 as done",
   **Then** the AI responds with a friendly "Task not found" and offers to list all tasks.

---

### User Story 2 — Email Inbox View via Chat (Priority: P2)

A logged-in user asks the AI to show their emails. The AI retrieves seeded email records
and presents them in a readable format.

**Why this priority**: Demonstrates multi-domain assistant capability — impressive for demo.

**Independent Test**: After seeding emails, user types "Show my emails" and receives a
formatted list with sender, subject, and preview.

**Acceptance Scenarios**:

1. **Given** emails seeded for the user, **When** they type "Show my emails",
   **Then** the AI lists recent emails with sender, subject, and preview text.

2. **Given** no emails seeded, **When** they type "Show my inbox",
   **Then** the AI replies with a friendly "No emails found" (not an error).

3. **Given** a user, **When** they type "Show my last 3 emails",
   **Then** the AI returns at most 3 emails.

---

### User Story 3 — Account Activity and Statistics (Priority: P3)

A logged-in user asks the AI about login history and project overview.

**Why this priority**: System-level awareness — adds demo depth.

**Independent Test**: User types "Give me a complete overview" and receives task counts,
conversation count, last login time, and member-since date.

**Acceptance Scenarios**:

1. **Given** a user with tasks and login history, **When** they type "Give me a complete
   overview", **Then** the AI shows total/pending/completed tasks, completion rate,
   conversation count, and last login.

2. **Given** a user, **When** they type "Who has logged into my account?",
   **Then** the AI shows login history with timestamp, IP, and device.

3. **Given** a user, **When** they type "What time is it?",
   **Then** the AI returns current date and time in a readable format.

---

### User Story 4 — Persistent Multi-Turn Conversation (Priority: P1)

A logged-in user can have a back-and-forth conversation. The AI remembers context within
the same session.

**Why this priority**: Multi-turn memory is what makes the AI feel intelligent vs a basic
chatbot — critical for demo quality.

**Independent Test**: User sends "Add a task to buy milk", then "Now mark it as done".
The AI marks the milk task without the user specifying the ID.

**Acceptance Scenarios**:

1. **Given** a conversation in progress, **When** the user sends a follow-up message,
   **Then** the AI has full context of the prior exchange and responds coherently.

2. **Given** a new page load, **When** the user starts chatting,
   **Then** a new conversation is created and the AI starts with the welcome message.

3. **Given** a conversation started, **When** the user sends subsequent messages,
   **Then** all messages use the same `conversation_id`.

---

### Edge Cases

- Empty message submission → button disabled; nothing sent.
- Groq rate limit hit → friendly retry message shown; no crash.
- User not logged in accessing `/chat` → redirect to `/login`.
- `user_id` in URL doesn't match JWT → 403 returned immediately.
- Referenced task does not exist → friendly error + offer to list all tasks.
- AI response fails → red error message shown; UI does not crash.

---

## Requirements *(mandatory)*

### Functional Requirements

**Environment and Packages:**
- **FR-001**: `GROQ_API_KEY` MUST be added to `backend/.env` only — never in source code.
  Free tier at console.groq.com (no credit card required).
- **FR-002**: New packages MUST be added to `backend/requirements.txt` without removing
  existing ones: `groq==0.11.0`, `mcp==1.0.0`, `python-dateutil==2.9.0`,
  `user-agents==2.2.0`.

**Database Models (append-only to `backend/models.py`):**
- **FR-003**: System MUST add `Conversation` model: id (PK), user_id (indexed), title
  (first message[:100]), created_at (UTC), updated_at (UTC).
- **FR-004**: System MUST add `Message` model: id (PK), conversation_id (FK+indexed),
  user_id (indexed), role ("user"|"assistant"), content, tool_calls_json (Optional),
  created_at (UTC). Messages MUST always load in ASC order.
- **FR-005**: System MUST add `UserActivity` model: id (PK), user_id (indexed),
  activity_type ("login"|"logout"|"signup"), ip_address (Optional), device (Optional,
  "Browser on OS" format), created_at (UTC).
- **FR-006**: System MUST add `EmailLog` model: id (PK), user_id (indexed), from_address,
  subject, preview (first 200 chars), received_at, is_read (default False).
- **FR-007**: System MUST add `ChatRequest` schema (conversation_id Optional[int],
  message str 1-2000 chars) and `ChatResponse` schema (conversation_id int, response str,
  tool_calls list).

**MCP Server (`backend/mcp_server.py` — CREATE new):**
- **FR-008**: System MUST implement 9 stateless tools: `add_task`, `list_tasks`,
  `complete_task`, `delete_task`, `update_task`, `get_emails`, `get_login_activity`,
  `get_current_datetime`, `get_project_stats`.
- **FR-009**: Every tool MUST open its own DB session and close after use (stateless).
- **FR-010**: Every tool MUST use `try/except` and return `{"error": str(e)}` on failure.
- **FR-011**: No tool schema MUST include `user_id` — always injected by `execute_tool()`.

**Groq Agent (`backend/groq_agent.py` — CREATE new):**
- **FR-012**: System MUST define `GROQ_TOOLS` list with 9 tool schemas in OpenAI function
  calling format.
- **FR-013**: System MUST implement `execute_tool(tool_name, arguments, user_id)` that
  injects `user_id` and dispatches to the correct MCP tool function.
- **FR-014**: System MUST implement `async run_agent(user_id, messages) -> dict`:
  - Prepend system prompt to message history
  - Call Groq (`llama-3.3-70b-versatile`, `max_tokens=1000`, `tool_choice="auto"`)
  - If `finish_reason == "tool_calls"`: execute tools, send results back to Groq, get
    final response
  - Return `{"response": str, "tool_calls": list}`
- **FR-015**: Agent MUST handle `groq.RateLimitError` (retry once, then friendly message)
  and all other exceptions (return friendly error message without crashing).

**Chat Endpoint (`backend/routes/chat.py` — CREATE new):**
- **FR-016**: System MUST implement `POST /api/{user_id}/chat` with stateless cycle:
  verify JWT + ownership → validate message → create/retrieve conversation → load history
  (ASC) → save user message → call agent → save assistant response → update timestamp →
  return `ChatResponse`.
- **FR-017**: HTTP errors: 401 (bad JWT), 403 (ownership mismatch), 404 (conversation
  not found), 422 (empty message). Never expose 500 — return ChatResponse with error text.

**Activity Endpoint (`backend/routes/activity.py` — CREATE new):**
- **FR-018**: System MUST implement `GET /api/{user_id}/activity` returning login events
  (limit 20, DESC).
- **FR-019**: System MUST implement `GET /api/{user_id}/conversations` returning past
  conversations (limit 20, DESC by `updated_at`).

**Login Tracking (ADD to `backend/main.py`):**
- **FR-020**: System MUST add HTTP middleware saving a `UserActivity` login record when
  `/api/auth/sign-in` returns 200, capturing IP and device from request headers.
- **FR-021**: System MUST register `chat_router` and `activity_router` in `main.py`
  without removing or changing existing routers.

**Email Seed Script (`backend/seed_emails.py` — CREATE new):**
- **FR-022**: System MUST provide `seed_emails.py --user_id <id>` that inserts 8 sample
  emails (various senders, subjects, preview text, dates) into `email_log`.

**Frontend Chat Page (`frontend/app/chat/page.tsx` — CREATE new):**
- **FR-023**: System MUST create `/chat` page (client component) with:
  - Message bubbles: user (right, blue), assistant (left, gray)
  - Tool call badges on assistant messages (green pill, "✅ tool_name")
  - Animated 3-dot loading indicator while AI is responding
  - 4 quick action buttons pre-filling input (not auto-sending)
  - Textarea input (Enter = send, Shift+Enter = newline)
  - Auto-scroll to bottom on new message
  - Red inline error on failure (UI does not crash)
  - Welcome message as first message on load
- **FR-024**: Chat page MUST attach JWT to all API calls. No token → redirect to `/login`.
- **FR-025**: Chat page MUST persist `conversationId` in state. First message sends null;
  all subsequent messages send the returned `conversation_id`.

**Frontend Navbar (ADD to `frontend/components/Navbar.tsx`):**
- **FR-026**: System MUST add ONE "💬 Chat" link between Dashboard and Logout in the
  existing Navbar. No restructuring, restyling, or removing of existing links.

### Key Entities

- **Conversation**: Chat session owned by one user. Title set from first message[:100].
  Never updated after creation.
- **Message**: Single turn in a conversation. Role = "user" or "assistant".
  `tool_calls_json` stores tools used (null for user messages).
- **UserActivity**: Audit log for login/logout/signup. Captures IP and device.
- **EmailLog**: Simulated email record. Used by AI to demonstrate email inbox reading.

---

## Security Requirements *(mandatory)*

### Auth Requirements

- [ ] **SR-001**: Every new endpoint MUST verify JWT via `Depends(get_current_user)`
- [ ] **SR-002**: Missing/invalid token MUST return 401
- [ ] **SR-003**: URL `{user_id}` MUST match JWT `user_id`; mismatch returns 403

### Data Isolation Requirements

- [ ] **SR-004**: All `conversations` queries MUST filter by `user_id`
- [ ] **SR-005**: All `messages` queries MUST trace to conversation owner's `user_id`
- [ ] **SR-006**: All `email_log` queries MUST filter by `user_id`
- [ ] **SR-007**: All `user_activity` queries MUST filter by `user_id`

### Secrets Requirements

- [ ] **SR-008**: `GROQ_API_KEY` only in `backend/.env` — never in source code
- [ ] **SR-009**: No secrets in git history

### Phase 2 Freeze Requirements

- [ ] **SR-010**: No frozen Phase 2 file modified
- [ ] **SR-011**: `models.py` append-only (new classes at bottom only)
- [ ] **SR-012**: `main.py` new imports and router registration only

### AI / MCP Safety Requirements

- [ ] **SR-013**: Groq free tier used — no OpenAI or paid AI
- [ ] **SR-014**: `user_id` not in any MCP tool schema
- [ ] **SR-015**: All MCP tools wrapped in `try/except`
- [ ] **SR-016**: `max_tokens=1000` in all Groq API calls

---

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: User completes a full task lifecycle (create → list → complete → delete)
  via natural language chat in under 2 minutes.
- **SC-002**: All 10 natural language test commands succeed in browser without errors.
- **SC-003**: Phase 2 regression test passes — dashboard, auth, and task CRUD work
  unchanged after Phase 3 implementation.
- **SC-004**: All 5 security sign-off gate layers pass before feature is marked done.
- **SC-005**: AI responds to user messages within 5 seconds on Groq free tier.
- **SC-006**: Rate limit errors produce a friendly message, not a crash or HTTP 500.
- **SC-007**: Unauthenticated users accessing `/chat` are redirected to `/login`.
- **SC-008**: Empty message submission is prevented by the UI (send button disabled).

---

## File Change Manifest

### NEW files (CREATE):

```
backend/mcp_server.py
backend/groq_agent.py
backend/routes/chat.py
backend/routes/activity.py
backend/seed_emails.py
frontend/app/chat/page.tsx
```

### MODIFIED files (ADD ONLY — never remove existing content):

```
backend/.env              ← add GROQ_API_KEY only
backend/requirements.txt  ← add 4 packages only
backend/main.py           ← add 2 router imports + 1 middleware only
backend/models.py         ← add 4 model classes at bottom only
frontend/components/Navbar.tsx ← add 1 chat link only
```

### FROZEN files (NEVER touch):

```
frontend/app/(auth)/login/page.tsx
frontend/app/(auth)/signup/page.tsx
frontend/app/dashboard/page.tsx
frontend/components/TaskList.tsx
frontend/components/TaskCard.tsx
frontend/components/TaskForm.tsx
frontend/lib/api.ts
frontend/lib/auth.ts
frontend/types/task.ts
backend/routes/tasks.py
backend/auth.py
backend/db.py
```
