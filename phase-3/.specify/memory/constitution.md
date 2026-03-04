<!--
SYNC IMPACT REPORT
==================
Version change: 1.0.0 → 1.1.0
Bump rationale: MINOR — Phase 3 additions: new stack articles, Golden Rule, 8 new constitutional
  laws, Phase 3 API contract, database schema laws, frontend laws, agent AI rules, extended
  security checklist, implementation steps 3-10, violation protocol additions, quick reference.
  No existing Phase 2 laws removed or redefined.

Modified sections:
  - API Contract → extended with 3 new Phase 3 endpoints
  - Security Constitution → extended with Phase 3 auth/data/secrets/AI-safety checks
  - Implementation Phases → extended with Phase 3 steps (3-10)
  - Violation Protocol → extended with Phase 3 common violations

Added sections:
  - Phase 3 Stack (Article I addition)
  - Golden Rule of Phase 3 (Article II)
  - Phase 3 Constitutional Laws (Laws X-XVII)
  - Phase 3 Database Laws (Article VI)
  - Phase 3 Frontend Laws (Article VII)
  - Phase 3 Agent AI Rules (Article VIII)
  - Phase 3 Quick Reference (Article IX)

Removed sections:
  - None (all Phase 2 content preserved)

Templates requiring updates:
  ✅ .specify/templates/plan-template.md  — Constitution Check gates include all Phase 3 laws
  ✅ .specify/templates/spec-template.md  — Security Requirements section (SR-001 to SR-014) added
  ✅ .specify/templates/tasks-template.md — Security Sign-Off Gate added (all 5 layers)

Deferred items:
  - TODO(GROQ_API_KEY): User must add actual key to backend/.env before running Phase 3.
  - TODO(LAW_7_BODY_ORIGINAL): Original Phase 2 Law VII wording partially reconstructed;
    confirmed intent preserved. Full verbatim wording TODO if team requires exact text.
-->

# Todo App — Hackathon Constitution

---

## Phase 2 Core Principles (FROZEN — Do Not Remove)

> **These laws govern Phase 2 (the existing Todo app) and remain permanently in force.**

### I. SPEC FIRST

Every feature begins with a written spec. The flow is strictly:
**Create spec → Get approval → Then code.**
No agent writes implementation code before a spec exists and is approved.
Rationale: prevents wasted effort and disqualification in a hackathon context where speed
requires clarity upfront.

### II. NO MANUAL CODING

All code MUST be generated through Claude Code.
No agent writes code directly by hand.
This is a hackathon rule — any violation disqualifies the project.
Rationale: consistency, auditability, and speed via AI-assisted generation.

### III. JWT ON EVERY ENDPOINT

Every single API endpoint MUST verify the JWT token before processing any request.
No endpoint is ever left unprotected.
No exceptions. "We'll add auth later" is not permitted.
Rationale: security cannot be retrofitted; every unprotected endpoint is a disqualifying
vulnerability in a production-ready hackathon demo.

### IV. USER DATA ISOLATION

Every database query MUST filter by `user_id`.
A user can NEVER see, edit, or delete another user's tasks, conversations, messages,
emails, or activity.
This rule is enforced at the **database query level**, not just the route level.
Rationale: data isolation is the primary multi-tenant security guarantee; route-level checks
alone are insufficient because ORM calls bypass them.

### V. SECRETS NEVER IN CODE

- `BETTER_AUTH_SECRET` lives ONLY in `.env` files.
- `DATABASE_URL` lives ONLY in `.env` files.
- `GROQ_API_KEY` lives ONLY in `backend/.env`.
- `.env` files are ALWAYS listed in `.gitignore`.
- If a secret appears in any source code file → **immediate stop and fix**.

Rationale: secrets in source code leak into git history and are unrotatable without
compromising the entire history.

### VI. SAME SECRET, BOTH SIDES

`BETTER_AUTH_SECRET` MUST be identical in:
- `frontend/.env.local`
- `backend/.env`

If they differ → auth breaks completely → 401 on every protected endpoint.
Rationale: Better Auth uses this secret to sign and verify JWT tokens across both services;
any mismatch makes every token invalid.

### VII. SPECS ARE SOURCE OF TRUTH

If a spec and implementation conflict, the spec wins.
No agent may change implemented behavior without first updating the spec and receiving approval.
Rationale: the spec is the contract; undocumented behavior is untestable and unmaintainable.

### VIII. FRONTEND COMPONENT RULES

