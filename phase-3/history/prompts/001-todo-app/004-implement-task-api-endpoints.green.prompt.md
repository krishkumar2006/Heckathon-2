---
id: "004"
title: Implement Task API Endpoints
stage: green
date: 2026-02-28
surface: agent
model: claude-sonnet-4-6
feature: 001-todo-app
branch: 001-todo-app
user: developer
command: "implement all 6 task API endpoints in backend/routes/tasks.py"
labels: ["fastapi","jwt","sqlmodel","crud","tasks","backend"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - backend/routes/tasks.py
tests:
  - "[ ] 401 raised when Authorization header is missing"
  - "[ ] 403 raised when token sub != URL user_id"
  - "[ ] GET /api/{user_id}/tasks returns [] when user has no tasks"
  - "[ ] GET /api/{user_id}/tasks?task_status=pending filters to completed==False"
  - "[ ] GET /api/{user_id}/tasks?task_status=completed filters to completed==True"
  - "[ ] POST /api/{user_id}/tasks returns 201 with TaskResponse"
  - "[ ] GET /api/{user_id}/tasks/{task_id} returns 404 when task not found"
  - "[ ] PUT /api/{user_id}/tasks/{task_id} only updates non-None fields"
  - "[ ] PUT /api/{user_id}/tasks/{task_id} sets updated_at to utc now"
  - "[ ] DELETE /api/{user_id}/tasks/{task_id} returns 204 with no body"
  - "[ ] PATCH /api/{user_id}/tasks/{task_id}/complete toggles completed flag"
  - "[ ] All queries filter WHERE user_id == user_id"
---

## Prompt

You need to implement all 6 task API endpoints in `backend/routes/tasks.py` for a Todo App. The working directory is `D:\Heckathon 2\Todo`.

## Current State
- `backend/routes/tasks.py` is just a skeleton with `router = APIRouter()`
- `backend/main.py` already imports and includes the router with `prefix="/api"`
- `backend/auth.py` has `get_current_user` dependency
- `backend/db.py` has `get_session` dependency
- `backend/models.py` has `Task`, `TaskCreate`, `TaskUpdate`, `TaskResponse` models

## Files to Read First
Please read these files before implementing:
1. `D:\Heckathon 2\Todo\backend\models.py`
2. `D:\Heckathon 2\Todo\backend\auth.py`
3. `D:\Heckathon 2\Todo\backend\db.py`

## Implementation Required: `backend/routes/tasks.py`

Replace the skeleton with the complete implementation of all 6 endpoints:

### Pattern for EVERY endpoint:
```python
1. current_user = Depends(get_current_user)  → 401 if no/bad token
2. if current_user["sub"] != user_id → raise HTTPException(403)
3. all queries MUST filter WHERE user_id == user_id
```

### Endpoints to implement:

**T033: GET /api/{user_id}/tasks** — list with optional status filter
**T030: POST /api/{user_id}/tasks** — create, return 201
**T037: GET /api/{user_id}/tasks/{task_id}** — get single, 404 if missing
**T038: PUT /api/{user_id}/tasks/{task_id}** — partial update, updated_at refresh
**T039: DELETE /api/{user_id}/tasks/{task_id}** — delete, return 204
**T042: PATCH /api/{user_id}/tasks/{task_id}/complete** — toggle completed

## Response snapshot

Implemented all 6 endpoints in `D:\Heckathon 2\Todo\backend\routes\tasks.py`.

Key decisions made from reading source files:
- `user_id` is `str` in the Task model, so URL param declared as `str`
- Ownership extracted via `current_user["sub"]` (JWT subject claim)
- Session is sync SQLModel `Session` (not async)
- Used `select(Task).where(...)` + `session.exec().first()` for all single-row queries
- List query uses `session.exec(...).all()` returning empty list (not 404) for no tasks
- Status filter uses query param `task_status` (not `status`, to avoid shadowing builtins)
- All mutating endpoints call `session.add()`, `session.commit()`, `session.refresh()`
- DELETE returns `Response(status_code=204)` with no body

## Outcome

- Impact: All 6 protected CRUD endpoints are now implemented. The router was previously empty; the backend is now functionally complete for task management.
- Tests: Acceptance checklist embedded in front-matter; no automated tests run yet.
- Files: backend/routes/tasks.py (created from skeleton)
- Next prompts: Add integration tests; wire up frontend task API calls; validate Neon SSL connection string in .env
- Reflection: Reading models.py first was essential — discovering user_id is str (not int) prevents a class of 403/404 bugs.

## Evaluation notes (flywheel)

- Failure modes observed: none during implementation
- Graders run and results (PASS/FAIL): none yet
- Prompt variant (if applicable): initial implementation
- Next experiment: run integration tests against a local Neon dev DB to verify all status codes
