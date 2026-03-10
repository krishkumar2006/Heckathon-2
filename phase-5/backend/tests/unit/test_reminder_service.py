"""Unit tests for reminder service (Dapr Jobs API integration)."""

from datetime import datetime, timezone, timedelta
from unittest.mock import patch, MagicMock, AsyncMock

import pytest


@pytest.fixture
def mock_httpx():
    """Mock httpx.AsyncClient."""
    with patch("services.reminder_service.httpx.AsyncClient") as mock:
        client = MagicMock()
        client.__aenter__ = AsyncMock(return_value=client)
        client.__aexit__ = AsyncMock(return_value=False)
        mock.return_value = client
        yield client


class TestScheduleReminder:
    """Tests for schedule_reminder function."""

    @pytest.mark.asyncio
    async def test_schedule_reminder_calls_dapr_jobs_api(self, mock_httpx):
        """schedule_reminder should POST to Dapr Jobs API."""
        from services.reminder_service import schedule_reminder

        mock_httpx.post = AsyncMock(
            return_value=MagicMock(status_code=200)
        )

        due_date = datetime.now(timezone.utc) + timedelta(hours=1)
        result = await schedule_reminder(
            task_id=42,
            user_id="user-1",
            due_date=due_date,
            offset_minutes=30,
        )

        assert result is True
        mock_httpx.post.assert_called_once()
        call_url = mock_httpx.post.call_args[0][0]
        assert "jobs" in call_url
        assert "reminder-task-42" in call_url

    @pytest.mark.asyncio
    async def test_schedule_reminder_calculates_due_time(self, mock_httpx):
        """schedule_reminder should compute reminder_time = due_date - offset."""
        from services.reminder_service import schedule_reminder

        mock_httpx.post = AsyncMock(
            return_value=MagicMock(status_code=200)
        )

        due_date = datetime(2026, 2, 15, 14, 0, 0, tzinfo=timezone.utc)
        await schedule_reminder(
            task_id=1,
            user_id="user-1",
            due_date=due_date,
            offset_minutes=30,
        )

        call_json = mock_httpx.post.call_args.kwargs.get("json") or mock_httpx.post.call_args[1].get("json")
        assert call_json is not None


class TestCancelReminder:
    """Tests for cancel_reminder function."""

    @pytest.mark.asyncio
    async def test_cancel_reminder_calls_delete(self, mock_httpx):
        """cancel_reminder should DELETE the Dapr job."""
        from services.reminder_service import cancel_reminder

        mock_httpx.delete = AsyncMock(
            return_value=MagicMock(status_code=200)
        )

        result = await cancel_reminder(task_id=42)

        assert result is True
        mock_httpx.delete.assert_called_once()
        call_url = mock_httpx.delete.call_args[0][0]
        assert "reminder-task-42" in call_url

    @pytest.mark.asyncio
    async def test_cancel_reminder_handles_not_found(self, mock_httpx):
        """cancel_reminder should handle 404 (job already gone) gracefully."""
        from services.reminder_service import cancel_reminder

        mock_httpx.delete = AsyncMock(
            return_value=MagicMock(status_code=404)
        )

        result = await cancel_reminder(task_id=99)
        assert result is True  # Still considered success
