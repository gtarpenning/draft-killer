"""
Chat endpoints for parlay analysis.

Provides endpoints for:
- Streaming chat completions
- Chat history retrieval
- Conversation management
"""

import json
from typing import Annotated
from uuid import UUID

import weave
from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from fastapi.responses import StreamingResponse
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.api.routes.auth import get_current_user
from app.core.database import get_db
from app.core.usage import get_session_id, track_and_check_usage
from app.models.database import Conversation, Message, MessageRole, User
from app.models.schemas import (
    ChatRequest,
    ConversationListItem,
    ConversationResponse,
)
from app.services.agent_service import get_agent_service
from app.services.llm_service import stream_parlay_analysis
from app.services.odds_api.helpers import get_odds_service
from app.services.odds_api.service import OddsService
from app.services.query_extraction_service import (
    QueryExtractionService,
    get_query_extraction_service,
)

router = APIRouter()


# ============================================================================
# Helper Functions
# ============================================================================

async def get_or_create_conversation(
    db: AsyncSession,
    user: User,
    conversation_id: UUID | None = None,
) -> Conversation:
    """
    Get an existing conversation or create a new one.

    Args:
        db: Database session
        user: Current user
        conversation_id: Optional existing conversation ID

    Returns:
        Conversation object

    Raises:
        404: If conversation_id provided but not found or doesn't belong to user
    """
    if conversation_id:
        # Get existing conversation
        result = await db.execute(
            select(Conversation)
            .where(
                Conversation.id == conversation_id,
                Conversation.user_id == user.id
            )
        )
        conversation = result.scalar_one_or_none()

        if not conversation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Conversation not found"
            )

        return conversation
    else:
        # Create new conversation
        conversation = Conversation(
            user_id=user.id,
            title=None,  # Will be set based on first message
        )
        db.add(conversation)
        await db.commit()
        await db.refresh(conversation)

        return conversation


async def save_message(
    db: AsyncSession,
    conversation_id: UUID,
    role: MessageRole,
    content: str,
    message_metadata: dict | None = None,
) -> Message:
    """
    Save a message to the database.

    Args:
        db: Database session
        conversation_id: Conversation ID
        role: Message role (user or assistant)
        content: Message content
        message_metadata: Optional metadata (tokens, cost, etc.)

    Returns:
        Saved message object
    """
    message = Message(
        conversation_id=conversation_id,
        role=role,
        content=content,
        message_metadata=message_metadata or {},
    )

    db.add(message)
    await db.commit()
    await db.refresh(message)

    return message


async def generate_conversation_title(first_message: str) -> str:
    """
    Generate a title for a conversation based on the first message.

    For MVP, just truncate the first message.
    Future: Use LLM to generate a concise title.

    Args:
        first_message: The user's first message

    Returns:
        Generated title (max 100 chars)
    """
    # Simple truncation for MVP
    max_length = 100
    if len(first_message) <= max_length:
        return first_message
    return first_message[:max_length - 3] + "..."


# ============================================================================
# Endpoints
# ============================================================================

async def get_optional_user(
    request: Request,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> User | None:
    """
    Get current user if authenticated, otherwise None.
    This allows endpoints to work for both authenticated and anonymous users.
    """
    # Try to extract bearer token from Authorization header
    auth_header = request.headers.get("Authorization")

    if not auth_header or not auth_header.startswith("Bearer "):
        return None

    try:
        token = auth_header.replace("Bearer ", "")
        from app.core.security import get_token_subject

        email = get_token_subject(token)
        if not email:
            return None

        result = await db.execute(
            select(User).where(User.email == email)
        )
        user = result.scalar_one_or_none()

        # Check if user is active
        if user and not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Your account has been disabled. Please contact support.",
            )

        return user
    except HTTPException:
        raise  # Re-raise HTTP exceptions
    except Exception:
        return None  # Any other error, treat as anonymous


