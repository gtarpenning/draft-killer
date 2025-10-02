"""
OpenAI client initialization for W&B Inference.

This module handles the setup of the AsyncOpenAI client configured
to use Weights & Biases Inference API.
"""

from openai import AsyncOpenAI
import weave

from app.core.config import settings


# Initialize Weave for tracking/observability
weave.init(settings.WEAVE_PROJECT)

base_url = settings.INFERENCE_API_URL or "https://api.openai.com/v1"
if base_url == "https://api.openai.com/v1":
    api_key = settings.OPENAI_API_KEY
else:
    api_key = settings.WANDB_API_KEY

# Initialize OpenAI client for W&B Inference
# This uses the OpenAI-compatible API provided by W&B
openai_client = AsyncOpenAI(
    base_url=base_url,
    api_key=api_key,
)

