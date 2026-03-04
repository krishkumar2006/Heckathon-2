# Tasks: Phase 3 — AI Chat Assistant

**Input**: Design documents from `/specs/002-phase3-ai-chat/`
**Prerequisites**: plan.md ✅ · spec.md ✅ · research.md ✅ · data-model.md ✅ · contracts/ ✅ · quickstart.md ✅

**Tests**: No dedicated test files — manual integration testing via curl and browser (per spec SC-001 to SC-008 and quickstart.md Step 10).

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story?] Description`

- **[P]**: Can run in parallel (different files, no blocking dependencies)
- **[Story]**: Which user story this task belongs to (US1–US4)
- Exact file paths included in every description

---

## Phase 1: Setup (Environment & Packages)

**Purpose**: Provision secrets and install Phase 3 dependencies before any code is written.

- [x] T001 Add `GROQ_API_KEY=gsk_xxxx` to `backend/.env` — get free key at console.groq.com (no credit card), verify it reads with `python -c "from dotenv import load_dotenv; import os; load_dotenv(); print(os.getenv('GROQ_API_KEY')[:4])"`
- [x] T002 Add four packages to `backend/requirements.txt` (no removals): `groq==0.11.0`, `mcp==1.0.0`, `python-dateutil==2.9.0`, `user-agents==2.2.0` — then run `pip install groq==0.11.0 mcp==1.0.0 python-dateutil==2.9.0 user-agents==2.2.0` inside activated `backend/venv` and verify with `python -c "import groq, mcp, dateutil, user_agents; print('All OK')"`

**Checkpoint**: GROQ_API_KEY resolves and all 4 packages import successfully.

---

## Phase 2: Foundational (Database Models — Blocks All User Stories)

**Purpose**: Append 4 new SQLModel table classes and 2 Pydantic schemas to `backend/models.py`, then create the tables in Neon. No user story can proceed without this phase.

**⚠️ CRITICAL**: Append-only. The existing `Task` model and all imports above it MUST remain untouched.

- [x] T003 Append `Conversation` (id PK, user_id indexed, title max 100 chars, created_at UTC, updated_at UTC), `Message` (id PK, conversation_id indexed, user_id indexed, role str, content str, tool_calls_json Optional[str], created_at UTC), `UserActivity` (id PK, user_id indexed, activity_type str, ip_address Optional[str], device Optional[str], created_at UTC), and `EmailLog` (id PK, user_id indexed, from_address str, subject str, preview str, received_at datetime, is_read bool default False) SQLModel table classes to the bottom of `backend/models.py` — verify with `python -c "from models import Conversation, Message, UserActivity, EmailLog; print('Models OK')"`
- [x] T004 Append `ChatRequest` (conversation_id: Optional[int] = None, message: str with min_length=1 max_length=2000) and `ChatResponse` (conversation_id: int, response: str, tool_calls: list) Pydantic `BaseModel` classes to the bottom of `backend/models.py` after the 4 table classes — verify with `python -c "from models import ChatRequest, ChatResponse; r = ChatRequest(message='hi'); print(r)"`
- [x] T005 Create all 4 new tables in Neon by running: `python -c "from db import engine; from models import SQLModel, Conversation, Message, UserActivity, EmailLog; SQLModel.metadata.create_all(engine); print('Tables: conversations, messages, user_activity, email_log created')"` — verify all 4 tables appear in Neon dashboard alongside existing `tasks` table

**Checkpoint**: `python -c "from models import Conversation, Message, UserActivity, EmailLog, ChatRequest, ChatResponse; print('All models OK')"` passes. 4 new tables visible in Neon. `tasks` table untouched.

---

## Phase 3: User Story 1 + User Story 4 (P1) — AI Task Management + Persistent Multi-Turn Conversation 🎯 MVP

**Goal**: User manages tasks (create, list, complete, delete, update) entirely via natural language chat. Conversation history persists across turns so the AI can reference prior context.

**Independent Test**: User signs in → navigates to `/chat` → types "Add a task to buy groceries" → sees confirmation with task ID in chat → types "Now mark it as done" → AI marks the groceries task without requiring the user to specify an ID.

### Implementation for User Story 1 + 4

- [x] T006 [P] [US1] Create `backend/mcp_server.py` with all 9 stateless tool functions: `add_task(user_id, title, description=None)`, `list_tasks(user_id, status="all")`, `complete_task(user_id, task_id)`, `delete_task(user_id, task_id)`, `update_task(user_id, task_id, title=None, description=None)`, `get_emails(user_id, limit=10)`, `get_login_activity(user_id, limit=10)`, `get_current_datetime()`, `get_project_stats(user_id)` — each function MUST: (a) open its own `Session(engine)` and close after, (b) filter all DB queries by `user_id`, (c) be wrapped in `try/except Exception as e: return {"error": str(e)}`, (d) return a `dict` or `list` (never raise)
- [x] T007 [P] [US1] Create `backend/groq_agent.py` with: (a) `GROQ_TOOLS` list of 9 function schemas in OpenAI format — no `user_id` in any schema's `parameters` (user_id is always injected server-side); (b) `execute_tool(tool_name: str, arguments: dict, user_id: str) -> dict | list` dispatcher that injects `user_id` and calls the correct `mcp_server` function (returns `{"error": "Unknown tool: <name>"}` for unrecognized tool); (c) `async run_agent(user_id: str, messages: list) -> dict` that prepends system prompt, calls Groq (`model="llama-3.3-70b-versatile"`, `max_tokens=1000`, `tool_choice="auto"`), loops on `finish_reason == "tool_calls"` (execute each tool, append tool result to messages, re-call Groq for final response), handles `groq.RateLimitError` (retry once after 1s sleep then return friendly rate-limit message), handles all other exceptions (return `{"response": "Sorry, I encountered an error...", "tool_calls": []}`) — returns `{"response": str, "tool_calls": list}`
- [x] T008 [US1] Create `backend/routes/chat.py` implementing `POST /api/{user_id}/chat` with exact 10-step stateless cycle per `contracts/chat-api.md`: (1) JWT verify + `_check_ownership` → 403 on mismatch; (2) validate `body.message.strip()` → 422 if empty; (3) if `body.conversation_id`: load `Conversation` WHERE id=conversation_id AND user_id=user_id → 404 if not found; else CREATE new `Conversation(user_id, title=body.message[:100], created_at, updated_at)`; (4) load `Message` history WHERE conversation_id=id ORDER BY created_at ASC; (5) save user `Message(conversation_id, user_id, role="user", content=body.message)`; (6) build agent history from loaded messages + new message; (7) `result = await run_agent(user_id, history)`; (8) save assistant `Message(conversation_id, user_id, role="assistant", content=result["response"], tool_calls_json=json.dumps(result["tool_calls"]))`; (9) update `conversation.updated_at = utc_now()`; (10) return `ChatResponse(conversation_id=conversation.id, response=result["response"], tool_calls=result["tool_calls"])` — HTTP 500 NEVER returned; all agent failures return 200 with error text in response field
- [x] T009 [US1] Add to `backend/main.py` (additive only — after existing tasks_router lines): `from routes.chat import router as chat_router` import and `app.include_router(chat_router, prefix="/api")` registration — verify by restarting server and testing: `curl -X POST http://localhost:8000/api/{user_id}/chat -H "Authorization: Bearer <token>" -H "Content-Type: application/json" -d '{"message": "Hello!"}'` → 200 with conversation_id, response, tool_calls
- [x] T010 [P] [US1] Create `frontend/app/chat/page.tsx` as `"use client"` component with: (a) auth guard using `authClient.getSession()` on mount → redirect to `/login` if no session or no token; (b) state: `messages: {role, content, toolCalls}[]`, `input: string`, `loading: boolean`, `conversationId: number | null`, `error: string | null`; (c) welcome message as first item in messages on load; (d) `sendMessage()` function using direct `fetch()` to `${process.env.NEXT_PUBLIC_API_URL}/api/${userId}/chat` with `Authorization: Bearer <token>` header — first call sends `conversation_id: null`, subsequent calls send stored `conversationId`; (e) message bubbles: user messages right-aligned with blue background, assistant messages left-aligned with gray background; (f) green pill badges on assistant messages for each tool call: `"✅ tool_name"`; (g) animated 3-dot loading indicator while AI is responding (`animate-bounce` Tailwind class); (h) 4 quick action buttons pre-filling textarea only (NOT auto-sending): "📋 List Tasks" → "Show all my tasks", "➕ Add Task" → "I want to add a new task: ", "📧 Emails" → "Show my recent emails", "📊 Stats" → "Give me an overview of everything"; (i) `<textarea>` with `onKeyDown`: Enter = send, Shift+Enter = newline; send button disabled when input empty or loading; (j) `useRef` + `scrollIntoView` for auto-scroll to bottom on new message; (k) red inline error message on failure — UI does not crash; Tailwind only, no inline styles, no new CSS files
- [x] T011 [US1] Add one `<Link href="/chat">💬 Chat</Link>` to `frontend/components/Navbar.tsx` inside the right-side `<div className="flex items-center gap-3 sm:gap-4">` before the `<button>` Sign out element — import `Link` from `"next/link"` at the top of the file, style the link consistently with existing elements (e.g., `text-sm font-medium text-gray-700`) — no other changes to Navbar.tsx

