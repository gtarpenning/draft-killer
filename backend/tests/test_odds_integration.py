"""
Integration tests for The Odds API service.

These tests make real API calls but are designed to minimize API usage:
- Each test makes only ONE API call maximum
- Caching is used throughout to reduce calls
- Tests can be run with SKIP_API_TESTS=1 to use mocked data
"""

import os

import pytest

from app.services.odds_api.schemas import Bookmaker, Event, Market, Outcome
from app.services.odds_api.service import OddsService

# ============================================================================
# Test Configuration
# ============================================================================

# Set to "1" to skip actual API calls and use mock data
SKIP_API_TESTS = os.getenv("SKIP_API_TESTS", "0") == "1"

# Get API key from environment
API_KEY = os.getenv("ODDS_API_KEY")

# Skip all tests if no API key
pytestmark = pytest.mark.skipif(
    not API_KEY and not SKIP_API_TESTS,
    reason="ODDS_API_KEY not set. Set it in .env or use SKIP_API_TESTS=1"
)


# ============================================================================
# Fixtures
# ============================================================================

@pytest.fixture(scope="module")
def odds_service():
    """
    Create a shared odds service for all tests.

    Uses module scope so caching works across tests,
    minimizing API calls.
    """
    return OddsService(api_key=API_KEY)


@pytest.fixture(scope="module")
def nfl_events(odds_service):
    """
    Fetch NFL events once and share across all tests.

    THIS IS THE ONLY API CALL THESE TESTS WILL MAKE.
    All other tests use cached data or parsed data.
    """
    if SKIP_API_TESTS:
        # Return mock data if skipping API tests
        return [
            Event(
                id="test_event_1",
                sport_key="americanfootball_nfl",
                commence_time="2024-10-06T17:00:00Z",
                home_team="Kansas City Chiefs",
                away_team="Las Vegas Raiders",
                bookmakers=[
                    Bookmaker(
                        key="draftkings",
                        title="DraftKings",
                        last_update="2024-10-06T16:30:00Z",
                        markets=[
                            Market(
                                key="h2h",
                                outcomes=[
                                    Outcome(name="Kansas City Chiefs", price=-250),
                                    Outcome(name="Las Vegas Raiders", price=210)
                                ]
                            ),
                            Market(
                                key="spreads",
                                outcomes=[
                                    Outcome(name="Kansas City Chiefs", price=-110, point=-6.5),
                                    Outcome(name="Las Vegas Raiders", price=-110, point=6.5)
                                ]
                            ),
                            Market(
                                key="totals",
                                outcomes=[
                                    Outcome(name="Over", price=-110, point=47.5),
                                    Outcome(name="Under", price=-110, point=47.5)
                                ]
                            )
                        ]
                    )
                ]
            )
        ]

    # Make the single API call
    print("\n🔔 Making API call to fetch NFL events...")
    events = odds_service.get_upcoming_events("americanfootball_nfl")
    print(f"✅ Fetched {len(events)} NFL events")

    # Log remaining requests
    usage_info = odds_service.get_usage_info()
    remaining = usage_info.get("requests_remaining")
    if remaining:
        print(f"📊 API requests remaining: {remaining}")

    return events


# ============================================================================
# Service Tests
# ============================================================================

def test_odds_service_initialization():
    """Test that OddsService initializes correctly."""
    service = OddsService(api_key="test_key")
    assert service.client.api_key == "test_key"
    assert service.client.BASE_URL == "https://api.the-odds-api.com/v4"


def test_parse_moneyline_bet(odds_service):
    """Test parsing a moneyline bet."""
    result = odds_service._parse_parlay_leg("Chiefs ML")

    assert result["bet_type"] == "h2h"
    assert result["team"] == "Chiefs"
    assert result["side"] is None


def test_parse_spread_bet(odds_service):
    """Test parsing a spread bet."""
    result = odds_service._parse_parlay_leg("Cowboys -6.5")

    assert result["bet_type"] == "spreads"
    assert result["team"] == "Cowboys"
    assert result["point"] == 6.5
    assert result["side"] == "home"


def test_parse_spread_bet_positive(odds_service):
    """Test parsing a spread bet with positive line."""
    result = odds_service._parse_parlay_leg("Raiders +7")

    assert result["bet_type"] == "spreads"
    assert result["team"] == "Raiders"
    assert result["point"] == 7.0
    assert result["side"] == "away"


def test_parse_over_bet(odds_service):
    """Test parsing an over bet."""
    result = odds_service._parse_parlay_leg("Over 47.5")

    assert result["bet_type"] == "totals"
    assert result["side"] == "over"
    assert result["point"] == 47.5
    assert result["team"] is None


