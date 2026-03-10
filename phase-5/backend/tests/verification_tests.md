# Phase 3 Verification Tests

This document outlines the manual verification tests required to validate the AI-Powered Todo Chatbot implementation.

## Prerequisites

1. Backend running: `uvicorn main:app --reload --port 8000`
2. Frontend running: `npm run dev`
3. Valid `.env` file with:
   - `DATABASE_URL` (Neon PostgreSQL)
   - `OPENAI_API_KEY`
   - `FRONTEND_URL`

## Test T032: Authentication for Chat

**Goal**: Verify unauthenticated requests to `/api/chat` return 401

```bash
# Test without auth token
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "test"}'

# Expected: 401 Unauthorized
# {"detail":"Not authenticated"}
```

**Pass Criteria**: Response status is 401 Unauthorized

---

## Test T044: Add Task via Natural Language

**Goal**: Verify "Add a task to buy groceries" creates task

**Steps**:
1. Sign in at http://localhost:3000/signin
2. Navigate to /chat
3. Type: "Add a task to buy groceries"
4. Verify response confirms task creation
5. Verify task exists in database

**Pass Criteria**:
- AI responds with confirmation
- Task "buy groceries" appears in task list

---

## Test T050: View Tasks via Natural Language

**Goal**: Verify "What's pending?" returns only pending tasks

**Steps**:
1. Ensure you have some pending and completed tasks
2. Ask: "What's pending?"
3. Verify response only shows pending tasks

**Pass Criteria**: Response lists only tasks where completed=false

---

## Test T056: Complete Task via Natural Language

**Goal**: Verify "Mark task 3 as done" completes task

**Steps**:
1. Note the ID of a pending task
2. Say: "Mark task [ID] as done"
3. Verify confirmation response
4. List tasks to confirm it's completed

**Pass Criteria**: Task status changes to completed=true

---

## Test T062: Delete Task via Natural Language

**Goal**: Verify "Delete task 2" removes task

**Steps**:
1. Note the ID of a task to delete
2. Say: "Delete task [ID]"
3. Verify confirmation response
4. List tasks to confirm it's gone

**Pass Criteria**: Task no longer appears in list

---

## Test T068: Update Task via Natural Language

**Goal**: Verify "Change task 1 to call mom tonight" updates title

**Steps**:
1. Note the ID of a task to update
2. Say: "Change task [ID] to call mom tonight"
3. Verify confirmation response
4. List tasks to confirm title changed

**Pass Criteria**: Task title is updated

---

## Test T078: Conversation Persistence

**Goal**: Verify conversation persists after page refresh

**Steps**:
1. Start a new conversation with a message
2. Note the conversation appears in sidebar
3. Refresh the page (F5)
4. Verify conversation and messages are still there

**Pass Criteria**: Messages and conversation persist after refresh

---

## Test T087: User Isolation

**Goal**: Verify User A cannot see User B's data

**Steps**:
1. Sign in as User A
2. Create a task and start a conversation
3. Sign out
4. Sign in as User B (different account)
5. Verify User A's tasks and conversations are not visible

**Pass Criteria**: Each user only sees their own data

---

## Test T088: Stateless Server Verification

**Goal**: Verify server restart doesn't lose data

**Steps**:
1. Create tasks and conversations
2. Stop the backend server (Ctrl+C)
3. Restart the backend server
4. Verify all data is still accessible

**Pass Criteria**: All data persists across server restarts

---

## Test T089: Quickstart Validation

**Goal**: Run through quickstart.md steps

**Steps**:
1. Health check: `curl http://localhost:8000/health`
2. Expected: `{"status": "healthy", "version": "phase-3"}`
3. Sign in and access /chat
4. Test: "Add a task to test the chatbot"
5. Test: "Show my tasks"

**Pass Criteria**: All quickstart steps complete successfully

---

## Summary Checklist

- [ ] T032: 401 on unauthenticated chat request
- [ ] T044: Add task via natural language
- [ ] T050: List pending tasks only
- [ ] T056: Complete task via natural language
- [ ] T062: Delete task via natural language
- [ ] T068: Update task via natural language
- [ ] T078: Conversation persists after refresh
- [ ] T087: User isolation verified
- [ ] T088: Data persists after server restart
- [ ] T089: Quickstart steps completed
