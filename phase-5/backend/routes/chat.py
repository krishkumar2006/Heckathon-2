"""Chat routes for AI-powered Todo Chatbot."""

import os
import json
from datetime import datetime
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlmodel import Session
from openai import RateLimitError, APIError

from db import get_session
from middleware.auth import CurrentUser, AuthenticatedUser
from models import Conversation, Message
from agent import create_agent
from services.conversation import ConversationService

router = APIRouter(prefix="/api/chat", tags=["chat"])

# Test user for development (only when FRONTEND_URL is localhost)
TEST_USER_ID = "test-user-123"


# Request/Response schemas
class ChatMessage(BaseModel):
    """Schema for sending a chat message."""

    message: str = Field(min_length=1, max_length=1000)
    conversation_id: str | None = None


class ChatResponse(BaseModel):
    """Schema for chat response."""

    response: str
    conversation_id: str
    tool_calls: list[dict] = []


class ConversationResponse(BaseModel):
    """Schema for conversation response."""

    id: str
    title: str | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class MessageResponse(BaseModel):
    """Schema for message response."""

    id: int
    role: str
    content: str
    tool_calls: list[dict] | None = None
    created_at: datetime

    model_config = {"from_attributes": True}


# Dependency type alias
SessionDep = Annotated[Session, Depends(get_session)]


@router.post("", response_model=ChatResponse)
def send_message(
    chat_data: ChatMessage, user: CurrentUser, session: SessionDep
) -> ChatResponse:
    """
    Send a chat message and get AI response.

    Creates a new conversation if conversation_id is not provided.
    Uses the AI agent to process the message and manage tasks.
    """
    conv_service = ConversationService(session, user.user_id)

    # Get or create conversation
    if chat_data.conversation_id:
        conversation = conv_service.get_conversation(chat_data.conversation_id)
        if not conversation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Conversation not found",
            )
    else:
        # Create new conversation with first message as title
        title = chat_data.message[:50] + "..." if len(chat_data.message) > 50 else chat_data.message
        conversation = conv_service.create_conversation(title=title)

    # Store user message
    conv_service.add_message(
        conversation_id=conversation.id,
        role="user",
        content=chat_data.message,
    )

    # Get conversation history for context
    history = conv_service.get_messages(conversation.id)

    # Create agent and process message
    agent = create_agent(user.user_id)

    try:
        result = agent.chat(chat_data.message, conversation_history=history[:-1])  # Exclude current message
    except RateLimitError as e:
        # Rate limiting - provide helpful message
        error_msg = "I'm currently experiencing high demand. Please wait a moment and try again."
        conv_service.add_message(
            conversation_id=conversation.id,
            role="assistant",
            content=error_msg,
        )
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Rate limit exceeded. Please wait a moment and try again.",
        )
    except APIError as e:
        # API error - provide appropriate message
        if e.status_code and e.status_code >= 500:
            error_msg = "The AI service is temporarily unavailable. Please try again in a few moments."
        else:
            error_msg = "I'm sorry, I encountered an error processing your request. Please try again."
        conv_service.add_message(
            conversation_id=conversation.id,
            role="assistant",
            content=error_msg,
        )
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE if e.status_code and e.status_code >= 500 else status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"AI service error: {str(e)}",
        )
    except Exception as e:
        # General error - store and re-raise
        error_msg = "I'm sorry, I encountered an error processing your request. Please try again."
        conv_service.add_message(
            conversation_id=conversation.id,
            role="assistant",
            content=error_msg,
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"AI processing error: {str(e)}",
        )

    # Store assistant response
    conv_service.add_message(
        conversation_id=conversation.id,
        role="assistant",
        content=result["response"],
        tool_calls=result.get("tool_calls"),
    )

    return ChatResponse(
        response=result["response"],
        conversation_id=conversation.id,
        tool_calls=result.get("tool_calls", []),
    )


