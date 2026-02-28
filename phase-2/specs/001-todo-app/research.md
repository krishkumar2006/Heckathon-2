# Research: Todo App — Phase 0 Findings

**Date**: 2026-02-27
**Branch**: `001-todo-app`
**Resolved by**: User input (SPEC 1.x and SPEC 2.x) + established library docs

---

## Decision 1: Authentication Library

**Decision**: Better Auth with JWT plugin

**Rationale**:
- Better Auth is a modern, TypeScript-first auth library with built-in JWT plugin
- The JWT plugin issues signed tokens using `BETTER_AUTH_SECRET` (HS256)
- Both the frontend (to get the token) and the backend (to verify it) use the same secret
- This avoids needing a separate auth service or JWKS endpoint
- Supports Neon PostgreSQL adapter natively via `@better-auth/pg`

**Alternatives considered**:
- NextAuth.js v5: More mature but heavier; session-cookie-based by default (JWT plugin is opt-in)
- Clerk: Fully managed auth — too opinionated and adds external dependency for hackathon
- Custom JWT: Too much implementation risk for hackathon timeframe

**Token flow**:
```
1. Frontend: authClient.signUp/signIn.email() → Better Auth issues JWT
2. Frontend: authClient.getSession() → returns session with JWT token field
3. Frontend: attaches JWT to all backend requests via Authorization: Bearer header
4. Backend: python-jose decodes JWT using same BETTER_AUTH_SECRET (HS256)
5. Backend: extracts user ID from token["sub"] field
```

---

## Decision 2: Backend Framework

**Decision**: FastAPI + SQLModel + python-jose

**Rationale**:
- FastAPI: Fastest Python web framework; async by default; auto OpenAPI docs at `/docs`
- SQLModel: Combines Pydantic v2 + SQLAlchemy; one class for both DB model and API schema
- python-jose[cryptography]: Standard JWT library for Python; supports HS256 natively

**Dependency list** (backend/requirements.txt):
```
fastapi==0.110.0
uvicorn[standard]==0.27.0
sqlmodel==0.0.16
psycopg2-binary==2.9.9
python-jose[cryptography]==3.3.0
python-dotenv==1.0.0
httpx==0.26.0
```

---

## Decision 3: Database

**Decision**: Neon PostgreSQL (serverless)

**Rationale**:
- Neon provides free-tier serverless PostgreSQL with instant provisioning
- Supports standard `psycopg2` driver with SSL (`?sslmode=require`)
- SQLModel works natively with PostgreSQL
- Neon dashboard provides visual confirmation of data for testing

**Connection string format**:
```
postgresql://user:password@host.neon.tech/dbname?sslmode=require
```

**WARNING**: Neon connection strings go dormant after inactivity. If the backend
fails to connect after idle time, restart the backend process — Neon will wake up.

---

## Decision 4: Frontend Stack

**Decision**: Next.js 16 with App Router + React 19 + Tailwind CSS 4 + TypeScript 5

**Rationale**:
- Next.js 16 App Router: Server Components by default (Constitution Rule 1)
- React 19: Latest stable, compatible with Next.js 16
- Tailwind CSS 4: Constitution Rule 2 mandates Tailwind-only styling
- TypeScript 5 strict mode: Constitution Rule 3 mandates no `any` types

**Initialization command** (from repo root):
```bash
npx create-next-app@latest frontend \
  --typescript \
  --tailwind \
  --app \
  --no-src-dir \
  --import-alias "@/*"
```

---

## Decision 5: JWT Field for User ID

**Decision**: Better Auth stores user ID in token `sub` field (JWT standard)

**Rationale**:
- Better Auth JWT plugin follows the JWT standard: `sub` = subject = user ID
- Backend ownership check: `current_user["sub"] != user_id` → 403
- This is verified in PLAN-04 (test token payload before building routes)

**Token payload structure** (Better Auth JWT):
```json
{
  "sub": "<user-uuid>",
  "email": "user@example.com",
  "iat": 1234567890,
  "exp": 1234567890
}
```

---

## Decision 6: CORS Strategy

**Decision**: Backend allows only the frontend origin (`FRONTEND_URL` env var)

**Rationale**:
- Restrictive CORS prevents cross-origin requests from other domains
- `FRONTEND_URL` is loaded from `backend/.env` — not hardcoded
- Development: `http://localhost:3000`
- Production: HTTPS domain URL

**CORS config**:
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=[os.getenv("FRONTEND_URL", "http://localhost:3000")],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH"],
    allow_headers=["Authorization", "Content-Type"],
)
```

---

## Decision 7: Database Index Strategy

**Decision**: Three indexes on the Task table

| Index | Fields | Reason |
|-------|--------|--------|
| Primary | `id` | Automatic — row lookup |
| Single | `user_id` | Fast "all tasks for user" queries |
| Single | `completed` | Fast status filter queries |
| Composite | `(user_id, completed)` | Fast "user's pending tasks" / "user's completed tasks" |

The composite index makes the filtered list endpoint (`GET /api/{user_id}/tasks?status=pending`)
efficient without full table scan.

---

## Unresolved Items

None. All technical decisions are fully resolved. Ready for Phase 1 design.
