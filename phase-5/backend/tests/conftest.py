"""Shared test fixtures with real in-memory SQLite database."""

import base64
import json
import time
from unittest.mock import patch, AsyncMock

import pytest
from fastapi.testclient import TestClient
from sqlmodel import SQLModel, Session, create_engine
from sqlalchemy.pool import StaticPool


@pytest.fixture(name="engine")
def fixture_engine():
    """Create an in-memory SQLite engine with all tables."""
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)
    yield engine
    SQLModel.metadata.drop_all(engine)


@pytest.fixture(name="session")
def fixture_session(engine):
    """Provide a database session for tests."""
    with Session(engine) as session:
        yield session


@pytest.fixture(name="client")
def fixture_client(engine):
    """Create a test client backed by real in-memory SQLite."""
    from db import get_session
    from main import app

    def override_get_session():
        with Session(engine) as session:
            yield session

    app.dependency_overrides[get_session] = override_get_session

    # Mock async services that call Dapr sidecar
    with patch(
        "routes.tasks.publish_event", new_callable=AsyncMock, return_value=True
    ), patch(
        "routes.tasks.schedule_reminder", new_callable=AsyncMock, return_value=True
    ), patch(
        "routes.tasks.cancel_reminder", new_callable=AsyncMock, return_value=True
    ):
        yield TestClient(app)

    app.dependency_overrides.clear()


@pytest.fixture(name="auth_headers")
def fixture_auth_headers():
    """Return auth headers with a demo token for test-user-1."""
    payload = {
        "sub": "test-user-1",
        "email": "test@example.com",
        "exp": int(time.time()) + 3600,
    }
    encoded = base64.b64encode(json.dumps(payload).encode()).decode()
    token = f"demo.{encoded}.testsig"
    return {"Authorization": f"Bearer {token}"}


def make_demo_token(user_id: str = "test-user-1") -> str:
    """Create a demo JWT token for testing."""
    payload = {
        "sub": user_id,
        "email": "test@example.com",
        "exp": int(time.time()) + 3600,
    }
    encoded = base64.b64encode(json.dumps(payload).encode()).decode()
    return f"demo.{encoded}.testsig"
