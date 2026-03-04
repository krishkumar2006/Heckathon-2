"""
backend/routes/activity.py — Phase 3 Activity & Conversations Endpoints
GET  /api/{user_id}/activity        → last 20 login events (DESC)
POST /api/{user_id}/activity/login  → record a login event (called by Next.js login page)
GET  /api/{user_id}/conversations   → last 20 conversations (DESC by updated_at)

Security (Constitution Laws X, XIII):
- JWT verified via Depends(get_current_user).
- URL user_id validated against JWT sub → 403 on mismatch.
- All queries filter by user_id.
"""

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlmodel import Session, select

from auth import get_current_user
from db import get_session
from models import Conversation, UserActivity
from user_agents import parse as parse_ua

router = APIRouter()


def _check_ownership(current_user: dict, user_id: str) -> None:
    if current_user["sub"] != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied: token user does not match resource owner",
        )


@router.post("/{user_id}/activity/login", status_code=201)
def record_login_activity(
    user_id: str,
    request: Request,
    current_user: dict = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> dict:
    """Record a login event for the authenticated user. Called by the Next.js login page."""
    _check_ownership(current_user, user_id)

    ip = (request.client.host if request.client else None) or "Unknown"
    ua_string = request.headers.get("user-agent", "")
    device = "Unknown device"
    try:
        ua = parse_ua(ua_string)
        browser = ua.browser.family or "Unknown"
        os_name = ua.os.family or "Unknown"
        device = f"{browser} on {os_name}"
    except Exception:
        pass

    activity = UserActivity(
        user_id=user_id,
        activity_type="login",
        ip_address=ip,
        device=device,
    )
    session.add(activity)
    session.commit()
    return {"status": "recorded"}


@router.get("/{user_id}/activity", status_code=200)
def get_activity(
    user_id: str,
    current_user: dict = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> list:
    """Return last 20 login events for the authenticated user."""
    _check_ownership(current_user, user_id)

    events = session.exec(
        select(UserActivity)
        .where(
            UserActivity.user_id == user_id,
            UserActivity.activity_type == "login",
        )
        .order_by(UserActivity.created_at.desc())  # type: ignore[arg-type]
        .limit(20)
    ).all()

    result = []
    for e in events:
        d = e.created_at
        day = str(d.day)
        hour_24 = d.hour
        hour_12 = hour_24 % 12 or 12
        am_pm = "AM" if hour_24 < 12 else "PM"
        fmt = d.strftime(f"%A, %B {day} at {hour_12}:{d.minute:02d} {am_pm}")
        result.append(
            {
                "activity_type": e.activity_type,
                "ip_address": e.ip_address or "Unknown",
                "device": e.device or "Unknown device",
                "created_at": fmt,
            }
        )
    return result


@router.get("/{user_id}/conversations", status_code=200)
def get_conversations(
    user_id: str,
    current_user: dict = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> list:
    """Return last 20 conversations for the authenticated user, ordered by updated_at DESC."""
    _check_ownership(current_user, user_id)

    convs = session.exec(
        select(Conversation)
        .where(Conversation.user_id == user_id)
        .order_by(Conversation.updated_at.desc())  # type: ignore[arg-type]
        .limit(20)
    ).all()

    return [
        {
            "id": c.id,
            "title": c.title,
            "created_at": c.created_at.isoformat(),
            "updated_at": c.updated_at.isoformat(),
        }
        for c in convs
    ]
