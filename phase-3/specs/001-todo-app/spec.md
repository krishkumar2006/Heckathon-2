# Feature Specification: Todo App — Full-Stack Task Manager

> **This spec follows `.specify/memory/constitution.md` — read it first.**

**Feature Branch**: `001-todo-app`
**Created**: 2026-02-27
**Status**: Draft

---

## User Scenarios & Testing *(mandatory)*

### User Story 1 — Account Registration & Login (Priority: P1)

A new user visits the app, creates an account with their name, email, and password,
then signs in and is taken directly to their personal task dashboard. A returning user
opens the app and is redirected to login; after signing in, they see their existing tasks.

**Why this priority**: Without authentication, no personalized task management is possible.
This is the entry gate to all other features. Every other story depends on this.

**Independent Test**: Can be tested by: (1) navigating to the signup page, creating
an account, and verifying the dashboard loads with an empty task list; (2) signing out
and signing back in, verifying the same dashboard is restored.

**Acceptance Scenarios**:

1. **Given** a visitor on the app's root URL with no account, **When** they click "Sign Up"
   and enter a valid name, email, and password (min 8 characters), **Then** their account
   is created and they are redirected to the dashboard.

2. **Given** a returning user on the login page, **When** they enter correct credentials,
   **Then** they are redirected to their personal dashboard showing their tasks.

3. **Given** a user on the login page, **When** they enter an incorrect password,
   **Then** a clear error message is shown and they remain on the login page.

4. **Given** a signed-in user, **When** they click "Logout", **Then** their session
   ends and they are redirected to the login page.

5. **Given** an unauthenticated visitor who navigates directly to `/dashboard`,
   **When** the page loads, **Then** they are automatically redirected to `/login`.

6. **Given** a user trying to sign up, **When** they submit a password shorter than
   8 characters or a mismatched confirmation password, **Then** a validation error
   is shown before the form is submitted.

---

### User Story 2 — Create a Task (Priority: P2)

A signed-in user wants to add a new task to their list. They enter a title (required)
and an optional description, submit the form, and immediately see the new task appear
in their list.

**Why this priority**: Creating tasks is the primary value action of the app. Without
it, the app has no functional purpose.

**Independent Test**: After signing in, a user submits the task creation form and
verifies the new task appears in their list without a page reload.

**Acceptance Scenarios**:

1. **Given** a signed-in user on the dashboard, **When** they enter a title (1–200 chars)
   and click "Add Task", **Then** the task appears at the top of their list and the
   form resets to empty.

2. **Given** a signed-in user, **When** they submit a task creation form with an empty
   title, **Then** the form is not submitted and a validation error is shown.

3. **Given** a signed-in user, **When** they add an optional description (up to 1000 chars),
   **Then** the description is saved and displayed on the task card.

4. **Given** a signed-in user, **When** the task is being saved, **Then** the submit
   button shows a loading state ("Adding...") and the form is disabled until complete.

5. **Given** a signed-in user, **When** the save fails, **Then** an error message is
   shown and the form data is preserved for retry.

---

### User Story 3 — View and Filter Tasks (Priority: P3)

A signed-in user can see all their tasks on the dashboard, and filter them by status:
All, Pending, or Completed. The filter shows a count for each category so the user
knows how many tasks are in each state.

**Why this priority**: Viewing tasks is the second most essential action — users must
be able to see what they've created. Filtering adds immediate productivity value.

**Independent Test**: After creating several tasks and marking some complete, a user
clicks each filter tab and verifies only the correct tasks are shown with accurate counts.

**Acceptance Scenarios**:

1. **Given** a signed-in user on the dashboard, **When** the page loads, **Then**
   all their tasks are displayed with their title, description (if any), creation date,
   and completion status.

2. **Given** a user with a mix of completed and pending tasks, **When** they click
   "Pending", **Then** only incomplete tasks are shown.

3. **Given** a user with a mix of completed and pending tasks, **When** they click
   "Completed", **Then** only completed tasks are shown.

4. **Given** a user with no tasks, **When** they view the dashboard, **Then** a
   "No tasks yet" message is shown.

5. **Given** a user whose tasks are loading, **When** the page first renders,
   **Then** a loading spinner is shown until tasks are fetched.

6. **Given** a user whose task fetch fails, **When** the error occurs, **Then**
   a clear error message is shown (not a blank screen or crash).

---

### User Story 4 — Edit and Delete Tasks (Priority: P4)

A signed-in user can edit an existing task's title or description inline, and delete
tasks they no longer need (with a confirmation step before permanent deletion).

**Why this priority**: Editable and deletable tasks are essential for a usable task
manager. Without them, mistakes cannot be corrected.

**Independent Test**: A user edits an existing task, saves, and sees the updated
values. Then a user clicks delete, confirms, and the task disappears from the list.

**Acceptance Scenarios**:

1. **Given** a task card, **When** the user clicks "Edit", **Then** an inline form
   appears pre-filled with the current title and description.

2. **Given** an open edit form, **When** the user saves changes, **Then** the task
   updates and the inline form closes, showing the updated values.

3. **Given** a task card, **When** the user clicks "Delete", **Then** a confirmation
   dialog appears before any deletion occurs.

4. **Given** the confirmation dialog, **When** the user confirms deletion,
   **Then** the task is permanently removed from their list.

5. **Given** the confirmation dialog, **When** the user cancels, **Then** the task
   is not deleted and the dialog closes.

---

### User Story 5 — Toggle Task Completion (Priority: P5)

A signed-in user can mark a task complete by clicking its checkbox. Completed tasks
are visually distinguished (strikethrough title). Clicking again marks it pending.

**Why this priority**: Toggling completion is the core progress-tracking interaction.
It gives users the satisfaction of "checking off" tasks.