**Checkpoint**: Navigate to `localhost:3000/chat` → welcome message appears → type "Add a task to buy milk" → task created (badge "✅ add_task" shown) → type "Mark it as done" → AI completes groceries task using conversation context. `conversationId` persists across messages in same session.

---

## Phase 4: User Story 2 (P2) — Email Inbox View via Chat

**Goal**: User types "Show my emails" and the AI retrieves seeded email records and presents them in a readable format.

**Independent Test**: Run `python seed_emails.py --user_id <id>` → in chat type "Show my emails" → AI calls `get_emails` tool and returns a formatted list of 8 emails with sender, subject, and preview. Type "Show my last 3 emails" → at most 3 returned.

### Implementation for User Story 2

- [x] T012 [US2] Create `backend/seed_emails.py` CLI script using `argparse` with required `--user_id` argument that inserts 8 sample `EmailLog` records into the database: include varied `from_address` values (e.g., "github@github.com", "noreply@netlify.app", "team@hackathon.dev"), descriptive `subject` lines, meaningful `preview` text (≤200 chars each), staggered `received_at` datetimes (7 days back to today), mix of `is_read=True/False` — print `"Successfully seeded 8 emails for user: {user_id}"` on completion — verify with: `python seed_emails.py --user_id <test_user_id>`
- [ ] T013 [US2] ⚠️ MANUAL Verify US2 end-to-end in browser: log in → go to `/chat` → type "Show my emails" → AI calls `get_emails` tool → response lists 8 emails with sender, subject, preview → type "Show my last 3 emails" → response contains at most 3 emails → type "Show my inbox" with no emails seeded for another user → friendly "No emails found" message

