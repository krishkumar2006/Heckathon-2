"""
backend/routes/chat.py — Phase 3 Chat Endpoint
POST /api/{user_id}/chat — 10-step stateless request cycle.

Security (Constitution Laws X, XIII):
- JWT verified via Depends(get_current_user).
- URL user_id validated against JWT sub → 403 on mismatch.
- All queries filter by user_id.
- HTTP 500 never returned — errors become friendly ChatResponse.
"""

import json
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select

from auth import get_current_user
from db import get_session
from groq_agent import run_agent
from models import ChatRequest, ChatResponse, Conversation, Message

router = APIRouter()


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


def _check_ownership(current_user: dict, user_id: str) -> None:
    if current_user["sub"] != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied: token user does not match resource owner",
        )


@router.post("/{user_id}/chat", response_model=ChatResponse, status_code=200)
async def chat(
    user_id: str,
    body: ChatRequest,
    current_user: dict = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> ChatResponse:
    """
    10-step stateless AI chat cycle.
    Never returns HTTP 500 — agent errors are surfaced as ChatResponse.
    """
    # STEP 1: JWT verify + ownership
    _check_ownership(current_user, user_id)

    # STEP 2: Validate message
    if not body.message.strip():
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Message cannot be empty",
        )

    # STEP 3: Handle conversation (create new or load existing)
    conversation: Conversation
    if body.conversation_id is not None:
        conv = session.exec(
            select(Conversation).where(
                Conversation.id == body.conversation_id,
                Conversation.user_id == user_id,
            )
        ).first()
        if conv is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Conversation not found",
            )
        conversation = conv
    else:
        conversation = Conversation(
            user_id=user_id,
            title=body.message[:100],
            created_at=_utc_now(),
            updated_at=_utc_now(),
        )
        session.add(conversation)
        session.commit()
        session.refresh(conversation)

    # STEP 4: Load message history (ASC order for AI context)
    past_messages = session.exec(
        select(Message)
        .where(Message.conversation_id == conversation.id)
        .order_by(Message.created_at)  # type: ignore[arg-type]
    ).all()
    history = [{"role": m.role, "content": m.content} for m in past_messages]

    # STEP 5: Save user message
    user_msg = Message(
        conversation_id=conversation.id,
        user_id=user_id,
        role="user",
        content=body.message,
        created_at=_utc_now(),
    )
    session.add(user_msg)
    session.commit()

    # STEP 6: Build agent input (history + new user message)
    history.append({"role": "user", "content": body.message})

    # STEP 7: Call agent (never raises — returns friendly error on failure)
    result = await run_agent(
        user_id,
        history,
        user_name=current_user.get("name"),
        user_email=current_user.get("email"),
    )

    # STEP 8: Save assistant response
    asst_msg = Message(
        conversation_id=conversation.id,
        user_id=user_id,
        role="assistant",
        content=result["response"],
        tool_calls_json=json.dumps(result["tool_calls"]) if result["tool_calls"] else None,
        created_at=_utc_now(),
    )
    session.add(asst_msg)
    session.commit()

    # STEP 9: Update conversation timestamp
    conversation.updated_at = _utc_now()
    session.add(conversation)
    session.commit()

    # STEP 10: Return response
    return ChatResponse(
        conversation_id=conversation.id,
        response=result["response"],
        tool_calls=result["tool_calls"],
    )
