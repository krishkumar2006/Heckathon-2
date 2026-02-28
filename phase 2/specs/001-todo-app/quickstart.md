# Quickstart: Todo App Development Setup

**Date**: 2026-02-27

## Prerequisites

- Node.js 20+ and npm
- Python 3.11+
- OpenSSL (for secret generation)
- Neon account at neon.tech (free tier)

---

## Step 1: Generate Shared Secret

Run once. Copy the output — you'll need it in both `.env` files.

```bash
openssl rand -base64 32
```

Keep this value safe. Never commit it.

---

## Step 2: Set Up Neon Database

1. Go to neon.tech and create a free account
2. Click "New Project" → name: `hackathon-todo`
3. Choose the region closest to you
4. Copy the connection string (format: `postgresql://user:pass@host.neon.tech/dbname?sslmode=require`)

---

## Step 3: Backend Setup

```bash
# From repo root
cd backend

# Create virtual environment
python -m venv venv

# Activate (Mac/Linux)
source venv/bin/activate
# Activate (Windows)
.\venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create .env file (copy from .env.example, fill in real values)
cp .env.example .env
```

Edit `backend/.env`:
```env
BETTER_AUTH_SECRET=<paste secret from Step 1>
DATABASE_URL=<paste Neon connection string from Step 2>
FRONTEND_URL=http://localhost:3000
```

```bash
# Start backend
uvicorn main:app --reload --port 8000

# Verify: open http://localhost:8000/health → should return {"status":"ok"}
# Verify: open http://localhost:8000/docs → should show all 6 task endpoints
```

---

## Step 4: Frontend Setup

```bash
# From repo root — run ONCE to scaffold (if frontend/ doesn't exist yet)
npx create-next-app@latest frontend \
  --typescript \
  --tailwind \
  --app \
  --no-src-dir \
  --import-alias "@/*"

# Enter frontend directory
cd frontend

# Install Better Auth
npm install better-auth

# Create .env.local (copy from .env.example, fill in real values)
cp .env.example .env.local
```

Edit `frontend/.env.local`:
```env
BETTER_AUTH_SECRET=<paste SAME secret from Step 1 — must match backend>
NEXT_PUBLIC_API_URL=http://localhost:8000
BETTER_AUTH_URL=http://localhost:3000
DATABASE_URL=<paste SAME Neon connection string from Step 2>
```

```bash
# Start frontend
npm run dev

# Verify: open http://localhost:3000 → should redirect to /login
```

---

## Step 5: Verify Both Services Running

| Service | URL | Expected |
|---------|-----|----------|
| Backend health | `http://localhost:8000/health` | `{"status":"ok"}` |
| Backend API docs | `http://localhost:8000/docs` | 6 task endpoints listed |
| Frontend | `http://localhost:3000` | Redirects to `/login` |
| Frontend login | `http://localhost:3000/login` | Login form renders |

---

## Step 6: End-to-End Smoke Test

1. Go to `localhost:3000/signup` → create account → should land on dashboard
2. Create a task → should appear in list
3. Toggle completion → title gets strikethrough
4. Filter by "Completed" → shows only completed task
5. Logout → redirected to `/login`
6. Login again → tasks still there (persisted in Neon)

---

## Common Issues

| Issue | Cause | Fix |
|-------|-------|-----|
| 401 on all API calls | `BETTER_AUTH_SECRET` mismatch | Copy-paste exact same value to both `.env` files |
| Backend connection error on start | Missing `?sslmode=require` | Append `?sslmode=require` to DATABASE_URL |
| CORS error in browser | `FRONTEND_URL` not set in backend | Add `FRONTEND_URL=http://localhost:3000` to `backend/.env` |
| 403 on task requests | URL user_id ≠ token sub | Ensure dashboard uses session user ID for all API calls |
| Neon timeout after idle | Neon serverless cold start | Restart backend process; Neon wakes up within 1-2 seconds |

---

## Run Commands

```bash
# Backend (from backend/ directory, venv activated)
uvicorn main:app --reload --port 8000

# Frontend (from frontend/ directory)
npm run dev
```
