---
id: "002"
title: Todo App Master Implementation Plan
stage: plan
date: 2026-02-27
surface: agent
model: claude-sonnet-4-6
feature: 001-todo-app
branch: 001-todo-app
user: HP
command: /sp.plan
labels: ["plan","todo-app","fastapi","nextjs","jwt","better-auth","neon","sqlmodel","hackathon"]
links:
  spec: specs/001-todo-app/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - specs/001-todo-app/plan.md
  - specs/001-todo-app/research.md
  - specs/001-todo-app/data-model.md
  - specs/001-todo-app/quickstart.md
  - specs/001-todo-app/contracts/tasks-api.yaml
  - specs/001-todo-app/contracts/auth-flow.md
tests:
  - none
---

## Prompt

MASTER PLAN — FULL PROJECT

PLAN: Master Implementation Plan
VERSION: 1.0
SPEC REF: SP.SPECIFY.md — All Sections
FOLDER: Both (coordinates frontend/ and backend/ separately)

SUB-PLANS IN ORDER:
PLAN-01: Project Foundation
PLAN-02: Database Setup
PLAN-03: Backend Foundation
PLAN-04: Backend Auth Middleware
PLAN-05: Backend CRUD Endpoints
PLAN-06: Frontend Foundation
PLAN-07: Frontend Auth Setup
PLAN-08: Frontend API Client
PLAN-09: Frontend UI Components
PLAN-10: Frontend Pages
PLAN-11: Integration and Testing

[Full technical details for each plan provided in command args — 11 sub-plans covering
project foundation, Neon DB setup, FastAPI backend with JWT middleware, 6 CRUD endpoints,
Next.js frontend with Better Auth, TypeScript types, centralized API client, 4 UI components,
4 pages (login, signup, dashboard, root redirect), and integration + security testing.]

## Response snapshot

Generated complete Phase 0 + Phase 1 plan artifacts for the full-stack Todo App:

**plan.md**: 11 ordered sub-plans (PLAN-01 through PLAN-11) with technical context,
Constitution Check (all 9 laws — ALL PASS), project structure for both frontend/ and
backend/, and risk register.

**research.md**: 7 architectural decisions:
- Auth: Better Auth + JWT plugin (HS256, 7-day expiry)
- Backend: FastAPI + SQLModel + python-jose
- DB: Neon PostgreSQL with psycopg2-binary + SSL
- Frontend: Next.js 16 + React 19 + Tailwind 4 + TypeScript 5
- JWT user ID field: token "sub" claim
- CORS: FRONTEND_URL env var, credentials=True
- DB indexes: user_id, completed, composite (user_id, completed)

**data-model.md**: Task entity (7 fields), 3 DB indexes, Pydantic schemas (Create/Update/Response),
TypeScript interfaces (Task, CreateTaskInput, UpdateTaskInput, ApiResponse<T>, User).

**contracts/tasks-api.yaml**: Full OpenAPI 3.1 spec for all 6 endpoints + /health.

**contracts/auth-flow.md**: Token issuance → retrieval → verification sequence diagrams,
env variable dependency diagram, error code table.

**quickstart.md**: Step-by-step dev setup (secret generation, Neon, backend venv, frontend
scaffold), common issues table, run commands.

## Outcome

- ✅ Impact: Complete implementation plan ready; all 11 sub-plans defined; all artifacts generated; ready for /sp.tasks
- 🧪 Tests: none (planning documents)
- 📁 Files: plan.md, research.md, data-model.md, quickstart.md, contracts/tasks-api.yaml, contracts/auth-flow.md
- 🔁 Next prompts: /sp.tasks to generate the dependency-ordered task list for implementation
- 🧠 Reflection: Constitution Check passed all 9 laws before planning began. Risk register
  identifies BETTER_AUTH_SECRET mismatch as highest-probability/highest-impact risk.

## Evaluation notes (flywheel)

- Failure modes observed: none — all technology decisions were explicitly provided by user
- Graders run and results (PASS/FAIL): Constitution Check — all 9 laws PASS
- Prompt variant (if applicable): none
- Next experiment (smallest change to try): run /sp.tasks to generate implementation task list
