"""
Autonomous Agent Service using OpenAI Agents Python SDK.

This service provides an intelligent agent that can:
- Analyze sports betting parlays
- Make tool calls to fetch odds data
- Provide streaming responses
- Maintain conversation context
"""

from typing import AsyncGenerator, Optional, Dict, Any, List
from agents import Agent, Runner
from rich.console import Console
import weave
import warnings

from app.services.odds_api.service import OddsService
from app.core.weave_config import get_weave_op_decorator
from .tools import get_odds_tools

# Suppress deprecation warnings from dependencies
warnings.filterwarnings("ignore", message=".*'warn' method is deprecated.*")

console = Console()


class AgentService:
    """
    Autonomous agent service for sports betting analysis.
    
    Uses OpenAI Agents Python SDK to provide intelligent responses with tool calling capabilities.
    """
    
    def __init__(self, odds_service: Optional[OddsService] = None):
        """
        Initialize the agent service.
        
        Args:
            odds_service: Optional odds service instance
        """
        self.odds_service = odds_service
        self.agent = self._create_agent()
    
    def _create_agent(self) -> Agent:
        """Create the main agent with tools and instructions."""
        system_prompt = """You are DraftKiller, an expert sports betting analyst and parlay builder.

Your capabilities:
- Analyze sports betting parlays and provide insights
- Fetch real-time odds data from multiple sportsbooks
- Suggest optimal parlay combinations
- Explain betting strategies and risk assessment
- Answer questions about sports betting

Guidelines:
- Always provide data-driven analysis
- Be transparent about risks and probabilities
- Use current odds data when making recommendations
- Explain your reasoning clearly
- Be helpful but responsible about gambling

When users ask about bets, parlays, or odds, use the available tools to fetch current data."""

        agent = Agent(
            name="DraftKiller",
            instructions=system_prompt,
            model="gpt-4o-mini",  # Cost-effective model
            tools=get_odds_tools(self.odds_service)
        )
        
        return agent
    
    @get_weave_op_decorator()
    async def stream_response(
        self, 
        user_message: str, 
        conversation_history: Optional[list] = None
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """
        Stream a response from the agent using OpenAI Agents Python SDK.
        
        Args:
            user_message: User's message
            conversation_history: Optional conversation history
            
        Yields:
            Event dictionaries with type and data
        """
        try:
            # Prepare input with conversation history if available
            input_data = user_message
            if conversation_history:
                # Convert history to the format expected by the agent
                messages = []
                for msg in conversation_history[-10:]:  # Last 10 messages
                    messages.append({
                        "role": msg.get("role", "user"),
                        "content": msg.get("content", "")
                    })
                input_data = messages + [{"role": "user", "content": user_message}]
            
            # Stream the agent response using OpenAI Agents SDK
            result = Runner.run_streamed(self.agent, input_data)
            async for event in result.stream_events():
                if event.type == "raw_response_event":
                    # Skip raw response events - we'll handle content separately
                    continue
                elif event.type == "run_item_stream_event":
                    if event.item.type == "tool_call_item":
                        # Try to get tool name from raw_item or function attribute
                        tool_name = 'unknown'
                        arguments = {}
                        
                        # Check raw_item first
                        raw_item = getattr(event.item, 'raw_item', None)
                        if raw_item and hasattr(raw_item, 'function'):
                            func_data = getattr(raw_item, 'function', {})
                            tool_name = func_data.get('name', 'unknown')
                            arguments = func_data.get('arguments', {})
                        elif raw_item and hasattr(raw_item, 'name'):
                            tool_name = getattr(raw_item, 'name', 'unknown')
                        else:
                            # Fallback to direct function attribute
                            function_data = getattr(event.item, 'function', {})
                            tool_name = function_data.get('name', 'unknown')
                            arguments = function_data.get('arguments', {})
                        
                        yield {
                            "type": "tool_call",
                            "data": {
                                "tool_name": tool_name,
                                "arguments": arguments
                            }
                        }
                    elif event.item.type == "tool_call_output_item":
                        # Try to get tool name from raw_item or name attribute
                        tool_name = 'unknown'
                        raw_item = getattr(event.item, 'raw_item', None)
                        
                        if raw_item and hasattr(raw_item, 'name'):
                            tool_name = getattr(raw_item, 'name', 'unknown')
                        else:
                            # Fallback to direct name attribute
                            tool_name = getattr(event.item, 'name', 'unknown')
                        
                        yield {
                            "type": "tool_output", 
                            "data": {
                                "tool_name": tool_name,
                                "output": getattr(event.item, 'output', '')
                            }
                        }
                    elif event.item.type == "message_output_item":
                        yield {
                            "type": "content",
                            "data": getattr(event.item, 'content', '')
                        }
                elif event.type == "agent_updated_stream_event":
                    yield {
                        "type": "agent_update",
                        "data": {
                            "agent_name": event.new_agent.name
                        }
                    }
        
        except Exception as e:
            console.print(f"[red]Agent error: {e}[/red]")
            yield {
                "type": "error",
                "data": f"I encountered an error while processing your request: {str(e)}"
            }
    
    @get_weave_op_decorator()
    async def get_response(
        self, 
        user_message: str, 
        conversation_history: Optional[list] = None
    ) -> str:
        """
        Get a complete response from the agent using OpenAI Agents Python SDK.
        
        Args:
            user_message: User's message
            conversation_history: Optional conversation history
            
        Returns:
            Complete agent response
        """
        try:
            # Prepare input with conversation history if available
            input_data = user_message
            if conversation_history:
                messages = []
                for msg in conversation_history[-10:]:  # Last 10 messages
                    messages.append({
                        "role": msg.get("role", "user"),
                        "content": msg.get("content", "")
                    })
                input_data = messages + [{"role": "user", "content": user_message}]
            
            # Get complete response using OpenAI Agents SDK
            result = await Runner.run(self.agent, input_data)
            return result.final_output
        
        except Exception as e:
            console.print(f"[red]Agent error: {e}[/red]")
            return f"I encountered an error while processing your request: {str(e)}"


def get_agent_service(odds_service: Optional[OddsService] = None) -> AgentService:
    """
    Get or create an agent service instance.
    
    Args:
        odds_service: Optional odds service instance
        
    Returns:
        AgentService instance
    """
    return AgentService(odds_service)
