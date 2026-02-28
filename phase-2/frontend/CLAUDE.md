# Frontend — Claude Code Guide

## Stack
- **Framework**: Next.js 16 (App Router)
- **Language**: TypeScript 5 (strict mode — no `any`)
- **UI**: React 19 + Tailwind CSS 4
- **Auth**: Better Auth (latest) with JWT plugin

## Folder Structure
```
frontend/
├── app/
│   ├── layout.tsx                    # Root layout — session provider + Tailwind
│   ├── page.tsx                      # Root redirect (/dashboard or /login)
│   ├── (auth)/
│   │   ├── login/page.tsx            # Login form (Client Component)
│   │   └── signup/page.tsx           # Signup form (Client Component)
│   ├── dashboard/page.tsx            # Protected dashboard (Server Component)
│   └── api/auth/[...all]/route.ts    # Better Auth handler
├── components/
│   ├── Navbar.tsx                    # App nav + logout
│   ├── TaskForm.tsx                  # Create task form
│   ├── TaskList.tsx                  # Task list with loading/error/empty states
│   └── TaskCard.tsx                  # Single task (edit, delete, toggle)
├── lib/
│   ├── auth.ts                       # Better Auth server config (server-only)
│   ├── auth-client.ts                # Better Auth client config
│   └── api.ts                        # ALL backend API calls (centralized)
├── types/
│   └── task.ts                       # TypeScript interfaces
├── .env.local                        # NEVER committed
└── .env.example                      # Safe to commit
```

## Run Command
```bash
# From frontend/ directory
npm run dev
```

## Environment Variables
| Variable | Required | Description |
|----------|----------|-------------|
| `BETTER_AUTH_SECRET` | ✅ | JWT signing secret — MUST match backend |
| `NEXT_PUBLIC_API_URL` | ✅ | Backend base URL (e.g. `http://localhost:8000`) |
| `BETTER_AUTH_URL` | ✅ | This app's base URL (e.g. `http://localhost:3000`) |
| `DATABASE_URL` | ✅ | Neon PostgreSQL — Better Auth stores sessions here |

## Constitutional Rules (MUST follow)

### RULE 1 — Server Components by Default
Use `"use client"` ONLY when the component needs:
- `useState` / `useEffect` hooks
- Browser event handlers (`onClick`, `onChange`)
- Browser-only APIs

### RULE 2 — No Inline Styles
Tailwind CSS utility classes ONLY. No `style={{}}` props.

### RULE 3 — TypeScript Strict
No `any` types. All props, return types, and state must be typed.

### RULE 4 — Centralized API Client
ALL backend calls go through `lib/api.ts` only.
No component makes direct `fetch()` calls to the backend.

### RULE 5 — Three UI States
Every async operation MUST handle:
1. **Loading** — show spinner
2. **Error** — show error message
3. **Success** — show data

### RULE 6 — Protected Routes
`app/dashboard/page.tsx` MUST check session and redirect to `/login` if absent.

### RULE 7 — JWT Always Attached
`lib/api.ts` `fetchWithAuth()` attaches JWT to every request.
Missing token → redirect to `/login` (never throw unhandled error).
