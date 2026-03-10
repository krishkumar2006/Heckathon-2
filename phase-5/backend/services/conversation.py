"""Conversation service for managing chat history."""

import json
from datetime import datetime
from typing import Any

from sqlalchemy import delete as sa_delete
from sqlmodel import Session, select

from models import Conversation, Message


class ConversationService:
    """Service for managing conversation persistence."""

    def __init__(self, session: Session, user_id: str):
        """
        Initialize the conversation service.

        Args:
            session: SQLModel database session
            user_id: The ID of the authenticated user
        """
        self.session = session
        self.user_id = user_id

    def create_conversation(self, title: str | None = None) -> Conversation:
        """
        Create a new conversation.

        Args:
            title: Optional title for the conversation

        Returns:
            The created Conversation object
        """
        conversation = Conversation(
            user_id=self.user_id,
            title=title,
        )
        self.session.add(conversation)
        self.session.commit()
        self.session.refresh(conversation)
        return conversation

    def get_conversation(self, conversation_id: str) -> Conversation | None:
        """
        Get a conversation by ID.

        Args:
            conversation_id: The ID of the conversation

        Returns:
            The Conversation object or None if not found
        """
        conversation = self.session.get(Conversation, conversation_id)
        if conversation and conversation.user_id == self.user_id:
            return conversation
        return None

    def list_conversations(self, limit: int = 50) -> list[Conversation]:
        """
        List conversations for the user.

        Args:
            limit: Maximum number of conversations to return

        Returns:
            List of Conversation objects
        """
        statement = (
            select(Conversation)
            .where(Conversation.user_id == self.user_id)
            .order_by(Conversation.updated_at.desc())
            .limit(limit)
        )
        return list(self.session.exec(statement).all())

    def delete_conversation(self, conversation_id: str) -> bool:
        """
        Delete a conversation and its messages.

        Args:
            conversation_id: The ID of the conversation to delete

        Returns:
            True if deleted, False if not found
        """
        conversation = self.get_conversation(conversation_id)
        if not conversation:
            return False

        # Delete all messages first using direct SQL to avoid FK constraint issues
        stmt = sa_delete(Message).where(Message.conversation_id == conversation_id)
        self.session.execute(stmt)
        self.session.commit()

        # Now delete the conversation
        self.session.delete(conversation)
        self.session.commit()
        return True

    def add_message(
        self,
        conversation_id: str,
        role: str,
        content: str,
        tool_calls: list[dict[str, Any]] | None = None,
    ) -> Message:
        """
        Add a message to a conversation.

        Args:
            conversation_id: The ID of the conversation
            role: The role of the message sender ('user' or 'assistant')
            content: The message content
            tool_calls: Optional list of tool calls made

        Returns:
            The created Message object
        """
        message = Message(
            conversation_id=conversation_id,
            role=role,
            content=content,
            tool_calls=json.dumps(tool_calls) if tool_calls else None,
        )
        self.session.add(message)

        # Update conversation's updated_at
        conversation = self.session.get(Conversation, conversation_id)
        if conversation:
            conversation.updated_at = datetime.utcnow()
            self.session.add(conversation)

        self.session.commit()
        self.session.refresh(message)
        return message

    def get_messages(
        self, conversation_id: str, limit: int = 100
    ) -> list[dict[str, Any]]:
        """
        Get messages for a conversation in OpenAI message format.

        Args:
            conversation_id: The ID of the conversation
            limit: Maximum number of messages to return

        Returns:
            List of messages in OpenAI format
        """
        # Verify conversation belongs to user
        conversation = self.get_conversation(conversation_id)
        if not conversation:
            return []

        statement = (
            select(Message)
            .where(Message.conversation_id == conversation_id)
            .order_by(Message.created_at.asc())
            .limit(limit)
        )
        messages = self.session.exec(statement).all()

        return [
            {
                "role": msg.role,
                "content": msg.content,
            }
            for msg in messages
        ]

    def update_conversation_title(
        self, conversation_id: str, title: str
    ) -> Conversation | None:
        """
        Update the title of a conversation.

        Args:
            conversation_id: The ID of the conversation
            title: The new title

        Returns:
            The updated Conversation or None if not found
        """
        conversation = self.get_conversation(conversation_id)
        if not conversation:
            return None

        conversation.title = title
        conversation.updated_at = datetime.utcnow()
        self.session.add(conversation)
        self.session.commit()
        self.session.refresh(conversation)
        return conversation
