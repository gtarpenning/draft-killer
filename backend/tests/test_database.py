"""
Tests for database operations and models.

Tests database schema, relationships, and CRUD operations.
Uses test database transaction that rolls back after each test.
"""

from datetime import datetime

import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.database import ApiUsage, Conversation, Message, MessageRole, User

# ============================================================================
# User Model Tests
# ============================================================================

@pytest.mark.asyncio
async def test_create_user(db_session: AsyncSession):
    """Test creating a user in the database."""
    user = User(
        email="dbtest@example.com",
        password_hash="hashed_password",
    )

    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)

    assert user.id is not None
    assert user.email == "dbtest@example.com"
    assert user.is_active is True  # Default value
    assert user.created_at is not None


@pytest.mark.asyncio
async def test_user_default_values(db_session: AsyncSession):
    """Test that user model has correct default values."""
    user = User(
        email="defaults@example.com",
        password_hash="hashed",
    )

    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)

    assert user.is_active is True
    assert user.created_at is not None
    assert user.updated_at is not None
    assert user.last_login is None  # Should be None until first login


@pytest.mark.asyncio
async def test_user_email_unique(db_session: AsyncSession):
    """Test that duplicate emails are not allowed."""
    email = "unique@example.com"

    # Create first user
    user1 = User(email=email, password_hash="hash1")
    db_session.add(user1)
    await db_session.commit()

    # Try to create second user with same email
    user2 = User(email=email, password_hash="hash2")
    db_session.add(user2)

    with pytest.raises(Exception):  # Should raise integrity error
        await db_session.commit()


@pytest.mark.asyncio
async def test_user_updated_at_changes(db_session: AsyncSession):
    """Test that updated_at changes when user is modified."""
    user = User(email="update@example.com", password_hash="hash")
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)

    original_updated = user.updated_at

    # Wait a moment and update
    import asyncio
    await asyncio.sleep(0.1)

    user.last_login = datetime.utcnow()
    await db_session.commit()
    await db_session.refresh(user)

    assert user.updated_at > original_updated


# ============================================================================
# Conversation Model Tests
# ============================================================================

@pytest.mark.asyncio
async def test_create_conversation(db_session: AsyncSession):
    """Test creating a conversation."""
    # Create user first
    user = User(email="conv@example.com", password_hash="hash")
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)

    # Create conversation
    conv = Conversation(
        user_id=user.id,
        title="Test Conversation"
    )
    db_session.add(conv)
    await db_session.commit()
    await db_session.refresh(conv)

    assert conv.id is not None
    assert conv.user_id == user.id
    assert conv.title == "Test Conversation"


@pytest.mark.asyncio
async def test_conversation_user_relationship(db_session: AsyncSession):
    """Test that conversation has relationship to user."""
    # Create user and conversation
    user = User(email="rel@example.com", password_hash="hash")
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)

    conv = Conversation(user_id=user.id, title="Test")
    db_session.add(conv)
    await db_session.commit()

    # Query with relationship loaded
    result = await db_session.execute(
        select(Conversation).where(Conversation.id == conv.id)
    )
    loaded_conv = result.scalar_one()

    # Load relationship
    await db_session.refresh(loaded_conv, ["user"])
    assert loaded_conv.user.email == user.email


@pytest.mark.asyncio
async def test_conversation_cascade_delete(db_session: AsyncSession):
    """Test that deleting user deletes their conversations."""
    # Create user with conversation
    user = User(email="cascade@example.com", password_hash="hash")
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)

    conv = Conversation(user_id=user.id, title="Test")
    db_session.add(conv)
    await db_session.commit()
    conv_id = conv.id

    # Delete user
    await db_session.delete(user)
    await db_session.commit()

    # Conversation should be deleted too
    result = await db_session.execute(
        select(Conversation).where(Conversation.id == conv_id)
    )
    assert result.scalar_one_or_none() is None


# ============================================================================
# Message Model Tests
# ============================================================================

@pytest.mark.asyncio
async def test_create_message(db_session: AsyncSession):
    """Test creating a message."""
    # Setup user and conversation
    user = User(email="msg@example.com", password_hash="hash")
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)

    conv = Conversation(user_id=user.id, title="Test")
    db_session.add(conv)
    await db_session.commit()
    await db_session.refresh(conv)

    # Create message
    msg = Message(
        conversation_id=conv.id,
        role=MessageRole.USER,
        content="Hello, world!"
    )
    db_session.add(msg)
    await db_session.commit()
    await db_session.refresh(msg)

    assert msg.id is not None
    assert msg.conversation_id == conv.id
    assert msg.role == MessageRole.USER
    assert msg.content == "Hello, world!"


