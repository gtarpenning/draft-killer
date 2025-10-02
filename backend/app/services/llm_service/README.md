# LLM Service

A modular service for managing LLM-based parlay analysis using Weights & Biases Weave.

## Structure

```
llm_service/
├── __init__.py           # Public API exports
├── client.py             # OpenAI client initialization & Weave setup
├── model.py              # ParlayAnalyzer Weave model
├── service.py            # High-level service functions
├── prompts.py            # Prompt loading and formatting utilities
├── prompts/              # Prompt templates directory
│   ├── system_prompt.txt        # System prompt for the LLM
│   └── user_prompt_template.txt # User prompt template
└── README.md             # This file
```

## Usage

Import from the package as before:

```python
from app.services.llm_service import (
    ParlayAnalyzer,
    stream_parlay_analysis,
    create_user_prompt,
    get_conversation_context,
    SYSTEM_PROMPT,
)
```

## Adding New Prompts

1. Create a new `.txt` file in the `prompts/` directory
2. Add a loader function in `prompts.py` if needed
3. Reference the prompt in your model or service code

Example:
```python
# In prompts.py
def get_fallback_prompt() -> str:
    return load_prompt("fallback_prompt.txt")
```

## Iterating on Prompts

To modify prompts:
1. Edit the `.txt` files directly in `prompts/`
2. Changes take effect on next import (restart server for development)
3. No code changes needed - just update the text files

## Future Agent Architecture

This structure is designed to support expansion into a full agent system:
- Add new prompt templates for different agent roles
- Create additional models for specialized tasks
- Implement tool-calling prompts
- Add memory/context management prompts

## Files

### `client.py`
Initializes the AsyncOpenAI client configured for W&B Inference API and sets up Weave tracking.

### `prompts.py`
Manages loading and formatting of all prompts. All prompt text should live in separate `.txt` files, not in code.

### `model.py`
Contains the `ParlayAnalyzer` Weave Model with `predict()` and `stream_predict()` methods.

### `service.py`
High-level service functions that application code calls:
- `analyze_parlay()` - Non-streaming analysis
- `stream_parlay_analysis()` - Streaming analysis
- `get_conversation_context()` - Build context from message history

### `__init__.py`
Exposes the public API that other parts of the application import.

