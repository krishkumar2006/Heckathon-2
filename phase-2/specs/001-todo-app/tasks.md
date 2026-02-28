---
description: "Task list for Todo App — Full-Stack Task Manager"
---

# Tasks: Todo App — Full-Stack Task Manager

**Input**: Design documents from `/specs/001-todo-app/`
**Prerequisites**: plan.md ✅ spec.md ✅ research.md ✅ data-model.md ✅ contracts/ ✅ quickstart.md ✅

**Tests**: No automated test suite (manual verification per quickstart.md and security checklist).

**Organization**: Tasks are grouped by user story to enable independent implementation and
testing of each story. Backend foundational tasks must complete before any user story begins.

## Format: `[ID] [P?] [Story?] Description`

- **[P]**: Can run in parallel (different files, no unresolved dependencies)
- **[Story]**: Which user story this task belongs to (US1–US5)
- All task descriptions include exact file paths

## Path Conventions

- Backend: `backend/` at repository root
- Frontend: `frontend/` at repository root
- Both are **separate environments** — never import one from the other

---

## Phase 1: Setup (Project Foundation)

**Purpose**: Scaffold directory structure, security files, and developer guidance docs.

- [x] T001 Create folder structure: `frontend/`, `backend/`, `backend/routes/` at repository root
- [x] T002 Create root `.gitignore` with entries: `frontend/.env.local`, `frontend/.env*.local`, `backend/.env`, `backend/.env.*`, `frontend/node_modules/`, `backend/__pycache__/`, `backend/venv/`, `backend/.venv/`, `frontend/.next/`
- [x] T003 [P] Create `backend/.env.example` with keys: `BETTER_AUTH_SECRET=generate-32-char-random-string`, `DATABASE_URL=postgresql://user:pass@host/dbname?sslmode=require`, `FRONTEND_URL=http://localhost:3000`
- [x] T004 [P] Create `frontend/.env.example` with keys: `BETTER_AUTH_SECRET=same-secret-as-backend`, `NEXT_PUBLIC_API_URL=http://localhost:8000`, `BETTER_AUTH_URL=http://localhost:3000`, `DATABASE_URL=your-neon-connection-string`
- [x] T005 [P] Create `backend/CLAUDE.md` documenting: stack (FastAPI + SQLModel + Neon PostgreSQL), JWT rule (every endpoint uses `Depends(get_current_user)`), user isolation rule (every query filters `WHERE user_id = current_user["sub"]`), run command (`uvicorn main:app --reload --port 8000`), env var list
- [x] T006 [P] Create `frontend/CLAUDE.md` documenting: stack (Next.js 16 + React 19 + TypeScript 5 + Tailwind 4 + Better Auth), Server Components by default rule, Tailwind-only styling rule, centralized API rule (all calls via `lib/api.ts`), run command (`npm run dev`), env var list

**Checkpoint**: Directory structure exists; `.gitignore` protects all `.env` files; documentation files present.

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Backend infrastructure + frontend scaffold that ALL user stories depend on.

**⚠️ CRITICAL**: No user story work can begin until this phase is complete.

### Backend Foundation

