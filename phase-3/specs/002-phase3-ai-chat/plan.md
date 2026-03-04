# Implementation Plan: Phase 3 — AI Chat Assistant

**Branch**: `002-phase3-ai-chat` | **Date**: 2026-03-01 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/002-phase3-ai-chat/spec.md`

---

## Summary

Extend the Phase 2 Todo App with a fully functional AI chat assistant powered by the Groq
API (llama-3.3-70b-versatile, free tier). The chat page lets users manage tasks, view emails,
and check account stats via natural language. The backend adds 4 new SQLModel tables,
2 new FastAPI route files, an MCP tool server (9 tools), a Groq agent, and an HTTP
middleware for login tracking. The frontend adds a single chat page and one Navbar link.
All changes are purely additive — Phase 2 files are frozen.

---

## Technical Context

**Language/Version**: Python 3.11 (backend) · TypeScript 5 strict mode (frontend)
**Primary Dependencies**:
- Backend: FastAPI 0.110 · SQLModel 0.0.16 · Groq 0.11.0 · MCP 1.0.0 · python-dateutil 2.9.0 · user-agents 2.2.0
- Frontend: Next.js 16 (App Router) · React 19 · Tailwind CSS 4 · Better Auth

**Storage**: Neon Serverless PostgreSQL (SSL required) — same instance as Phase 2
**Testing**: Manual curl + browser integration tests (per spec success criteria)
**Target Platform**: Linux server (backend) · Browser (frontend)
**Project Type**: Web application — existing fullstack monorepo
**Performance Goals**: AI responds within 5 seconds on Groq free tier (SC-005)
**Constraints**:
- `max_tokens=1000` on all Groq calls (Law XVII, FR-016)
- Groq free tier: ~30 RPM — rate limit handled gracefully (429 → retry once + friendly message)
- Stateless server: no in-memory caches for user data (Law XIV)
- Phase 2 frozen files MUST remain untouched (Golden Rule)

**Scale/Scope**: Single-tenant hackathon demo; ~10–20 messages per conversation session.

---

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

> **Constitution v1.1.0** — All gates apply to Phase 2 and Phase 3 features.

**PHASE 2 GOLDEN RULE (Phase 3 features only):**
- [x] Feature is purely ADDITIVE — no Phase 2 files modified except `models.py` (append only)
- [x] All Phase 2 frozen files untouched (login, signup, dashboard, TaskList, TaskCard, TaskForm,
      api.ts, auth.ts, task.ts, tasks.py, auth.py, db.py)
  - **Exception**: `Navbar.tsx` — ADD 1 chat link only (no restructuring); `main.py` — ADD
    2 router imports + 1 middleware only; `models.py` — APPEND 4 new classes only

**AUTH GATE:**
- [x] Every new endpoint uses `Depends(get_current_user)` — no unprotected routes
- [x] JWT verified before any data access
- [x] 401 returned for missing/invalid token; 403 for ownership mismatch
  - Pattern: `_check_ownership(current_user, user_id)` (identical to tasks.py)

**DATA ISOLATION GATE:**
- [x] Every DB query filters by `user_id`
- [x] URL `user_id` validated against JWT `user_id` (`current_user["sub"]`)
- [x] New models (conversations, messages, user_activity, email_log) all include `user_id` index

**SECRETS GATE:**
- [x] `GROQ_API_KEY` in `backend/.env` only — not in any source file
- [x] `BETTER_AUTH_SECRET` identical in `frontend/.env.local` and `backend/.env`
- [x] `.env` files listed in `.gitignore`

**STATELESS SERVER GATE (Phase 3):**
- [x] No in-memory user state between requests
- [x] Conversation history loaded from DB on every chat request (Law XIV)

**FREE TIER GATE (Phase 3):**
- [x] Groq API used — not OpenAI, not any paid AI service (Law XII)
- [x] MCP SDK via `pip install mcp` — no paid tool SDK

**MCP TOOLS GATE (Phase 3):**
- [x] Each MCP tool opens and closes its own DB session (Law XVII)
- [x] No `user_id` in tool schemas — always injected server-side in `execute_tool()`
- [x] Every tool wrapped in `try/except` returning `{"error": str(e)}` on failure

**Complexity Violations** (fill only if a gate cannot be met):

| Gate | Why Cannot Meet | Mitigation |
|------|----------------|------------|
| RULE 4 (centralized API) | `api.ts` is frozen; chat page must call backend directly | Chat page makes direct `fetch()` with JWT; documented in research.md Decision 7 |

---

## Project Structure

### Documentation (this feature)

```text
specs/002-phase3-ai-chat/
├── plan.md              # This file (/sp.plan command output)
├── research.md          # Phase 0 output — all decisions resolved ✅
├── data-model.md        # Phase 1 output — 4 new tables + 2 schemas ✅
├── quickstart.md        # Phase 1 output — step-by-step dev guide ✅
├── contracts/
│   ├── chat-api.md      # POST /api/{user_id}/chat contract ✅
│   └── activity-api.md  # GET /api/{user_id}/activity + conversations + MCP tools ✅
└── tasks.md             # Phase 2 output (/sp.tasks command — NOT created by /sp.plan)
```

### Source Code (repository root)

```text
# Web application — existing fullstack monorepo

