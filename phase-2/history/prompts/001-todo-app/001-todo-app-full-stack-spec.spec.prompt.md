---
id: "001"
title: Todo App Full-Stack Spec
stage: spec
date: 2026-02-27
surface: agent
model: claude-sonnet-4-6
feature: 001-todo-app
branch: 001-todo-app
user: HP
command: /sp.specify
labels: ["spec","todo-app","fastapi","nextjs","jwt","better-auth","task-crud","hackathon"]
links:
  spec: specs/001-todo-app/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - specs/001-todo-app/spec.md
  - specs/001-todo-app/checklists/requirements.md
tests:
  - none
---

## Prompt

[User provided a detailed technical spec covering:]

Frontend dependencies (next@^16, react@^19, better-auth, tailwindcss@^4, typescript@^5)

SPEC 1.3 — TypeScript interfaces: Task, CreateTaskInput, UpdateTaskInput, ApiResponse<T>

SPEC 1.4 — frontend/lib/api.ts: centralized API client with JWT attachment, 6 functions
(getTasks, createTask, getTask, updateTask, deleteTask, toggleComplete), global 401/403/404/500
error handling.

SPEC 1.6 — App Router pages: layout.tsx, root redirect page, (auth)/login, (auth)/signup,
dashboard (Server Component, protected).

SPEC 1.7 — UI Components: Navbar, TaskForm, TaskList, TaskCard (with checkbox, edit inline,
delete confirm dialog, onUpdate callback).

Backend Task model with SQLModel: id, user_id, title, description, completed, created_at,
updated_at — with indexes on user_id, completed, and composite (user_id, completed).

Pydantic schemas: TaskCreate, TaskUpdate, TaskResponse.

SPEC 2.5 — backend/auth.py: JWT middleware using python-jose, HS256, verify_token(),
get_current_user() FastAPI dependency, HTTPException(401) on failure.

SPEC 2.6 — backend/main.py: FastAPI app, CORS middleware (FRONTEND_URL origin), /api router,
startup table creation, GET /health endpoint.

SPEC 2.7 — backend/routes/tasks.py: All 6 endpoints with JWT verify + ownership check +
user_id-filtered DB queries:
  GET    /api/{user_id}/tasks              → 200
  POST   /api/{user_id}/tasks              → 201
  GET    /api/{user_id}/tasks/{id}         → 200
  PUT    /api/{user_id}/tasks/{id}         → 200
  DELETE /api/{user_id}/tasks/{id}         → 204
  PATCH  /api/{user_id}/tasks/{id}/complete → 200

Golden Rule: frontend/ and backend/ are SEPARATE folders, environments, .env files.

## Response snapshot

Created branch `001-todo-app` and wrote `specs/001-todo-app/spec.md`. Translated
implementation-heavy technical input into user-facing spec with:
- 5 prioritized user stories (P1: Auth, P2: Create, P3: View/Filter, P4: Edit/Delete,
  P5: Toggle Complete)
- 19 testable functional requirements across Auth, Task Management, Data Isolation,
  and UI States
- 7 measurable, technology-agnostic success criteria
- Edge cases including cross-user 403 scenario
- Scope boundaries explicitly excluding: password reset, social login, sharing,
  pagination, file attachments
- Assumptions section capturing hackathon simplifications

Quality checklist at `specs/001-todo-app/checklists/requirements.md` — all 14 items
passed on first validation. Zero NEEDS CLARIFICATION markers.

## Outcome

- ✅ Impact: Feature spec created; all 5 user stories defined with acceptance scenarios; ready for /sp.plan
- 🧪 Tests: none (spec document)
- 📁 Files: specs/001-todo-app/spec.md, specs/001-todo-app/checklists/requirements.md
- 🔁 Next prompts: /sp.plan to generate architecture plan and implementation design
- 🧠 Reflection: User's input was implementation-level (code, file paths, endpoint logic).
  Successfully abstracted to user-value language while preserving all behavioral contracts.

## Evaluation notes (flywheel)

- Failure modes observed: User provided technical spec, not business spec — required
  full abstraction pass to comply with spec-template guidelines
- Graders run and results (PASS/FAIL): Manual quality checklist — all 14 items PASS
- Prompt variant (if applicable): none
- Next experiment (smallest change to try): run /sp.plan with this spec to validate
  that the abstracted requirements still drive the correct technical decisions
