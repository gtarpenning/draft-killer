"""
Tests for the query extraction service.

Tests the LLM-based extraction of betting intent from natural language.
"""

import pytest
from unittest.mock import Mock, patch, AsyncMock
from app.services.query_extraction_service import QueryExtractionService
from app.models.schemas import BettingIntent, EntityType


@pytest.fixture
def mock_openai_client():
    """Mock OpenAI client for testing."""
    with patch("openai.OpenAI") as mock:
        yield mock


@pytest.fixture
def extraction_service(mock_openai_client):
    """Create a query extraction service with mocked OpenAI."""
    with patch.dict('os.environ', {'OPENAI_API_KEY': 'test-key'}):
        return QueryExtractionService(api_key="test-key")


class TestQueryExtractionService:
    """Test suite for QueryExtractionService."""
    
    @pytest.mark.asyncio
    async def test_extract_player_mention(self, extraction_service, mock_openai_client):
        """Test extracting a player mention from natural language."""
        # Mock OpenAI response
        mock_response = Mock()
        mock_response.choices = [
            Mock(message=Mock(content='{"intent": "lookup_odds", "sport": "baseball_mlb", '
                             '"confidence": 0.95, "entities": [{"type": "player", "value": "Aaron Judge", '
                             '"sport_inferred": "baseball_mlb", "confidence": 1.0}], '
                             '"suggested_queries": [{"query_type": "team_odds", "sport": "baseball_mlb", '
                             '"team_name": "New York Yankees"}], "reasoning": "User wants odds for Aaron Judge"}'))
        ]
        extraction_service.client.chat.completions.create = Mock(return_value=mock_response)
        
        # Test extraction
        result = await extraction_service.extract_betting_intent("I want to bet on Aaron Judge")
        
        assert result.intent == BettingIntent.LOOKUP_ODDS
        assert result.sport == "baseball_mlb"
        assert len(result.entities) == 1
        assert result.entities[0].type == EntityType.PLAYER
        assert result.entities[0].value == "Aaron Judge"
    
    @pytest.mark.asyncio
    async def test_extract_suggestion_request(self, extraction_service, mock_openai_client):
        """Test extracting a parlay suggestion request."""
        # Mock OpenAI response
        mock_response = Mock()
        mock_response.choices = [
            Mock(message=Mock(content='{"intent": "request_suggestions", "sport": "americanfootball_nfl", '
                             '"confidence": 0.90, "entities": [], '
                             '"suggested_queries": [{"query_type": "suggestions", "sport": "americanfootball_nfl", '
                             '"params": {"num_legs": 3}}], "reasoning": "User wants parlay suggestions"}'))
        ]
        extraction_service.client.chat.completions.create = Mock(return_value=mock_response)
        
        # Test extraction
        result = await extraction_service.extract_betting_intent("what's a good parlay?")
        
        assert result.intent == BettingIntent.REQUEST_SUGGESTIONS
        assert result.sport == "americanfootball_nfl"
        assert len(result.suggested_queries) == 1
        assert result.suggested_queries[0].query_type.value == "suggestions"
    
    @pytest.mark.asyncio
    async def test_extract_specific_bets(self, extraction_service, mock_openai_client):
        """Test extracting specific bet analysis request."""
        # Mock OpenAI response
        mock_response = Mock()
        mock_response.choices = [
            Mock(message=Mock(content='{"intent": "analyze_specific_bets", "sport": "americanfootball_nfl", '
                             '"confidence": 0.99, "entities": [{"type": "team", "value": "Chiefs", '
                             '"sport_inferred": "americanfootball_nfl", "confidence": 1.0}, '
                             '{"type": "bet_type", "value": "spread", "confidence": 1.0}, '
                             '{"type": "line", "value": "-6.5", "confidence": 1.0}], '
                             '"suggested_queries": [{"query_type": "team_odds", "sport": "americanfootball_nfl", '
                             '"team_name": "Chiefs", "market": "spreads"}], '
                             '"reasoning": "User wants to analyze specific bets"}'))
        ]
        extraction_service.client.chat.completions.create = Mock(return_value=mock_response)
        
        # Test extraction
        result = await extraction_service.extract_betting_intent("Chiefs -6.5, Cowboys ML")
        
        assert result.intent == BettingIntent.ANALYZE_SPECIFIC
        assert result.sport == "americanfootball_nfl"
        assert len(result.entities) == 3
        assert any(e.type == EntityType.TEAM for e in result.entities)
        assert any(e.type == EntityType.BET_TYPE for e in result.entities)
        assert any(e.type == EntityType.LINE for e in result.entities)
    
    @pytest.mark.asyncio
    async def test_fallback_on_error(self, extraction_service, mock_openai_client):
        """Test fallback behavior when OpenAI fails."""
        # Mock OpenAI to raise an error
        extraction_service.client.chat.completions.create = Mock(side_effect=Exception("API Error"))
        
        # Test extraction - should not raise, should return fallback
        result = await extraction_service.extract_betting_intent("what's a good parlay?")
        
        # Should have a fallback query
        assert result.intent in [BettingIntent.REQUEST_SUGGESTIONS, BettingIntent.GENERAL_QUESTION]
        assert result.confidence < 1.0  # Fallback should have lower confidence
    
    def test_sport_detection_from_text(self, extraction_service):
        """Test sport detection using keyword matching."""
        assert extraction_service._detect_sport_from_text("Chiefs game") == "americanfootball_nfl"
        assert extraction_service._detect_sport_from_text("Aaron Judge") == "baseball_mlb"
        assert extraction_service._detect_sport_from_text("Lakers tonight") == "basketball_nba"
        assert extraction_service._detect_sport_from_text("NFL parlay") == "americanfootball_nfl"
        assert extraction_service._detect_sport_from_text("baseball odds") == "baseball_mlb"
    
    def test_sport_mappings(self, extraction_service):
        """Test that sport mappings are correctly built."""
        assert "chiefs" in extraction_service._sport_mappings
        assert extraction_service._sport_mappings["chiefs"] == "americanfootball_nfl"
        assert "aaron judge" in extraction_service._sport_mappings
        assert extraction_service._sport_mappings["aaron judge"] == "baseball_mlb"


class TestFallbackParsing:
    """Test the fallback parsing when LLM extraction fails."""
    
    @pytest.mark.asyncio
    async def test_fallback_suggestion_detection(self, extraction_service):
        """Test that fallback correctly identifies suggestion requests."""
        extraction_service.client.chat.completions.create = Mock(side_effect=Exception("Error"))
        
        result = await extraction_service.extract_betting_intent("suggest a good parlay")
        
        assert result.intent == BettingIntent.REQUEST_SUGGESTIONS
    
    @pytest.mark.asyncio
    async def test_fallback_odds_lookup(self, extraction_service):
        """Test that fallback correctly identifies odds lookup requests."""
        extraction_service.client.chat.completions.create = Mock(side_effect=Exception("Error"))
        
        result = await extraction_service.extract_betting_intent("what are the odds for tonight's game?")
        
        assert result.intent == BettingIntent.LOOKUP_ODDS
    
    @pytest.mark.asyncio
    async def test_fallback_specific_bets(self, extraction_service):
        """Test that fallback correctly identifies specific bet analysis."""
        extraction_service.client.chat.completions.create = Mock(side_effect=Exception("Error"))
        
        result = await extraction_service.extract_betting_intent("Chiefs -6.5, Cowboys ML, over 47")
        
        assert result.intent == BettingIntent.ANALYZE_SPECIFIC