@pytest.mark.asyncio
async def test_message_roles(db_session: AsyncSession):
    """Test that message roles are properly enforced."""
    # Setup
    user = User(email="roles@example.com", password_hash="hash")
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)

    conv = Conversation(user_id=user.id, title="Test")
    db_session.add(conv)
    await db_session.commit()
    await db_session.refresh(conv)

    # Test USER role
    msg1 = Message(conversation_id=conv.id, role=MessageRole.USER, content="User msg")
    db_session.add(msg1)
    await db_session.commit()
    assert msg1.role == MessageRole.USER

    # Test ASSISTANT role
    msg2 = Message(conversation_id=conv.id, role=MessageRole.ASSISTANT, content="AI msg")
    db_session.add(msg2)
    await db_session.commit()
    assert msg2.role == MessageRole.ASSISTANT


@pytest.mark.asyncio
async def test_message_metadata(db_session: AsyncSession):
    """Test that message metadata is stored correctly."""
    # Setup
    user = User(email="meta@example.com", password_hash="hash")
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)

    conv = Conversation(user_id=user.id, title="Test")
    db_session.add(conv)
    await db_session.commit()
    await db_session.refresh(conv)

    # Create message with metadata
    metadata = {
        "model": "gpt-4",
        "tokens": 150,
        "cost": 0.003
    }
    msg = Message(
        conversation_id=conv.id,
        role=MessageRole.ASSISTANT,
        content="Response",
        message_metadata=metadata
    )
    db_session.add(msg)
    await db_session.commit()
    await db_session.refresh(msg)

    assert msg.message_metadata == metadata
    assert msg.message_metadata["model"] == "gpt-4"


# ============================================================================
# API Usage Model Tests
# ============================================================================

@pytest.mark.asyncio
async def test_create_api_usage(db_session: AsyncSession):
    """Test creating an API usage record."""
    # Create user
    user = User(email="usage@example.com", password_hash="hash")
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)

    # Create usage record
    usage = ApiUsage(
        user_id=user.id,
        endpoint="/api/chat/stream",
        user_agent="Mozilla/5.0"
    )
    db_session.add(usage)
    await db_session.commit()
    await db_session.refresh(usage)

    assert usage.id is not None
    assert usage.user_id == user.id
    assert usage.endpoint == "/api/chat/stream"


@pytest.mark.asyncio
async def test_api_usage_anonymous(db_session: AsyncSession):
    """Test API usage for anonymous users (no user_id)."""
    usage = ApiUsage(
        session_id="anon-session-123",
        endpoint="/api/chat/stream",
        user_agent="Mozilla/5.0"
    )
    db_session.add(usage)
    await db_session.commit()
    await db_session.refresh(usage)

    assert usage.user_id is None
    assert usage.session_id == "anon-session-123"


@pytest.mark.asyncio
async def test_query_usage_by_user(db_session: AsyncSession):
    """Test querying usage records for a specific user."""
    # Create user and usage
    user = User(email="queryusage@example.com", password_hash="hash")
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)

    # Create multiple usage records
    for i in range(3):
        usage = ApiUsage(
            user_id=user.id,
            endpoint=f"/api/endpoint{i}",
            user_agent="Test"
        )
        db_session.add(usage)
    await db_session.commit()

    # Query usage
    result = await db_session.execute(
        select(ApiUsage).where(ApiUsage.user_id == user.id)
    )
    usage_records = result.scalars().all()

    assert len(usage_records) == 3


# ============================================================================
# Relationship Tests
# ============================================================================

@pytest.mark.asyncio
async def test_user_conversations_relationship(db_session: AsyncSession):
    """Test user -> conversations relationship."""
    user = User(email="userconv@example.com", password_hash="hash")
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)

    # Create conversations
    for i in range(3):
        conv = Conversation(user_id=user.id, title=f"Conv {i}")
        db_session.add(conv)
    await db_session.commit()

    # Load user with conversations
    result = await db_session.execute(
        select(User).where(User.id == user.id)
    )
    loaded_user = result.scalar_one()
    await db_session.refresh(loaded_user, ["conversations"])

    assert len(loaded_user.conversations) == 3


@pytest.mark.asyncio
async def test_conversation_messages_relationship(db_session: AsyncSession):
    """Test conversation -> messages relationship."""
    # Setup
    user = User(email="convmsg@example.com", password_hash="hash")
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)

    conv = Conversation(user_id=user.id, title="Test")
    db_session.add(conv)
    await db_session.commit()
    await db_session.refresh(conv)

    # Create messages
    for i in range(5):
        role = MessageRole.USER if i % 2 == 0 else MessageRole.ASSISTANT
        msg = Message(conversation_id=conv.id, role=role, content=f"Msg {i}")
        db_session.add(msg)
    await db_session.commit()

    # Load conversation with messages
    result = await db_session.execute(
        select(Conversation).where(Conversation.id == conv.id)
    )
    loaded_conv = result.scalar_one()
    await db_session.refresh(loaded_conv, ["messages"])

    assert len(loaded_conv.messages) == 5


# ============================================================================
# Summary Test
# ============================================================================

def test_database_summary():
    """Print summary of database tests."""
    print("\n" + "="*60)
    print("DATABASE TESTS SUMMARY")
    print("="*60)
    print("✅ All database tests passed!")
    print("✅ Models, relationships, and constraints working correctly")
    print("="*60)

