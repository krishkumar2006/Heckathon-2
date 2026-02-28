---
id: "001"
title: Ratify Hackathon Todo Constitution
stage: constitution
date: 2026-02-27
surface: agent
model: claude-sonnet-4-6
feature: none
branch: master
user: HP
command: /sp.constitution
labels: ["constitution","jwt","security","hackathon","todo-app","better-auth","fastapi","nextjs"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - .specify/memory/constitution.md
tests:
  - none
---

## Prompt

ate spec → get approval → then code.

LAW 2 — NO MANUAL CODING
All code is generated through Claude Code.
No agent writes code directly by hand.
This is a hackathon rule — violation disqualifies the project.

LAW 3 — JWT ON EVERY ENDPOINT
Every single API endpoint must verify JWT token.
No endpoint is ever left unprotected.
No exceptions. No "we'll add auth later."

LAW 4 — USER DATA ISOLATION
Every database query must filter by user_id.
A user can NEVER see, edit, or delete another user's tasks.
This is enforced at the database query level, not just the route level.

LAW 5 — SECRETS NEVER IN CODE
BETTER_AUTH_SECRET lives only in .env files.
DATABASE_URL lives only in .env files.
.env files are always in .gitignore.
If a secret appears in any code file → immediate stop and fix.

LAW 6 — SAME SECRET, BOTH SIDES
BETTER_AUTH_SECRET must be identical in:
- frontend/.env.local
- backend/.env
If they differ → auth breaks completely → 401 on everything.

LAW 7 — SPECS ARE SOURCE OF TRUTH
If c[...truncated in original input]

[API Contract]
GET      /api/{user_id}/tasks                  200
POST     /api/{user_id}/tasks                  201
GET      /api/{user_id}/tasks/{id}             200
PUT      /api/{user_id}/tasks/{id}             200
DELETE   /api/{user_id}/tasks/{id}             204
PATCH    /api/{user_id}/tasks/{id}/complete    200

Error Response Standards:
401 → Missing or invalid JWT token
403 → Authenticated user does not own this resource
404 → Task or resource not found
422 → Validation error (bad input data)
500 → Server or database error

[Frontend Rules - 7 rules]
[Security Constitution - Article VII - 4-layer checklist]
[Implementation Phases - 7 phases]
[Violation Protocol - Article IX - 6-step protocol]

## Response snapshot

Constitution ratified at v1.0.0. All 9 constitutional laws filled, API contract table
locked, security checklist embedded, 7 implementation phases defined, violation protocol
codified with common-violation fix table. One deferred item: LAW 7 body was truncated
in input — marked TODO(LAW_7_BODY) in the constitution. Constitution written to
`.specify/memory/constitution.md`.

## Outcome

- ✅ Impact: Constitution v1.0.0 ratified; all agents now have binding governance for the hackathon Todo app
- 🧪 Tests: none (governance document)
- 📁 Files: .specify/memory/constitution.md (created/overwritten)
- 🔁 Next prompts: /sp.specify to create feature spec; /sp.plan to generate architecture plan
- 🧠 Reflection: LAW 7 body was garbled in transmission — confirm full wording with team before first spec review

## Evaluation notes (flywheel)

- Failure modes observed: Input truncation caused LAW 7 body loss; reconstructed from context
- Graders run and results (PASS/FAIL): no automated graders; visual validation passed
- Prompt variant (if applicable): none
- Next experiment (smallest change to try): confirm LAW 7 wording, then re-amend to v1.0.1