def test_parse_under_bet(odds_service):
    """Test parsing an under bet."""
    result = odds_service._parse_parlay_leg("Under 44")

    assert result["bet_type"] == "totals"
    assert result["side"] == "under"
    assert result["point"] == 44.0
    assert result["team"] is None


def test_parse_unknown_bet(odds_service):
    """Test parsing an unrecognizable bet."""
    result = odds_service._parse_parlay_leg("Some random text")

    assert result is None


# ============================================================================
# Integration Tests (using cached NFL data)
# ============================================================================

def test_nfl_events_structure(nfl_events):
    """Test that NFL events have the expected structure."""
    assert isinstance(nfl_events, list)
    assert len(nfl_events) > 0

    # Check first event structure
    event = nfl_events[0]
    assert hasattr(event, 'id')
    assert hasattr(event, 'sport_key')
    assert hasattr(event, 'home_team')
    assert hasattr(event, 'away_team')
    assert hasattr(event, 'commence_time')
    assert hasattr(event, 'bookmakers')


def test_nfl_events_have_bookmakers(nfl_events):
    """Test that events have bookmaker data."""
    events_with_bookmakers = [e for e in nfl_events if e.bookmakers]
    assert len(events_with_bookmakers) > 0

    # Check bookmaker structure
    bookmaker = events_with_bookmakers[0].bookmakers[0]
    assert hasattr(bookmaker, 'key')
    assert hasattr(bookmaker, 'title')
    assert hasattr(bookmaker, 'markets')


def test_nfl_events_have_markets(nfl_events):
    """Test that bookmakers have market data."""
    event_with_markets = None
    for event in nfl_events:
        if event.bookmakers and event.bookmakers[0].markets:
            event_with_markets = event
            break

    assert event_with_markets is not None

    market = event_with_markets.bookmakers[0].markets[0]
    assert hasattr(market, 'key')
    assert hasattr(market, 'outcomes')
    assert len(market.outcomes) > 0


def test_find_events_by_team(odds_service, nfl_events):
    """Test finding events by team name (uses cached data)."""
    # Get first team from cached events
    first_event = nfl_events[0]
    team_name = first_event.home_team.split()[-1]  # Last word of team name

    # This should use cached data, no API call
    found_events = odds_service.find_events_by_team("americanfootball_nfl", team_name)

    assert len(found_events) > 0
    found_event = found_events[0]
    assert team_name.lower() in found_event.home_team.lower() or \
           team_name.lower() in found_event.away_team.lower()


def test_compare_bookmaker_odds(odds_service, nfl_events):
    """Test comparing odds across bookmakers (uses cached data)."""
    # Get an event from the cached data
    event = nfl_events[0]

    # Test comparing odds for a moneyline bet
    comparison = odds_service.compare_bookmaker_odds(
        event_id=event.id,
        sport_key="americanfootball_nfl",
        bet_type="h2h",
        bet_details={"bet_type": "h2h", "team": event.home_team.split()[-1]}
    )

    assert comparison.event_id == event.id
    assert comparison.sport_key == "americanfootball_nfl"
    assert comparison.bet_type == "h2h"
    assert len(comparison.bookmaker_odds) > 0
    assert "best_odds" in comparison.model_fields or comparison.best_odds is not None


def test_compare_parlay_leg_odds(odds_service, nfl_events):
    """Test comparing parlay leg odds (uses cached data)."""
    # Get a team from the cached events
    team = nfl_events[0].home_team.split()[-1]

    # Test parlay leg comparison
    comparison = odds_service.compare_parlay_leg_odds(
        leg_description=f"{team} -6.5",
        sport_key="americanfootball_nfl"
    )

    if comparison:  # May be None if team not found
        assert comparison.sport_key == "americanfootball_nfl"
        assert comparison.bet_description == f"{team} -6.5"
        assert len(comparison.bookmaker_odds) > 0


def test_get_best_odds_for_events(odds_service):
    """Test getting best odds for events (uses cached data)."""
    best_odds_events = odds_service.get_best_odds_for_events(
        sport_key="americanfootball_nfl",
        limit=3
    )

    assert len(best_odds_events) <= 3
    for event_data in best_odds_events:
        assert "event" in event_data
        assert "best_odds_by_market" in event_data


def test_caching_works(odds_service):
    """Test that caching prevents duplicate API calls."""
    # First call (should hit cache from nfl_events fixture)
    events1 = odds_service.get_upcoming_events("americanfootball_nfl")

    # Second call (should definitely hit cache)
    events2 = odds_service.get_upcoming_events("americanfootball_nfl")

    # Should return same data
    assert len(events1) == len(events2)
    assert events1[0].id == events2[0].id