@router.post("/stream")
@weave.op()
async def stream_chat(
    chat_request: ChatRequest,
    request: Request,
    response: Response,
    db: Annotated[AsyncSession, Depends(get_db)],
    odds_service: Annotated[OddsService, Depends(get_odds_service)],
    query_extraction_service: Annotated[QueryExtractionService, Depends(get_query_extraction_service)],
    session_id: Annotated[str, Depends(get_session_id)],
    current_user: User | None = Depends(get_optional_user),
):
    """
    Stream a chat response for parlay analysis with live odds data.

    Accepts a user message and streams back an AI-generated analysis.
    The response is streamed token-by-token for a typewriter effect.

    If the message contains parlay information, it will be enriched with
    current odds from The Odds API before being sent to the LLM.

    Works for both authenticated and anonymous users.
    Anonymous users are limited to 10 free requests.

    Args:
        chat_request: Chat request with message and optional conversation_id
        request: FastAPI request object
        response: FastAPI response object
        db: Database session
        odds_service: Odds API service
        session_id: Session ID for anonymous users
        current_user: Optional authenticated user

    Returns:
        Server-Sent Events stream with analysis chunks
    """
    # Track usage and check rate limits
    await track_and_check_usage(
        request,
        response,
        db,
        session_id,
        user_id=current_user.id if current_user else None,
    )

    # Only authenticated users can have conversations
    # Anonymous users get one-off responses
    conversation = None
    if current_user:
        # Get or create conversation
        conversation = await get_or_create_conversation(
            db, current_user, chat_request.conversation_id
        )

    # Save user message only for authenticated users
    if conversation:
        await save_message(
            db,
            conversation.id,
            MessageRole.USER,
            chat_request.message
        )

        # Generate title if this is the first user message
        if not conversation.title:
            conversation.title = await generate_conversation_title(chat_request.message)
            await db.commit()

    # ========================================================================
    # NEW: Two-Stage LLM Pipeline for Intelligent Odds Fetching
    # ========================================================================
    # Stage 1: Extract betting intent and entities using LLM
    # Stage 2: Fetch relevant odds based on extracted queries
    # ========================================================================

    enriched_odds = None
    query_context = None

    try:
        # Stage 1: Extract structured betting query from natural language
        query_context = await query_extraction_service.extract_betting_intent(
            chat_request.message,
            conversation_history=None  # TODO: Add conversation history
        )

        print(f"Extracted query: intent={query_context.intent}, sport={query_context.sport}, "
              f"entities={len(query_context.entities)}, queries={len(query_context.suggested_queries)}")

        # Stage 2: Fetch odds based on intent
        if query_context.intent == "analyze_specific_bets":
            # User has specific bets to analyze
            # Try to use suggested queries first, fallback to naive parsing
            if query_context.suggested_queries:
                enriched_odds = odds_service.enrich_from_api_queries(
                    [q.model_dump() for q in query_context.suggested_queries]
                )
            else:
                # Fallback to old parsing method
                leg_texts = []
                if ',' in chat_request.message:
                    leg_texts = [leg.strip() for leg in chat_request.message.split(',')]
                elif ' and ' in chat_request.message.lower():
                    leg_texts = [leg.strip() for leg in chat_request.message.lower().split(' and ')]

                if leg_texts:
                    parsed_legs = [odds_service.parse_parlay_leg(leg) for leg in leg_texts]
                    enriched_odds = odds_service.enrich_parlay_with_odds(
                        parsed_legs,
                        sport_key=query_context.sport or 'americanfootball_nfl'
                    )

        elif query_context.intent == "request_suggestions":
            # User wants parlay suggestions
            sport = query_context.sport or "americanfootball_nfl"
            enriched_odds = odds_service.get_suggestions_for_sport(sport, num_legs=3)

        elif query_context.intent == "lookup_odds":
            # User wants to look up odds for something
            if query_context.suggested_queries:
                enriched_odds = odds_service.enrich_from_api_queries(
                    [q.model_dump() for q in query_context.suggested_queries]
                )

        # else: general_question - no odds needed

    except Exception as e:
        # If extraction or enrichment fails, log but continue without odds
        print(f"Warning: Failed in LLM pipeline: {e}")
        import traceback
        traceback.print_exc()

    async def event_stream():
        """Generate Server-Sent Events stream."""
        accumulated_content = []

        try:
            # Stream the LLM response with enriched odds
            async for chunk in stream_parlay_analysis(chat_request.message, enriched_odds):
                accumulated_content.append(chunk)

                # Send chunk as SSE
                data = json.dumps({
                    "content": chunk,
                    "done": False,
                    "conversation_id": str(conversation.id) if conversation else None,
                })
                yield f"data: {data}\n\n"

            # Save complete assistant message (only for authenticated users)
            if conversation:
                full_content = "".join(accumulated_content)
                metadata = {
                    "model": "meta-llama/Llama-3.3-70B-Instruct",  # W&B Inference model
                    "streamed": True,
                }

                # Add odds metadata if available
                if enriched_odds:
                    metadata["odds_enriched"] = True
                    metadata["odds_legs"] = enriched_odds.get("num_legs", 0)
                    if odds_service.get_remaining_requests():
                        metadata["api_requests_remaining"] = odds_service.get_remaining_requests()

                await save_message(
                    db,
                    conversation.id,
                    MessageRole.ASSISTANT,
                    full_content,
                    message_metadata=metadata
                )

            # Send final "done" event
            data = json.dumps({
                "content": "",
                "done": True,
                "conversation_id": str(conversation.id) if conversation else None,
            })
            yield f"data: {data}\n\n"

        except Exception as e:
            # Send error event
            error_data = json.dumps({
                "error": str(e),
                "done": True,
            })
            yield f"data: {error_data}\n\n"

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",  # Disable buffering in nginx
        }
    )