- [x] T007 Create `backend/requirements.txt` with: `fastapi==0.110.0`, `uvicorn[standard]==0.27.0`, `sqlmodel==0.0.16`, `psycopg2-binary==2.9.9`, `python-jose[cryptography]==3.3.0`, `python-dotenv==1.0.0`
- [x] T008 Create Python virtual environment in `backend/venv/` (`python -m venv venv`) and install all requirements (`pip install -r requirements.txt`)
- [x] T009 Create `backend/.env` (real values — never commit): obtain `DATABASE_URL` from Neon dashboard (must include `?sslmode=require`); set `FRONTEND_URL=http://localhost:3000`
- [x] T010 Create `backend/db.py`: load `DATABASE_URL` from env via `python-dotenv`; create SQLModel `engine`; implement `get_session()` as a FastAPI dependency that yields a `Session` and closes after request
- [x] T011 Create `backend/models.py`: define `Task` SQLModel table with fields `id` (int PK), `user_id` (str, `index=True`), `title` (str, min 1, max 200), `description` (Optional[str], max 1000), `completed` (bool, default False, `index=True`), `created_at` (datetime, default UTC now), `updated_at` (datetime, default UTC now); add composite index on `(user_id, completed)`; define `TaskCreate`, `TaskUpdate`, `TaskResponse` Pydantic schemas
- [x] T012 [P] Create empty `backend/routes/__init__.py`
- [x] T013 Create `backend/routes/tasks.py`: initialize `APIRouter()` instance; add all imports (`db`, `models`, `auth`); no endpoints yet — router skeleton only
- [x] T014 Create `backend/main.py`: create `FastAPI()` instance; load `.env` with `python-dotenv`; add `CORSMiddleware` (origins from `FRONTEND_URL` env var, `allow_credentials=True`, methods `GET POST PUT DELETE PATCH`, headers `Authorization Content-Type`); add startup event `SQLModel.metadata.create_all(engine)`; add `GET /health → {"status": "ok"}`; import and include tasks router with `prefix="/api"`
- [x] T015 Generate `BETTER_AUTH_SECRET` using `openssl rand -base64 32`; update `backend/.env` with the generated value; start backend with `uvicorn main:app --reload --port 8000`; verify `GET http://localhost:8000/health` returns `{"status":"ok"}`
- [x] T016 Create `backend/auth.py`: load `BETTER_AUTH_SECRET` from env; implement `verify_token(token: str) → dict` that calls `jose.jwt.decode(token, secret, algorithms=["HS256"])`, returns payload on success, raises `HTTPException(status_code=401)` on any failure; implement `get_current_user(credentials=Depends(HTTPBearer())) → dict` that extracts Bearer token, calls `verify_token`, returns user dict, raises `HTTPException(401)` if any error

### Frontend Foundation

- [x] T017 Scaffold Next.js app: run `npx create-next-app@latest frontend --typescript --tailwind --app --no-src-dir --import-alias "@/*"` from repo root; then run `cd frontend && npm install better-auth`
- [x] T018 Create `frontend/.env.local` (real values — never commit): `BETTER_AUTH_SECRET=<SAME value as backend/.env>`, `NEXT_PUBLIC_API_URL=http://localhost:8000`, `BETTER_AUTH_URL=http://localhost:3000`, `DATABASE_URL=<same Neon connection string as backend>`
- [x] T019 [P] Create `frontend/types/task.ts` with strict TypeScript interfaces (no `any`): `Task` (id, user_id, title, description|null, completed, created_at, updated_at), `CreateTaskInput` (title required, description optional), `UpdateTaskInput` (title optional, description optional), `ApiResponse<T>` (data, error?), `User` (id, email, name)
- [x] T020 Create `frontend/lib/auth.ts` (server-only): call `betterAuth({ database: neon(DATABASE_URL), secret: BETTER_AUTH_SECRET, plugins: [jwt({ expirationTime: "7d" })] })`; export `auth` object
- [x] T021 Create `frontend/lib/auth-client.ts` (client-safe, `"use client"` compatible): call `createAuthClient({ baseURL: process.env.BETTER_AUTH_URL, plugins: [jwtClient()] })`; export `authClient`
- [x] T022 Create `frontend/app/api/auth/[...all]/route.ts`: export `GET` and `POST` from `auth.handler` imported from `frontend/lib/auth.ts`
- [x] T023 Update `frontend/app/layout.tsx`: add `"use client"` to a session provider wrapper component; import global Tailwind CSS; wrap children with Better Auth session provider; set `metadata = { title: "Todo App" }`
- [x] T024 Create `frontend/lib/api.ts`: implement `fetchWithAuth(path, options)` helper that calls `authClient.getSession()`, extracts JWT token (if no token → `redirect("/login")`), adds `Authorization: Bearer <token>` header, handles HTTP 401 (clear session → redirect `/login`), 403 (throw `Error("Access denied")`), 404 (throw `Error("Task not found")`), 500 (throw `Error("Server error, try again")`); implement all 6 typed functions: `getTasks(userId, status?)`, `createTask(userId, data)`, `getTask(userId, taskId)`, `updateTask(userId, taskId, data)`, `deleteTask(userId, taskId)`, `toggleComplete(userId, taskId)`