backend/
├── main.py              # ADD: 2 router imports + 1 login-tracking middleware
├── models.py            # APPEND: 4 new model classes (Conversation, Message,
│                        #          UserActivity, EmailLog) + 2 schemas (ChatRequest, ChatResponse)
├── mcp_server.py        # CREATE: 9 stateless tool functions
├── groq_agent.py        # CREATE: GROQ_TOOLS list + execute_tool() + async run_agent()
├── seed_emails.py       # CREATE: CLI script — inserts 8 sample emails for a user
├── routes/
│   ├── __init__.py      # existing — untouched
│   ├── tasks.py         # FROZEN — do not touch
│   ├── chat.py          # CREATE: POST /api/{user_id}/chat
│   └── activity.py      # CREATE: GET /api/{user_id}/activity + GET /api/{user_id}/conversations
├── auth.py              # FROZEN — do not touch
├── db.py                # FROZEN — do not touch
└── requirements.txt     # ADD: groq==0.11.0, mcp==1.0.0, python-dateutil==2.9.0, user-agents==2.2.0

frontend/
├── app/
│   ├── chat/
│   │   └── page.tsx     # CREATE: full AI chat UI (client component)
│   ├── dashboard/       # FROZEN — do not touch
│   └── (auth)/          # FROZEN — do not touch
├── components/
│   └── Navbar.tsx       # ADD: 1 "💬 Chat" link only (between app title and Sign out)
└── lib/
    └── api.ts           # FROZEN — do not touch
