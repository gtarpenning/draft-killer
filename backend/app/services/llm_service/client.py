"""
LLM client initialization with automatic provider switching.

This module handles the setup of the AsyncOpenAI client configured
to use either OpenAI or W&B Inference API based on environment configuration.
"""

# Initialize Weave for tracking/observability using centralized configuration
import os

from openai import AsyncOpenAI

from app.core.weave_config import init_weave_for_production, init_weave_for_tests
from app.services.llm_service.provider_config import (
    get_current_api_key,
    get_current_base_url,
    get_current_provider_config,
)

if os.getenv("WEAVE_TEST_MODE") == "true":
    init_weave_for_tests()
else:
    init_weave_for_production()

# Get current provider configuration
provider_config = get_current_provider_config()
base_url = get_current_base_url()
api_key = get_current_api_key()

# Initialize OpenAI client with current provider settings
# This works with both OpenAI and W&B Inference (OpenAI-compatible)
openai_client = AsyncOpenAI(
    base_url=base_url,
    api_key=api_key,
)

