"""
Weave Model for parlay analysis.

This module defines the ParlayAnalyzer model that handles the core
logic for analyzing sports betting parlays using LLM inference.
"""

from collections.abc import AsyncGenerator
from typing import Any

import weave
from weave import Model

from .client import openai_client
from .prompts import create_user_prompt, get_system_prompt


class ParlayAnalyzer(Model):
    """
    Weave Model for parlay analysis.

    This model handles the core logic for analyzing sports betting parlays
    using LLM inference through Weave.
    """

    # model_name: str = "meta-llama/Llama-3.3-70B-Instruct"  # W&B Inference model
    model_name: str = "gpt-4o-mini"
    temperature: float = 0.7
    max_tokens: int = 2000

    @weave.op()
    async def predict(self, user_message: str, enriched_odds: dict[str, Any] | None = None) -> str:
        """
        Generate a parlay analysis.

        Args:
            user_message: User's parlay description
            enriched_odds: Optional enriched odds data from The Odds API

        Returns:
            LLM-generated analysis
        """
        messages = [
            {"role": "system", "content": get_system_prompt()},
            {"role": "user", "content": create_user_prompt(user_message, enriched_odds)},
        ]

        # Use OpenAI client with W&B Inference API
        # The @weave.op() decorator will automatically track this
        response = await openai_client.chat.completions.create(
            model=self.model_name,
            messages=messages,
            temperature=self.temperature,
            max_tokens=self.max_tokens,
        )

        return response.choices[0].message.content

    @weave.op()
    async def stream_predict(self, user_message: str, enriched_odds: dict[str, Any] | None = None) -> AsyncGenerator[str, None]:
        """
        Generate a streaming parlay analysis.

        Yields tokens as they are generated for a typewriter effect.

        Args:
            user_message: User's parlay description
            enriched_odds: Optional enriched odds data from The Odds API

        Yields:
            Individual tokens or chunks from the LLM
        """
        messages = [
            {"role": "system", "content": get_system_prompt()},
            {"role": "user", "content": create_user_prompt(user_message, enriched_odds)},
        ]

        # Stream response using OpenAI client with W&B Inference
        # The @weave.op() decorator will automatically track this
        stream = await openai_client.chat.completions.create(
            model=self.model_name,
            messages=messages,
            temperature=self.temperature,
            max_tokens=self.max_tokens,
            stream=True,  # Enable streaming
        )

        async for chunk in stream:
            # Handle chunks that might have empty choices (e.g., the last chunk)
            if chunk.choices and chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content

