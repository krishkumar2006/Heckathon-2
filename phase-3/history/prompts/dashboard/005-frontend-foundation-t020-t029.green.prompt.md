---
id: 005
title: Frontend Foundation T020-T029
stage: green
date: 2026-02-28
surface: agent
model: claude-sonnet-4-6
feature: todo-app
branch: 001-todo-app
user: user
command: implement T020-T029 frontend foundation
labels: ["next.js", "better-auth", "auth", "dashboard", "api-client", "tailwind"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - frontend/lib/auth.ts
  - frontend/lib/auth-client.ts
  - frontend/lib/api.ts
  - frontend/app/api/auth/[...all]/route.ts
  - frontend/app/layout.tsx
  - frontend/app/page.tsx
  - frontend/app/(auth)/login/page.tsx
  - frontend/app/(auth)/signup/page.tsx
  - frontend/components/Navbar.tsx
  - frontend/app/dashboard/page.tsx
tests:
  - npx tsc --noEmit (PASS — zero errors)
---

## Prompt

You are implementing a Todo App frontend using Next.js 16, TypeScript 5, Tailwind CSS 4, and Better Auth. The working directory is `D:\Heckathon 2\Todo`.

## Current State
- Next.js 16 app is scaffolded in `frontend/` with better-auth@1.4.19 installed
- `frontend/types/task.ts` exists with all TypeScript interfaces
- `frontend/app/layout.tsx` is the default Next.js layout (needs to be updated)
- `frontend/app/page.tsx` is the default Next.js page (needs to be replaced)
- `frontend/lib/` directory does NOT exist yet
- `frontend/components/` directory does NOT exist yet
- `frontend/app/(auth)/` directory does NOT exist yet
- `frontend/app/dashboard/` directory does NOT exist yet
- `frontend/app/api/` directory does NOT exist yet

Tasks T020–T029: Create auth.ts (server), auth-client.ts (client), API route handler, layout update, api.ts with fetchWithAuth, root redirect page, login page, signup page, Navbar component, and protected dashboard page.

## Response snapshot

Implemented all 10 tasks (T020–T029) across the frontend foundation:

1. **T020 `frontend/lib/auth.ts`**: Server-only Better Auth config using `betterAuth` with Kysely PostgresDialect wrapping `@neondatabase/serverless` Pool, JWT plugin (7d expiry), emailAndPassword enabled. Installed `@neondatabase/serverless` package.

2. **T021 `frontend/lib/auth-client.ts`**: Client-safe auth client using `createAuthClient` from `better-auth/client` with `jwtClient` plugin. Uses `NEXT_PUBLIC_BETTER_AUTH_URL` env var.

3. **T022 `frontend/app/api/auth/[...all]/route.ts`**: Better Auth catch-all handler using `toNextJsHandler` from `better-auth/next-js`.

4. **T023 `frontend/app/layout.tsx`**: Updated metadata title to "Todo App", kept Geist fonts, added `bg-gray-50 min-h-screen` to body.

5. **T024 `frontend/lib/api.ts`**: Centralized API client with `fetchWithAuth` (JWT via `/api/auth/token` endpoint), 6 typed task functions: getTasks, createTask, getTask, updateTask, deleteTask, toggleComplete. All error codes (401/403/404/5xx) throw typed errors.

6. **T025 `frontend/app/page.tsx`**: Server Component root redirect — checks session via `auth.api.getSession`, redirects to `/dashboard` or `/login`.

7. **T026 `frontend/app/(auth)/login/page.tsx`**: Client Component login form — email + password, client-side validation, authClient.signIn.email(), loading state, inline errors, accessible labels, link to signup.

8. **T027 `frontend/app/(auth)/signup/page.tsx`**: Client Component signup form — name + email + password + confirm, min-8-char validation, password match check, authClient.signUp.email(), loading state, inline errors, link to login.

9. **T028 `frontend/components/Navbar.tsx`**: Client Component fixed top navbar — "Todo App" left, userName + sign-out button right, authClient.signOut() + redirect to /login on logout.

10. **T029 `frontend/app/dashboard/page.tsx`**: Server Component protected page — session check via auth.api.getSession, redirect(/login) if absent, renders Navbar with userName, placeholder main content.

TypeScript check: `npx tsc --noEmit` → 0 errors.

## Outcome

- Impact: Full frontend authentication and routing foundation established. Users can sign up, log in, and access a protected dashboard. All API calls are centralized in lib/api.ts with JWT auth.
- Tests: TypeScript strict mode compilation passes with zero errors.
- Files: 10 files created/modified across lib/, components/, app/(auth)/, app/dashboard/, app/api/
- Next prompts: Implement TaskForm, TaskList, TaskCard components for dashboard; wire up filter state with useSearchParams.
- Reflection: Used Kysely PostgresDialect + @neondatabase/serverless Pool instead of direct neon() call — neon() returns a query function (NeonQueryFunction), not a PostgresPool-compatible object. This was the correct adapter pattern for better-auth 1.x.

## Evaluation notes (flywheel)

- Failure modes observed: Task spec said `database: neon(process.env.DATABASE_URL!)` but neon() returns a query function, not a pool. Used PostgresDialect + Pool wrapper instead.
- Graders run and results (PASS/FAIL): tsc --noEmit PASS
- Prompt variant (if applicable): none
- Next experiment (smallest change to try): Add TaskForm/TaskList/TaskCard components and wire filter state