Frontend development MUST follow these non-negotiable rules:

- **RULE 1 — Server Components by default.** Use `"use client"` ONLY when the component
  needs `useState`/`useEffect` hooks, browser event handlers, or browser-only APIs.
- **RULE 2 — No inline styles.** Tailwind CSS ONLY.
- **RULE 3 — TypeScript strict mode.** No `any` types permitted anywhere.
- **RULE 4 — Centralized API calls.** All API calls MUST go through `/frontend/lib/api.ts`
  only. No component makes direct `fetch()` calls to the backend.
- **RULE 5 — Always handle three UI states:** Loading (spinner), Error (message), Success (data).
- **RULE 6 — Protected routes.** Redirect to `/login` if no active session exists.
- **RULE 7 — JWT always attached.** JWT token MUST be attached to every API request.
  If token is missing → redirect to login; do NOT throw an unhandled error.

### IX. VIOLATION PROTOCOL

If any agent violates a Constitutional Law, it MUST follow these steps in order:

1. **STOP** immediately. Do not continue implementation.
2. **IDENTIFY** which law was violated.
3. **REVERT** the violating change.
4. **FIX** the root cause.
5. **VERIFY** the fix does not break other laws.
6. **RESUME** only after the fix is confirmed.

---

## Phase 3 Stack (ADDITIVE — Free Tier Only)

> Phase 3 extends the Todo app with AI chat, MCP tools, and activity tracking.
> All additions are free-tier only. No paid services. No OpenAI.

| Component | Technology | Cost |
|-----------|-----------|------|
| AI Model | Groq API (console.groq.com) | FREE |
| Tool Protocol | MCP SDK (`pip install mcp`) | FREE |
| Chat UI | Custom Next.js page | FREE |
| Backend | Python FastAPI (Phase 2) | unchanged |
| ORM | SQLModel (Phase 2) | unchanged |
| Database | Neon Serverless PostgreSQL (Phase 2) | unchanged |
| Auth | Better Auth + JWT (Phase 2) | unchanged |

**Free Tier Commitments (NEVER replace with paid):**
- Groq API: FREE tier — no credit card, no OpenAI, no paid AI
- MCP SDK: `pip install mcp` — completely free
- Chat UI: custom built — no OpenAI ChatKit
- All others: same free tools as Phase 2

---

## The Golden Rule of Phase 3

**PHASE 2 MUST NEVER BREAK.**

This is the most important rule in Phase 3.
All Phase 3 work is purely ADDITIVE.
You only ADD new files, new routes, new models.
You NEVER modify, delete, or refactor Phase 2 code.

