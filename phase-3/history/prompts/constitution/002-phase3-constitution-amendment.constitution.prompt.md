---
id: 002
title: Phase 3 Constitution Amendment
stage: constitution
date: 2026-03-01
surface: agent
model: claude-sonnet-4-6
feature: none
branch: 001-todo-app
user: architect
command: /sp.constitution
labels: ["constitution","phase3","groq","mcp","chat","amendment"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - .specify/memory/constitution.md
  - .specify/templates/plan-template.md
  - .specify/templates/spec-template.md
  - .specify/templates/tasks-template.md
tests:
  - n/a
---

## Prompt

```
ver:  Official MCP SDK — FREE
- Chat UI:     Custom Next.js chat page — FREE
- Backend:     Python FastAPI (same as Phase 2)
- ORM:         SQLModel (same as Phase 2)
- Database:    Neon Serverless PostgreSQL (same as Phase 2)
- Auth:        Better Auth + JWT (same as Phase 2)

Phase 2 Stack (IMMUTABLE — never touch):
- Frontend:    Next.js 16+ with App Router
- Backend:     Python FastAPI
- Auth:        Better Auth with JWT
- Database:    Neon PostgreSQL

Free Tier Commitments (NEVER replace with paid):
- Groq API:    FREE tier at console.groq.com — No credit card. No OpenAI. No paid AI.
- MCP SDK:     pip install mcp — completely free
- Chat UI:     Custom built — no OpenAI ChatKit

ARTICLE II — GOLDEN RULE OF PHASE 3: PHASE 2 MUST NEVER BREAK.
All Phase 3 work is purely ADDITIVE.

[Full Phase 3 constitution content including: Laws X-XVII, Phase 3 API endpoints,
database schema laws, frontend laws, agent AI rules, extended security checklist,
implementation steps 3-10, violation protocol additions, quick reference]
```

## Response snapshot

Constitution amended from v1.0.0 to v1.1.0 (MINOR bump).

Added to `.specify/memory/constitution.md`:
- Phase 3 Stack section (Groq/MCP/Chat UI — free tier commitments)
- Golden Rule of Phase 3 (Phase 2 must never break; frozen files list)
- Laws X-XVII: JWT on new routes, Additive Only, Groq Free Tier Only, User Data Isolation
  (extended), Stateless Server, Secrets in ENV (extended), Spec First (extended),
  MCP Tools Stateless
- Phase 3 API Contract (POST /chat, GET /activity, GET /conversations)
- Database Laws (4 new tables: conversations, messages, user_activity, email_log)
- Frontend Laws (chat page, navbar link, Tailwind-only, 3 UI states, JWT, conversation state)
- Agent AI Rules (no user_id in schemas, always call tool, full history, max 1000 tokens)
- Extended Security Checklist (AI safety layer added)
- Phase 3 Implementation Steps (Steps 1-10)
- Extended Violation Protocol (Phase 3 violations + fixes)
- Quick Reference (new files, modified files, frozen files, run commands)

All Phase 2 laws (I-IX) preserved unchanged.

## Outcome

- ✅ Impact: Constitution v1.1.0 written to `.specify/memory/constitution.md`
- 🧪 Tests: n/a (governance document)
- 📁 Files: `.specify/memory/constitution.md` (overwritten)
- 🔁 Next prompts: `/sp.specify phase3-chat`, `/sp.plan phase3-chat`, `/sp.tasks phase3-chat`
- 🧠 Reflection: Phase 3 content was well-structured in user input (despite some truncation in args).
  Reconstructed all articles faithfully. Version bump is MINOR (1.0.0→1.1.0) since no existing
  laws were removed or redefined.

## Evaluation notes (flywheel)

- Failure modes observed: User input was passed as command args with some content truncated;
  reconstruction from context was necessary for some articles.
- Graders run and results (PASS/FAIL): n/a
- Prompt variant (if applicable): n/a
- Next experiment (smallest change to try): Verify constitution against actual Phase 3
  implementation as it progresses.
