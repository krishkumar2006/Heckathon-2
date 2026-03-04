# Feature Specification: [FEATURE NAME]

**Feature Branch**: `[###-feature-name]`  
**Created**: [DATE]  
**Status**: Draft  
**Input**: User description: "$ARGUMENTS"

## User Scenarios & Testing *(mandatory)*

<!--
  IMPORTANT: User stories should be PRIORITIZED as user journeys ordered by importance.
  Each user story/journey must be INDEPENDENTLY TESTABLE - meaning if you implement just ONE of them,
  you should still have a viable MVP (Minimum Viable Product) that delivers value.
  
  Assign priorities (P1, P2, P3, etc.) to each story, where P1 is the most critical.
  Think of each story as a standalone slice of functionality that can be:
  - Developed independently
  - Tested independently
  - Deployed independently
  - Demonstrated to users independently
-->

### User Story 1 - [Brief Title] (Priority: P1)

[Describe this user journey in plain language]

**Why this priority**: [Explain the value and why it has this priority level]

**Independent Test**: [Describe how this can be tested independently - e.g., "Can be fully tested by [specific action] and delivers [specific value]"]

**Acceptance Scenarios**:

1. **Given** [initial state], **When** [action], **Then** [expected outcome]
2. **Given** [initial state], **When** [action], **Then** [expected outcome]

---

### User Story 2 - [Brief Title] (Priority: P2)

[Describe this user journey in plain language]

**Why this priority**: [Explain the value and why it has this priority level]

**Independent Test**: [Describe how this can be tested independently]

**Acceptance Scenarios**:

1. **Given** [initial state], **When** [action], **Then** [expected outcome]

---

### User Story 3 - [Brief Title] (Priority: P3)

[Describe this user journey in plain language]

**Why this priority**: [Explain the value and why it has this priority level]

**Independent Test**: [Describe how this can be tested independently]

**Acceptance Scenarios**:

1. **Given** [initial state], **When** [action], **Then** [expected outcome]

---

[Add more user stories as needed, each with an assigned priority]

### Edge Cases

<!--
  ACTION REQUIRED: The content in this section represents placeholders.
  Fill them out with the right edge cases.
-->

- What happens when [boundary condition]?
- How does system handle [error scenario]?

## Requirements *(mandatory)*

<!--
  ACTION REQUIRED: The content in this section represents placeholders.
  Fill them out with the right functional requirements.
-->

### Functional Requirements

- **FR-001**: System MUST [specific capability, e.g., "allow users to create accounts"]
- **FR-002**: System MUST [specific capability, e.g., "validate email addresses"]  
- **FR-003**: Users MUST be able to [key interaction, e.g., "reset their password"]
- **FR-004**: System MUST [data requirement, e.g., "persist user preferences"]
- **FR-005**: System MUST [behavior, e.g., "log all security events"]

*Example of marking unclear requirements:*

- **FR-006**: System MUST authenticate users via [NEEDS CLARIFICATION: auth method not specified - email/password, SSO, OAuth?]
- **FR-007**: System MUST retain user data for [NEEDS CLARIFICATION: retention period not specified]

### Key Entities *(include if feature involves data)*

- **[Entity 1]**: [What it represents, key attributes without implementation]
- **[Entity 2]**: [What it represents, relationships to other entities]

## Security Requirements *(mandatory for Phase 3 features)*

<!--
  ACTION REQUIRED: Verify each item applies to this feature. Check boxes that apply.
  If this is a Phase 2 feature only, this section can be marked N/A.
  For any Phase 3 feature (chat, activity, MCP tools), ALL items are mandatory.
-->

### Auth Requirements

- [ ] **SR-001**: Every new endpoint MUST verify JWT via `Depends(get_current_user)`
- [ ] **SR-002**: Missing/invalid token MUST return 401 (not 403, not 500)
- [ ] **SR-003**: URL `{user_id}` MUST be validated against JWT `user_id`; mismatch returns 403

### Data Isolation Requirements

- [ ] **SR-004**: Every DB query for new models MUST include `WHERE user_id = current_user.id`
- [ ] **SR-005**: Users MUST NOT be able to access another user's conversations, messages,
      emails, or activity — enforced at query level, not just route level

### Secrets Requirements

- [ ] **SR-006**: `GROQ_API_KEY` MUST exist only in `backend/.env` — never in source code
- [ ] **SR-007**: No new secrets introduced in source files or committed to git

### Phase 2 Freeze Requirements *(Phase 3 features only)*

- [ ] **SR-008**: Feature MUST NOT modify any frozen Phase 2 file
  (login, signup, dashboard pages; TaskList/Card/Form components; api.ts, auth.ts, task.ts,
  tasks.py, auth.py, db.py)
- [ ] **SR-009**: `models.py` changes MUST be append-only (new classes at bottom only)
- [ ] **SR-010**: `main.py` changes MUST be new router imports only

### AI / MCP Safety Requirements *(chat feature only)*

- [ ] **SR-011**: Groq free tier MUST be used — no OpenAI or paid AI
- [ ] **SR-012**: `user_id` MUST be injected server-side; MUST NOT appear in MCP tool schemas
- [ ] **SR-013**: All MCP tools MUST be wrapped in `try/except`; errors returned as
      `{"error": str(e)}`, never raised
- [ ] **SR-014**: Max tokens MUST be set to 1000 in all Groq API calls

---

## Success Criteria *(mandatory)*

<!--
  ACTION REQUIRED: Define measurable success criteria.
  These must be technology-agnostic and measurable.
-->

### Measurable Outcomes

- **SC-001**: [Measurable metric, e.g., "Users can complete account creation in under 2 minutes"]
- **SC-002**: [Measurable metric, e.g., "System handles 1000 concurrent users without degradation"]
- **SC-003**: [User satisfaction metric, e.g., "90% of users successfully complete primary task on first attempt"]
- **SC-004**: [Business metric, e.g., "Reduce support tickets related to [X] by 50%"]