### Phase 2 Frozen Files (NEVER touch)

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
backend/models.py       ← ONLY add new model classes; never remove or change existing ones
```

The ONE exception to `models.py`: You MAY add new SQLModel classes at the bottom.
You MUST NOT modify or delete existing model classes.

---

## Phase 3 Constitutional Laws

### LAW X — JWT ON ALL NEW ROUTES

Applies to: `/api/{user_id}/chat` and all new Phase 3 routes.
Same auth middleware as Phase 2 (`Depends(get_current_user)`).
No Phase 3 endpoint is ever left unprotected.

### LAW XI — ADDITIVE ONLY

All Phase 3 changes MUST be purely additive.
If any Phase 2 test fails after a Phase 3 change → STOP and revert.
"We'll fix Phase 2 later" is never acceptable.

### LAW XII — GROQ FREE TIER ONLY

MUST use Groq API at console.groq.com — free tier.
MUST NOT use OpenAI, Anthropic, or any paid AI service.
MUST NOT use any AI SDK that requires a credit card.
If Groq rate limit is hit → return 429 with friendly message; do not switch providers.

### LAW XIII — USER DATA ISOLATION (EXTENDED)

Every database query MUST filter by `user_id` for ALL new models:
- `conversations` → WHERE user_id = current_user.id
- `messages` → WHERE conversation.user_id = current_user.id
- `user_activity` → WHERE user_id = current_user.id
- `email_log` → WHERE user_id = current_user.id

URL `user_id` MUST be validated against JWT `user_id`.
Return 403 if they don't match.

### LAW XIV — STATELESS SERVER

Server holds NO state between requests.
All state lives in Neon database only.
Conversation history MUST be loaded from DB on every chat request.
Any server restart MUST lose nothing (no in-memory caches for user data).

### LAW XV — SECRETS IN ENV ONLY (EXTENDED)

Phase 3 adds one new secret:
- `GROQ_API_KEY` → ONLY in `backend/.env`

No API keys appear in any source file.
`.env` files are in `.gitignore`.
No secrets in git history.

### LAW XVI — SPEC FIRST (EXTENDED)

Read the spec before writing any Phase 3 code.
Read the plan before starting any Phase 3 task.
No code is written without a spec backing it.
This law applies identically to Phase 3 as to Phase 2.

### LAW XVII — MCP TOOLS ARE STATELESS

Every MCP tool MUST open its own DB session.
Every MCP tool MUST close its session after use.
No tool stores state between invocations.
Tools NEVER include `user_id` as a schema parameter — it is always injected server-side.

---

## API Contract

### Phase 2 Endpoints (FROZEN — never rename, restructure, or remove)

| METHOD | ENDPOINT | STATUS CODE |
|--------|----------------------------------------|-------------|
| GET | `/api/{user_id}/tasks` | 200 |
| POST | `/api/{user_id}/tasks` | 201 |
| GET | `/api/{user_id}/tasks/{id}` | 200 |
| PUT | `/api/{user_id}/tasks/{id}` | 200 |
| DELETE | `/api/{user_id}/tasks/{id}` | 204 |
| PATCH | `/api/{user_id}/tasks/{id}/complete` | 200 |

### Phase 3 Endpoints (NEW)

| METHOD | ENDPOINT | STATUS | DESCRIPTION |
|--------|--------------------------------------|--------|-------------|
| POST | `/api/{user_id}/chat` | 200 | Send AI message |
| GET | `/api/{user_id}/activity` | 200 | Login activity |
| GET | `/api/{user_id}/conversations` | 200 | List past chats |
| GET | `/health` | 200 | Health check (already exists) |

**Chat Request Format** (`POST /api/{user_id}/chat`):

```json
{
  "conversation_id": "integer | null",
  "message": "string (required, 1-2000 chars)"
}
```

**Chat Response Format**:

```json
{
  "conversation_id": "integer",
  "response": "string",
  "tool_calls": [{"tool": "string", "result": {}}]
}
```

**Error Response Standards** (ALL agents MUST follow for ALL endpoints):

| Code | Meaning |
|------|---------|
| 401 | Missing or invalid JWT token |
| 403 | Authenticated user does not own this resource |
| 404 | Task or resource not found |
| 422 | Validation error (bad input data / empty message) |
| 429 | Groq rate limit hit (friendly message required) |
| 500 | Server or database error |

---

## Database Laws (Phase 3)

### New Tables

| Table | Purpose |
|-------|---------|
| `conversations` | Chat sessions |
| `messages` | Full chat history |
| `user_activity` | Login tracking |
| `email_log` | Email records |

### Schema Rules

- **RULE 1** — Every new table MUST have: `user_id` (indexed), `created_at` (UTC default),
  primary key auto-increment.
- **RULE 2** — Never hard delete conversations or messages.
  For hackathon: hard delete is acceptable. If soft delete needed later: add `is_deleted` bool.
- **RULE 3** — Message history MUST be loaded in ASC order (`ORDER BY created_at ASC`).
  This ensures correct conversation flow for AI.
- **RULE 4** — Conversation title = `first_message[:100]`.
  Set when conversation is first created. Never update the title after creation.
- **RULE 5** — `models.py` is the only file where new models go.
  Add new SQLModel classes at the bottom only. Never modify existing classes.

---

## Frontend Laws (Phase 3)

- **RULE 1** — Chat page is the ONLY new page.
  Path: `frontend/app/chat/page.tsx`. No other new pages without explicit approval.

- **RULE 2** — Navbar gets ONE new link only.
  Add "💬 Chat" link between Dashboard and Logout.
  Do not restructure or restyle the Navbar. Do not change existing links.

- **RULE 3** — Chat UI uses Tailwind only.
  No new CSS files. No inline styles. No new UI libraries.

- **RULE 4** — Chat page MUST show three states:
  - Loading: animated typing indicator
  - Error: red error message, not crash
  - Success: assistant message with tool badges

- **RULE 5** — JWT token MUST be attached to chat API calls.
  Same pattern as `frontend/lib/api.ts`. Get session from authClient.
  Attach `Authorization: Bearer <token>`. If no token → redirect to `/login`.

- **RULE 6** — Conversation ID MUST be persisted in state.
  First message → `conversationId` is null.
  After first response → store `conversationId`.
  All subsequent messages send that `conversationId`.

---

## Agent / AI Rules (Phase 3)

These rules govern how the Groq AI agent behaves.

- **RULE 1** — Agent uses tool schemas without `user_id`.
  Tool schemas NEVER include `user_id` as a parameter.
  `user_id` is always injected in `execute_tool()` on the server side.
  The user never needs to say their own user ID.

- **RULE 2** — Agent MUST always call a tool (never make up data).
  - User asks about tasks → call a task tool.
  - User asks about emails → call `get_emails`.
  - User asks about time → call `get_current_datetime`.
  Never fabricate data without calling a tool first.

- **RULE 3** — Full conversation history on every call.
  Pass complete message history to Groq on every request.
  Include system prompt at the beginning always.
  History loaded fresh from database every request.

- **RULE 4** — Max tokens: 1000 per response.
  Set `max_tokens=1000` in all Groq API calls.
  This controls cost and response length.

---

## Security Constitution

**MANDATORY SECURITY CHECKLIST**
Every agent MUST verify this checklist before marking any task complete:

**AUTH LAYER:**
- ✓ JWT token verified on every Phase 2 endpoint
- ✓ JWT token verified on `/api/{user_id}/chat` (Phase 3)
- ✓ JWT token verified on `/api/{user_id}/activity` (Phase 3)
- ✓ Token expiry checked (7 days max)
- ✓ `BETTER_AUTH_SECRET` same in both services
- ✓ Authorization header format: `Bearer <token>`
- ✓ 401 returned for missing or invalid token

**DATA LAYER:**
- ✓ Every task query filtered by authenticated `user_id`
- ✓ Every conversation query filtered by `user_id`
- ✓ Every message query filtered by conversation owner's `user_id`
- ✓ Every email query filtered by `user_id`
- ✓ Every activity query filtered by `user_id`
- ✓ URL `user_id` validated against JWT `user_id`
- ✓ 403 returned for ownership mismatch
- ✓ No raw SQL queries (use SQLModel ORM only)

**SECRETS LAYER:**
- ✓ No secrets in source code
- ✓ No secrets in git history
- ✓ `.env` in `.gitignore`
- ✓ `GROQ_API_KEY` only in `backend/.env`
- ✓ Different secrets for dev and production

**NETWORK LAYER:**
- ✓ CORS allows only frontend origin
- ✓ HTTPS in production
- ✓ No sensitive data in URLs or logs

**AI SAFETY LAYER:**
- ✓ AI cannot access other users' data (user_id always server-injected)
- ✓ Tool results are user-scoped always
- ✓ Rate limit errors (429) handled gracefully
- ✓ AI errors never crash the server (all tools wrapped in try/except)

---

## Implementation Phases

All implementation MUST proceed through phases in order. No phase may be marked
complete without passing its checkpoint.

### Phase 2 Phases (COMPLETED)

**PHASE 1 — Project Setup** ✅
**PHASE 2 — Database & Models** ✅
**PHASE 3 — Backend Auth** ✅
**PHASE 4 — Backend CRUD** ✅
**PHASE 5 — Frontend Auth** ✅
**PHASE 6 — Frontend CRUD** ✅
**PHASE 7 — Integration** ✅

### Phase 3 Steps (NEW — execute in order)

**STEP 1 — Groq API Key**
- [ ] Get free API key at console.groq.com (no credit card)
- [ ] Add `GROQ_API_KEY=gsk_xxxx` to `backend/.env`
- [ ] Verify key works before proceeding

**STEP 2 — Install Phase 3 Dependencies**
- [ ] Add `mcp`, `groq` to `backend/requirements.txt`
- [ ] Run `pip install -r requirements.txt`
- [ ] Verify imports work

**STEP 3 — Add New Models to models.py**
- [ ] Add `Conversation` model (append only, no existing model changes)
- [ ] Add `Message` model
- [ ] Add `UserActivity` model
- [ ] Add `EmailLog` model
- [ ] Verify Phase 2 models untouched

**STEP 4 — MCP Server**
- [ ] Create `backend/mcp_server.py`
- [ ] Implement all 9 tools
- [ ] Test each tool independently

**STEP 5 — Groq Agent**
- [ ] Create `backend/groq_agent.py`
- [ ] Define all 9 tool schemas
- [ ] Implement `run_agent()` function
- [ ] Test with sample message

**STEP 6 — Chat Endpoint**
- [ ] Create `backend/routes/chat.py`
- [ ] Implement stateless request cycle
- [ ] Register router in `main.py`
- [ ] Test with curl

**STEP 7 — Activity Tracking**
- [ ] Create `backend/routes/activity.py`
- [ ] Add login tracking middleware
- [ ] Seed emails: `python seed_emails.py`

**STEP 8 — Frontend Chat UI**
- [ ] Create `frontend/app/chat/page.tsx`
- [ ] Add Chat link to Navbar only (one link, no restructure)
- [ ] Test in browser

**STEP 9 — Phase 2 Regression Test**
- [ ] Verify all Phase 2 features still work
- [ ] Fix anything broken before continuing

**STEP 10 — Full Integration Test**
- [ ] Test all natural language commands via chat
- [ ] Verify security checklist passes

---

## Violation Protocol (Extended for Phase 3)

When any Constitutional Law is violated, follow Law IX steps (Stop, Identify, Revert, Fix,
Verify, Resume).

**Common violations and mandatory fixes:**

| Violation | Mandatory Fix |
|-----------|---------------|
| Endpoint created without JWT check | Add `Depends(get_current_user)` immediately, retest |
| Secret found in source code | Remove from code, rotate the secret, add to `.env` |
| Query not filtered by `user_id` | Add `WHERE user_id = current_user.id` to query |
| Code written without reading spec | Stop, read spec, verify code matches |
| OpenAI or paid AI used | Remove immediately, replace with Groq free tier |
| Phase 2 file modified | Restore original from git, implement differently |
| Tool returns another user's data | Add `user_id` filter to every DB query in that tool |
| Server crashes on bad input | Add `try/except` to all tool functions and agent runner |
| Tool raises exception instead of returning error | Wrap in `try/except`, return `{"error": str(e)}` |
| Phase 2 test fails after Phase 3 change | STOP immediately, revert Phase 3 change |

---

## Quick Reference (Phase 3)

### New Files in Phase 3

```
backend/mcp_server.py          ← MCP tools (9 tools)
backend/groq_agent.py          ← AI agent + tool schemas
backend/routes/chat.py         ← chat endpoint
backend/routes/activity.py     ← activity endpoint
backend/seed_emails.py         ← email seed script
frontend/app/chat/page.tsx     ← chat UI
```

### Modified Files in Phase 3

```
backend/models.py              ← add 4 new model classes only (bottom of file)
backend/main.py                ← add 2 new router imports only
backend/requirements.txt       ← add mcp, groq packages only
frontend/components/Navbar.tsx ← add Chat link only (one link, no restructure)
backend/.env                   ← add GROQ_API_KEY only
```

### Frozen Files (NEVER touch)

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

### Run Commands

```bash
# Backend
cd backend && uvicorn main:app --reload --port 8000