@router.get("/conversations", response_model=list[ConversationResponse])
def list_conversations(user: CurrentUser, session: SessionDep) -> list[Conversation]:
    """List all conversations for the authenticated user."""
    conv_service = ConversationService(session, user.user_id)
    return conv_service.list_conversations()


@router.get("/conversations/{conversation_id}", response_model=ConversationResponse)
def get_conversation(
    conversation_id: str, user: CurrentUser, session: SessionDep
) -> Conversation:
    """Get a single conversation by ID."""
    conv_service = ConversationService(session, user.user_id)
    conversation = conv_service.get_conversation(conversation_id)

    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found",
        )

    return conversation


@router.get("/conversations/{conversation_id}/messages", response_model=list[MessageResponse])
def get_conversation_messages(
    conversation_id: str, user: CurrentUser, session: SessionDep
) -> list[dict]:
    """Get all messages for a conversation."""
    conv_service = ConversationService(session, user.user_id)

    # Verify conversation exists and belongs to user
    conversation = conv_service.get_conversation(conversation_id)
    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found",
        )

    # Get messages directly from database for full details
    from sqlmodel import select
    from models import Message

    statement = (
        select(Message)
        .where(Message.conversation_id == conversation_id)
        .order_by(Message.created_at.asc())
    )
    messages = session.exec(statement).all()

    return [
        {
            "id": msg.id,
            "role": msg.role,
            "content": msg.content,
            "tool_calls": json.loads(msg.tool_calls) if msg.tool_calls else None,
            "created_at": msg.created_at,
        }
        for msg in messages
    ]


@router.delete("/conversations/{conversation_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_conversation(
    conversation_id: str, user: CurrentUser, session: SessionDep
) -> None:
    """Delete a conversation and all its messages."""
    conv_service = ConversationService(session, user.user_id)

    if not conv_service.delete_conversation(conversation_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found",
        )


# Test endpoint for development (only available when FRONTEND_URL is localhost)
@router.post("/test", response_model=ChatResponse)
def test_chat(chat_data: ChatMessage, session: SessionDep) -> ChatResponse:
    """
    Test endpoint for development - bypasses JWT auth.
    Only available when FRONTEND_URL contains 'localhost'.
    """
    frontend_url = os.getenv("FRONTEND_URL", "")
    if "localhost" not in frontend_url and "127.0.0.1" not in frontend_url:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Test endpoint only available in development",
        )

    # Use test user
    user = AuthenticatedUser(user_id=TEST_USER_ID, email="test@example.com")
    conv_service = ConversationService(session, user.user_id)

    # Get or create conversation
    if chat_data.conversation_id:
        conversation = conv_service.get_conversation(chat_data.conversation_id)
        if not conversation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Conversation not found",
            )
    else:
        title = chat_data.message[:50] + "..." if len(chat_data.message) > 50 else chat_data.message
        conversation = conv_service.create_conversation(title=title)

    # Store user message
    conv_service.add_message(
        conversation_id=conversation.id,
        role="user",
        content=chat_data.message,
    )

    # Get conversation history
    history = conv_service.get_messages(conversation.id)

    # Create agent and process message
    agent = create_agent(user.user_id)

    try:
        result = agent.chat(chat_data.message, conversation_history=history[:-1])
    except RateLimitError:
        error_msg = "Rate limit exceeded. Please wait and try again."
        conv_service.add_message(conversation_id=conversation.id, role="assistant", content=error_msg)
        raise HTTPException(status_code=status.HTTP_429_TOO_MANY_REQUESTS, detail=error_msg)
    except Exception as e:
        error_msg = f"AI processing error: {str(e)}"
        conv_service.add_message(conversation_id=conversation.id, role="assistant", content=error_msg)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=error_msg)

    # Store assistant response
    conv_service.add_message(
        conversation_id=conversation.id,
        role="assistant",
        content=result["response"],
        tool_calls=result.get("tool_calls"),
    )

    return ChatResponse(
        response=result["response"],
        conversation_id=conversation.id,
        tool_calls=result.get("tool_calls", []),
    )