**Checkpoint**: Backend health check passes; `GET /health` → 200; `npm run dev` starts; TypeScript compiles; Better Auth routes accessible at `/api/auth/*`.

---

## Phase 3: User Story 1 — Account Registration & Login (Priority: P1) 🎯 MVP

**Goal**: Users can sign up, sign in, sign out, and be protected from accessing the dashboard unauthenticated.

**Independent Test**: (1) Navigate to `/signup` → create account → verify redirect to `/dashboard`; (2) click Logout → verify redirect to `/login`; (3) navigate directly to `/dashboard` without session → verify redirect to `/login`; (4) return to `/login` → enter credentials → verify redirect to `/dashboard`.

### Implementation for User Story 1

- [x] T025 [US1] Create `frontend/app/page.tsx` as a Server Component: call `auth.api.getSession(...)` or `getServerSession()`; if session exists redirect to `/dashboard`; if no session redirect to `/login`
- [x] T026 [P] [US1] Create `frontend/app/(auth)/login/page.tsx` as a Client Component (`"use client"`): render email input (type="email", required), password input (type="password", required), submit button, and link to `/signup`; on submit call `authClient.signIn.email({ email, password })`; on success redirect to `/dashboard`; on error show error message below form; during submission show "Signing in..." and disable button; validate email format and password min 8 chars before submit
- [x] T027 [P] [US1] Create `frontend/app/(auth)/signup/page.tsx` as a Client Component (`"use client"`): render name input (required), email input (type="email", required), password input (type="password", required), confirm password input (required), submit button, link to `/login`; validate password min 8 chars and confirm must match before submit; on submit call `authClient.signUp.email({ name, email, password })`; on success redirect to `/dashboard`; on error show error message; loading state shows "Creating account..."
- [x] T028 [US1] Create `frontend/components/Navbar.tsx` as a Client Component (`"use client"`): accept prop `{ userName: string }`; render fixed top bar with "Todo App" text on left and user name + logout button on right; logout button calls `authClient.signOut()` then redirects to `/login`; Tailwind only — no inline styles
- [x] T029 [US1] Create `frontend/app/dashboard/page.tsx` as a Server Component: call session check — if no session `redirect("/login")`; extract `user.name` and `user.id` from session; render `<Navbar userName={user.name} />`; add placeholder `<main>` content ("Your tasks will appear here") to be replaced in later stories

**Checkpoint**: Full auth flow works end-to-end: signup → dashboard; login → dashboard; logout → login; unauthenticated /dashboard → login.

---

## Phase 4: User Story 2 — Create a Task (Priority: P2)

**Goal**: Signed-in users can create tasks that immediately appear on their dashboard.

**Independent Test**: After logging in, fill in title in TaskForm, click "Add Task", verify the new task appears in the list below the form without a page reload.

### Implementation for User Story 2

- [x] T030 [US2] Add `POST /api/{user_id}/tasks` endpoint to `backend/routes/tasks.py`: add `Depends(get_current_user)` to get `current_user`; check `current_user["sub"] == user_id` → raise `HTTPException(403)` if mismatch; accept `TaskCreate` body; validate title 1–200 chars (Pydantic raises 422 if invalid); create `Task(user_id=user_id, **task_data)`; add to session and commit; return `TaskResponse` with status 201
- [x] T031 [US2] Create `frontend/components/TaskForm.tsx` as a Client Component (`"use client"`): accept props `{ userId: string, onTaskCreated: () => void }`; render title input (required, maxLength 200) and description textarea (optional, maxLength 1000); on submit call `api.createTask(userId, { title, description })`; on success clear form fields and call `onTaskCreated()`; on error show error message; during submission show "Adding..." and disable all form inputs; show character count or validation error for title > 200 chars
- [x] T032 [US2] Update `frontend/app/dashboard/page.tsx` to render `<TaskForm userId={user.id} onTaskCreated={refresh} />` below Navbar; implement `refresh` as a state-triggered re-render that causes TaskList to refetch (use `useState` for a refresh counter key passed to TaskList — convert page to Client Component or pass a server action)

