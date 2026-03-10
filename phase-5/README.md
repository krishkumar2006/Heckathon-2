# Phase 5: Advanced Cloud Deployment — FlowTask AI

Event-driven, AI-powered task manager with natural language interface, deployed on Kubernetes with Dapr and Kafka.

## Architecture

```
Frontend (Next.js) --> Backend (FastAPI) --> Dapr Sidecar --> Kafka (Redpanda)
                           |                    |
                           v                    v
                      PostgreSQL          Dapr Jobs API
                      (Neon/Local)        (Reminders)
```

**Stack:** Next.js 15 + FastAPI + SQLModel + Dapr + Redpanda (Kafka) + Helm + GitHub Actions + Groq LLaMA 3.3

## Features

### Basic
- Add, delete, update, view, and complete tasks via natural language
- User authentication with JWT

### Intermediate
- Task priorities (high/medium/low)
- Tags and categories
- Search by keyword, filter by status/priority/date
- Sort by due date, priority, or alphabetically

### Advanced
- Recurring tasks (daily/weekly/monthly) with auto-spawn on completion
- Due dates with time-based reminders via Dapr Jobs API
- Event-driven architecture: task CRUD publishes events via Dapr Pub/Sub to Kafka
- SSE (Server-Sent Events) for real-time reminder notifications
- Request logging middleware with `/metrics` endpoint

## Quick Start

### Prerequisites
- Python 3.11+, Node.js 20+, Docker Desktop

### Docker Compose (fastest)

```bash
# Create .env file
cp .env.example .env  # Fill in your values

# Start all services
docker-compose up --build

# Frontend: http://localhost:3000
# Backend API: http://localhost:8000
# API Docs: http://localhost:8000/docs
```

### Local Development

```bash
# Backend
cd backend
pip install -r requirements.txt
DATABASE_URL="sqlite:///./dev.db" uvicorn main:app --reload --port 8000

# Frontend
cd frontend
npm install
npm run dev
```

### Minikube Deployment

```bash
# 1. Start Minikube
minikube start --driver=docker

# 2. Install Dapr
dapr init -k --wait

# 3. Build images
eval $(minikube docker-env)
docker build -t todo-backend:local ./backend
docker build -t todo-frontend:local ./frontend

# 4. Deploy with Helm
helm install todo-chatbot ./helm/todo-chatbot \
  -f ./helm/todo-chatbot/values-minikube.yaml

# 5. Access frontend
minikube service todo-frontend --url
```

### Cloud Deployment (Vercel + Render)

**Frontend → Vercel**
1. Connect GitHub repo on vercel.com
2. Set root directory: `phase-5/frontend`
3. Add env var: `NEXT_PUBLIC_API_URL` = your Render backend URL

**Backend → Render**
1. Connect GitHub repo on render.com
2. Set root directory: `phase-5/backend`
3. Build command: `pip install -r requirements.txt`
4. Start command: `uvicorn main:app --host 0.0.0.0 --port $PORT`
5. Add env vars: `DATABASE_URL`, `GROK_API_KEY`, `BETTER_AUTH_SECRET`, `FRONTEND_URL`

**CI/CD — GitHub Actions**

Push to `master` → runs tests automatically → triggers Render deploy.

Required GitHub Secret:

| Secret | Description |
|--------|-------------|
| `RENDER_DEPLOY_HOOK_URL` | Render deploy hook URL |

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | Liveness probe |
| GET | `/ready` | Readiness probe (DB check) |
| GET | `/metrics` | Application metrics |
| GET | `/api/{user_id}/tasks` | List tasks (search, filter, sort) |
| POST | `/api/{user_id}/tasks` | Create task |
| GET | `/api/{user_id}/tasks/{id}` | Get task |
| PUT | `/api/{user_id}/tasks/{id}` | Update task |
| DELETE | `/api/{user_id}/tasks/{id}` | Delete task |
| PATCH | `/api/{user_id}/tasks/{id}/complete` | Toggle completion |
| POST | `/api/{user_id}/tasks/{id}/tags` | Add tags |
| DELETE | `/api/{user_id}/tasks/{id}/tags/{tag}` | Remove tag |
| POST | `/api/chat` | AI chatbot endpoint |
| GET | `/api/notifications/{user_id}/sse` | SSE notifications |

## Project Structure

```
phase-5/
├── backend/
│   ├── main.py                    # FastAPI entry point
│   ├── models.py                  # SQLModel database models
│   ├── db.py                      # Database connection
│   ├── middleware/
│   │   └── logging_middleware.py  # Request logging + metrics
│   ├── routes/
│   │   ├── tasks.py               # Task CRUD + events
│   │   ├── chat.py                # AI chatbot
│   │   ├── health.py              # Health + readiness + metrics
│   │   ├── events.py              # Dapr subscription handlers
│   │   ├── jobs.py                # Dapr Jobs callback
│   │   └── notifications.py       # SSE endpoint
│   ├── services/
│   │   ├── event_publisher.py     # Dapr Pub/Sub publisher
│   │   ├── reminder_service.py    # Dapr Jobs scheduler
│   │   └── recurring_service.py   # Recurring task spawner
│   ├── agent/
│   │   └── todo_agent.py          # AI agent (Groq LLaMA 3.3)
│   ├── mcp/
│   │   └── tools.py               # MCP tools for AI agent
│   └── tests/                     # 38 tests (contract, integration, unit)
├── frontend/                      # Next.js 15 — FlowTask UI
├── helm/todo-chatbot/             # Kubernetes Helm chart
├── dapr-components/               # Local Dapr component configs
├── .github/workflows/
│   ├── ci.yml                     # Run tests on push
│   └── cd.yml                     # Deploy to Render
├── docker-compose.yml             # Local full-stack with Dapr
└── render.yaml                    # Render deployment config
```

## Testing

```bash
cd backend
pip install pytest pytest-asyncio httpx
pytest tests/ -v
```

38 tests across 3 layers:
- **Contract tests**: health, priorities, tags, search/filter/sort, due dates
- **Integration tests**: event publishing, Dapr subscriptions
- **Unit tests**: reminder service scheduling/cancellation

## Environment Variables

### Backend

| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASE_URL` | PostgreSQL connection string | Required |
| `GROK_API_KEY` | Groq API key | Required |
| `BETTER_AUTH_SECRET` | JWT signing secret | Required |
| `FRONTEND_URL` | Frontend URL for CORS | `http://localhost:3000` |
| `EXTRA_ORIGINS` | Extra CORS origins (comma-separated) | - |
| `DAPR_HTTP_PORT` | Dapr sidecar HTTP port | `3500` |
| `LOG_LEVEL` | Logging level | `INFO` |

### Frontend

| Variable | Description | Default |
|----------|-------------|---------|
| `NEXT_PUBLIC_API_URL` | Backend URL | `http://localhost:8000` |
