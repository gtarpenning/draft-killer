"""
Usage tracking service for authenticated and anonymous users.

Tracks API usage for rate limiting and analytics.
Anonymous users are identified by session_id (cookie + user-agent hash).
"""

import hashlib
from datetime import datetime, timedelta
from typing import Optional
from uuid import UUID

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.database import UsageRecord, User


def generate_session_id(cookie_value: str, user_agent: str) -> str:
    """
    Generate a unique session identifier from cookie and user-agent.
    
    Args:
        cookie_value: Random cookie value stored in browser
        user_agent: User's browser user-agent string
        
    Returns:
        SHA256 hash of combined cookie and user-agent
    """
    combined = f"{cookie_value}:{user_agent}"
    return hashlib.sha256(combined.encode()).hexdigest()


async def record_usage(
    db: AsyncSession,
    endpoint: str,
    user_id: Optional[UUID] = None,
    session_id: Optional[str] = None,
    user_agent: Optional[str] = None,
    ip_address: Optional[str] = None,
) -> UsageRecord:
    """
    Record a usage event.
    
    Args:
        db: Database session
        endpoint: API endpoint being accessed
        user_id: Optional authenticated user ID
        session_id: Optional anonymous session ID
        user_agent: Optional user agent string
        ip_address: Optional IP address
        
    Returns:
        Created usage record
    """
    record = UsageRecord(
        user_id=user_id,
        session_id=session_id,
        endpoint=endpoint,
        user_agent=user_agent,
        ip_address=ip_address,
    )
    
    db.add(record)
    await db.commit()
    await db.refresh(record)
    
    return record


async def get_usage_count(
    db: AsyncSession,
    user_id: Optional[UUID] = None,
    session_id: Optional[str] = None,
    endpoint: Optional[str] = None,
    since: Optional[datetime] = None,
) -> int:
    """
    Get usage count for a user or session.
    
    Args:
        db: Database session
        user_id: Optional user ID to filter by
        session_id: Optional session ID to filter by
        endpoint: Optional endpoint to filter by
        since: Optional datetime to count from (e.g., last 24 hours)
        
    Returns:
        Number of usage records matching the filters
    """
    query = select(func.count(UsageRecord.id))
    
    # Apply filters
    if user_id is not None:
        query = query.where(UsageRecord.user_id == user_id)
    if session_id is not None:
        query = query.where(UsageRecord.session_id == session_id)
    if endpoint is not None:
        query = query.where(UsageRecord.endpoint == endpoint)
    if since is not None:
        query = query.where(UsageRecord.created_at >= since)
    
    result = await db.execute(query)
    return result.scalar() or 0


async def check_anonymous_rate_limit(
    db: AsyncSession,
    session_id: str,
    limit: int = 10,
) -> tuple[bool, int]:
    """
    Check if an anonymous session has exceeded the rate limit.
    
    Args:
        db: Database session
        session_id: Anonymous session identifier
        limit: Maximum number of requests allowed
        
    Returns:
        Tuple of (is_allowed, current_count)
        is_allowed: True if under limit, False if limit exceeded
        current_count: Current number of requests
    """
    # Count all usage for this session (no time limit - lifetime limit)
    count = await get_usage_count(db, session_id=session_id)
    
    return count < limit, count


async def get_all_usage_stats(
    db: AsyncSession,
    limit: int = 100,
) -> list[dict]:
    """
    Get usage statistics for all users and anonymous sessions.
    
    Args:
        db: Database session
        limit: Maximum number of results
        
    Returns:
        List of usage statistics with user/session info
    """
    # Query for authenticated users
    user_query = (
        select(
            User.id.label("user_id"),
            User.email.label("user_email"),
            User.is_active.label("is_active"),
            func.count(UsageRecord.id).label("request_count"),
            func.max(UsageRecord.created_at).label("last_request")
        )
        .join(UsageRecord, UsageRecord.user_id == User.id, isouter=False)
        .group_by(User.id, User.email, User.is_active)
        .order_by(func.count(UsageRecord.id).desc())
    )
    
    user_result = await db.execute(user_query)
    user_rows = user_result.all()
    
    stats = []
    
    # Add authenticated user stats
    for row in user_rows:
        stats.append({
            "type": "authenticated",
            "user_id": str(row.user_id),
            "email": row.user_email,
            "is_active": row.is_active,
            "request_count": row.request_count,
            "last_request": row.last_request.isoformat() if row.last_request else None,
        })
    
    # Query for anonymous sessions
    anon_query = (
        select(
            UsageRecord.session_id,
            func.count(UsageRecord.id).label("request_count"),
            func.max(UsageRecord.created_at).label("last_request"),
            func.max(UsageRecord.user_agent).label("user_agent"),
        )
        .where(UsageRecord.session_id.isnot(None))
        .where(UsageRecord.user_id.is_(None))
        .group_by(UsageRecord.session_id)
        .order_by(func.count(UsageRecord.id).desc())
        .limit(limit)
    )
    
    anon_result = await db.execute(anon_query)
    anon_rows = anon_result.all()
    
    # Add anonymous session stats
    for row in anon_rows:
        stats.append({
            "type": "anonymous",
            "session_id": row.session_id,
            "request_count": row.request_count,
            "last_request": row.last_request.isoformat() if row.last_request else None,
            "user_agent": row.user_agent,
        })
    
    return stats


async def toggle_user_access(
    db: AsyncSession,
    user_id: UUID,
) -> User:
    """
    Toggle a user's access (enable/disable).
    
    Args:
        db: Database session
        user_id: User ID to toggle
        
    Returns:
        Updated user object
        
    Raises:
        ValueError: If user not found
    """
    result = await db.execute(
        select(User).where(User.id == user_id)
    )
    user = result.scalar_one_or_none()
    
    if not user:
        raise ValueError(f"User with id {user_id} not found")
    
    user.is_active = not user.is_active
    await db.commit()
    await db.refresh(user)
    
    return user

