"""
Data models for The Odds API integration.

Comprehensive schemas for all API endpoints with proper typing and validation.
"""

from typing import Any

from pydantic import BaseModel


class Sport(BaseModel):
    """Sport information from /sports endpoint."""
    key: str
    group: str
    title: str
    description: str
    active: bool
    has_outrights: bool


class Outcome(BaseModel):
    """Betting outcome with odds and optional point spread."""
    name: str
    price: float
    point: float | None = None
    description: str | None = None


class Market(BaseModel):
    """Betting market with outcomes."""
    key: str
    last_update: str | None = None
    outcomes: list[Outcome]


class Bookmaker(BaseModel):
    """Bookmaker with their markets."""
    key: str
    title: str
    last_update: str
    markets: list[Market]


class Event(BaseModel):
    """Sports event with bookmaker odds."""
    id: str
    sport_key: str
    sport_title: str | None = None
    commence_time: str
    home_team: str
    away_team: str
    bookmakers: list[Bookmaker]


class Score(BaseModel):
    """Live or final score for an event."""
    name: str
    score: int


class EventScore(BaseModel):
    """Event with live/final scores."""
    id: str
    sport_key: str
    commence_time: str
    completed: bool
    home_team: str
    away_team: str
    scores: list[Score] | None = None
    last_update: str | None = None


class HistoricalSnapshot(BaseModel):
    """Historical odds snapshot with timestamp info."""
    timestamp: str
    previous_timestamp: str | None = None
    next_timestamp: str | None = None
    data: Event


class Participant(BaseModel):
    """Event participant information."""
    id: str
    name: str
    name_display: str | None = None


class EventParticipants(BaseModel):
    """Event with participant details."""
    id: str
    sport_key: str
    commence_time: str
    home_team: str
    away_team: str
    participants: list[Participant]


class OddsApiResponse(BaseModel):
    """Base response wrapper with usage tracking."""
    requests_remaining: int | None = None
    requests_used: int | None = None
    requests_last_cost: int | None = None


class BookmakerComparison(BaseModel):
    """Comparison of odds across bookmakers for a single bet."""
    event_id: str
    sport_key: str
    home_team: str
    away_team: str
    commence_time: str
    bet_type: str
    bet_details: dict[str, Any]
    bookmaker_odds: list[dict[str, Any]]
    best_odds: dict[str, Any] | None = None
    worst_odds: dict[str, Any] | None = None
    odds_range: float | None = None


class ParlayLegComparison(BaseModel):
    """Comparison of parlay leg odds across bookmakers."""
    leg_id: str
    bet_description: str
    event_id: str
    sport_key: str
    home_team: str
    away_team: str
    commence_time: str
    bookmaker_odds: list[dict[str, Any]]
    best_odds: dict[str, Any] | None = None
    worst_odds: dict[str, Any] | None = None
    odds_range: float | None = None


class ApiError(BaseModel):
    """API error response."""
    error: str
    message: str
    status_code: int
