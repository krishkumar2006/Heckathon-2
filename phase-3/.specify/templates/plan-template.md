# Implementation Plan: [FEATURE]

**Branch**: `[###-feature-name]` | **Date**: [DATE] | **Spec**: [link]
**Input**: Feature specification from `/specs/[###-feature-name]/spec.md`

**Note**: This template is filled in by the `/sp.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

[Extract from feature spec: primary requirement + technical approach from research]

## Technical Context

<!--
  ACTION REQUIRED: Replace the content in this section with the technical details
  for the project. The structure here is presented in advisory capacity to guide
  the iteration process.
-->

**Language/Version**: [e.g., Python 3.11, Swift 5.9, Rust 1.75 or NEEDS CLARIFICATION]  
**Primary Dependencies**: [e.g., FastAPI, UIKit, LLVM or NEEDS CLARIFICATION]  
**Storage**: [if applicable, e.g., PostgreSQL, CoreData, files or N/A]  
**Testing**: [e.g., pytest, XCTest, cargo test or NEEDS CLARIFICATION]  
**Target Platform**: [e.g., Linux server, iOS 15+, WASM or NEEDS CLARIFICATION]
**Project Type**: [single/web/mobile - determines source structure]  
**Performance Goals**: [domain-specific, e.g., 1000 req/s, 10k lines/sec, 60 fps or NEEDS CLARIFICATION]  
**Constraints**: [domain-specific, e.g., <200ms p95, <100MB memory, offline-capable or NEEDS CLARIFICATION]  
**Scale/Scope**: [domain-specific, e.g., 10k users, 1M LOC, 50 screens or NEEDS CLARIFICATION]

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

> **Constitution v1.1.0** — All gates apply to Phase 2 and Phase 3 features.

**PHASE 2 GOLDEN RULE (Phase 3 features only):**
- [ ] Feature is purely ADDITIVE — no Phase 2 files modified except `models.py` (append only)
- [ ] All Phase 2 frozen files untouched (login, signup, dashboard, TaskList, TaskCard, TaskForm,
      api.ts, auth.ts, task.ts, tasks.py, auth.py, db.py)

**AUTH GATE:**
- [ ] Every new endpoint uses `Depends(get_current_user)` — no unprotected routes
- [ ] JWT verified before any data access
- [ ] 401 returned for missing/invalid token; 403 for ownership mismatch

**DATA ISOLATION GATE:**
- [ ] Every DB query filters by `user_id`
- [ ] URL `user_id` validated against JWT `user_id`
- [ ] New models (conversations, messages, user_activity, email_log) all include `user_id` index

**SECRETS GATE:**
- [ ] `GROQ_API_KEY` in `backend/.env` only — not in any source file
- [ ] `BETTER_AUTH_SECRET` identical in `frontend/.env.local` and `backend/.env`
- [ ] `.env` files listed in `.gitignore`

**STATELESS SERVER GATE (Phase 3):**
- [ ] No in-memory user state between requests
- [ ] Conversation history loaded from DB on every chat request

**FREE TIER GATE (Phase 3):**
- [ ] Groq API used — not OpenAI, not any paid AI service
- [ ] MCP SDK via `pip install mcp` — no paid tool SDK

**MCP TOOLS GATE (Phase 3):**
- [ ] Each MCP tool opens and closes its own DB session
- [ ] No `user_id` in tool schemas — always injected server-side in `execute_tool()`
- [ ] Every tool wrapped in `try/except` returning `{"error": str(e)}` on failure

**Complexity Violations** (fill only if a gate cannot be met):

| Gate | Why Cannot Meet | Mitigation |
|------|----------------|------------|
| | | |

## Project Structure

### Documentation (this feature)

```text
specs/[###-feature]/
├── plan.md              # This file (/sp.plan command output)
├── research.md          # Phase 0 output (/sp.plan command)
├── data-model.md        # Phase 1 output (/sp.plan command)
├── quickstart.md        # Phase 1 output (/sp.plan command)
├── contracts/           # Phase 1 output (/sp.plan command)
└── tasks.md             # Phase 2 output (/sp.tasks command - NOT created by /sp.plan)
```

### Source Code (repository root)
<!--
  ACTION REQUIRED: Replace the placeholder tree below with the concrete layout
  for this feature. Delete unused options and expand the chosen structure with
  real paths (e.g., apps/admin, packages/something). The delivered plan must
  not include Option labels.
-->

```text
# [REMOVE IF UNUSED] Option 1: Single project (DEFAULT)
src/
├── models/
├── services/
├── cli/
└── lib/

tests/
├── contract/
├── integration/
└── unit/

# [REMOVE IF UNUSED] Option 2: Web application (when "frontend" + "backend" detected)
backend/
├── src/
│   ├── models/
│   ├── services/
│   └── api/
└── tests/

frontend/
├── src/
│   ├── components/
│   ├── pages/
│   └── services/
└── tests/

# [REMOVE IF UNUSED] Option 3: Mobile + API (when "iOS/Android" detected)
api/
└── [same as backend above]

ios/ or android/
└── [platform-specific structure: feature modules, UI flows, platform tests]
```

**Structure Decision**: [Document the selected structure and reference the real
directories captured above]

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| [e.g., 4th project] | [current need] | [why 3 projects insufficient] |
| [e.g., Repository pattern] | [specific problem] | [why direct DB access insufficient] |