**Checkpoint**: AI lists seeded emails via chat. Empty inbox returns friendly message (not error).

---

## Phase 5: User Story 3 (P3) — Account Activity and Statistics

**Goal**: User asks about login history, project stats, and current time — AI returns live data from the database.

**Independent Test**: User types "Give me a complete overview" → AI calls `get_project_stats` → response includes total tasks, pending tasks, completed tasks, completion rate (%), conversation count, and last login timestamp.

### Implementation for User Story 3

- [x] T014 [P] [US3] Create `backend/routes/activity.py` with two protected endpoints: (a) `GET /api/{user_id}/activity` using `Depends(get_current_user)`, ownership check, returns last 20 `UserActivity` records WHERE user_id=user_id AND activity_type="login" ORDER BY created_at DESC as a list of dicts with `activity_type`, `ip_address` (or "Unknown"), `device` (or "Unknown device"), `created_at` formatted as human-readable string; (b) `GET /api/{user_id}/conversations` using `Depends(get_current_user)`, ownership check, returns last 20 `Conversation` records WHERE user_id=user_id ORDER BY updated_at DESC as list with `id`, `title`, `created_at`, `updated_at`
- [x] T015 [US3] Add HTTP login tracking middleware to `backend/main.py` (additive only — add before `app.include_router` calls): `@app.middleware("http")` async function that intercepts all requests, calls `response = await call_next(request)`, if `"/api/auth/sign-in"` in `str(request.url)` and `response.status_code == 200`: buffer response body (`body = b""; async for chunk in response.body_iterator: body += chunk`), parse `data = json.loads(body)`, extract `user_id = data.get("user", {}).get("id")`, parse IP from `request.client.host`, parse device from `User-Agent` header using `user_agents.parse()` → `f"{ua.browser.family} on {ua.os.family}"`, save `UserActivity(user_id, "login", ip, device)` in new `Session(engine)`, return `Response(content=body, status_code=response.status_code, headers=dict(response.headers), media_type=response.media_type)`; for all other requests return response unchanged — add `import json` and `from starlette.responses import Response` imports
- [x] T016 [US3] Register activity_router in `backend/main.py` (additive only — after chat_router registration): append `from routes.activity import router as activity_router` import and `app.include_router(activity_router, prefix="/api")` — restart server and verify: `curl -H "Authorization: Bearer <token>" http://localhost:8000/api/{user_id}/activity` → 200 with login events list; `curl ... /api/{user_id}/conversations` → 200 with conversation list

