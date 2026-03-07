# AI-Powered Todo App — Phase 4

A full-stack productivity application with AI chat integration. Users can manage their tasks through a dashboard UI **or** by chatting with an AI assistant powered by Groq (LLaMA 3.3 70B).

---

## Features

### Task Management
- Create, update, delete, and complete tasks
- Filter tasks by status: All / Pending / Completed
- Every task is isolated per user (JWT-based ownership)

### AI Chat Assistant
- Full-page chat interface at `/chat`
- Floating chat widget available on the dashboard
- The AI can:
  - List, add, update, complete, and delete your tasks
  - Show your recent emails and login activity
  - Give a project stats overview
  - Tell you the current date and time
- Quick action buttons for common commands
- Smooth auto-scroll and animated thinking dots

### Authentication
- Signup / Login with email and password
- JWT-based session management via Better Auth
- All API routes are protected — no endpoint is left unprotected

---

## Tech Stack

| Layer          | Technology                              |
|----------------|-----------------------------------------|
| Frontend       | Next.js 16, React 19, TypeScript 5, Tailwind CSS 4 |
| Auth           | Better Auth (JWT plugin)                |
| Backend        | FastAPI 0.115, Python 3.11+             |
| AI Agent       | Groq SDK — LLaMA 3.3 70B Versatile     |
| ORM            | SQLModel 0.0.16 (Pydantic v2 + SQLAlchemy) |
| Database       | Neon PostgreSQL (serverless)            |
| Containerization | Docker (multi-stage builds)           |
| Orchestration  | Kubernetes via Minikube (local)         |
| K8s Packaging  | Helm 3                                  |

---

## Project Structure

```
phase3/
├── backend/
│   ├── main.py           # FastAPI app, CORS, startup
│   ├── auth.py           # JWT middleware
│   ├── db.py             # Database engine + session
│   ├── models.py         # SQLModel tables + Pydantic schemas
│   ├── groq_agent.py     # Groq AI agent with tool-calling loop
│   ├── mcp_server.py     # MCP tool implementations
│   ├── seed_emails.py    # Script to seed sample emails
│   ├── routes/
│   │   ├── tasks.py      # Task CRUD endpoints
│   │   ├── chat.py       # AI chat endpoint
│   │   └── activity.py   # User activity logging
│   └── requirements.txt
│
├── frontend/
│   ├── app/
│   │   ├── (auth)/
│   │   │   ├── login/    # Login page
│   │   │   └── signup/   # Signup page
│   │   ├── dashboard/    # Protected task dashboard
│   │   ├── chat/         # Full-page AI chat
│   │   └── api/          # Better Auth + JWT token routes
│   ├── components/
│   │   ├── ChatWidget.tsx    # Floating AI chat widget
│   │   ├── Navbar.tsx        # Navigation + logout
│   │   ├── TaskForm.tsx      # Create task form
│   │   ├── TaskList.tsx      # Task list with filters
│   │   └── TaskCard.tsx      # Single task card
│   └── lib/
│       ├── api.ts            # All backend API calls (centralized)
│       ├── auth.ts           # Better Auth server config
│       └── auth-client.ts    # Better Auth client config
│
├── docker/
│   ├── frontend.Dockerfile   # Multi-stage Next.js build (3 stages)
│   ├── backend.Dockerfile    # Single-stage FastAPI build
│   └── .dockerignore
│
├── helm/
│   ├── todo-frontend/        # Helm chart — Next.js frontend
│   └── todo-backend/         # Helm chart — FastAPI backend
│
└── k8s/
    ├── namespace.yaml         # todo-app namespace
    ├── configmap.yaml         # Non-sensitive env vars
    └── secrets.yaml           # K8s Secrets (gitignored)
```

---

## API Endpoints

### Tasks
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/{user_id}/tasks` | List all tasks |
| POST | `/api/{user_id}/tasks` | Create a task |
| GET | `/api/{user_id}/tasks/{task_id}` | Get a task |
| PUT | `/api/{user_id}/tasks/{task_id}` | Update a task |
| DELETE | `/api/{user_id}/tasks/{task_id}` | Delete a task |
| PATCH | `/api/{user_id}/tasks/{task_id}/complete` | Mark complete |

### Chat (AI)
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/{user_id}/chat` | Send message to AI agent |

