"""
Service functions for LLM-based parlay analysis.

This module provides the main service-level functions that other parts
of the application use to interact with the LLM service.
"""

from collections.abc import AsyncGenerator
from typing import Any

from .model import ParlayAnalyzer

# Global analyzer instance
_analyzer = ParlayAnalyzer()


async def analyze_parlay(user_message: str) -> str:
    """
    Analyze a parlay (non-streaming).

    Args:
        user_message: User's parlay description

    Returns:
        Complete analysis text
    """
    return await _analyzer.predict(user_message)


async def stream_parlay_analysis(
    user_message: str,
    enriched_odds: dict[str, Any] | None = None
) -> AsyncGenerator[str, None]:
    """
    Analyze a parlay with streaming response.

    Args:
        user_message: User's parlay description
        enriched_odds: Optional enriched odds data from The Odds API

    Yields:
        Analysis text chunks
    """
    async for chunk in _analyzer.stream_predict(user_message, enriched_odds):
        yield chunk


def get_conversation_context(
    messages: list[dict[str, Any]],
    max_messages: int = 10
) -> str:
    """
    Build conversation context from message history.

    Useful for maintaining context across multiple turns.

    Args:
        messages: List of previous messages
        max_messages: Maximum number of messages to include

    Returns:
        Formatted context string
    """
    recent_messages = messages[-max_messages:] if len(messages) > max_messages else messages

    context_parts = ["Previous conversation:"]
    for msg in recent_messages:
        role = msg.get("role", "unknown")
        content = msg.get("content", "")
        context_parts.append(f"{role.upper()}: {content}")

    return "\n\n".join(context_parts)

