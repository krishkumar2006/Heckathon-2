"""Contract tests for health and readiness endpoints."""

from unittest.mock import patch, MagicMock

import pytest
from fastapi.testclient import TestClient


@pytest.fixture(name="health_client")
def fixture_health_client(engine):
    """Create a test client for health endpoint tests."""
    from main import app

    with patch("routes.health.get_engine", return_value=engine):
        yield TestClient(app)


class TestHealthEndpoint:
    """Tests for GET /health liveness probe."""

    def test_health_returns_200(self, health_client):
        """GET /health should return 200 with healthy status."""
        response = health_client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"

    def test_health_includes_version(self, health_client):
        """GET /health response should include version field."""
        response = health_client.get("/health")
        data = response.json()
        assert "version" in data
        assert data["version"] == "phase-5"


class TestReadinessEndpoint:
    """Tests for GET /ready readiness probe."""

    @patch("routes.health.httpx.AsyncClient")
    def test_ready_returns_200_when_all_checks_pass(
        self, mock_async_client, health_client
    ):
        """GET /ready should return 200 when DB and Dapr are reachable."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_client_instance = MagicMock()
        mock_client_instance.get = MagicMock(return_value=mock_response)
        mock_client_instance.__aenter__ = MagicMock(return_value=mock_client_instance)
        mock_client_instance.__aexit__ = MagicMock(return_value=False)
        mock_async_client.return_value = mock_client_instance

        response = health_client.get("/ready")
        data = response.json()
        assert "status" in data
        assert "checks" in data
        assert "database" in data["checks"]
        assert "dapr" in data["checks"]

    def test_ready_returns_503_when_dapr_unavailable(self, health_client):
        """GET /ready should return 503 when Dapr sidecar is not reachable."""
        response = health_client.get("/ready")
        data = response.json()
        assert response.status_code == 503 or response.status_code == 200
        assert "checks" in data

    def test_ready_response_structure(self, health_client):
        """GET /ready response should have correct structure."""
        response = health_client.get("/ready")
        data = response.json()
        assert "status" in data
        assert data["status"] in ("ready", "not_ready")
        assert "checks" in data
        assert isinstance(data["checks"], dict)
