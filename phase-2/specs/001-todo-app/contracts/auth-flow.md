# Auth Flow Contract: Todo App

**Date**: 2026-02-27

## Overview

Better Auth manages user registration and login on the frontend. It issues a JWT token
signed with `BETTER_AUTH_SECRET`. The backend uses the same secret to independently
verify tokens without network round-trips to an auth service.

---

## Token Issuance (Frontend)

```
User submits signup form
       │
       ▼
authClient.signUp.email({ name, email, password })
       │
       ▼
Better Auth Server (frontend/app/api/auth/[...all]/route.ts)
  - Hashes password
  - Creates user record in Neon (users table managed by Better Auth)
  - Issues JWT signed with BETTER_AUTH_SECRET (HS256, 7-day expiry)
       │
       ▼
Session stored (cookie or local storage — Better Auth handles this)
       │
       ▼
redirect("/dashboard")
```

Same flow for `authClient.signIn.email({ email, password })`.

---

## Token Retrieval (Frontend → Backend)

```
Component needs to call backend
       │
       ▼
fetchWithAuth() in frontend/lib/api.ts
       │
       ▼
authClient.getSession()
       │
       ├── No session? → redirect("/login")
       │
       └── Session found → extract token from session.token (or session.user.jwt)
              │
              ▼
       Add header: Authorization: Bearer <jwt_token>
              │
              ▼
       HTTP request to backend (http://localhost:8000)
```

---

## Token Verification (Backend)

```
Request arrives at backend route
       │
       ▼
Depends(get_current_user) in backend/auth.py
       │
       ▼
HTTPBearer() extracts token from Authorization header
       │
       ├── No token? → HTTPException(401, "Authorization required")
       │
       └── Token found → verify_token(token)
              │
              ▼
       jose.jwt.decode(token, BETTER_AUTH_SECRET, algorithms=["HS256"])
              │
              ├── Invalid signature? → HTTPException(401, "Invalid token")
              ├── Expired? → HTTPException(401, "Token expired")
              │
              └── Valid → return payload dict { "sub": user_id, "email": ..., "exp": ... }
                     │
                     ▼
              Route handler receives current_user dict
                     │
                     ▼
              Ownership check: current_user["sub"] == path_user_id
                     │
                     ├── Mismatch → HTTPException(403, "Access denied")
                     │
                     └── Match → execute DB query WHERE user_id = current_user["sub"]
```

---

## Environment Variable Dependency

```
frontend/.env.local              backend/.env
─────────────────────────        ─────────────────────────
BETTER_AUTH_SECRET=abc123   ──── BETTER_AUTH_SECRET=abc123
                             ↑
                     MUST BE IDENTICAL
                     Generated once with: openssl rand -base64 32
```

If these values differ:
- Better Auth signs tokens with frontend secret
- python-jose verifies with backend secret
- Signatures never match → 401 on every protected endpoint

---

## Token Expiry

- Better Auth JWT plugin: `expirationTime: "7d"` (7 days)
- python-jose `decode()` automatically verifies `exp` claim
- Expired tokens → 401 → frontend redirects to `/login`
- No refresh token flow in scope for hackathon

---

## Error Codes

| Scenario | HTTP Code |
|----------|-----------|
| No Authorization header | 401 |
| Malformed Bearer token | 401 |
| Invalid JWT signature | 401 |
| Expired JWT | 401 |
| Valid token, wrong user_id in path | 403 |
| Valid token, correct user, task not found | 404 |
