"""
SQLAlchemy database models.

Defines the core database schema:
- User: Authentication and user data
- Conversation: Chat conversation metadata
- Message: Individual chat messages (user and assistant)
"""

import enum
import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, Text
from sqlalchemy import Enum as SQLEnum
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    """Base class for all database models."""
    pass


class User(Base):
    """
    User model for authentication and profile data.

    Stores user credentials and metadata. Passwords are never stored
    in plain text - only bcrypt hashes are persisted.

    Relationships:
        - conversations: All conversations created by this user
    """
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )
    email: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        index=True,
        nullable=False
    )
    password_hash: Mapped[str] = mapped_column(
        String(255),
        nullable=False
    )
    is_active: Mapped[bool] = mapped_column(
        default=True,
        nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False
    )
    last_login: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True
    )

    # Relationships
    conversations: Mapped[list["Conversation"]] = relationship(
        "Conversation",
        back_populates="user",
        cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<User(id={self.id}, email={self.email})>"


class Conversation(Base):
    """
    Conversation model for organizing chat sessions.

    Each conversation represents a distinct chat session with the AI.
    Conversations contain multiple messages and can be titled for
    easy identification.

    Relationships:
        - user: The user who owns this conversation
        - messages: All messages in this conversation
    """
    __tablename__ = "conversations"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    title: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False
    )

    # Relationships
    user: Mapped["User"] = relationship(
        "User",
        back_populates="conversations"
    )
    messages: Mapped[list["Message"]] = relationship(
        "Message",
        back_populates="conversation",
        cascade="all, delete-orphan",
        order_by="Message.created_at"
    )

    def __repr__(self) -> str:
        return f"<Conversation(id={self.id}, title={self.title})>"


class MessageRole(str, enum.Enum):
    """Enum for message roles in a conversation."""
    USER = "user"
    ASSISTANT = "assistant"


class Message(Base):
    """
    Message model for chat messages.

    Stores individual messages within a conversation. Each message
    has a role (user or assistant) and can include metadata such as
    token counts, model information, and processing costs.

    The message_metadata field uses JSONB for flexible storage of additional
    information without requiring schema changes.

    Relationships:
        - conversation: The conversation this message belongs to
    """
    __tablename__ = "messages"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )
    conversation_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("conversations.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    role: Mapped[MessageRole] = mapped_column(
        SQLEnum(MessageRole),
        nullable=False
    )
    content: Mapped[str] = mapped_column(
        Text,
        nullable=False
    )
    message_metadata: Mapped[dict | None] = mapped_column(
        JSONB,
        nullable=True,
        default=dict
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
        index=True
    )

    # Relationships
    conversation: Mapped["Conversation"] = relationship(
        "Conversation",
        back_populates="messages"
    )

    def __repr__(self) -> str:
        content_preview = self.content[:50] + "..." if len(self.content) > 50 else self.content
        return f"<Message(id={self.id}, role={self.role}, content='{content_preview}')>"


class UsageRecord(Base):
    """
    Usage tracking model for both authenticated and anonymous users.

    Tracks API usage for rate limiting and analytics.
    Anonymous users are tracked by a session identifier (cookie + user-agent hash).

    Relationships:
        - user: Optional link to authenticated user
    """
    __tablename__ = "usage_records"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=True,
        index=True
    )
    session_id: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
        index=True
    )
    endpoint: Mapped[str] = mapped_column(
        String(255),
        nullable=False
    )
    user_agent: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )
    ip_address: Mapped[str | None] = mapped_column(
        String(45),  # IPv6 max length
        nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
        index=True
    )

    # Relationships
    user: Mapped["User | None"] = relationship("User")

    def __repr__(self) -> str:
        identifier = f"user_id={self.user_id}" if self.user_id else f"session_id={self.session_id}"
        return f"<UsageRecord(id={self.id}, {identifier}, endpoint={self.endpoint})>"