@router.get("/history", response_model=list[ConversationListItem])
async def get_chat_history(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
    limit: int = 50,
    offset: int = 0,
) -> list[ConversationListItem]:
    """
    Get user's conversation history.

    Returns a list of conversations with basic metadata.
    Does not include full message history (use GET /conversations/{id} for that).

    Args:
        current_user: Authenticated user
        db: Database session
        limit: Maximum number of conversations to return
        offset: Number of conversations to skip (for pagination)

    Returns:
        List of conversation metadata
    """
    # Get conversations with message count
    result = await db.execute(
        select(
            Conversation,
            func.count(Message.id).label("message_count")
        )
        .outerjoin(Message)
        .where(Conversation.user_id == current_user.id)
        .group_by(Conversation.id)
        .order_by(Conversation.updated_at.desc())
        .limit(limit)
        .offset(offset)
    )

    conversations = []
    for conversation, message_count in result:
        item = ConversationListItem(
            id=conversation.id,
            title=conversation.title,
            created_at=conversation.created_at,
            updated_at=conversation.updated_at,
            message_count=message_count,
        )
        conversations.append(item)

    return conversations


@router.get("/conversations/{conversation_id}", response_model=ConversationResponse)
async def get_conversation(
    conversation_id: UUID,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> ConversationResponse:
    """
    Get a specific conversation with full message history.

    Args:
        conversation_id: Conversation ID
        current_user: Authenticated user
        db: Database session

    Returns:
        Conversation with all messages

    Raises:
        404: If conversation not found or doesn't belong to user
    """
    result = await db.execute(
        select(Conversation)
        .options(selectinload(Conversation.messages))
        .where(
            Conversation.id == conversation_id,
            Conversation.user_id == current_user.id
        )
    )
    conversation = result.scalar_one_or_none()

    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found"
        )

    return ConversationResponse.model_validate(conversation)


@router.delete("/conversations/{conversation_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_conversation(
    conversation_id: UUID,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """
    Delete a conversation and all its messages.

    Args:
        conversation_id: Conversation ID
        current_user: Authenticated user
        db: Database session

    Raises:
        404: If conversation not found or doesn't belong to user
    """
    result = await db.execute(
        select(Conversation)
        .where(
            Conversation.id == conversation_id,
            Conversation.user_id == current_user.id
        )
    )
    conversation = result.scalar_one_or_none()

    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found"
        )

    await db.delete(conversation)
    await db.commit()


