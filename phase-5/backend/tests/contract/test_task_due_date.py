"""Contract tests for task due date functionality."""


class TestTaskDueDate:
    """Tests for due date in task endpoints."""

    def test_create_task_with_due_date(self, client, auth_headers):
        """POST with due_date should store and return it."""
        response = client.post(
            "/api/test-user-1/tasks",
            json={
                "title": "Task with deadline",
                "due_date": "2026-02-15T14:00:00Z",
            },
            headers=auth_headers,
        )
        assert response.status_code == 201
        data = response.json()
        assert data["due_date"] is not None

    def test_create_task_with_reminder(self, client, auth_headers):
        """POST with reminder_offset_minutes should store it."""
        response = client.post(
            "/api/test-user-1/tasks",
            json={
                "title": "Task with reminder",
                "due_date": "2026-02-15T14:00:00Z",
                "reminder_offset_minutes": 30,
            },
            headers=auth_headers,
        )
        assert response.status_code == 201
        data = response.json()
        assert data["reminder_offset_minutes"] == 30

    def test_create_task_without_due_date(self, client, auth_headers):
        """POST without due_date should return null."""
        response = client.post(
            "/api/test-user-1/tasks",
            json={"title": "No deadline"},
            headers=auth_headers,
        )
        assert response.status_code == 201
        assert response.json()["due_date"] is None

    def test_get_task_returns_due_date(self, client, auth_headers):
        """GET should return due_date field."""
        create_resp = client.post(
            "/api/test-user-1/tasks",
            json={
                "title": "Due date check",
                "due_date": "2026-03-01T09:00:00Z",
            },
            headers=auth_headers,
        )
        task_id = create_resp.json()["id"]

        get_resp = client.get(
            f"/api/test-user-1/tasks/{task_id}",
            headers=auth_headers,
        )
        assert get_resp.status_code == 200
        assert get_resp.json()["due_date"] is not None

    def test_filter_tasks_by_due_date_range(self, client, auth_headers):
        """GET with due_from and due_to should filter tasks."""
        response = client.get(
            "/api/test-user-1/tasks?due_from=2026-02-01T00:00:00Z&due_to=2026-02-28T23:59:59Z",
            headers=auth_headers,
        )
        assert response.status_code == 200
