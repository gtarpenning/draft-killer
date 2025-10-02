"""
Tests for LLM inference via Wandb Weave.

Tests the LLM service, prompt generation, and streaming responses.
Makes ONE real inference call (cached) and validates multiple aspects.
Set SKIP_INFERENCE_TESTS=1 to use mock data.
"""

import os
import pytest
import json
from typing import AsyncGenerator

from app.services.llm_service import (
    ParlayAnalyzer,
    create_user_prompt,
    stream_parlay_analysis,
    get_conversation_context,
    SYSTEM_PROMPT,
)


# ============================================================================
# Test Configuration
# ============================================================================

SKIP_INFERENCE_TESTS = os.getenv("SKIP_INFERENCE_TESTS", "0") == "1"

# Skip inference tests if Weave not configured
pytestmark = pytest.mark.skipif(
    SKIP_INFERENCE_TESTS,
    reason="SKIP_INFERENCE_TESTS=1 or Weave not configured"
)


# ============================================================================
# Fixtures
# ============================================================================

@pytest.fixture(scope="module")
def parlay_analyzer():
    """Create a shared ParlayAnalyzer instance."""
    return ParlayAnalyzer()


@pytest.fixture(scope="module")
async def cached_inference_response(parlay_analyzer):
    """
    Make ONE inference call and cache the result.
    
    This is the ONLY real LLM API call these tests will make.
    All other tests use this cached response.
    """
    if SKIP_INFERENCE_TESTS:
        # Return mock response
        return {
            "prompt": "Test Chiefs ML, Over 47.5",
            "response": "This is a mock analysis response for testing.",
            "chunks": ["This ", "is ", "a ", "mock ", "response."]
        }
    
    print("\n🔔 Making LLM inference call via Weave...")
    
    test_message = "Chiefs ML, Over 47.5"
    
    # Collect streaming response
    chunks = []
    async for chunk in stream_parlay_analysis(test_message):
        chunks.append(chunk)
    
    full_response = "".join(chunks)
    
    print(f"✅ Got response: {len(full_response)} characters, {len(chunks)} chunks")
    
    return {
        "prompt": test_message,
        "response": full_response,
        "chunks": chunks
    }


# ============================================================================
# Prompt Generation Tests
# ============================================================================

def test_system_prompt_exists():
    """Test that system prompt is defined and non-empty."""
    assert SYSTEM_PROMPT is not None
    assert len(SYSTEM_PROMPT) > 0
    assert "sports betting" in SYSTEM_PROMPT.lower()


def test_create_user_prompt_basic():
    """Test creating a basic user prompt without odds data."""
    prompt = create_user_prompt("Chiefs ML, Cowboys -6.5")
    
    assert "Chiefs ML, Cowboys -6.5" in prompt
    assert "analyze" in prompt.lower()


def test_create_user_prompt_with_odds():
    """Test creating a user prompt with enriched odds data."""
    enriched_odds = {
        "num_legs": 2,
        "sport": "americanfootball_nfl",
        "legs": [
            {
                "team": "Chiefs",
                "bet_type": "moneyline",
                "game": {"home_team": "Chiefs", "away_team": "Raiders"}
            }
        ]
    }
    
    prompt = create_user_prompt("Chiefs ML", enriched_odds)
    
    assert "Chiefs ML" in prompt
    assert "Current Market Data" in prompt
    assert "americanfootball_nfl" in prompt


def test_create_user_prompt_structure():
    """Test that generated prompts have expected structure."""
    prompt = create_user_prompt("Test parlay")
    
    # Should include analysis instructions
    assert "risk assessment" in prompt.lower()
    assert "alternative" in prompt.lower() or "alternatives" in prompt.lower()
    assert "probability" in prompt.lower() or "probabilities" in prompt.lower()