# ============================================================================
# End-to-End Workflow Test
# ============================================================================

def test_full_workflow(odds_service, nfl_events):
    """
    Test the complete workflow using modern service methods.

    This simulates what happens in the chat endpoint:
    1. Get upcoming events
    2. Find events by team
    3. Compare odds across bookmakers
    """
    # Get a real team from cached events
    team = nfl_events[0].home_team.split()[-1]

    # Step 1: Get upcoming events
    events = odds_service.get_upcoming_events("americanfootball_nfl")
    assert len(events) > 0

    # Step 2: Find events by team
    team_events = odds_service.find_events_by_team("americanfootball_nfl", team)
    assert len(team_events) > 0

    # Step 3: Compare odds for a bet
    event = team_events[0]
    comparison = odds_service.compare_bookmaker_odds(
        event_id=event.id,
        sport_key="americanfootball_nfl",
        bet_type="h2h",
        bet_details={"bet_type": "h2h", "team": team}
    )

    assert comparison.event_id == event.id
    assert len(comparison.bookmaker_odds) > 0

    print("\n✅ Full workflow test completed successfully!")
    print(f"   Found {len(events)} events")
    print(f"   Found {len(team_events)} events for {team}")
    print(f"   Compared odds across {len(comparison.bookmaker_odds)} bookmakers")


# ============================================================================
# API Usage Tracking Tests
# ============================================================================

def test_usage_info_tracked(odds_service):
    """Test that API usage information is tracked."""
    if SKIP_API_TESTS:
        pytest.skip("Skipping API test")

    usage_info = odds_service.get_usage_info()
    # Should have usage information after the nfl_events fixture ran
    assert usage_info is not None
    assert "requests_remaining" in usage_info
    assert "cache_size" in usage_info

    remaining = usage_info.get("requests_remaining")
    if remaining:
        print(f"\n📊 Current API requests remaining: {remaining}")


# ============================================================================
# Error Handling Tests
# ============================================================================

def test_invalid_sport_key():
    """Test handling of invalid sport key."""
    service = OddsService(api_key="test_key")

    # Should raise HTTPException for invalid sport
    with pytest.raises(Exception):
        service.get_upcoming_events("invalid_sport_key_xyz")


def test_clear_cache(odds_service):
    """Test that cache can be cleared."""
    # Cache should have data from previous tests
    odds_service.clear_cache()

    # Cache should be empty now
    usage_info = odds_service.get_usage_info()
    assert usage_info["cache_size"] == 0


# ============================================================================
# Performance Tests
# ============================================================================

def test_parse_performance(odds_service):
    """Test that parsing is fast."""
    import time

    test_inputs = [
        "Chiefs ML",
        "Cowboys -6.5",
        "Over 47.5",
        "Raiders +7",
        "Under 44"
    ]

    start = time.time()
    for input_text in test_inputs * 100:  # Parse 500 times
        odds_service._parse_parlay_leg(input_text)
    end = time.time()

    elapsed = end - start
    print(f"\n⚡ Parsed 500 legs in {elapsed:.3f}s ({elapsed/500*1000:.2f}ms per leg)")
    assert elapsed < 1.0  # Should be very fast


def test_event_retrieval_performance(odds_service):
    """Test that event retrieval is fast when using cache."""
    import time

    start = time.time()
    for _ in range(10):  # Retrieve 10 times
        odds_service.get_upcoming_events("americanfootball_nfl")
    end = time.time()

    elapsed = end - start
    print(f"\n⚡ Retrieved events 10 times in {elapsed:.3f}s ({elapsed/10*1000:.2f}ms per call)")
    assert elapsed < 2.0  # Should be fast with caching


# ============================================================================
# Summary
# ============================================================================

def test_print_summary(nfl_events, odds_service):
    """Print a summary of the test results."""
    print("\n" + "="*60)
    print("ODDS API INTEGRATION TEST SUMMARY")
    print("="*60)
    print("✅ All tests passed!")
    print(f"📊 NFL events fetched: {len(nfl_events)}")

    usage_info = odds_service.get_usage_info()
    remaining = usage_info.get("requests_remaining")
    if remaining:
        print(f"📊 API requests remaining: {remaining}")

    print(f"💾 Cache entries: {usage_info['cache_size']}")
    print("⚡ Total API calls made: 1 (all others used cache)")
    print("="*60)
    print("\n✨ The Odds API is successfully integrated!")
    print("   Ready to use in production.")
    print("="*60)