# Frontend
cd frontend && npm run dev

# Seed emails
cd backend && python seed_emails.py --user_id <id>

# Test DB connection
cd backend && python -c "from db import engine; print('OK')"

# Test AI agent
cd backend && python -c "
import asyncio, os
from dotenv import load_dotenv
load_dotenv()
from groq_agent import run_agent
r = asyncio.run(run_agent('u1', [{'role':'user','content':'hi'}]))
print(r)"
```

### Environment Variables Added in Phase 3

```
backend/.env       → GROQ_API_KEY=gsk_xxxx
frontend/.env.local → nothing new needed
```

---

## Governance

This constitution supersedes all other practices, preferences, or prior agreements.

**Amendment procedure:**
1. Propose the amendment in writing with rationale.
2. Get explicit team approval before merging.
3. Update this file, increment the version, update `LAST_AMENDED_DATE`.
4. Propagate changes to `.specify/templates/` as needed.

**Versioning policy:**
- MAJOR: Removal or redefinition of a Constitutional Law.
- MINOR: New law, article, or materially expanded guidance added.
- PATCH: Clarifications, wording fixes, non-semantic refinements.

**Compliance review:**
- Every PR MUST pass the Security Constitution checklist before merge.
- Every completed task MUST pass the relevant phase checkpoint.
- Any agent detecting a violation MUST follow Law IX (Violation Protocol) immediately.
- Phase 3 tasks MUST also pass the Phase 2 regression test (Step 9) before marking done.

**Version**: 1.1.0 | **Ratified**: 2026-02-27 | **Last Amended**: 2026-03-01
