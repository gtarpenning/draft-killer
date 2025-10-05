"""
Tests for the autonomous agent service.

Tests the agent's ability to make tool calls and provide responses.
"""

from unittest.mock import AsyncMock, MagicMock

import pytest

from app.services.agent_service import AgentService, get_agent_service
from app.services.odds_api.service import OddsService


@pytest.fixture
def mock_odds_service():
    """Mock odds service for testing."""
    service = MagicMock(spec=OddsService)
    service.get_odds_for_sport.return_value = [
        {
            "home_team": "Kansas City Chiefs",
            "away_team": "Buffalo Bills",
            "commence_time": "2024-01-15T20:00:00Z",
            "bookmakers": [
                {
                    "title": "DraftKings",
                    "markets": [
                        {
                            "key": "h2h",
                            "outcomes": [
                                {"name": "Kansas City Chiefs", "price": -150},
                                {"name": "Buffalo Bills", "price": +130}
                            ]
                        }
                    ]
                }
            ]
        }
    ]
    service.find_game_odds.return_value = None
    service.get_suggestions_for_sport.return_value = {
        "suggestions": [
            {
                "bet_type": "moneyline",
                "team": "Kansas City Chiefs",
                "current_odds": -150,
                "reasoning": "Chiefs are favored"
            }
        ]
    }
    service.get_available_sports.return_value = [
        {"key": "americanfootball_nfl", "title": "NFL", "active": True},
        {"key": "basketball_nba", "title": "NBA", "active": True}
    ]
    return service


@pytest.mark.asyncio
async def test_agent_service_initialization(mock_odds_service):
    """Test that agent service initializes correctly."""
    service = AgentService(mock_odds_service)

    assert service.odds_service == mock_odds_service
    assert service.agent is not None
    assert service.agent.name == "DraftKiller"


@pytest.mark.asyncio
async def test_get_response_basic(mock_odds_service):
    """Test basic response generation."""
    service = AgentService(mock_odds_service)

    # Mock the Runner.run method
    with pytest.MonkeyPatch().context() as m:
        mock_result = MagicMock()
        mock_result.final_output = "Here are the current NFL odds..."

        m.setattr("app.services.agent_service.Runner.run", AsyncMock(return_value=mock_result))

        response = await service.get_response("What are the best NFL bets today?")

        assert response == "Here are the current NFL odds..."


@pytest.mark.asyncio
async def test_stream_response_basic(mock_odds_service):
    """Test streaming response generation."""
    service = AgentService(mock_odds_service)

    # Mock the Runner.run_streamed method
    with pytest.MonkeyPatch().context() as m:
        mock_chunks = [
            MagicMock(content="Here "),
            MagicMock(content="are "),
            MagicMock(content="the "),
            MagicMock(final_output="odds...")
        ]

        async def mock_stream():
            for chunk in mock_chunks:
                yield chunk

        m.setattr("app.services.agent_service.Runner.run_streamed", mock_stream)

        chunks = []
        async for chunk in service.stream_response("Show me NFL odds"):
            chunks.append(chunk)

        assert len(chunks) > 0
        assert "".join(chunks).startswith("Here")


def test_get_agent_service_singleton(mock_odds_service):
    """Test that get_agent_service returns consistent instances."""
    service1 = get_agent_service(mock_odds_service)
    service2 = get_agent_service(mock_odds_service)

    # Should return new instances each time (not singleton)
    assert service1 is not service2
    assert isinstance(service1, AgentService)
    assert isinstance(service2, AgentService)


@pytest.mark.asyncio
async def test_agent_service_error_handling(mock_odds_service):
    """Test error handling in agent service."""
    service = AgentService(mock_odds_service)

    # Mock Runner.run to raise an exception
    with pytest.MonkeyPatch().context() as m:
        m.setattr("app.services.agent_service.Runner.run", AsyncMock(side_effect=Exception("Test error")))

        response = await service.get_response("Test message")

        assert "error" in response.lower()
        assert "test error" in response.lower()


if __name__ == "__main__":
    pytest.main([__file__])
