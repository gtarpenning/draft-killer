"""
Usage tracking middleware and dependencies.

Provides request tracking and rate limiting for authenticated and anonymous users.
"""

import secrets
from typing import Annotated, Optional
from uuid import UUID

from fastapi import Cookie, Depends, HTTPException, Request, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.services.usage_service import (
    generate_session_id,
    record_usage,
    check_anonymous_rate_limit,
)


# Cookie name for anonymous session tracking
SESSION_COOKIE_NAME = "draft_killer_session"
ANONYMOUS_REQUEST_LIMIT = 10


async def get_or_create_session_cookie(
    request: Request,
    response: Response,
    session_cookie: Optional[str] = Cookie(None, alias=SESSION_COOKIE_NAME),
) -> str:
    """
    Get existing session cookie or create a new one.
    
    This dependency ensures every anonymous user has a session cookie
    for tracking purposes.
    
    Args:
        request: FastAPI request object
        response: FastAPI response object (to set cookie)
        session_cookie: Existing session cookie value (if any)
        
    Returns:
        Session cookie value
    """
    if not session_cookie:
        # Generate new random session ID
        session_cookie = secrets.token_urlsafe(32)
        
        # Set cookie (expires in 1 year)
        response.set_cookie(
            key=SESSION_COOKIE_NAME,
            value=session_cookie,
            max_age=31536000,  # 1 year in seconds
            httponly=True,
            samesite="lax",
            secure=False,  # Set to True in production with HTTPS
        )
    
    return session_cookie


async def get_session_id(
    request: Request,
    session_cookie: Annotated[str, Depends(get_or_create_session_cookie)],
) -> str:
    """
    Generate session ID from cookie and user-agent.
    
    Args:
        request: FastAPI request object
        session_cookie: Session cookie value
        
    Returns:
        Hashed session identifier
    """
    user_agent = request.headers.get("user-agent", "unknown")
    return generate_session_id(session_cookie, user_agent)


async def track_and_check_usage(
    request: Request,
    response: Response,
    db: Annotated[AsyncSession, Depends(get_db)],
    session_id: Annotated[str, Depends(get_session_id)],
    user_id: Optional[UUID] = None,
) -> None:
    """
    Track usage and enforce rate limits for anonymous users.
    
    This dependency should be used on endpoints that need usage tracking.
    Authenticated users have unlimited access.
    Anonymous users are limited to ANONYMOUS_REQUEST_LIMIT requests.
    
    Args:
        request: FastAPI request object
        response: FastAPI response object
        db: Database session
        session_id: Session identifier
        user_id: Optional authenticated user ID
        
    Raises:
        HTTPException: If anonymous user exceeds rate limit
    """
    # Get request info
    endpoint = str(request.url.path)
    user_agent = request.headers.get("user-agent")
    ip_address = request.client.host if request.client else None
    
    # If user is authenticated, just track usage (no limit)
    if user_id is not None:
        await record_usage(
            db,
            endpoint=endpoint,
            user_id=user_id,
            user_agent=user_agent,
            ip_address=ip_address,
        )
        return
    
    # For anonymous users, check rate limit first
    is_allowed, current_count = await check_anonymous_rate_limit(db, session_id)
    
    if not is_allowed:
        # User has exceeded the limit
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail={
                "error": "Free request limit exceeded",
                "message": f"You have used all {ANONYMOUS_REQUEST_LIMIT} free requests. Please register or log in to continue.",
                "limit": ANONYMOUS_REQUEST_LIMIT,
                "current_count": current_count,
            }
        )
    
    # Record usage for anonymous user
    await record_usage(
        db,
        endpoint=endpoint,
        session_id=session_id,
        user_agent=user_agent,
        ip_address=ip_address,
    )
    
    # Add rate limit headers to response
    response.headers["X-RateLimit-Limit"] = str(ANONYMOUS_REQUEST_LIMIT)
    response.headers["X-RateLimit-Remaining"] = str(ANONYMOUS_REQUEST_LIMIT - current_count - 1)