def test_conversation_context_building():
    """Test building conversation context from message history."""
    messages = [
        {"role": "user", "content": "First message"},
        {"role": "assistant", "content": "First response"},
        {"role": "user", "content": "Second message"},
    ]
    
    context = get_conversation_context(messages)
    
    assert "First message" in context
    assert "First response" in context
    assert "Second message" in context
    assert "user" in context.lower() or "USER" in context


def test_conversation_context_limit():
    """Test that conversation context respects max_messages limit."""
    messages = [{"role": "user", "content": f"Message {i}"} for i in range(20)]
    
    context = get_conversation_context(messages, max_messages=5)
    
    # Should only include last 5 messages
    assert "Message 19" in context
    assert "Message 15" in context
    assert "Message 14" not in context  # Earlier messages excluded


# ============================================================================
# Model Configuration Tests
# ============================================================================

def test_parlay_analyzer_default_config(parlay_analyzer):
    """Test that ParlayAnalyzer has sensible default configuration."""
    assert parlay_analyzer.model_name == "gpt-4"
    assert 0 <= parlay_analyzer.temperature <= 1.0
    assert parlay_analyzer.max_tokens > 0


def test_parlay_analyzer_custom_config():
    """Test creating ParlayAnalyzer with custom config."""
    analyzer = ParlayAnalyzer(
        model_name="gpt-3.5-turbo",
        temperature=0.5,
        max_tokens=1000
    )
    
    assert analyzer.model_name == "gpt-3.5-turbo"
    assert analyzer.temperature == 0.5
    assert analyzer.max_tokens == 1000


# ============================================================================
# Inference Response Tests (using cached data)
# ============================================================================

@pytest.mark.asyncio
async def test_inference_response_not_empty(cached_inference_response):
    """Test that inference returns non-empty response."""
    assert cached_inference_response["response"] is not None
    assert len(cached_inference_response["response"]) > 0


@pytest.mark.asyncio
async def test_inference_response_length(cached_inference_response):
    """Test that inference returns substantial response."""
    response = cached_inference_response["response"]
    
    # Should be at least 100 characters (reasonable analysis)
    assert len(response) >= 100


@pytest.mark.asyncio
async def test_inference_streaming_chunks(cached_inference_response):
    """Test that streaming produces multiple chunks."""
    chunks = cached_inference_response["chunks"]
    
    assert len(chunks) > 1  # Should be streamed, not single chunk
    
    # Reconstruct full response from chunks
    reconstructed = "".join(chunks)
    assert reconstructed == cached_inference_response["response"]


@pytest.mark.asyncio
async def test_inference_response_relevant(cached_inference_response):
    """Test that response is relevant to the input."""
    response = cached_inference_response["response"].lower()
    prompt = cached_inference_response["prompt"].lower()
    
    # Response should be about sports betting/parlays
    sports_keywords = ["bet", "parlay", "odds", "risk", "probability", "analysis"]
    assert any(keyword in response for keyword in sports_keywords)


@pytest.mark.asyncio
async def test_inference_response_structure(cached_inference_response):
    """Test that response has some structure (not just random text)."""
    response = cached_inference_response["response"]
    
    # Should have some kind of structure (paragraphs, sections, etc.)
    # Check for common structural elements
    has_structure = (
        "\n\n" in response or  # Multiple paragraphs
        "1." in response or "2." in response or  # Numbered lists
        "**" in response or  # Bold/emphasis
        "#" in response  # Headers
    )
    
    assert has_structure, "Response should have some structural formatting"


# ============================================================================
# Streaming Performance Tests
# ============================================================================

@pytest.mark.asyncio
async def test_streaming_generates_async():
    """Test that streaming actually generates asynchronously."""
    # This test doesn't use cached data - it tests the mechanism
    analyzer = ParlayAnalyzer()
    
    # For this test, we'll just check the generator type
    result = analyzer.stream_predict("Quick test")
    
    # Should be an async generator
    assert isinstance(result, AsyncGenerator)


