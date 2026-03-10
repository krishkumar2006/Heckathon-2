"""Database connection for Neon PostgreSQL using SQLModel."""

import os
from dotenv import load_dotenv
from sqlmodel import SQLModel, create_engine, Session
from sqlalchemy.pool import NullPool

# Import all models to ensure tables are created
from models import Task, TaskTag, Conversation, Message  # noqa: F401

# Load environment variables
load_dotenv()

# Engine will be created lazily
_engine = None


def get_engine():
    """Get or create database engine (lazy initialization)."""
    global _engine
    if _engine is None:
        database_url = os.getenv("DATABASE_URL")
        if not database_url:
            raise ValueError("DATABASE_URL environment variable is not set")
        # Configure for Neon serverless PostgreSQL
        # Use NullPool for serverless - creates new connection per request
        # This handles Neon's auto-suspend/resume behavior properly
        _engine = create_engine(
            database_url,
            echo=False,
            poolclass=NullPool,  # No connection pooling - better for serverless
        )
    return _engine


def create_db_and_tables():
    """Create all tables defined in SQLModel models."""
    SQLModel.metadata.create_all(get_engine())


def get_session():
    """Dependency for getting database session."""
    with Session(get_engine()) as session:
        yield session
