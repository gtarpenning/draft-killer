# Odds API Service Package

A comprehensive, well-organized service for integrating with The Odds API v4. Designed for efficiency with intelligent caching and minimal API calls.

## Features

- **Complete API Coverage**: All Odds API v4 endpoints
- **Intelligent Caching**: Minimizes API calls and costs
- **Bookmaker Comparison**: Compare odds across sportsbooks
- **Parlay Analysis**: Analyze parlay legs across bookmakers
- **Clean Architecture**: Well-organized, type-safe, and maintainable
- **Backward Compatibility**: Legacy service wrapper included

## Package Structure

```
odds_api/
├── __init__.py          # Package exports
├── client.py            # Base API client with caching
├── service.py           # High-level service with comparisons
├── schemas.py           # Pydantic data models
├── helpers.py           # Convenience functions
├── examples.py          # Usage examples
└── README.md           # This file
```

## Quick Start

### Basic Usage

```python
from app.services.odds_api import OddsService

# Initialize service (automatic caching)
service = OddsService()

# Get active sports (cached 1 hour)
sports = service.get_active_sports()

# Get upcoming NFL games (cached 30 minutes)
games = service.get_upcoming_events('americanfootball_nfl')

# Find games for specific team
chiefs_games = service.find_events_by_team('americanfootball_nfl', 'Chiefs')
```

### Bookmaker Comparison

```python
# Compare moneyline odds across all bookmakers
comparison = service.compare_bookmaker_odds(
    event_id='event_123',
    sport_key='americanfootball_nfl',
    bet_type='h2h',
    bet_details={'bet_type': 'h2h', 'team': 'Chiefs'}
)

print(f"Best odds: {comparison.best_odds}")
print(f"Worst odds: {comparison.worst_odds}")
print(f"Odds range: {comparison.odds_range}")
```

### Parlay Analysis

```python
# Compare parlay leg across bookmakers
leg_comparison = service.compare_parlay_leg_odds(
    "Chiefs -6.5", 
    sport_key='americanfootball_nfl'
)

# Compare entire parlay
from app.services.odds_api.helpers import compare_parlay_across_books

parlay_analysis = compare_parlay_across_books([
    "Chiefs -6.5",
    "Over 47.5", 
    "Cowboys ML"
], sport='americanfootball_nfl')
```

## Helper Functions

Convenient functions for common operations:

```python
from app.services.odds_api.helpers import (
    find_best_moneylines,
    find_best_spreads,
    get_arbitrage_opportunities,
    find_team_odds,
    get_api_usage_summary
)

# Find best moneyline odds
best_moneylines = find_best_moneylines('americanfootball_nfl', limit=5)

# Find arbitrage opportunities
arbitrage = get_arbitrage_opportunities('americanfootball_nfl')

# Analyze specific team
team_odds = find_team_odds("Chiefs", "americanfootball_nfl")
```

## Caching Strategy

The service uses intelligent caching to minimize API calls:

- **Sports List**: Cached for 1 hour (changes rarely)
- **Game Odds**: Cached for 30 minutes
- **Event-specific**: Cached for 30 minutes
- **Request Deduplication**: Prevents duplicate simultaneous requests

## API Usage Monitoring

```python
# Check API usage
usage = service.get_usage_info()
print(f"Requests remaining: {usage['requests_remaining']}")

# Get usage recommendations
from app.services.odds_api.helpers import get_api_usage_summary
summary = get_api_usage_summary()
```

## Data Models

All API responses are validated with Pydantic models:

- `Sport`: Sport information
- `Event`: Game with bookmaker odds
- `Bookmaker`: Sportsbook with markets
- `Market`: Betting market with outcomes
- `Outcome`: Individual bet option
- `BookmakerComparison`: Odds comparison across books
- `ParlayLegComparison`: Parlay leg analysis

## Error Handling

The service includes comprehensive error handling:

- **Rate Limiting**: Automatic 429 handling
- **Quota Exceeded**: Clear error messages
- **Network Issues**: Timeout and retry logic
- **Data Validation**: Pydantic model validation

## Usage

Import the service and helper functions:

```python
from app.services.odds_api.service import OddsService
from app.services.odds_api.helpers import get_odds_service, find_best_moneylines

# Create service instance
service = OddsService()

# Or use the singleton helper
service = get_odds_service()
```

## Cost Optimization

The service is designed to minimize API costs:

1. **Aggressive Caching**: Reduces redundant requests
2. **Request Deduplication**: Prevents simultaneous identical requests
3. **Smart Defaults**: Uses most common parameters
4. **Batch Operations**: Combines related requests when possible

## Examples

See `examples.py` for comprehensive usage examples covering:

- Basic API operations
- Bookmaker comparisons
- Parlay analysis
- Team-specific analysis
- Arbitrage detection
- Usage monitoring

## Migration Guide

### From Legacy Service

1. **Imports**: Change imports to new package
2. **Method Names**: Some methods renamed for clarity
3. **Return Types**: Now returns Pydantic models
4. **Caching**: Automatic, no manual cache management needed

### Key Changes

| Legacy Method | New Method | Notes |
|---------------|------------|-------|
| `get_available_sports()` | `get_active_sports()` | Returns Pydantic models |
| `get_odds_for_sport()` | `get_upcoming_events()` | Better naming |
| `find_game_odds()` | `find_events_by_team()` | Returns list of events |

## Performance Tips

1. **Use Helper Functions**: They're optimized for common operations
2. **Monitor Usage**: Check API quota regularly
3. **Cache Management**: Service handles this automatically
4. **Batch Requests**: Group related operations when possible

## Future Enhancements

- Redis caching for production
- WebSocket support for live odds
- Historical data analysis
- Machine learning predictions
- Advanced arbitrage detection