**Checkpoint**: After submitting TaskForm, the new task appears in the task area; empty title is rejected with validation error; loading state shows during submission.

---

## Phase 5: User Story 3 — View and Filter Tasks (Priority: P3)

**Goal**: Signed-in users can view all their tasks and filter by All / Pending / Completed with task counts per filter.

**Independent Test**: After creating 3 tasks and toggling 1 complete, click "Pending" → see 2 tasks; click "Completed" → see 1 task; click "All" → see 3 tasks; count badges match.

### Implementation for User Story 3

- [x] T033 [US3] Add `GET /api/{user_id}/tasks` endpoint to `backend/routes/tasks.py`: add `Depends(get_current_user)`; check ownership → 403 if mismatch; accept optional `status` query param (`"all"` | `"pending"` | `"completed"`, default `"all"`); query `SELECT * FROM task WHERE user_id = user_id`; if `status == "pending"` add `AND completed = False`; if `status == "completed"` add `AND completed = True`; return `List[TaskResponse]` with status 200; return empty list (not 404) when user has no tasks
- [x] T034 [US3] Create `frontend/components/TaskCard.tsx` as a Client Component (`"use client"`): accept props `{ task: Task, userId: string, onUpdate: () => void }`; display task title (apply `line-through` Tailwind class if `task.completed`), description (if not null, greyed out), formatted created date; render Edit and Delete button placeholders (disabled, to be expanded in US4); checkbox placeholder (to be expanded in US5); Tailwind only — no inline styles
- [x] T035 [US3] Create `frontend/components/TaskList.tsx` as a Client Component (`"use client"`): accept props `{ userId: string, filter: 'all' | 'pending' | 'completed' }`; call `api.getTasks(userId, filter)` on mount and when `filter` changes; show loading spinner (Tailwind animated) while fetching; show "No tasks yet" message if response is empty array; show error message if fetch fails; render `<TaskCard>` for each task with `onUpdate` callback that triggers refetch
- [x] T036 [US3] Update `frontend/app/dashboard/page.tsx` to render filter buttons (All | Pending | Completed) above TaskList; add state for active filter (default `"all"`); fetch all tasks to compute counts for each filter tab badge; pass active filter to `<TaskList userId={user.id} filter={activeFilter} />`; highlight active filter button with distinct Tailwind style

**Checkpoint**: Dashboard shows all tasks on load; Pending filter shows only incomplete tasks; Completed filter shows only complete tasks; empty state shows "No tasks yet"; loading spinner shows on fetch.

---

## Phase 6: User Story 4 — Edit and Delete Tasks (Priority: P4)

**Goal**: Users can edit a task's title/description inline and permanently delete tasks after confirmation.

**Independent Test**: Click Edit on a task → inline form pre-filled with current values appears → change title → save → card shows updated title; click Delete → confirmation dialog → confirm → task disappears from list; click Delete → confirmation → cancel → task remains.

### Implementation for User Story 4

