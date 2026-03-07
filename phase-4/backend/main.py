import os

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from db import create_db_and_tables
from routes.tasks import router as tasks_router
from routes.chat import router as chat_router
from routes.activity import router as activity_router

load_dotenv()

app = FastAPI(title="Todo API", version="1.0.0")

FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:3000")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[FRONTEND_URL],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH"],
    allow_headers=["Authorization", "Content-Type"],
)


@app.on_event("startup")
def on_startup() -> None:
    create_db_and_tables()


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@app.get("/")
def root() -> dict:
    return {"status": "ok"}


@app.get("/health")
def health_check() -> dict:
    return {"status": "ok"}


app.include_router(tasks_router, prefix="/api")
app.include_router(chat_router, prefix="/api")
app.include_router(activity_router, prefix="/api")
