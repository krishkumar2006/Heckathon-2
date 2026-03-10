"""Integration tests for event publishing via Dapr Pub/Sub."""

from unittest.mock import patch, AsyncMock

from fastapi.testclient import TestClient


class TestEventPublishing:
    """Tests that task CRUD operations publish events via Dapr."""

    def test_create_task_publishes_event(self, engine, auth_headers):
        """Creating a task should publish a task.created event."""
        from db import get_session
        from main import app
        from sqlmodel import Session

        def override():
            with Session(engine) as s:
                yield s

        app.dependency_overrides[get_session] = override

        mock_publish = AsyncMock(return_value=True)
        mock_schedule = AsyncMock(return_value=True)
        mock_cancel = AsyncMock(return_value=True)

        with patch("routes.tasks.publish_event", mock_publish), \
             patch("routes.tasks.schedule_reminder", mock_schedule), \
             patch("routes.tasks.cancel_reminder", mock_cancel):
            c = TestClient(app)
            response = c.post(
                "/api/test-user-1/tasks",
                json={"title": "Test event publishing"},
                headers=auth_headers,
            )
            assert response.status_code == 201
            mock_publish.assert_called_once()
            assert mock_publish.call_args.kwargs["event_type"] == "task.created"
            assert mock_publish.call_args.kwargs["user_id"] == "test-user-1"

        app.dependency_overrides.clear()

    def test_update_task_publishes_event(self, engine, auth_headers):
        """Updating a task should publish a task.updated event."""
        from db import get_session
        from main import app
        from sqlmodel import Session

        def override():
            with Session(engine) as s:
                yield s

        app.dependency_overrides[get_session] = override

        mock_publish = AsyncMock(return_value=True)
        mock_schedule = AsyncMock(return_value=True)
        mock_cancel = AsyncMock(return_value=True)

        with patch("routes.tasks.publish_event", mock_publish), \
             patch("routes.tasks.schedule_reminder", mock_schedule), \
             patch("routes.tasks.cancel_reminder", mock_cancel):
            c = TestClient(app)
            create_resp = c.post(
                "/api/test-user-1/tasks",
                json={"title": "Original"},
                headers=auth_headers,
            )
            task_id = create_resp.json()["id"]
            mock_publish.reset_mock()

            c.put(
                f"/api/test-user-1/tasks/{task_id}",
                json={"title": "Updated"},
                headers=auth_headers,
            )
            mock_publish.assert_called_once()
            assert mock_publish.call_args.kwargs["event_type"] == "task.updated"

        app.dependency_overrides.clear()

    def test_complete_task_publishes_event(self, engine, auth_headers):
        """Completing a task should publish a task.completed event."""
        from db import get_session
        from main import app
        from sqlmodel import Session

        def override():
            with Session(engine) as s:
                yield s

        app.dependency_overrides[get_session] = override

        mock_publish = AsyncMock(return_value=True)
        mock_schedule = AsyncMock(return_value=True)
        mock_cancel = AsyncMock(return_value=True)

        with patch("routes.tasks.publish_event", mock_publish), \
             patch("routes.tasks.schedule_reminder", mock_schedule), \
             patch("routes.tasks.cancel_reminder", mock_cancel):
            c = TestClient(app)
            create_resp = c.post(
                "/api/test-user-1/tasks",
                json={"title": "Complete me"},
                headers=auth_headers,
            )
            task_id = create_resp.json()["id"]
            mock_publish.reset_mock()

            c.patch(
                f"/api/test-user-1/tasks/{task_id}/complete",
                headers=auth_headers,
            )
            mock_publish.assert_called_once()
            assert mock_publish.call_args.kwargs["event_type"] == "task.completed"

        app.dependency_overrides.clear()

    def test_delete_task_publishes_event(self, engine, auth_headers):
        """Deleting a task should publish a task.deleted event."""
        from db import get_session
        from main import app
        from sqlmodel import Session

        def override():
            with Session(engine) as s:
                yield s

        app.dependency_overrides[get_session] = override

        mock_publish = AsyncMock(return_value=True)
        mock_schedule = AsyncMock(return_value=True)
        mock_cancel = AsyncMock(return_value=True)

        with patch("routes.tasks.publish_event", mock_publish), \
             patch("routes.tasks.schedule_reminder", mock_schedule), \
             patch("routes.tasks.cancel_reminder", mock_cancel):
            c = TestClient(app)
            create_resp = c.post(
                "/api/test-user-1/tasks",
                json={"title": "Delete me"},
                headers=auth_headers,
            )
            task_id = create_resp.json()["id"]
            mock_publish.reset_mock()

            c.delete(
                f"/api/test-user-1/tasks/{task_id}",
                headers=auth_headers,
            )
            mock_publish.assert_called_once()
            assert mock_publish.call_args.kwargs["event_type"] == "task.deleted"

        app.dependency_overrides.clear()

    def test_event_handler_accepts_task_event(self, client):
        """POST /api/events/task should accept and process events."""
        event = {
            "event_type": "task.created",
            "task_id": 1,
            "user_id": "test-user-1",
            "task_data": {"title": "Test task"},
            "timestamp": "2026-02-07T00:00:00Z",
        }
        response = client.post("/api/events/task", json=event)
        assert response.status_code == 200
        assert response.json()["status"] == "SUCCESS"

    def test_event_handler_accepts_reminder_event(self, client):
        """POST /api/events/reminder should accept and process events."""
        event = {
            "task_id": 1,
            "user_id": "test-user-1",
            "title": "Test reminder",
        }
        response = client.post("/api/events/reminder", json=event)
        assert response.status_code == 200
        assert response.json()["status"] == "SUCCESS"

    def test_dapr_subscribe_returns_subscriptions(self, client):
        """GET /dapr/subscribe should return topic subscriptions."""
        response = client.get("/dapr/subscribe")
        assert response.status_code == 200
        subs = response.json()
        topics = [s["topic"] for s in subs]
        assert "task-events" in topics
        assert "reminders" in topics