**Checkpoint**: Type "Who has logged into my account?" → AI calls `get_login_activity` and lists login events. Type "What time is it?" → AI calls `get_current_datetime` and returns readable date/time. Type "Give me a complete overview" → AI calls `get_project_stats` with all 7 data points.

---

## Phase 6: Polish & Verification

**Purpose**: Validate the complete Phase 3 feature end-to-end, confirm Phase 2 remains intact, and pass the security sign-off gate.

- [ ] T017 [P] Run Phase 2 regression test — verify all existing functionality unchanged after Phase 3 additions: `curl http://localhost:8000/health` → 200; `curl -H "Authorization: Bearer <token>" http://localhost:8000/api/{user_id}/tasks` → 200 with task list; create/edit/delete/complete task via dashboard UI; login/logout via browser — if anything breaks: STOP, revert the Phase 3 change that broke it, fix before continuing
- [ ] T018 Run full 10-command NL integration test from browser at `localhost:3000/chat` per `quickstart.md` Step 10 test table: "Add a task to buy groceries" → `add_task` ✅; "Show all my tasks" → `list_tasks` ✅; "What's still pending?" → `list_tasks(pending)` ✅; "Mark task 1 as done" → `complete_task` ✅; "Delete task 2" → `delete_task` ✅; "Change task 1 title to Call mom tonight" → `update_task` ✅; "Show my emails" → `get_emails` ✅; "Who has logged into my account?" → `get_login_activity` ✅; "What time is it right now?" → `get_current_datetime` ✅; "Give me a complete overview" → `get_project_stats` ✅
- [ ] T019 [P] Verify all edge cases: (a) empty message → send button disabled, nothing sent; (b) Groq rate limit hit → friendly retry message shown, UI does not crash; (c) unauthenticated user accesses `/chat` → redirected to `/login`; (d) URL `user_id` does not match JWT → 403 returned immediately; (e) task not found (ID 999) → AI responds with friendly "Task not found" and offers to list all tasks; (f) no session token → redirect to `/login`, no unhandled error
- [ ] T020 Pass security sign-off gate (all 5 layers — per tasks-template Security Sign-Off Gate section)

---

## Security Sign-Off Gate *(Constitution v1.1.0 — mandatory before marking feature DONE)*

> **This gate MUST pass before any task or feature is marked complete.**

**AUTH LAYER:**
- [ ] JWT verified on every new endpoint: `POST /api/{user_id}/chat`, `GET /api/{user_id}/activity`, `GET /api/{user_id}/conversations` all use `Depends(get_current_user)`
- [ ] 401 returned for missing/invalid token (handled by `get_current_user` dependency)
- [ ] Token expiry checked automatically via Better Auth JWT

**DATA LAYER:**
- [ ] All queries in chat.py, activity.py, and all 9 mcp_server.py tools filter by `user_id`
- [ ] URL `user_id` validated against `current_user["sub"]` in all new routes (403 on mismatch)
- [ ] No raw SQL — SQLModel ORM only in all new files

**SECRETS LAYER:**
- [ ] No secrets in source code — `GROQ_API_KEY` only in `backend/.env`
- [ ] `backend/.env` listed in `.gitignore`
- [ ] No secrets in git history

**PHASE 2 FREEZE LAYER:**
- [ ] No frozen Phase 2 file was modified: login, signup, dashboard, TaskList, TaskCard, TaskForm, api.ts, auth.ts, task.ts, tasks.py, auth.py, db.py all untouched
- [ ] `models.py` changes are append-only — existing `Task` model unchanged, 4 new classes + 2 schemas added at bottom
- [ ] `main.py` additions are additive only — existing routes/middleware untouched
- [ ] Phase 2 regression test passes (T017 green)

**AI SAFETY LAYER:**
- [ ] `user_id` not in any MCP tool JSON schema in `GROQ_TOOLS` — always injected by `execute_tool()`
- [ ] All 9 MCP tool functions wrapped in `try/except` returning `{"error": str(e)}` on failure
- [ ] Groq free tier used (`llama-3.3-70b-versatile`) — no OpenAI, no paid AI
- [ ] `max_tokens=1000` set in every Groq API call in `groq_agent.py`

