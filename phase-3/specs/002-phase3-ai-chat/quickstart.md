# Quickstart: Phase 3 — AI Chat Assistant

**Feature**: `002-phase3-ai-chat`
**Date**: 2026-03-01
**Prerequisites**: Phase 2 fully working (dashboard, auth, tasks)

---

## Pre-requisites Checklist

Before starting Phase 3 implementation:

- [ ] Phase 2 running: `cd backend && uvicorn main:app --reload --port 8000`
- [ ] Phase 2 frontend running: `cd frontend && npm run dev`
- [ ] Neon database connected (test: `cd backend && python -c "from db import engine; print('OK')"`)
- [ ] `backend/venv` activated
- [ ] You can log in to the app at `localhost:3000`

---

## Step 1: Get Groq API Key (5 minutes)

1. Open browser → go to `console.groq.com`
2. Sign up with email (no credit card required)
3. Verify email → log in
4. Navigate to `console.groq.com/keys`
5. Click **"Create API Key"**
6. Name: `hackathon-todo-phase3`
7. Copy the key (starts with `gsk_`)

Add to `backend/.env` (never commit this file):
```env
GROQ_API_KEY=gsk_your_key_here
```

Your final `backend/.env` should look like:
```env
BETTER_AUTH_SECRET=your_existing_secret
DATABASE_URL=your_existing_neon_url
FRONTEND_URL=http://localhost:3000
GROQ_API_KEY=gsk_your_new_key_here
```

---

## Step 2: Install New Python Packages

```bash
cd backend
# Activate your virtual environment first
source venv/bin/activate    # Mac/Linux
# OR
venv\Scripts\activate       # Windows

pip install groq==0.11.0 mcp==1.0.0 python-dateutil==2.9.0 user-agents==2.2.0
pip freeze > requirements.txt
```

Verify:
```bash
python -c "import groq; import mcp; import dateutil; import user_agents; print('All Phase 3 packages OK!')"
```

---

## Step 3: Add New Models to models.py

Open `backend/models.py` and **ADD** these 4 model classes and 2 schemas at the **bottom**.
Do NOT modify or remove the existing `Task` model.

See [data-model.md](./data-model.md) for the exact Python code.

After adding models, create the new tables:
```bash
cd backend
python -c "
from db import engine
from models import SQLModel, Conversation, Message, UserActivity, EmailLog
SQLModel.metadata.create_all(engine)
print('New tables created: conversations, messages, user_activity, email_log')
"
```

Verify in Neon dashboard: 4 new tables should appear alongside the existing `tasks` table.

---

## Step 4: Create MCP Server

Create `backend/mcp_server.py` with all 9 tool functions.
See [contracts/activity-api.md](./contracts/activity-api.md) for tool schemas.
See [spec.md](./spec.md) SPEC 1.4 for implementation details.

Test each tool:
```bash
cd backend
python -c "
from mcp_server import add_task, list_tasks, get_current_datetime

result = add_task('test_user', 'Test task from MCP')
print('add_task:', result)
assert result.get('status') == 'created', f'Expected created, got: {result}'

tasks = list_tasks('test_user', 'all')
print('list_tasks:', tasks)
assert isinstance(tasks, list)

dt = get_current_datetime()
print('get_current_datetime:', dt)
assert 'date' in dt

print('MCP tools basic test PASSED!')
"
```

---

## Step 5: Create Groq Agent

Create `backend/groq_agent.py` with:
- `GROQ_TOOLS` list (9 tool schemas)
- `execute_tool(tool_name, arguments, user_id)` function
- `async run_agent(user_id, messages)` function

Test:
```bash
cd backend
python -c "
import asyncio
from dotenv import load_dotenv
load_dotenv()
from groq_agent import run_agent

async def test():
    result = await run_agent('test_user', [{'role': 'user', 'content': 'Hello!'}])
    print('Response:', result['response'][:80])
    print('Tools called:', result['tool_calls'])
    assert 'response' in result
    print('Groq agent test PASSED!')

asyncio.run(test())
"
```

---

## Step 6: Create Chat Endpoint

Create `backend/routes/chat.py` with `POST /api/{user_id}/chat`.
Create `backend/routes/activity.py` with `GET /api/{user_id}/activity` and
`GET /api/{user_id}/conversations`.

Add to `backend/main.py` (additive only — after existing imports and router):
```python
from routes.chat import router as chat_router
from routes.activity import router as activity_router

app.include_router(chat_router, prefix="/api")
app.include_router(activity_router, prefix="/api")
```