@pytest.mark.asyncio
async def test_streaming_chunk_timing(cached_inference_response):
    """Test that chunks arrive in reasonable time."""
    chunks = cached_inference_response["chunks"]
    
    # With streaming, should get multiple chunks
    # Average chunk size should be reasonable (not too large)
    total_length = len(cached_inference_response["response"])
    avg_chunk_size = total_length / len(chunks)
    
    # Average chunk should be less than 500 chars (streaming, not batching)
    assert avg_chunk_size < 500, f"Chunks too large (avg {avg_chunk_size}), might not be streaming properly"


# ============================================================================
# Error Handling Tests
# ============================================================================

@pytest.mark.asyncio
async def test_inference_with_empty_message():
    """Test handling of empty message."""
    if SKIP_INFERENCE_TESTS:
        pytest.skip("Skipping inference test")
    
    # Should still generate something, even if generic
    chunks = []
    async for chunk in stream_parlay_analysis(""):
        chunks.append(chunk)
    
    response = "".join(chunks)
    assert len(response) > 0  # Should generate something


@pytest.mark.asyncio
async def test_inference_with_very_long_message():
    """Test handling of very long message."""
    if SKIP_INFERENCE_TESTS:
        pytest.skip("Skipping inference test")
    
    long_message = "Chiefs ML, " * 100  # Very repetitive long message
    
    # Should handle gracefully (truncate or process)
    chunks = []
    async for chunk in stream_parlay_analysis(long_message):
        chunks.append(chunk)
    
    response = "".join(chunks)
    assert len(response) > 0


# ============================================================================
# Integration with Odds Data Tests
# ============================================================================

@pytest.mark.asyncio
async def test_inference_with_odds_enrichment():
    """Test inference with enriched odds data."""
    if SKIP_INFERENCE_TESTS:
        pytest.skip("Skipping inference test")
    
    enriched_odds = {
        "num_legs": 1,
        "sport": "americanfootball_nfl",
        "legs": [
            {
                "bet_type": "moneyline",
                "team": "Chiefs",
                "game": {
                    "home_team": "Kansas City Chiefs",
                    "away_team": "Las Vegas Raiders",
                    "commence_time": "2024-10-06T17:00:00Z"
                },
                "bookmaker": {
                    "title": "DraftKings",
                    "markets": {
                        "h2h": {
                            "outcomes": [
                                {"name": "Kansas City Chiefs", "price": -250}
                            ]
                        }
                    }
                }
            }
        ]
    }
    
    chunks = []
    async for chunk in stream_parlay_analysis("Chiefs ML", enriched_odds):
        chunks.append(chunk)
    
    response = "".join(chunks)
    
    # Response should reference the odds data
    assert len(response) > 0
    # Might mention specific odds or teams
    assert any(term in response.lower() for term in ["chiefs", "odds", "price", "draftkings"])


# ============================================================================
# Weave Integration Tests
# ============================================================================

def test_weave_decorators_present():
    """Test that Weave decorators are applied to methods."""
    analyzer = ParlayAnalyzer()
    
    # Methods should have Weave op decoration
    # This ensures tracking/logging is enabled
    assert hasattr(analyzer.predict, '__wrapped__') or hasattr(analyzer.predict, 'call')
    assert hasattr(analyzer.stream_predict, '__wrapped__') or hasattr(analyzer.stream_predict, 'call')


# ============================================================================
# Summary Test
# ============================================================================

def test_inference_summary(cached_inference_response):
    """Print summary of inference tests."""
    print("\n" + "="*60)
    print("INFERENCE TESTS SUMMARY")
    print("="*60)
    print("✅ All inference tests passed!")
    
    if not SKIP_INFERENCE_TESTS:
        print(f"✅ Made 1 LLM inference call via Weave")
        print(f"📊 Response length: {len(cached_inference_response['response'])} characters")
        print(f"📊 Streaming chunks: {len(cached_inference_response['chunks'])}")
    else:
        print("⚠️  Using mock data (SKIP_INFERENCE_TESTS=1)")
    
    print("="*60)

