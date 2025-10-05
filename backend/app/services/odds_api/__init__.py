"""
The Odds API Service Package.

Comprehensive integration with The Odds API v4 for sports betting data.
Optimized for minimal API calls with intelligent caching and efficient data structures.
"""

from .client import OddsApiClient
from .schemas import (
    ApiError,
    Bookmaker,
    BookmakerComparison,
    Event,
    EventScore,
    HistoricalSnapshot,
    Market,
    Outcome,
    ParlayLegComparison,
    Sport,
)
from .service import OddsService

__all__ = [
    "OddsApiClient",
    "OddsService",
    "Sport",
    "Event",
    "Bookmaker",
    "Market",
    "Outcome",
    "EventScore",
    "HistoricalSnapshot",
    "BookmakerComparison",
    "ParlayLegComparison",
    "ApiError"
]