```

**Structure Decision**: Web application (Option 2) using existing `backend/` + `frontend/`
monorepo layout. All new files follow established conventions exactly. No new folders
created except `frontend/app/chat/`.

---

## Implementation Phases (Phase 3 Steps in Order)

### Step 1 — Groq API Key (Manual — human must do)
- Get free API key at `console.groq.com` (no credit card)
- Add `GROQ_API_KEY=gsk_xxxx` to `backend/.env`
- Verify: `python -c "import os; from dotenv import load_dotenv; load_dotenv(); print(os.getenv('GROQ_API_KEY')[:10])"`

### Step 2 — Install Phase 3 Dependencies
- Add to `backend/requirements.txt`: `groq==0.11.0`, `mcp==1.0.0`, `python-dateutil==2.9.0`, `user-agents==2.2.0`
- Run: `pip install groq==0.11.0 mcp==1.0.0 python-dateutil==2.9.0 user-agents==2.2.0`
- Verify: `python -c "import groq; import mcp; import dateutil; import user_agents; print('OK')"`

### Step 3 — Add New Models to models.py (APPEND ONLY)
- Add `Conversation`, `Message`, `UserActivity`, `EmailLog` model classes at bottom
- Add `ChatRequest`, `ChatResponse` Pydantic schemas after models
- Verify: `python -c "from models import Conversation, Message, UserActivity, EmailLog; print('OK')"`
- Create tables: `python -c "from db import engine; from models import SQLModel; SQLModel.metadata.create_all(engine); print('Tables created')"`
- **Acceptance**: 4 new tables in Neon dashboard; existing `tasks` table unchanged

### Step 4 — MCP Server (backend/mcp_server.py — CREATE)
- Implement 9 tool functions: `add_task`, `list_tasks`, `complete_task`, `delete_task`, `update_task`, `get_emails`, `get_login_activity`, `get_current_datetime`, `get_project_stats`
- Each function: (a) opens its own `Session(engine)`, (b) filters by `user_id`, (c) closes session, (d) wrapped in `try/except` → returns `{"error": str(e)}` on failure
- **Acceptance**: Each tool returns correct data dict; errors return `{"error": "..."}`

### Step 5 — Groq Agent (backend/groq_agent.py — CREATE)
- Define `GROQ_TOOLS` list (9 tool schemas, no `user_id` in schemas)
- Implement `execute_tool(tool_name, arguments, user_id)` dispatcher
- Implement `async run_agent(user_id, messages) -> dict`:
  - Prepend system prompt
  - Call Groq (`llama-3.3-70b-versatile`, `max_tokens=1000`, `tool_choice="auto"`)
  - If `finish_reason == "tool_calls"`: execute tools, send results back, get final response
  - Handle `groq.RateLimitError` (retry once with 1s delay, then friendly message)
  - Handle all other exceptions (return friendly error message)
- **Acceptance**: `run_agent("test_user", [{"role":"user","content":"Hello"}])` returns `{"response": str, "tool_calls": list}`

### Step 6 — Chat Endpoint (backend/routes/chat.py — CREATE)
- Implement `POST /api/{user_id}/chat` — 10-step stateless request cycle (see contracts/chat-api.md)
- Add to `main.py`: `from routes.chat import router as chat_router` + `app.include_router(chat_router, prefix="/api")`
- **Acceptance**: `curl -X POST .../api/{user_id}/chat -H "Authorization: Bearer <token>" -d '{"message": "Hello"}'` → 200 with `conversation_id`, `response`, `tool_calls`
- **Error paths**: 401 (bad JWT), 403 (ownership), 404 (conversation not found), 422 (empty message)

### Step 7 — Activity Tracking + Email Seed
- Create `backend/routes/activity.py`:
  - `GET /api/{user_id}/activity` → last 20 login events (DESC)
  - `GET /api/{user_id}/conversations` → last 20 conversations (DESC by `updated_at`)
- Add to `main.py`: `from routes.activity import router as activity_router` + `app.include_router(activity_router, prefix="/api")`
- Add HTTP middleware to `main.py` (before router registration):
  - Intercepts `/api/auth/sign-in` responses with status 200
  - Buffers response body to extract `user.id`
  - Saves `UserActivity(user_id, "login", ip, device)` to DB
  - Returns buffered response (no content change)
- Create `backend/seed_emails.py` with `--user_id` CLI arg, inserts 8 sample emails
- **Acceptance**: `python seed_emails.py --user_id <id>` → "Seeded 8 emails"

### Step 8 — Frontend Chat UI
- Create `frontend/app/chat/page.tsx` (`"use client"`):
  - Auth guard: `authClient.getSession()` → if no session → redirect `/login`
  - State: `messages[]`, `input`, `loading`, `conversationId`, `error`
  - Welcome message as first message on load
  - Message bubbles: user (right, blue), assistant (left, gray)
  - Tool call badges: green pill "✅ tool_name" on assistant messages
  - Animated 3-dot loading indicator (`animate-bounce`)
  - 4 quick action buttons pre-filling input (not auto-sending)
  - Textarea: Enter = send, Shift+Enter = newline
  - Auto-scroll to bottom on new message (`useRef` + `scrollIntoView`)
  - Red inline error on failure (no crash)
  - Direct `fetch()` to `${NEXT_PUBLIC_API_URL}/api/${userId}/chat` with JWT token attached
- Add to `frontend/components/Navbar.tsx` (ONE link, no restructuring):
  - `<Link href="/chat" className="...">💬 Chat</Link>` between app title and Sign out button
- **Acceptance**: Chat page loads, sends message, AI responds, tool badges shown

### Step 9 — Phase 2 Regression Test
- Verify: `/health`, `/api/{user_id}/tasks` (GET/POST/PUT/DELETE/PATCH), login, dashboard all work
- Any failure → STOP, revert Phase 3 change, fix before continuing (Golden Rule)

### Step 10 — Full Integration Test
- Test all 10 natural language commands from spec (SC-002)
- Verify 5-layer security checklist (SC-004)
- Verify AI responds within 5s (SC-005)
- Verify rate limit produces friendly message (SC-006)
- Verify unauthenticated access → redirect to `/login` (SC-007)
- Verify empty message disabled in UI (SC-008)

---

## Key Technical Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| AI Provider | Groq `llama-3.3-70b-versatile` | Free tier, function calling support, fast |
| Tool Protocol | MCP SDK (in-process, no transport) | Free, stateless, matches Law XVII |
| Login Tracking | HTTP middleware buffering response body | Purely additive; no existing code changed |
| Device Parsing | `user-agents==2.2.0` | Lightweight, returns "Browser on OS" format |
| Frontend Auth | `authClient.getSession()` directly in chat page | `api.ts` is frozen — direct fetch with JWT |
| Conversation History | Full load from DB on every request | Matches Law XIV (Stateless Server) |
| API Error Contract | HTTP 500 never returned from chat endpoint | Agent errors return 200 with friendly text |
| Date Format | Cross-platform `str(now.day)` (no `%-d`) | Windows compatibility (no `strftime %-d`) |

---

## Risk Analysis

| Risk | Blast Radius | Mitigation |
|------|-------------|------------|
| Groq rate limit (30 RPM free) | Chat feature degrades | Built-in retry (1x) + friendly 429 message |
| Login middleware breaks Phase 2 auth | All sign-in flows fail | Response body buffered and re-wrapped exactly; test immediately after adding |
| models.py append breaks existing Task table | All Phase 2 CRUD fails | Append-only SQLModel classes at EOF; verify `tasks` table unmodified after migration |

---

## Complexity Tracking

> **Exception documented**: Chat page makes direct `fetch()` instead of using `api.ts` because `api.ts` is frozen (Phase 2 constraint). This is explicitly permitted in spec FR-024 and documented in research.md Decision 7. The chat page itself is new code and still attaches JWT correctly.

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| Direct `fetch()` in chat page (violates RULE 4) | `api.ts` is frozen | Cannot add `sendChatMessage()` to frozen file; would break Golden Rule |
