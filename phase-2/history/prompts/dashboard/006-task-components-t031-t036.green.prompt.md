---
id: 006
title: Task UI Components — TaskForm, TaskCard, TaskList, Dashboard Wiring
stage: green
date: 2026-02-28
surface: agent
model: claude-sonnet-4-6
feature: dashboard
branch: 001-todo-app
user: user
command: implement TaskForm, TaskCard, TaskList, update dashboard page
labels: ["task-ui","client-components","better-auth","typescript"]
links:
  spec: null
  ticket: T031, T034, T035, T036
  adr: null
  pr: null
files:
  - frontend/components/TaskForm.tsx
  - frontend/components/TaskCard.tsx
  - frontend/components/TaskList.tsx
  - frontend/app/dashboard/page.tsx
  - frontend/lib/auth-client.ts
tests:
  - npx tsc --noEmit (PASS — zero errors)
---

## Prompt

You are implementing the remaining frontend UI components for a Todo App in Next.js 16 with TypeScript 5, Tailwind CSS 4, and Better Auth.

Tasks to implement:
- T031: TaskForm.tsx — create task form, client component
- T034: TaskCard.tsx — full card with toggle/edit/delete, client component
- T035: TaskList.tsx — fetches and renders task list, client component
- T036: Update dashboard/page.tsx to be a Client Component with useSession()

Constraints: TypeScript strict mode, no any types, Tailwind only, all API calls via lib/api.ts.

## Response snapshot

Created 3 new components and updated 2 files:

1. `frontend/components/TaskForm.tsx` — controlled form with title (maxLength 200) and description (maxLength 1000), character count hints, loading spinner during submission, inline error display, clears on success, calls onTaskCreated().

2. `frontend/components/TaskCard.tsx` — three render modes: normal (checkbox + text + edit/delete buttons), edit form (inline, save/cancel), delete confirmation (confirm/cancel). Error and loading states on every async operation.

3. `frontend/components/TaskList.tsx` — useEffect fetches tasks on userId/filter/refreshKey/internal-refetchCount change. Loading spinner, error banner, filter-aware empty state, sorted newest-first, renders TaskCard per item.

4. `frontend/app/dashboard/page.tsx` — converted to Client Component. Uses authClient.useSession() for session. isPending -> loading spinner. No session -> router.push('/login'). Renders Navbar, TaskForm, filter buttons (All/Pending/Completed with aria-pressed), TaskList. refreshKey incremented when task created.

5. `frontend/lib/auth-client.ts` — fixed import from "better-auth/client" to "better-auth/react" so useSession() is a proper React hook (not a nanostores Atom). All other methods (signIn.email, signUp.email, signOut, getSession) remain intact.

TypeScript: `npx tsc --noEmit` exits 0 — zero type errors.

## Outcome

- Impact: All task management UI components implemented and wired to dashboard; users can create, toggle, edit, and delete tasks
- Tests: TypeScript strict check passes — zero errors
- Files: 3 created, 2 updated
- Next prompts: Integration testing with live backend, styling review, error boundary considerations
- Reflection: Key insight — better-auth/client exports useSession as a nanostores Atom; must use better-auth/react for proper React hook behavior

## Evaluation notes (flywheel)

- Failure modes observed: "better-auth/client" useSession is an Atom, not a hook — must use "better-auth/react" createAuthClient for React apps
- Graders run and results (PASS/FAIL): TypeScript — PASS
- Prompt variant (if applicable): none
- Next experiment: Add optimistic toggle update to avoid full refetch on checkbox change