### Other
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | Backend health check |
| GET | `/api/{user_id}/activity` | Login activity log |

> All endpoints require a valid JWT Bearer token.

---

## AI Agent Tools

The Groq agent has access to 9 tools:

| Tool | Description |
|------|-------------|
| `add_task` | Create a new task |
| `list_tasks` | List tasks with optional status filter |
| `complete_task` | Mark a task as done |
| `delete_task` | Permanently delete a task |
| `update_task` | Update title or description |
| `get_emails` | Fetch recent inbox emails |
| `get_login_activity` | View login history |
| `get_current_datetime` | Get current date and time |
| `get_project_stats` | Full project overview (tasks, conversations, last login) |

---

## Local Setup (Development)

### Prerequisites
- Python 3.11+
- Node.js 18+
- Neon PostgreSQL database
- Groq API key (free tier at [console.groq.com](https://console.groq.com))

### Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

Create `backend/.env`:
```env
DATABASE_URL=postgresql://user:pass@host/dbname?sslmode=require
BETTER_AUTH_SECRET=your-secret-key
FRONTEND_URL=http://localhost:3000
GROQ_API_KEY=your-groq-api-key
```

```bash
uvicorn main:app --reload --port 8000
```

### Frontend

```bash
cd frontend
npm install
```

Create `frontend/.env.local`:
```env
BETTER_AUTH_SECRET=your-secret-key        # Must match backend
BETTER_AUTH_URL=http://localhost:3000
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_BETTER_AUTH_URL=http://localhost:3000
DATABASE_URL=postgresql://user:pass@host/dbname?sslmode=require
```

```bash
npm run dev
```

Open [http://localhost:3000](http://localhost:3000)

---

## Kubernetes Deployment (Phase 4)

### Prerequisites
- Docker Desktop
- Minikube
- kubectl
- Helm 3

### Deploy

```bash
# 1. Start Minikube
minikube start --driver=docker

# 2. Point Docker CLI to Minikube daemon (Windows PowerShell)
minikube -p minikube docker-env --shell powershell | Invoke-Expression

# 3. Build images inside Minikube
docker build -f docker/backend.Dockerfile -t todo-backend:v1.0.0 ./backend
docker build -f docker/frontend.Dockerfile -t todo-frontend:v1.0.0 \
  --build-arg NEXT_PUBLIC_API_URL=http://localhost:8000 \
  --build-arg NEXT_PUBLIC_BETTER_AUTH_URL=http://localhost:3000 \
  ./frontend

# 4. Apply K8s resources
kubectl apply -f k8s/namespace.yaml
kubectl apply -f k8s/secrets.yaml      # Fill values from backend/.env first

# 5. Deploy with Helm
helm install todo-backend ./helm/todo-backend --namespace todo-app
helm install todo-frontend ./helm/todo-frontend --namespace todo-app

# 6. Verify pods
kubectl get pods -n todo-app

# 7. Access the app (run in separate terminals)
kubectl port-forward svc/todo-backend-todo-backend 8000:8000 -n todo-app
kubectl port-forward svc/todo-frontend-todo-frontend 3001:3000 -n todo-app
```

Open [http://localhost:3001](http://localhost:3001)

---

## Security

- JWT verified on every single endpoint via `Depends(get_current_user)`
- All database queries filter by `user_id` — users cannot access each other's data
- URL `user_id` is validated against JWT `sub` claim (403 on mismatch)
- Secrets live only in `.env` files — never in source code
- `.env` files are git-ignored

---

## Database Models

| Table | Description |
|-------|-------------|
| `task` | User tasks with title, description, completed status |
| `conversations` | AI chat conversation sessions |
| `messages` | Individual chat messages (user + assistant) |
| `user_activity` | Login/logout/signup event log |
| `email_log` | Sample inbox emails for AI queries |

---

## Hackathon — Phase 4

This is Phase 4 of a hackathon project:
- **Phase 1**: Basic project setup
- **Phase 2**: Full-stack Todo app with JWT auth, task CRUD, Next.js dashboard
- **Phase 3**: AI chat integration with Groq LLaMA, MCP tool server, conversation history
- **Phase 4 (this)**: Docker containerization + Kubernetes deployment on Minikube with Helm
