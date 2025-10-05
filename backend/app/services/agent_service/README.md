# Agent Service

Autonomous agent service using OpenAI Agents SDK for intelligent sports betting analysis.

## Features

- **Tool Calling**: Agent can call tools to fetch real-time odds data
- **Conversation Context**: Maintains conversation history for better responses
- **Streaming Support**: Provides streaming responses for real-time chat
- **Odds Integration**: Direct access to odds API through tools

## Architecture

```
agent_service/
├── __init__.py          # Public API exports
├── service.py           # Main AgentService class
├── tools.py            # Tool registry for odds API functions
└── README.md           # This file
```

## Usage

### Basic Usage

```python
from app.services.agent_service import get_agent_service

# Get agent service with odds integration
agent_service = get_agent_service(odds_service)

# Stream response
async for chunk in agent_service.stream_response("What are the best NFL bets today?"):
    print(chunk, end="")

# Get complete response
response = await agent_service.get_response("Show me Chiefs odds")
```

### Available Tools

The agent has access to these tools:

1. **get_odds_for_sport**: Get odds for all games in a sport
2. **find_team_odds**: Find odds for a specific team
3. **get_parlay_suggestions**: Get suggested parlay legs
4. **get_available_sports**: List available sports

## API Endpoint

Use the `/agent-stream` endpoint for agent-powered chat:

```bash
POST /chat/agent-stream
{
  "message": "What are the best NFL parlays today?",
  "conversation_id": "optional-uuid"
}
```

## TODOs

- [ ] Add more sophisticated betting analysis tools
- [ ] Implement conversation memory optimization
- [ ] Add error handling for tool failures
- [ ] Create specialized agents for different betting types
- [ ] Add support for more complex parlay analysis