- [x] T037 [P] [US4] Add `GET /api/{user_id}/tasks/{task_id}` endpoint to `backend/routes/tasks.py`: `Depends(get_current_user)`; ownership check → 403; query `WHERE id = task_id AND user_id = user_id`; return 404 if not found; return `TaskResponse` with 200
- [x] T038 [P] [US4] Add `PUT /api/{user_id}/tasks/{task_id}` endpoint to `backend/routes/tasks.py`: `Depends(get_current_user)`; ownership check → 403; query task → 404 if not found; accept `TaskUpdate` body; update only provided (non-None) fields; set `updated_at = datetime.utcnow()`; commit and return `TaskResponse` with 200
- [x] T039 [US4] Add `DELETE /api/{user_id}/tasks/{task_id}` endpoint to `backend/routes/tasks.py`: `Depends(get_current_user)`; ownership check → 403; query task → 404 if not found; delete from session and commit; return `Response(status_code=204)` with no body
- [x] T040 [US4] Expand `frontend/components/TaskCard.tsx` with inline edit form: clicking Edit button sets local `isEditing` state to true; show form pre-filled with `task.title` and `task.description`; Save button calls `api.updateTask(userId, task.id, { title, description })`; on success call `onUpdate()` and set `isEditing` to false; Cancel button sets `isEditing` to false without saving; show loading state during save; show error message if save fails; validate title min 1 char before save
- [x] T041 [US4] Expand `frontend/components/TaskCard.tsx` with delete confirmation: clicking Delete button sets local `showConfirm` state to true; render confirmation dialog with "Are you sure?" text and Confirm + Cancel buttons; Confirm calls `api.deleteTask(userId, task.id)` then calls `onUpdate()`; Cancel sets `showConfirm` to false; show loading state during delete; show error if delete fails

**Checkpoint**: Inline edit form appears on Edit click; task updates in list after save; confirmation dialog appears on Delete click; task removed after confirm; cancel preserves task.

---

## Phase 7: User Story 5 — Toggle Task Completion (Priority: P5)

**Goal**: Users can toggle task completion by clicking a checkbox; completed tasks show strikethrough title.

**Independent Test**: Click checkbox on pending task → title gets strikethrough and task counted as completed; click checkbox again → strikethrough removed and task counted as pending. Calling toggle twice returns to original state.

### Implementation for User Story 5

- [x] T042 [US5] Add `PATCH /api/{user_id}/tasks/{task_id}/complete` endpoint to `backend/routes/tasks.py`: `Depends(get_current_user)`; ownership check → 403; query task → 404 if not found; flip `task.completed` (True → False, False → True); set `updated_at = datetime.utcnow()`; commit and return `TaskResponse` with 200
- [x] T043 [US5] Expand `frontend/components/TaskCard.tsx` with checkbox toggle: add `<input type="checkbox">` checked when `task.completed`; `onChange` calls `api.toggleComplete(userId, task.id)` then calls `onUpdate()`; apply `line-through` Tailwind class to title when `task.completed`; show loading indicator during toggle; show error if toggle fails; checkbox is disabled during loading to prevent double-submission

**Checkpoint**: Checkbox click toggles completed state; title strikethrough appears/disappears; clicking twice returns to original state; both pending and completed counts update correctly in filter tabs.

---

## Phase 8: Polish & Cross-Cutting Concerns

**Purpose**: Integration verification, security checklist, and final validation.

- [ ] T044 Start both servers (Terminal 1: `cd backend && uvicorn main:app --reload --port 8000`; Terminal 2: `cd frontend && npm run dev`) and run the 9-step integration test from `specs/001-todo-app/quickstart.md`: signup → dashboard → create 3 tasks → toggle one complete → filter Completed → edit task title → delete task → logout → login again → verify tasks persist
- [ ] T045 Run security verification per Constitution Article IV: (1) `curl http://localhost:8000/api/test-user/tasks` (no token) → verify 401; (2) `curl -H "Authorization: Bearer invalid.token"` → verify 401; (3) use valid token for User A to access User B's URL → verify 403; (4) `git status` → verify no `.env` files appear as tracked; (5) search source code for hardcoded secret values → verify only env reads found
- [ ] T046 [P] Verify all 6 task endpoints are visible and documented at `http://localhost:8000/docs` (FastAPI auto-generated OpenAPI UI)
- [ ] T047 [P] Verify mobile-responsive layout renders correctly on all 4 pages (use browser DevTools device simulation): login, signup, dashboard, and root redirect

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies — start immediately
- **Foundational (Phase 2)**: Depends on Phase 1 completion — **BLOCKS ALL user stories**
- **User Story 1 (Phase 3)**: Depends on Foundational — no dependency on other stories
- **User Story 2 (Phase 4)**: Depends on Foundational + US1 (needs auth to test)
- **User Story 3 (Phase 5)**: Depends on Foundational + US1 + US2 (needs tasks to view)
- **User Story 4 (Phase 6)**: Depends on Foundational + US1 + US3 (needs tasks displayed to edit/delete)
- **User Story 5 (Phase 7)**: Depends on Foundational + US1 + US3 (needs tasks displayed to toggle)
  - US4 and US5 can be worked in parallel after US3 completes
