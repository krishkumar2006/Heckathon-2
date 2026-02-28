from datetime import datetime, timezone
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlmodel import Session, select

from auth import get_current_user
from db import get_session
from models import Task, TaskCreate, TaskResponse, TaskUpdate

router = APIRouter()


def _check_ownership(current_user: dict, user_id: str) -> None:
    """Raise 403 if the token subject does not match the URL user_id."""
    if current_user["sub"] != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied: token user does not match resource owner",
        )


# ---------------------------------------------------------------------------
# T033: GET /api/{user_id}/tasks
# ---------------------------------------------------------------------------
@router.get("/{user_id}/tasks", response_model=List[TaskResponse], status_code=200)
def list_tasks(
    user_id: str,
    task_status: Optional[str] = "all",
    current_user: dict = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> List[TaskResponse]:
    """Return all tasks for *user_id* with optional status filter."""
    _check_ownership(current_user, user_id)

    statement = select(Task).where(Task.user_id == user_id)

    if task_status == "pending":
        statement = statement.where(Task.completed == False)  # noqa: E712
    elif task_status == "completed":
        statement = statement.where(Task.completed == True)  # noqa: E712
    # "all" (or any unrecognised value) → no extra filter

    tasks = session.exec(statement).all()
    return list(tasks)


# ---------------------------------------------------------------------------
# T030: POST /api/{user_id}/tasks
# ---------------------------------------------------------------------------
@router.post("/{user_id}/tasks", response_model=TaskResponse, status_code=201)
def create_task(
    user_id: str,
    task_data: TaskCreate,
    current_user: dict = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> TaskResponse:
    """Create a new task owned by *user_id*."""
    _check_ownership(current_user, user_id)

    task = Task(
        user_id=user_id,
        title=task_data.title,
        description=task_data.description,
    )
    session.add(task)
    session.commit()
    session.refresh(task)
    return task


# ---------------------------------------------------------------------------
# T037: GET /api/{user_id}/tasks/{task_id}
# ---------------------------------------------------------------------------
@router.get("/{user_id}/tasks/{task_id}", response_model=TaskResponse, status_code=200)
def get_task(
    user_id: str,
    task_id: int,
    current_user: dict = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> TaskResponse:
    """Return a single task, enforcing ownership."""
    _check_ownership(current_user, user_id)

    statement = select(Task).where(Task.id == task_id, Task.user_id == user_id)
    task = session.exec(statement).first()

    if task is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task {task_id} not found",
        )
    return task


# ---------------------------------------------------------------------------
# T038: PUT /api/{user_id}/tasks/{task_id}
# ---------------------------------------------------------------------------
@router.put("/{user_id}/tasks/{task_id}", response_model=TaskResponse, status_code=200)
def update_task(
    user_id: str,
    task_id: int,
    task_data: TaskUpdate,
    current_user: dict = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> TaskResponse:
    """Update title and/or description of an existing task."""
    _check_ownership(current_user, user_id)

    statement = select(Task).where(Task.id == task_id, Task.user_id == user_id)
    task = session.exec(statement).first()

    if task is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task {task_id} not found",
        )

    if task_data.title is not None:
        task.title = task_data.title
    if task_data.description is not None:
        task.description = task_data.description

    task.updated_at = datetime.now(timezone.utc)

    session.add(task)
    session.commit()
    session.refresh(task)
    return task


# ---------------------------------------------------------------------------
# T039: DELETE /api/{user_id}/tasks/{task_id}
# ---------------------------------------------------------------------------
@router.delete("/{user_id}/tasks/{task_id}", status_code=204)
def delete_task(
    user_id: str,
    task_id: int,
    current_user: dict = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> Response:
    """Permanently delete a task."""
    _check_ownership(current_user, user_id)

    statement = select(Task).where(Task.id == task_id, Task.user_id == user_id)
    task = session.exec(statement).first()

    if task is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task {task_id} not found",
        )

    session.delete(task)
    session.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


# ---------------------------------------------------------------------------
# T042: PATCH /api/{user_id}/tasks/{task_id}/complete
# ---------------------------------------------------------------------------
@router.patch(
    "/{user_id}/tasks/{task_id}/complete",
    response_model=TaskResponse,
    status_code=200,
)
def toggle_task_complete(
    user_id: str,
    task_id: int,
    current_user: dict = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> TaskResponse:
    """Toggle the completed state of a task (True -> False, False -> True)."""
    _check_ownership(current_user, user_id)

    statement = select(Task).where(Task.id == task_id, Task.user_id == user_id)
    task = session.exec(statement).first()

    if task is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task {task_id} not found",
        )

    task.completed = not task.completed
    task.updated_at = datetime.now(timezone.utc)

    session.add(task)
    session.commit()
    session.refresh(task)
    return task