**Sign-off**: `[ ] Security gate passed — Phase 3 feature ready for review`

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1 (Setup)**: No dependencies — start immediately
- **Phase 2 (Foundational)**: Depends on Phase 1 — BLOCKS all user story phases
- **Phase 3 (US1+US4 P1)**: Depends on Phase 2 — start immediately after foundation
- **Phase 4 (US2 P2)**: Depends on Phase 2 (models) + Phase 3 (chat endpoint + mcp_server.py exists) — start after Phase 3 complete
- **Phase 5 (US3 P3)**: Depends on Phase 2 (models) + Phase 3 (chat endpoint working) — can start after Phase 3
- **Phase 6 (Polish)**: Depends on all story phases complete

### User Story Dependencies

- **US1 + US4 (Phase 3)**: Must complete before US2 or US3 — provides core chat infrastructure
- **US2 (Phase 4)**: Independent of US3; can start after Phase 3; only needs mcp_server.py and seed data
- **US3 (Phase 5)**: Independent of US2; can start after Phase 3; needs activity.py and login middleware

### Within Each Phase

- T003 → T004 → T005 (sequential — same file, then table creation)
- T006 ∥ T007 ∥ T010 (parallel — different files: mcp_server.py / groq_agent.py / page.tsx)
- T008 depends on T007 (needs run_agent from groq_agent.py)
- T009 depends on T008 (register chat.py router)
- T011 depends on T010 existing (imports Link in Navbar)
- T014 ∥ T015 can be written in parallel (different files: activity.py / main.py middleware)
- T016 depends on T014 (registers activity router)

### Parallel Opportunities

```bash
# Phase 3 — launch all three in parallel:
Task T006: "Create backend/mcp_server.py with 9 tool functions"
Task T007: "Create backend/groq_agent.py with GROQ_TOOLS + run_agent"
Task T010: "Create frontend/app/chat/page.tsx client component"

# Phase 5 — launch two in parallel:
Task T014: "Create backend/routes/activity.py"
Task T015: "Add login tracking middleware to backend/main.py"

# Phase 6 — launch two in parallel:
Task T017: "Phase 2 regression test"
Task T019: "Edge case verification"
```

---

## Implementation Strategy

### MVP First (US1 + US4 Only — Phase 1 → Phase 3)

1. Complete Phase 1: Setup (T001–T002)
2. Complete Phase 2: Foundational (T003–T005) ← blocks everything
3. Complete Phase 3: US1 + US4 (T006–T011)
4. **STOP and VALIDATE**: Full chat works for task management with multi-turn context
5. Demo-ready at this point

### Incremental Delivery

1. Setup + Foundational → Foundation ready
2. US1+US4 → Task management AI chat works (MVP!)
3. US2 → Add email view capability
4. US3 → Add stats and activity view
5. Phase 6 → Regression + Integration + Security gate

### Solo Developer Order (Recommended)

```
T001 → T002 → T003 → T004 → T005
     → T006 (mcp_server.py)  ← write alongside T007
     → T007 (groq_agent.py)  ← write alongside T006
     → T008 (chat.py)
     → T009 (register router)
     → T010 (page.tsx)        ← write alongside T008 since API contract is fixed
     → T011 (Navbar link)
     → T012 (seed_emails.py)
     → T013 (verify US2)
     → T014 (activity.py)
     → T015 (login middleware)
     → T016 (register activity router)
     → T017 ∥ T019 (regression + edge cases)
     → T018 (10-command integration test)
     → T020 (security gate)
```

---

## Notes

- **[P]** tasks operate on different files — can be written simultaneously
- **US1/US4** are merged into Phase 3 because they share the chat endpoint implementation
- **No test files**: per spec, validation is manual (curl + browser) following quickstart.md
- **Frozen files** (`api.ts`, `tasks.py`, `auth.py`, `db.py`, frozen pages): never open these
- **models.py**: only append at EOF — read existing content first before editing
- **main.py**: only append new imports + router/middleware registrations — never modify existing code
- Commit after T005 (tables created), after T009 (backend chat working), after T011 (MVP complete), after T013 (US2 complete), after T016 (US3 complete), after T020 (security gate passed)