- **Polish (Phase 8)**: Depends on all user stories complete

### Within Each User Story

- Backend endpoint → can be built in parallel with frontend component (different files)
- Frontend component → depends on types/task.ts (T019) and api.ts (T024) from Foundational
- Dashboard page updates → depend on component(s) being ready

### Parallel Opportunities

**Phase 1**: T003, T004, T005, T006 can all run in parallel after T001+T002

**Phase 2 Backend**:
```bash
# These can overlap once T001 is done:
Task: "Create backend/requirements.txt" (T007)
Task: "Create backend/routes/__init__.py" (T012)
# Then sequential: T008 → T009 → T010 → T011 → T013 → T014 → T015 → T016
```

**Phase 2 Frontend** (can start in parallel with backend after T001):
```bash
Task: "Scaffold Next.js app" (T017)
# After T017:
Task: "Create frontend/types/task.ts" (T019)    # parallel
Task: "Create frontend/lib/auth.ts" (T020)      # parallel
Task: "Create frontend/lib/auth-client.ts" (T021) # parallel
```

**Phase 3 (US1)**:
```bash
Task: "Create login page" (T026)    # parallel
Task: "Create signup page" (T027)   # parallel
```

**Phase 6 (US4)**:
```bash
Task: "GET single task endpoint" (T037)    # parallel
Task: "PUT update task endpoint" (T038)    # parallel
# Then: T039 → T040 → T041 (sequential — all modify tasks.py or TaskCard.tsx)
```

**Phase 8**:
```bash
Task: "Verify /docs routes" (T046)        # parallel
Task: "Verify mobile layout" (T047)       # parallel
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (T001–T006)
2. Complete Phase 2: Foundational (T007–T024)
3. Complete Phase 3: User Story 1 (T025–T029)
4. **STOP and VALIDATE**: Full auth flow works (signup/login/logout/protected route)
5. Demo: auth-only MVP is functional

### Incremental Delivery

1. Phase 1+2 → Foundation ready
2. Phase 3 (US1) → Auth works → demo-able ✅
3. Phase 4 (US2) → Can create tasks → demo-able ✅
4. Phase 5 (US3) → Can view + filter tasks → demo-able ✅
5. Phase 6 (US4) → Can edit + delete tasks → full CRUD ✅
6. Phase 7 (US5) → Can toggle completion → complete feature set ✅
7. Phase 8 → Security verified → hackathon submission ready ✅

### Parallel Team Strategy (if 2 developers)

After Phase 2 completes:
- **Developer A**: US1 (auth pages) → US2 (TaskForm) → US3 frontend (TaskList, TaskCard, dashboard)
- **Developer B**: Backend endpoints (US2 POST → US3 GET → US4 PUT/DELETE → US5 PATCH)

Both can work simultaneously from Phase 4 onwards since backend routes and frontend components are in different files.

---

## Notes

- `[P]` tasks have no dependency conflicts with concurrent tasks in the same phase
- `[US#]` label maps each task to its user story for traceability
- Every user story is independently completable and testable
- Backend endpoints can be verified with curl before frontend is ready
- Stop at each phase checkpoint before proceeding to the next story
- Constitution security checklist (Article IV) MUST pass before Phase 8 is marked complete
- Total tasks: 47 | Parallelizable: 14 | Sequential: 33
