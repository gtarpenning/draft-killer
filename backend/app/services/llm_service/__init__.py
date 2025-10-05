"""
LLM service for chat completions using Weights & Biases Weave.

Provides an abstraction layer for LLM interactions, making it easy
to generate responses for parlay analysis.

This package is organized into:
- prompts/: Text files containing system and user prompt templates
- client.py: OpenAI client initialization and Weave setup
- prompts.py: Prompt loading and formatting utilities
- model.py: ParlayAnalyzer Weave model
- service.py: High-level service functions
"""

# Export public API
from .model import ParlayAnalyzer
from .prompts import (
    SYSTEM_PROMPT,
    create_user_prompt,
    get_system_prompt,
)
from .service import (
    analyze_parlay,
    get_conversation_context,
    stream_parlay_analysis,
)

__all__ = [
    "ParlayAnalyzer",
    "analyze_parlay",
    "stream_parlay_analysis",
    "get_conversation_context",
    "SYSTEM_PROMPT",
    "create_user_prompt",
    "get_system_prompt",
]

