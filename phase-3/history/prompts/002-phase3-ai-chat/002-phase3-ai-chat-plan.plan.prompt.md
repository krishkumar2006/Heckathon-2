---
id: 002
title: Phase 3 AI Chat Plan
stage: plan
date: 2026-03-01
surface: agent
model: claude-sonnet-4-6
feature: 002-phase3-ai-chat
branch: 002-phase3-ai-chat
user: architect
command: /sp.plan
labels: ["plan","phase3","groq","mcp","chat","ai-agent","fastapi","nextjs","data-model","contracts"]
links:
  spec: specs/002-phase3-ai-chat/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - specs/002-phase3-ai-chat/plan.md
  - specs/002-phase3-ai-chat/research.md
  - specs/002-phase3-ai-chat/data-model.md
  - specs/002-phase3-ai-chat/quickstart.md
  - specs/002-phase3-ai-chat/contracts/chat-api.md
  - specs/002-phase3-ai-chat/contracts/activity-api.md
  - history/prompts/002-phase3-ai-chat/002-phase3-ai-chat-plan.plan.prompt.md
tests:
  - n/a (plan stage — no tests run)
---

## Prompt

Phase 3 AI Chat implementation plan. Full 11-plan 38-task roadmap including:
- PLAN-01: Environment Setup (Groq API key, packages, connection verification)
- PLAN-02: New Database Models (Conversation, Message, UserActivity, EmailLog, schemas, table creation)
- PLAN-03: MCP Server Task Tools (add_task, list_tasks, complete_task, delete_task, update_task)
- PLAN-04: MCP Server Extra Tools (get_emails, get_login_activity, get_current_datetime, get_project_stats)
- PLAN-05: Groq AI Agent (groq_agent.py, GROQ_TOOLS schemas, execute_tool(), run_agent())
- PLAN-06: Chat API Endpoint (chat.py, activity.py, route registration, curl tests)
- PLAN-07: Activity Tracking + Email Seeds (login middleware, seed_emails.py)
- PLAN-08: Frontend Chat UI (page.tsx with MessageItem, state, bubbles, badges, loading, input, scroll)
- PLAN-09: Navbar Update (add "💬 Chat" link)
- PLAN-10: Phase 2 Regression Test (backend endpoints, frontend UI, security checks)
- PLAN-11: Full Integration Test (17 NL test cases including edge cases, security verification)

## Response snapshot

Executed full `/sp.plan` workflow:

1. Ran `setup-plan.ps1 -Json` → scaffolded `plan.md`, got FEATURE_SPEC and IMPL_PLAN paths.

2. Read existing codebase:
   - `backend/main.py`: FastAPI app with CORS, tasks_router, /health endpoint
   - `backend/models.py`: Task model with user_id/title/description/completed/created_at/updated_at
   - `backend/auth.py`: `get_current_user()` dependency using python-jose JWT HS256
   - `backend/db.py`: SQLModel engine + `get_session()` + `create_db_and_tables()`
   - `frontend/components/Navbar.tsx`: App name + logout button, no existing nav links
   - `backend/requirements.txt`: 6 packages (fastapi, uvicorn, sqlmodel, psycopg2, python-jose, dotenv)

3. Filled `plan.md`:
   - Technical Context: Python 3.11 + TS5, Groq + MCP + dateutil + user-agents
   - Constitution Check: All 7 gates PASS (Golden Rule, Auth, Data Isolation, Secrets, Stateless, Free Tier, MCP Tools)
   - Project Structure: Web application, 6 CREATE + 5 ADD-ONLY files
   - Phase 0 decisions: Groq provider, MCP as in-process tools, middleware tracking, UA parsing

4. Phase 0: Generated `research.md` with 8 key decisions:
   - AI provider: Groq llama-3.3-70b-versatile (free, tool_calls support)
   - Tool protocol: mcp==1.0.0 in-process (no transport server needed)
   - Login tracking: HTTP middleware with response body buffering for user_id extraction
   - UA parsing: user-agents==2.2.0 for "Browser on OS" format
   - Date formatting: python-dateutil with strftime patterns (cross-platform noted)
   - History strategy: Full load from DB on every request (stateless, hackathon scale)
   - Frontend auth: authClient.getSession() direct (frozen api.ts pattern exception)
   - Quick buttons: pre-fill only, no auto-send (per spec FR-023)

5. Phase 1: Generated all design artifacts:
   - `data-model.md`: 4 new SQLModel tables + 2 Pydantic schemas with full field specs
   - `contracts/chat-api.md`: POST /chat with 10-step cycle, request/response schemas, examples
   - `contracts/activity-api.md`: GET /activity, GET /conversations, all 9 GROQ_TOOLS schemas
   - `quickstart.md`: 10-step developer guide (Steps 1-10 from env setup to integration test)

6. Ran `update-agent-context.ps1 -AgentType claude` → updated CLAUDE.md with Phase 3 stack.

## Outcome

- ✅ Impact: Full architecture plan written for Phase 3 AI Chat (backend + frontend). 6 design artifacts produced. Agent context updated.
- 🧪 Tests: n/a (plan stage)
- 📁 Files: plan.md, research.md, data-model.md, quickstart.md, contracts/chat-api.md, contracts/activity-api.md
- 🔁 Next prompts: `/sp.tasks` → `/sp.implement`
- 🧠 Reflection: User input was a detailed 11-plan 38-task implementation roadmap. The plan translated
  this faithfully into SDD artifacts (research, data-model, contracts, quickstart). Key insight: login
  tracking middleware requires response body buffering — documented in research.md. Frontend auth
  exception (direct fetch vs. frozen api.ts) clearly documented and justified.

## Evaluation notes (flywheel)

- Failure modes observed: None — user input was comprehensive and all decisions were resolvable from context
- Graders run and results (PASS/FAIL): Constitution Check — all 7 gates PASS
- Prompt variant (if applicable): n/a
- Next experiment (smallest change to try): Proceed to /sp.tasks for implementation task generation