Restart the server and test:
```bash
# Get a JWT token from your login response first, then:
curl -X POST http://localhost:8000/api/{your_user_id}/chat \
  -H "Authorization: Bearer <your_jwt_token>" \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello! What can you do?"}'
```

Expected: `200` with `conversation_id`, `response`, and `tool_calls: []`

---

## Step 7: Add Login Tracking + Seed Emails

Add HTTP middleware to `backend/main.py` (additive — before router registration).
See [spec.md](./spec.md) SPEC 1.8 for implementation.

Create `backend/seed_emails.py` (8 sample emails).

Run email seed:
```bash
cd backend
python seed_emails.py --user_id <your_user_id>
# Expected: "Successfully seeded 8 emails for user: <id>"
```

Test via chat:
```bash
curl -X POST http://localhost:8000/api/{your_user_id}/chat \
  -H "Authorization: Bearer <your_jwt_token>" \
  -H "Content-Type: application/json" \
  -d '{"message": "Show my recent emails"}'
```

Expected: AI calls `get_emails` tool and lists all 8 emails.

---

## Step 8: Build Frontend Chat UI

Create `frontend/app/chat/page.tsx` as a `"use client"` component.
See [spec.md](./spec.md) PART 2 for complete implementation.

Add ONE chat link to `frontend/components/Navbar.tsx`:
- Between the app title and the "Sign out" button
- `href="/chat"`, text `"💬 Chat"`
- Same styling as existing elements

**Do NOT** modify any other part of Navbar.tsx.

---

## Step 9: Phase 2 Regression Test

Before marking Phase 3 complete, verify Phase 2 still works:

```bash
# All should return 200/201:
curl http://localhost:8000/health
curl -H "Authorization: Bearer <token>" http://localhost:8000/api/{user_id}/tasks
curl -X POST -H "Authorization: Bearer <token>" -H "Content-Type: application/json" \
  -d '{"title": "Regression test task"}' \
  http://localhost:8000/api/{user_id}/tasks
```

In browser:
1. `/login` → login works
2. `/dashboard` → tasks visible, create/edit/delete/filter all work
3. Click "Sign out" → redirected to `/login`

---

## Step 10: Full Integration Test

Open browser at `localhost:3000/chat`.

Test all 10 natural language commands (from spec.md SPEC 3.3):

| Command | Expected Tool | Expected Result |
|---------|--------------|-----------------|
| "Add a task to buy groceries" | `add_task` | Task created ✅ with ID |
| "Show all my tasks" | `list_tasks` | Numbered list |
| "What's still pending?" | `list_tasks(pending)` | Only incomplete tasks |
| "Mark task 1 as done" | `complete_task` | Confirmation |
| "Delete task 2" | `delete_task` | Deletion confirmed |
| "Change task 1 title to Call mom tonight" | `update_task` | Updated title shown |
| "Show my emails" | `get_emails` | 8 seeded emails |
| "Who has logged into my account?" | `get_login_activity` | Login history |
| "What time is it right now?" | `get_current_datetime` | Current date/time |
| "Give me a complete overview" | `get_project_stats` | All 7 stats fields |

---

## Environment Variables Summary

**`backend/.env`** (additions only):
```env
GROQ_API_KEY=gsk_xxxx   # New in Phase 3
```

**`frontend/.env.local`**: No changes needed for Phase 3.

---

## Troubleshooting

**"GROQ_API_KEY environment variable not set"**
→ Ensure `load_dotenv()` is called before creating Groq client
→ Check `backend/.env` has the key set correctly

**401 on chat endpoint**
→ JWT token expired or missing; re-login and get a fresh token
→ Ensure `BETTER_AUTH_SECRET` matches in both `.env` files

**Groq rate limit (429)**
→ Free tier: 30 requests/minute — wait 1 minute and retry
→ The agent has built-in retry logic (1 retry with 1 second delay)

**Tool returns error dict**
→ Normal behavior — tools return `{"error": "message"}` on failure
→ The AI agent will handle gracefully and tell the user in a friendly way

**Phase 2 tests fail after Phase 3 changes**
→ STOP immediately — this violates the Golden Rule
→ Revert the change that broke Phase 2, then re-implement differently
→ Use `git diff backend/main.py` to check what changed

**Tables not found in DB**
→ Run `SQLModel.metadata.create_all(engine)` again
→ Check Neon dashboard for table existence
