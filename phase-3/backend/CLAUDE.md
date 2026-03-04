# Backend — Claude Code Guide

## Stack
- **Runtime**: Python 3.11+
- **Framework**: FastAPI 0.110
- **ORM**: SQLModel 0.0.16 (Pydantic v2 + SQLAlchemy)
- **Database**: Neon PostgreSQL (serverless, SSL required)
- **Auth**: python-jose[cryptography] for JWT verification (HS256)
- **Env**: python-dotenv

## Folder Structure
```
backend/
├── main.py          # FastAPI app, CORS, startup, /health
├── auth.py          # JWT middleware — verify_token(), get_current_user()
├── db.py            # SQLModel engine, get_session() dependency
├── models.py        # Task SQLModel table + Pydantic schemas
├── routes/
│   ├── __init__.py
│   └── tasks.py     # All 6 task endpoints
├── requirements.txt
├── .env             # NEVER committed
└── .env.example     # Safe to commit
```

## Run Command
```bash
# From backend/ directory with venv activated
uvicorn main:app --reload --port 8000
```

## Environment Variables
| Variable | Required | Description |
|----------|----------|-------------|
| `BETTER_AUTH_SECRET` | ✅ | JWT signing secret — MUST match frontend |
| `DATABASE_URL` | ✅ | Neon PostgreSQL connection string (include `?sslmode=require`) |
| `FRONTEND_URL` | ✅ | Frontend origin for CORS (e.g. `http://localhost:3000`) |

## Constitutional Laws (MUST follow)

### LAW III — JWT ON EVERY ENDPOINT
Every task route MUST use `Depends(get_current_user)`.
No endpoint is left unprotected. No exceptions.

### LAW IV — USER DATA ISOLATION
Every database query MUST filter by `user_id`:
```python
WHERE task.user_id == current_user["sub"]
```
URL `user_id` must be verified against `current_user["sub"]` → 403 if mismatch.

### LAW V — SECRETS NEVER IN CODE
`BETTER_AUTH_SECRET` and `DATABASE_URL` live ONLY in `.env`.
If a secret appears in source code → STOP and fix immediately.

## Error Response Standards
| Code | When |
|------|------|
| 401 | Missing or invalid JWT token |
| 403 | Authenticated user does not own this resource |
| 404 | Task not found |
| 422 | Validation error (title/description constraints) |
| 500 | Server or database error |

## API Endpoints (FIXED — do not rename)
```
GET    /api/{user_id}/tasks
POST   /api/{user_id}/tasks
GET    /api/{user_id}/tasks/{task_id}
PUT    /api/{user_id}/tasks/{task_id}
DELETE /api/{user_id}/tasks/{task_id}
PATCH  /api/{user_id}/tasks/{task_id}/complete
GET    /health
```
