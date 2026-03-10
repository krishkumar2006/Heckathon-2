# Phase 5: Advanced Cloud Deployment - AI Todo Chatbot

Event-driven, AI-powered todo chatbot deployed on Kubernetes with Dapr and Kafka.

## Architecture

```
Frontend (Next.js) --> Backend (FastAPI) --> Dapr Sidecar --> Kafka (Redpanda)
                           |                    |
                           v                    v
                      PostgreSQL          Dapr Jobs API
                      (Neon/Local)        (Reminders)
```

**Stack:** Next.js 16 + FastAPI + SQLModel + Dapr + Redpanda (Kafka) + Helm + GitHub Actions

## Features

### Basic
- Add, delete, update, view, and complete tasks via natural language chatbot
- User authentication with Better Auth + JWT

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
- For Minikube: Minikube, Helm 3, Dapr CLI

### Docker Compose (fastest)

```bash
# Create .env file
cp .env.example .env  # Edit with your values

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

# 3. Build images in Minikube's Docker
eval $(minikube docker-env)    # Linux/Mac
# Windows: minikube docker-env --shell powershell | Invoke-Expression
docker build -t todo-backend:local ./backend
docker build -t todo-frontend:local ./frontend

# 4. Deploy with Helm
helm install todo-chatbot ./helm/todo-chatbot \
  -f ./helm/todo-chatbot/values-minikube.yaml

# 5. Access frontend
minikube service todo-frontend --url
```

### Cloud Deployment (CI/CD)

The GitHub Actions pipeline handles cloud deployment automatically.

**Required GitHub Secrets:**

| Secret | Description |
|--------|-------------|
| `KUBE_CONFIG` | Base64-encoded kubeconfig for cloud cluster |
| `DATABASE_URL` | Neon PostgreSQL connection string |
| `OPENAI_API_KEY` | OpenAI API key |
| `BETTER_AUTH_SECRET` | JWT signing secret |
| `FRONTEND_URL` | Deployed frontend URL |
| `KAFKA_BROKERS` | Redpanda Cloud bootstrap servers |
| `KAFKA_USERNAME` | SASL username |
| `KAFKA_PASSWORD` | SASL password |

Push to `master` to trigger CI (test + build) then CD (deploy to cloud K8s).

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | Liveness probe |
| GET | `/ready` | Readiness probe (DB + Dapr) |
| GET | `/metrics` | Application metrics |
| GET | `/api/{user_id}/tasks` | List tasks (supports search, filter, sort) |
| POST | `/api/{user_id}/tasks` | Create task |
| GET | `/api/{user_id}/tasks/{id}` | Get task |
| PUT | `/api/{user_id}/tasks/{id}` | Update task |
| DELETE | `/api/{user_id}/tasks/{id}` | Delete task |
| PATCH | `/api/{user_id}/tasks/{id}/complete` | Toggle completion |
| POST | `/api/{user_id}/tasks/{id}/tags` | Add tags |
| DELETE | `/api/{user_id}/tasks/{id}/tags/{tag}` | Remove tag |
| POST | `/api/chat` | AI chatbot endpoint |
| GET | `/api/notifications/stream` | SSE notifications |

## Project Structure

```
phase-5-advanced-cloud-deployment/
├── backend/
│   ├── main.py                    # FastAPI entry point
│   ├── models.py                  # SQLModel database models
│   ├── db.py                      # Database connection
│   ├── middleware/
│   │   └── logging_middleware.py   # Request logging + metrics
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
│   ├── mcp/
│   │   └── tools.py               # MCP tools for AI agent
│   └── tests/                     # 38 tests (contract, integration, unit)
├── frontend/                      # Next.js chat interface
├── helm/todo-chatbot/
│   ├── Chart.yaml
│   ├── values.yaml                # Base values
│   ├── values-minikube.yaml       # Local Minikube config
│   ├── values-cloud.yaml          # Cloud production config
│   └── templates/
│       ├── backend-deployment.yaml
│       ├── frontend-deployment.yaml
│       ├── postgres-statefulset.yaml
│       ├── redpanda-deployment.yaml
│       ├── dapr-components.yaml
│       ├── secrets.yaml
│       └── configmap.yaml
├── dapr-components/               # Local Dapr component configs
├── .github/workflows/
│   ├── ci.yml                     # Build + test + push images
│   └── cd.yml                     # Deploy to cloud K8s
├── docker-compose.yml             # Local full-stack with Dapr
├── specs/                         # SDD specification files
└── history/prompts/               # Prompt History Records
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

## Spec-Driven Development

This project was built using **Spec-Driven Development (SDD)** with Claude Code and Spec-Kit Plus:

1. **Constitution** - Project principles and constraints
2. **Specification** - Feature requirements and acceptance criteria
3. **Plan** - Architectural decisions and component design
4. **Tasks** - Atomic, testable implementation tasks
5. **Implementation** - AI-generated code from specifications

All spec artifacts are in `specs/` and prompt history in `history/prompts/`.

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASE_URL` | PostgreSQL connection string | Required |
| `OPENAI_API_KEY` | OpenAI API key | Required |
| `BETTER_AUTH_SECRET` | JWT signing secret | Required |
| `FRONTEND_URL` | Frontend URL for CORS | `http://localhost:3000` |
| `DAPR_HTTP_PORT` | Dapr sidecar HTTP port | `3500` |
| `LOG_LEVEL` | Logging level | `INFO` |
