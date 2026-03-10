"""FastAPI backend entry point for AI-powered Todo Chatbot."""

import os
import logging
from contextlib import asynccontextmanager

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from db import create_db_and_tables
from middleware.logging_middleware import RequestLoggingMiddleware
from routes.tasks import router as tasks_router
from routes.chat import router as chat_router
from routes.health import router as health_router
from routes.events import router as events_router
from routes.jobs import router as jobs_router
from routes.notifications import router as notifications_router

# Load environment variables
load_dotenv()

# Configure structured logging
log_level = os.getenv("LOG_LEVEL", "INFO").upper()
logging.basicConfig(
    level=getattr(logging, log_level, logging.INFO),
    format="%(asctime)s %(levelname)s %(name)s [%(funcName)s] %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize database on startup."""
    create_db_and_tables()
    yield


app = FastAPI(
    title="AI Todo Chatbot API",
    description="Phase 5 Advanced Cloud Deployment - Event-Driven Todo Chatbot",
    version="2.0.0",
    lifespan=lifespan,
)

# CORS configuration - allow frontend to communicate with backend
frontend_url = os.getenv("FRONTEND_URL", "http://localhost:3000")
allowed_origins = [frontend_url]

# Add localhost origins for development
if "localhost" in frontend_url or "127.0.0.1" in frontend_url:
    allowed_origins.extend([
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ])

# Add any extra origins from env (comma-separated)
extra_origins = os.getenv("EXTRA_ORIGINS", "")
if extra_origins:
    allowed_origins.extend([o.strip() for o in extra_origins.split(",") if o.strip()])

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request logging and metrics middleware
app.add_middleware(RequestLoggingMiddleware)

# Include routers
app.include_router(health_router)
app.include_router(events_router)
app.include_router(jobs_router)
app.include_router(notifications_router)
app.include_router(tasks_router)
app.include_router(chat_router)
