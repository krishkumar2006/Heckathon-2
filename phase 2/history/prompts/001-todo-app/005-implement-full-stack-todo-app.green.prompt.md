---
id: 005
title: Implement Full-Stack Todo App
stage: green
date: 2026-02-28
surface: agent
model: claude-sonnet-4-6
feature: 001-todo-app
branch: 001-todo-app
user: HP
command: /sp.implement
labels: ["implementation","fastapi","nextjs","better-auth","full-stack"]
links:
  spec: specs/001-todo-app/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - backend/routes/tasks.py
  - frontend/lib/auth.ts
  - frontend/lib/auth-client.ts
  - frontend/lib/api.ts
  - frontend/app/api/auth/[...all]/route.ts
  - frontend/app/layout.tsx
  - frontend/app/page.tsx
  - frontend/app/(auth)/login/page.tsx
  - frontend/app/(auth)/signup/page.tsx
  - frontend/app/dashboard/page.tsx
  - frontend/components/Navbar.tsx
  - frontend/components/TaskForm.tsx
  - frontend/components/TaskCard.tsx
  - frontend/components/TaskList.tsx
  - specs/001-todo-app/tasks.md
tests:
  - npx tsc --noEmit (0 errors)
  - git ls-files | grep .env (no .env files tracked)
  - grep hardcoded secrets in source (none found)
---

## Prompt

/sp.implement — Execute the implementation plan by processing and executing all tasks defined in tasks.md

## Response snapshot

Executed full-stack Todo App implementation across 47 tasks in 8 phases:

**Phase 1 (Setup)**: Already complete — T001-T006 [x] in tasks.md. Verified .gitignore, CLAUDE.md files, .env.example files, and folder structure.

**Phase 2 (Foundational)**: Backend files (db.py, models.py, auth.py, main.py, routes/tasks.py skeleton) already existed [x]. Frontend (Next.js scaffold, better-auth installed, types/task.ts) already existed [x]. Marked T007-T019 as done.

**Phase 2 Frontend (T020-T024)**: Created via nextjs-task-ui-builder agent:
- `frontend/lib/auth.ts` — betterAuth with Neon PostgreSQL via @neondatabase/serverless + Kysely
- `frontend/lib/auth-client.ts` — createAuthClient with jwtClient plugin
- `frontend/app/api/auth/[...all]/route.ts` — toNextJsHandler(auth)
- `frontend/app/layout.tsx` — updated with Todo App title
- `frontend/lib/api.ts` — fetchWithAuth + all 6 typed API functions

**Phase 3 (US1, T025-T029)**: Created via nextjs-task-ui-builder agent:
- Root redirect page, login page, signup page, Navbar, dashboard placeholder

**Backend Endpoints (T030, T033, T037-T039, T042)**: Implemented via fastapi-backend-dev agent:
- All 6 endpoints in `backend/routes/tasks.py` with JWT auth, ownership check, user isolation
- Note: query param named `task_status` (not `status`) to avoid Python built-in conflict

**Phase 4-7 (T031-T036, T040-T041, T043)**: Implemented via nextjs-task-ui-builder agent:
- TaskForm with character count, validation, loading states
- TaskCard with all 3 modes: normal/edit inline/delete confirm + checkbox toggle
- TaskList with filter, empty state, loading spinner, sort by newest
- Dashboard converted to Client Component using authClient.useSession() with filter state

**API URL Fix**: Corrected frontend/lib/api.ts paths from `/users/{id}/tasks` to `/api/{id}/tasks` and methods from PATCH to PUT for updateTask, from `/toggle` to `/complete` for toggleComplete.

**Security verification**: No .env files tracked in git; no hardcoded secrets in source code; TypeScript: 0 errors.

**Phase 8 (T044-T047)**: Manual verification tasks left for user — require running servers.

## Outcome

- ✅ Impact: Complete full-stack Todo App implementation — all 43 automated tasks complete, 4 manual validation tasks remaining
- 🧪 Tests: TypeScript: 0 errors; no .env tracked in git; no hardcoded secrets found
- 📁 Files: 14 files created/modified across backend and frontend
- 🔁 Next prompts: Start both servers (uvicorn + npm run dev), run quickstart.md smoke test, run security curl checks from T045
- 🧠 Reflection: backend query param renamed to `task_status` to avoid Python built-in shadowing; frontend auth-client changed from better-auth/client to better-auth/react for useSession hook support

## Evaluation notes (flywheel)

- Failure modes observed: API path mismatch (frontend used /users/{id} vs backend /api/{id}); HTTP method mismatch (PATCH vs PUT for update); toggle endpoint path mismatch (/toggle vs /complete)
- Graders run and results (PASS/FAIL): TypeScript compile PASS; git .env check PASS; hardcoded secret scan PASS
- Prompt variant (if applicable): null
- Next experiment: Add automated integration test script to T044 for CI
