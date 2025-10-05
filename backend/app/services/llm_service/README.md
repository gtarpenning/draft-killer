# LLM Service - Provider Switching

This module provides a comprehensive switching mechanism between different LLM providers (OpenAI and Weights & Biases Inference) using a single environment variable.

## Quick Start

### Environment Variables

Set one of these to control the provider:

```bash
# Use OpenAI (default)
export LLM_PROVIDER=openai

# Use W&B Inference
export LLM_PROVIDER=wandb

# Auto-detect based on available API keys (default behavior)
unset LLM_PROVIDER
```

### API Keys

Make sure you have the appropriate API key set:

```bash
# For OpenAI
export OPENAI_API_KEY=your_openai_key

# For W&B Inference  
export WANDB_API_KEY=your_wandb_key
```

## Usage

### Basic Usage

```python
from app.services.llm_service.client import openai_client

# The client is automatically configured based on LLM_PROVIDER
async def chat_completion(messages):
    response = await openai_client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages
    )
    return response
```

### Provider Management

```python
from app.services.llm_service.provider_config import (
    provider_manager,
    get_current_provider_config,
    get_current_base_url,
    get_current_api_key,
    LLMProvider
)

# Get current provider info
info = provider_manager.get_provider_info()
print(f"Using {info['name']} at {info['base_url']}")

# Switch providers programmatically
provider_manager.switch_provider(LLMProvider.WANDB)

# Get configuration details
config = get_current_provider_config()
base_url = get_current_base_url()
api_key = get_current_api_key()
```

## Configuration

### Provider Detection Logic

1. **Explicit Setting**: If `LLM_PROVIDER` is set, use that provider
2. **Auto-detection**: If not set, detect based on available API keys:
   - If only `WANDB_API_KEY` is available → Use W&B
   - If only `OPENAI_API_KEY` is available → Use OpenAI  
   - If both are available → Prefer OpenAI
   - If neither is available → Use OpenAI (will fail at runtime)

### Supported Providers

| Provider | Base URL | API Key Env Var | Description |
|----------|----------|-----------------|-------------|
| `openai` | `https://api.openai.com/v1` | `OPENAI_API_KEY` | OpenAI's official API |
| `wandb` | `https://api.inference.wandb.ai/v1` | `WANDB_API_KEY` | W&B Inference API (OpenAI-compatible) |

## Error Handling

The system provides clear error messages when API keys are missing:

```python
# This will raise a clear error if the required API key is not set
api_key = get_current_api_key()
```

## Benefits

- ✅ **Single Environment Variable**: Just set `LLM_PROVIDER` to switch
- ✅ **Automatic Configuration**: Base URL, API key, and model selection handled automatically
- ✅ **Easy Switching**: Change providers without code changes
- ✅ **Graceful Fallback**: Clear error messages for missing configuration
- ✅ **Backward Compatible**: Existing code continues to work unchanged