**Independent Test**: A user clicks the checkbox on a pending task and verifies it
shows as completed (strikethrough). Clicking again verifies it returns to pending.

**Acceptance Scenarios**:

1. **Given** a pending task, **When** the user clicks the checkbox, **Then** the task
   is marked completed and the title displays with a strikethrough style.

2. **Given** a completed task, **When** the user clicks the checkbox, **Then** the
   task is marked pending and the strikethrough is removed.

3. **Given** a task being toggled, **When** the action is in progress, **Then**
   the UI reflects the change immediately (optimistic or loading state).

---

### Edge Cases

- What happens when a user tries to access another user's tasks via URL manipulation?
  → They receive a "403 Access Denied" response; no task data is exposed.
- What happens when the session token expires mid-session?
  → The next request returns 401; the user is redirected to `/login`.
- What happens when a task title exceeds 200 characters?
  → The form shows a character-limit error before submission.
- What happens when a description exceeds 1000 characters?
  → The form shows a character-limit error before submission.
- What happens when the backend is unreachable?
  → The UI shows a "Server error, try again" message; no crash occurs.
- What happens if a user submits the task form twice rapidly?
  → The submit button is disabled during the first submission to prevent duplicates.

---

## Requirements *(mandatory)*

### Functional Requirements

**Authentication:**
- **FR-001**: System MUST allow users to create an account with name, email, and password.
- **FR-002**: System MUST validate email format and enforce a minimum 8-character password.
- **FR-003**: System MUST authenticate users via email and password and issue a session token.
- **FR-004**: System MUST protect all task-related actions behind authentication; unauthenticated
  requests MUST be rejected.
- **FR-005**: System MUST redirect unauthenticated visitors from protected pages to the login page.
- **FR-006**: System MUST allow users to sign out, ending their session immediately.

**Task Management:**
- **FR-007**: Authenticated users MUST be able to create tasks with a title (required, 1–200 chars)
  and an optional description (max 1000 chars).
- **FR-008**: Authenticated users MUST be able to view all their tasks on the dashboard.
- **FR-009**: Users MUST be able to filter their task list by status: All, Pending, or Completed.
- **FR-010**: Users MUST be able to edit the title and/or description of any of their tasks.
- **FR-011**: Users MUST be able to delete any of their tasks, with a confirmation step.
- **FR-012**: Users MUST be able to toggle a task between "pending" and "completed" status.

**Data Isolation & Security:**
- **FR-013**: System MUST ensure each user can only view, create, edit, complete, or delete
  their own tasks — never another user's tasks.
- **FR-014**: System MUST return a 403 error when an authenticated user attempts to access
  a task they do not own.
- **FR-015**: Session tokens MUST expire after a maximum of 7 days.
- **FR-016**: All secrets (auth secret, database URL) MUST be stored outside source code
  in environment configuration files that are never committed to version control.

**UI States:**
- **FR-017**: Every data-fetching operation MUST display a loading state while in progress.
- **FR-018**: Every operation MUST display a user-friendly error message on failure.
- **FR-019**: Every form MUST show validation errors for invalid input before submission.

### Key Entities

- **User**: Represents a registered person. Has a unique identifier, display name, email
  address, and hashed password. One user owns many tasks.

- **Task**: Represents a single to-do item belonging to one user. Has a title (required),
  optional description, completion status (pending or completed), creation timestamp,
  and last-updated timestamp. A task always belongs to exactly one user and can never
  be transferred.

---

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A new user can complete signup, reach their dashboard, and create their
  first task in under 2 minutes from a cold start.

- **SC-002**: A signed-in user can create, edit, complete, and delete a task — completing
  the full task lifecycle — in under 30 seconds.

- **SC-003**: All 6 task endpoints respond within 500ms for a single user's task list
  of up to 100 tasks under normal operating conditions.

- **SC-004**: 100% of task-data requests are rejected with a clear error (not silently
  ignored or served) when the user is unauthenticated or accessing another user's data.

- **SC-005**: The dashboard correctly shows 0 tasks for a new user, and after creating
  5 tasks, the "All" filter shows exactly 5, "Pending" shows 5, and "Completed" shows 0.

- **SC-006**: After marking 3 of 5 tasks complete, the "Completed" filter shows exactly 3
  and "Pending" shows exactly 2 — with no page reload required.

- **SC-007**: The app remains fully functional (all 6 CRUD operations working) when accessed
  by two different users simultaneously, with zero data leakage between accounts.

---

## Assumptions

- Users access the app via a web browser on desktop or mobile.
- Email/password authentication is the only sign-in method for this hackathon scope.
  Social login (Google, GitHub, etc.) is out of scope.
- Task list pagination is out of scope; all of a user's tasks are loaded at once.
- Real-time updates (e.g., WebSockets for live task sync across tabs) are out of scope.
- Email verification on signup is out of scope for the hackathon.
- Password reset flow is out of scope for the hackathon.
- The app is a single-tenant web app; there are no teams, sharing, or collaboration features.
- Task ordering is by creation date (newest first) by default; custom ordering is out of scope.

---

## Scope Boundaries

**In Scope:**
- User signup and login (email/password)
- Session management with token-based auth (7-day expiry)
- Full task CRUD: create, read (list + single), update, delete
- Task completion toggle
- Task list filtering: All / Pending / Completed
- Per-user data isolation enforced on every operation
- Three UI states on every async operation: loading, error, success
- Mobile-responsive UI

**Out of Scope:**
- Password reset or email verification
- Social/OAuth login
- Task sharing, collaboration, or teams
- Task due dates, priorities, or labels
- File attachments on tasks
- Search within tasks
- Notifications or reminders
- Pagination or infinite scroll
- Offline mode
- Admin dashboard