@router.post("/agent-stream")
@weave.op()
async def stream_agent_chat(
    chat_request: ChatRequest,
    request: Request,
    response: Response,
    db: Annotated[AsyncSession, Depends(get_db)],
    odds_service: Annotated[OddsService, Depends(get_odds_service)],
    session_id: Annotated[str, Depends(get_session_id)],
    current_user: User | None = Depends(get_optional_user),
):
    """
    Stream a chat response using the autonomous agent with tool calling.

    This endpoint uses the OpenAI Agents SDK to provide intelligent responses
    with the ability to make tool calls for fetching odds data.

    Works for both authenticated and anonymous users.
    Anonymous users are limited to 10 free requests.

    Args:
        chat_request: Chat request with message and optional conversation_id
        request: FastAPI request object
        response: FastAPI response object
        db: Database session
        odds_service: Odds API service
        session_id: Session ID for anonymous users
        current_user: Optional authenticated user

    Returns:
        Server-Sent Events stream with agent response chunks
    """
    # Track usage and check rate limits
    await track_and_check_usage(
        request,
        response,
        db,
        session_id,
        user_id=current_user.id if current_user else None,
    )

    # Only authenticated users can have conversations
    # Anonymous users get one-off responses
    conversation = None
    if current_user:
        # Get or create conversation
        conversation = await get_or_create_conversation(
            db, current_user, chat_request.conversation_id
        )

    # Save user message only for authenticated users
    if conversation:
        await save_message(
            db,
            conversation.id,
            MessageRole.USER,
            chat_request.message
        )

        # Generate title if this is the first user message
        if not conversation.title:
            conversation.title = await generate_conversation_title(chat_request.message)
            await db.commit()

    # Get conversation history for context
    conversation_history = []
    if conversation:
        # Get recent messages for context
        result = await db.execute(
            select(Message)
            .where(Message.conversation_id == conversation.id)
            .order_by(Message.created_at.desc())
            .limit(10)
        )
        recent_messages = result.scalars().all()

        # Convert to the format expected by the agent
        for msg in reversed(recent_messages):
            conversation_history.append({
                "role": msg.role.value,
                "content": msg.content
            })

    # Initialize agent service
    agent_service = get_agent_service(odds_service)

    async def event_stream():
        """Generate Server-Sent Events stream."""
        accumulated_content = []

        try:
            # Stream the agent response
            async for event in agent_service.stream_response(
                chat_request.message,
                conversation_history
            ):
                if event["type"] == "content":
                    accumulated_content.append(event["data"])

                # Send event as SSE
                data = json.dumps({
                    "event": event,
                    "done": False,
                    "conversation_id": str(conversation.id) if conversation else None,
                })
                yield f"data: {data}\n\n"

            # Save complete assistant message (only for authenticated users)
            if conversation:
                full_content = "".join(accumulated_content)
                metadata = {
                    "model": "gpt-4o-mini",  # Agent model
                    "streamed": True,
                    "agent_mode": True,
                    "tools_available": True,
                }

                # Add odds metadata if available
                if odds_service.get_remaining_requests():
                    metadata["api_requests_remaining"] = odds_service.get_remaining_requests()

                await save_message(
                    db,
                    conversation.id,
                    MessageRole.ASSISTANT,
                    full_content,
                    message_metadata=metadata
                )

            # Send final "done" event
            data = json.dumps({
                "event": {"type": "done", "data": ""},
                "done": True,
                "conversation_id": str(conversation.id) if conversation else None,
            })
            yield f"data: {data}\n\n"

        except Exception as e:
            # Send error event
            error_data = json.dumps({
                "event": {"type": "error", "data": str(e)},
                "done": True,
            })
            yield f"data: {error_data}\n\n"

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",  # Disable buffering in nginx
        }
    )


