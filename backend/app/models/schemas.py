"""
Pydantic schemas for request/response validation.

These schemas define the shape of data for API requests and responses.
They provide automatic validation, serialization, and documentation.
"""

from datetime import datetime
from enum import Enum
from typing import Any
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field, field_validator

# ============================================================================
# Authentication Schemas
# ============================================================================

class UserRegister(BaseModel):
    """Schema for user registration request."""
    email: EmailStr = Field(..., description="User email address")
    password: str = Field(..., min_length=8, description="User password (min 8 characters)")

    @field_validator("password")
    @classmethod
    def validate_password_strength(cls, v: str) -> str:
        """Ensure password meets minimum strength requirements."""
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters long")
        if not any(c.isupper() for c in v):
            raise ValueError("Password must contain at least one uppercase letter")
        if not any(c.islower() for c in v):
            raise ValueError("Password must contain at least one lowercase letter")
        if not any(c.isdigit() for c in v):
            raise ValueError("Password must contain at least one number")
        return v


class UserLogin(BaseModel):
    """Schema for user login request."""
    email: EmailStr = Field(..., description="User email address")
    password: str = Field(..., description="User password")


class Token(BaseModel):
    """Schema for authentication token response."""
    access_token: str = Field(..., description="JWT access token")
    token_type: str = Field(default="bearer", description="Token type")


class UserResponse(BaseModel):
    """Schema for user data in responses."""
    id: UUID
    email: str
    created_at: datetime
    last_login: datetime | None = None

    model_config = {"from_attributes": True}


# ============================================================================
# Chat Schemas
# ============================================================================

class ChatRequest(BaseModel):
    """Schema for chat message request."""
    message: str = Field(..., min_length=1, max_length=5000, description="User message")
    conversation_id: UUID | None = Field(None, description="Existing conversation ID (optional)")

    @field_validator("message")
    @classmethod
    def validate_message(cls, v: str) -> str:
        """Ensure message is not empty or only whitespace."""
        if not v.strip():
            raise ValueError("Message cannot be empty or only whitespace")
        return v.strip()


class MessageResponse(BaseModel):
    """Schema for a single message in responses."""
    id: UUID
    role: str
    content: str
    message_metadata: dict[str, Any] | None = None
    created_at: datetime

    model_config = {"from_attributes": True}


class ConversationResponse(BaseModel):
    """Schema for conversation data in responses."""
    id: UUID
    title: str | None = None
    created_at: datetime
    updated_at: datetime
    messages: list[MessageResponse] = []

    model_config = {"from_attributes": True}


class ConversationListItem(BaseModel):
    """Schema for conversation list items (without full message history)."""
    id: UUID
    title: str | None = None
    created_at: datetime
    updated_at: datetime
    message_count: int = 0

    model_config = {"from_attributes": True}


# ============================================================================
# Generic Response Schemas
# ============================================================================

class HealthResponse(BaseModel):
    """Schema for health check endpoint response."""
    status: str = Field(default="healthy", description="Service health status")
    version: str = Field(..., description="API version")
    environment: str = Field(..., description="Environment (development/production)")


class ErrorResponse(BaseModel):
    """Schema for error responses."""
    detail: str = Field(..., description="Error message")
    code: str | None = Field(None, description="Error code for programmatic handling")


class StreamChunk(BaseModel):
    """Schema for streaming response chunks."""
    content: str = Field(..., description="Chunk of generated text")
    done: bool = Field(default=False, description="Whether this is the final chunk")
    metadata: dict[str, Any] | None = Field(None, description="Optional metadata")


# ============================================================================
# Query Extraction Schemas
# ============================================================================

class BettingIntent(str, Enum):
    """Types of betting intents extracted from user messages."""
    ANALYZE_SPECIFIC = "analyze_specific_bets"
    REQUEST_SUGGESTIONS = "request_suggestions"
    LOOKUP_ODDS = "lookup_odds"
    GENERAL_QUESTION = "general_question"


class EntityType(str, Enum):
    """Types of entities that can be extracted from betting queries."""
    PLAYER = "player"
    TEAM = "team"
    BET_TYPE = "bet_type"
    LINE = "line"
    SPORT = "sport"


class ExtractedEntity(BaseModel):
    """A single entity extracted from user's message."""
    type: EntityType = Field(..., description="Type of entity")
    value: str = Field(..., description="Entity value")
    sport_inferred: str | None = Field(None, description="Sport inferred from entity")
    confidence: float = Field(default=1.0, ge=0.0, le=1.0, description="Confidence score")


class ApiQueryType(str, Enum):
    """Types of API queries to fetch odds."""
    PLAYER_PROPS = "player_props"
    TEAM_ODDS = "team_odds"
    GAME_ODDS = "game_odds"
    SUGGESTIONS = "suggestions"


class SuggestedApiQuery(BaseModel):
    """A suggested API query to fetch relevant odds data."""
    query_type: ApiQueryType = Field(..., description="Type of query")
    sport: str | None = Field(None, description="Sport key for API")
    team_name: str | None = Field(None, description="Team name to look up")
    player_name: str | None = Field(None, description="Player name to look up")
    market: str | None = Field(None, description="Market type (h2h, spreads, totals, etc)")
    params: dict[str, Any] = Field(default_factory=dict, description="Additional query parameters")


class BettingQuery(BaseModel):
    """Structured betting query extracted from user message."""
    intent: BettingIntent = Field(..., description="Primary intent of the message")
    sport: str | None = Field(None, description="Sport key (e.g., americanfootball_nfl)")
    confidence: float = Field(default=1.0, ge=0.0, le=1.0, description="Overall confidence score")
    entities: list[ExtractedEntity] = Field(default_factory=list, description="Extracted entities")
    suggested_queries: list[SuggestedApiQuery] = Field(default_factory=list, description="API queries to execute")
    reasoning: str | None = Field(None, description="Explanation of extraction (for debugging)")


