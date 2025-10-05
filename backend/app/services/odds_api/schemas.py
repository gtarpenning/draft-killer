"""
Data models for The Odds API integration.

Comprehensive schemas for all API endpoints with proper typing and validation.
"""

from typing import List, Dict, Any, Optional, Union
from datetime import datetime
from pydantic import BaseModel, Field


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
    point: Optional[float] = None
    description: Optional[str] = None


class Market(BaseModel):
    """Betting market with outcomes."""
    key: str
    last_update: Optional[str] = None
    outcomes: List[Outcome]


class Bookmaker(BaseModel):
    """Bookmaker with their markets."""
    key: str
    title: str
    last_update: str
    markets: List[Market]


class Event(BaseModel):
    """Sports event with bookmaker odds."""
    id: str
    sport_key: str
    sport_title: Optional[str] = None
    commence_time: str
    home_team: str
    away_team: str
    bookmakers: List[Bookmaker]


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
    scores: Optional[List[Score]] = None
    last_update: Optional[str] = None


class HistoricalSnapshot(BaseModel):
    """Historical odds snapshot with timestamp info."""
    timestamp: str
    previous_timestamp: Optional[str] = None
    next_timestamp: Optional[str] = None
    data: Event


class Participant(BaseModel):
    """Event participant information."""
    id: str
    name: str
    name_display: Optional[str] = None


class EventParticipants(BaseModel):
    """Event with participant details."""
    id: str
    sport_key: str
    commence_time: str
    home_team: str
    away_team: str
    participants: List[Participant]


class OddsApiResponse(BaseModel):
    """Base response wrapper with usage tracking."""
    requests_remaining: Optional[int] = None
    requests_used: Optional[int] = None
    requests_last_cost: Optional[int] = None


class BookmakerComparison(BaseModel):
    """Comparison of odds across bookmakers for a single bet."""
    event_id: str
    sport_key: str
    home_team: str
    away_team: str
    commence_time: str
    bet_type: str
    bet_details: Dict[str, Any]
    bookmaker_odds: List[Dict[str, Any]]
    best_odds: Optional[Dict[str, Any]] = None
    worst_odds: Optional[Dict[str, Any]] = None
    odds_range: Optional[float] = None


class ParlayLegComparison(BaseModel):
    """Comparison of parlay leg odds across bookmakers."""
    leg_id: str
    bet_description: str
    event_id: str
    sport_key: str
    home_team: str
    away_team: str
    commence_time: str
    bookmaker_odds: List[Dict[str, Any]]
    best_odds: Optional[Dict[str, Any]] = None
    worst_odds: Optional[Dict[str, Any]] = None
    odds_range: Optional[float] = None


class ApiError(BaseModel):
    """API error response."""
    error: str
    message: str
    status_code: int
