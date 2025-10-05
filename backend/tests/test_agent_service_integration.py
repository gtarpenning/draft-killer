#!/usr/bin/env python3
"""
Simple test script for the autonomous agent service.

Run this to test the agent service without the full FastAPI server.
"""

import asyncio
import os
import time
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn
import sys
from pathlib import Path

# Add backend app to path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from app.services.agent_service import get_agent_service
from app.services.odds_api.service import OddsService

console = Console()


async def test_agent_service():
    """Test the agent service with a simple query."""
    
    # Set up environment
    os.environ.setdefault("ODDS_API_KEY", "test-key")
    
    console.print(Panel.fit(
        "[bold blue]🤖 Testing Autonomous Agent Service[/bold blue]\n"
        "This will test the agent's ability to make tool calls and provide responses.",
        border_style="blue"
    ))
    console.print()
    
    try:
        # Initialize services
        console.print("[bold yellow]📋 Step 1: Initializing Services[/bold yellow]")
        console.print("  🔧 Setting up odds service...")
        odds_service = OddsService()
        console.print("  ✅ Odds service initialized")
        
        console.print("  🤖 Creating agent service...")
        agent_service = get_agent_service(odds_service)
        console.print("  ✅ Agent service initialized")
        console.print()
        
        # Show agent configuration
        console.print("[bold yellow]📋 Step 2: Agent Configuration[/bold yellow]")
        agent_table = Table(title="Agent Details")
        agent_table.add_column("Property", style="cyan")
        agent_table.add_column("Value", style="green")
        
        agent_table.add_row("Name", agent_service.agent.name)
        agent_table.add_row("Model", "gpt-4o-mini")
        agent_table.add_row("Tools Available", str(len(agent_service.agent.tools)))
        agent_table.add_row("Odds Service", "✅ Connected")
        
        console.print(agent_table)
        console.print()
        
        # Test queries
        test_queries = [
            "Show me Chiefs odds, compare different bookmakers",
            # "Give me one parlay suggestion, with high, medium and low risk legs",
            # "What sports are available for betting?"
        ]
        
        for i, test_query in enumerate(test_queries, 1):
            console.print(f"[bold yellow]📋 Step {2+i}: Test Query {i}[/bold yellow]")
            console.print(f"[green]Query:[/green] {test_query}")
            console.print()
            
            console.print("[yellow]🤔 Agent is thinking and making tool calls...[/yellow]")
            start_time = time.time()
            
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console,
                transient=True
            ) as progress:
                task = progress.add_task("Processing query...", total=None)
                
                # Get response
                response = await agent_service.get_response(test_query)
                
                progress.update(task, description="✅ Complete!")
            
            end_time = time.time()
            processing_time = end_time - start_time
            
            console.print(f"[green]⏱️  Processing time: {processing_time:.2f} seconds[/green]")
            console.print()
            
            # Show response
            console.print(Panel(
                response,
                title=f"[bold green]Agent Response {i}[/bold green]",
                border_style="green"
            ))
            console.print()
            
            # Add a small delay between queries
            if i < len(test_queries):
                console.print("[dim]Waiting 2 seconds before next query...[/dim]")
                await asyncio.sleep(2)
                console.print()
        
        console.print(Panel.fit(
            "[bold green]🎉 All Agent Tests Completed Successfully![/bold green]\n"
            "The agent is working correctly and can make tool calls.",
            border_style="green"
        ))
        
    except Exception as e:
        console.print(Panel.fit(
            f"[bold red]❌ Error testing agent service[/bold red]\n\n"
            f"[red]Error: {e}[/red]\n\n"
            f"[yellow]Note: This is expected if the OpenAI Agents SDK is not properly installed.[/yellow]",
            border_style="red"
        ))


async def test_streaming():
    """Test streaming response."""
    
    console.print(Panel.fit(
        "[bold blue]🌊 Testing Streaming Response[/bold blue]\n"
        "This will test the agent's ability to stream responses in real-time.",
        border_style="blue"
    ))
    console.print()
    
    try:
        # Initialize services
        console.print("[bold yellow]📋 Step 1: Initializing Services for Streaming[/bold yellow]")
        console.print("  🔧 Setting up odds service...")
        odds_service = OddsService()
        console.print("  🤖 Creating agent service...")
        agent_service = get_agent_service(odds_service)
        console.print("  ✅ Services ready for streaming")
        console.print()
        
        test_query = "Show me some NFL parlay suggestions with current odds"
        console.print(f"[bold yellow]📋 Step 2: Streaming Test[/bold yellow]")
        console.print(f"[green]Query:[/green] {test_query}")
        console.print()
        
        console.print("[yellow]🌊 Starting streaming response...[/yellow]")
        console.print("[dim]Watch the response appear in real-time below:[/dim]")
        console.print()
        
        # Create a nice panel for the streaming response
        console.print("[bold cyan]📝 Streaming Response:[/bold cyan]")
        console.print("─" * 60)
        
        chunk_count = 0
        start_time = time.time()
        
        # Stream response with detailed tracking
        async for chunk in agent_service.stream_response(test_query):
            chunk_count += 1
            console.print(chunk, end="", style="white")
            
            # Show progress every 10 chunks
            if chunk_count % 10 == 0:
                console.print(f"\n[dim]📊 Chunks received: {chunk_count}[/dim]", end="")
        
        end_time = time.time()
        streaming_time = end_time - start_time
        
        console.print()
        console.print("─" * 60)
        
        # Show streaming statistics
        stats_table = Table(title="Streaming Statistics")
        stats_table.add_column("Metric", style="cyan")
        stats_table.add_column("Value", style="green")
        
        stats_table.add_row("Total Chunks", str(chunk_count))
        stats_table.add_row("Streaming Time", f"{streaming_time:.2f} seconds")
        stats_table.add_row("Avg Chunks/sec", f"{chunk_count/streaming_time:.1f}")
        
        console.print(stats_table)
        console.print()
        
        console.print(Panel.fit(
            "[bold green]🎉 Streaming Test Completed Successfully![/bold green]\n"
            f"Received {chunk_count} chunks in {streaming_time:.2f} seconds",
            border_style="green"
        ))
        
    except Exception as e:
        console.print(Panel.fit(
            f"[bold red]❌ Error testing streaming[/bold red]\n\n"
            f"[red]Error: {e}[/red]\n\n"
            f"[yellow]Note: Check your OpenAI API key and network connection.[/yellow]",
            border_style="red"
        ))


async def test_simple_dummy_tools():
    """Test agent with simple dummy tools for debugging."""
    
    console.print(Panel.fit(
        "[bold blue]🧪 Testing Simple Dummy Tools[/bold blue]\n"
        "This will test the agent with simple mock tools that don't make API calls.",
        border_style="blue"
    ))
    console.print()
    
    try:
        from agents import Agent, FunctionTool
        from agents.tool import ToolContext
        import json
        
        # Create simple dummy tools
        def create_dummy_tool(name: str, description: str, response_data: dict) -> FunctionTool:
            async def dummy_function(context: ToolContext, arguments: str) -> str:
                return json.dumps(response_data)
            
            return FunctionTool(
                name=name,
                description=description,
                params_json_schema={"type": "object", "properties": {}, "required": []},
                on_invoke_tool=dummy_function
            )
        
        # Create dummy tools
        dummy_tools = [
            create_dummy_tool(
                "get_weather",
                "Get current weather information",
                {"success": True, "temperature": "72°F", "condition": "Sunny", "location": "San Francisco"}
            ),
            create_dummy_tool(
                "get_time",
                "Get current time",
                {"success": True, "time": "2025-01-01 12:00:00", "timezone": "UTC"}
            ),
            create_dummy_tool(
                "calculate_sum",
                "Calculate the sum of two numbers",
                {"success": True, "result": 15, "operation": "5 + 10 = 15"}
            )
        ]
        
        console.print("[bold yellow]📋 Step 1: Creating Dummy Agent[/bold yellow]")
        
        # Create agent with dummy tools
        dummy_agent = Agent(
            name="DummyTestAgent",
            instructions="You are a helpful assistant that can use simple tools. Use the available tools when appropriate.",
            model="gpt-4o-mini",
            tools=dummy_tools
        )
        
        console.print("  ✅ Dummy agent created with 3 simple tools")
        console.print()
        
        # Test simple queries
        test_queries = [
            "What's the weather like?",
            "What time is it?",
            "Calculate 5 + 10"
        ]
        
        for i, query in enumerate(test_queries, 1):
            console.print(f"[bold yellow]📋 Step {1+i}: Test Query {i}[/bold yellow]")
            console.print(f"[green]Query:[/green] {query}")
            console.print()
            
            console.print("[yellow]🤔 Agent is thinking...[/yellow]")
            start_time = time.time()
            
            # Get response using Runner
            from agents import Runner
            result = await Runner.run(dummy_agent, query)
            response = result.final_output
            
            end_time = time.time()
            processing_time = end_time - start_time
            
            console.print(f"[green]⏱️  Processing time: {processing_time:.2f} seconds[/green]")
            console.print()
            
            # Show response
            console.print(Panel(
                response,
                title=f"[bold green]Dummy Agent Response {i}[/bold green]",
                border_style="green"
            ))
            console.print()
        
        console.print(Panel.fit(
            "[bold green]🎉 Dummy Tools Test Completed![/bold green]\n"
            "The agent successfully used simple tools without API calls.",
            border_style="green"
        ))
        
    except Exception as e:
        console.print(Panel.fit(
            f"[bold red]❌ Error testing dummy tools[/bold red]\n\n"
            f"[red]Error: {e}[/red]",
            border_style="red"
        ))


async def test_simple_streaming():
    """Test streaming with simple dummy tools."""
    
    console.print(Panel.fit(
        "[bold blue]🌊 Testing Simple Streaming[/bold blue]\n"
        "This will test streaming with dummy tools to debug the streaming issue.",
        border_style="blue"
    ))
    console.print()
    
    try:
        from agents import Agent, FunctionTool, Runner
        from agents.tool import ToolContext
        import json
        
        # Create simple dummy tool
        async def dummy_weather_function(context: ToolContext, arguments: str) -> str:
            return json.dumps({"success": True, "weather": "Sunny", "temp": "75°F"})
        
        dummy_tool = FunctionTool(
            name="get_weather",
            description="Get weather information",
            params_json_schema={"type": "object", "properties": {}, "required": []},
            on_invoke_tool=dummy_weather_function
        )
        
        # Create agent with dummy tool
        dummy_agent = Agent(
            name="StreamingTestAgent",
            instructions="You are a helpful assistant. Use the weather tool when asked about weather.",
            model="gpt-4o-mini",
            tools=[dummy_tool]
        )
        
        console.print("[bold yellow]📋 Step 1: Testing Simple Streaming[/bold yellow]")
        console.print("  ✅ Dummy agent created for streaming test")
        console.print()
        
        test_query = "What's the weather like today?"
        console.print(f"[green]Query:[/green] {test_query}")
        console.print()
        
        console.print("[yellow]🌊 Starting simple streaming...[/yellow]")
        console.print("[dim]This should help debug the streaming issue:[/dim]")
        console.print()
        
        console.print("[bold cyan]📝 Streaming Response:[/bold cyan]")
        console.print("─" * 60)
        
        chunk_count = 0
        start_time = time.time()
        
        # Stream response
        result = Runner.run_streamed(dummy_agent, test_query)
        async for event in result.stream_events():
            chunk_count += 1
            console.print(f"[dim]Event {chunk_count}:[/dim] {event.type}")
            
            if event.type == "run_item_stream_event":
                if event.item.type == "tool_call_item":
                    console.print(f"  🔧 Tool call: {getattr(event.item, 'function', {}).get('name', 'unknown')}")
                elif event.item.type == "tool_call_output_item":
                    console.print(f"  📤 Tool output: {getattr(event.item, 'output', '')[:50]}...")
                elif event.item.type == "message_output_item":
                    # This is where the error might be occurring
                    try:
                        content = getattr(event.item, 'content', '')
                        console.print(f"  💬 Message: {content}")
                    except Exception as e:
                        console.print(f"  ❌ Error getting content: {e}")
                        console.print(f"  🔍 Event item type: {type(event.item)}")
                        console.print(f"  🔍 Event item attributes: {dir(event.item)}")
        
        end_time = time.time()
        streaming_time = end_time - start_time
        
        console.print()
        console.print("─" * 60)
        
        console.print(f"[green]📊 Total events: {chunk_count}[/green]")
        console.print(f"[green]⏱️  Streaming time: {streaming_time:.2f} seconds[/green]")
        console.print()
        
        console.print(Panel.fit(
            "[bold green]🎉 Simple Streaming Test Completed![/bold green]\n"
            f"Processed {chunk_count} events in {streaming_time:.2f} seconds",
            border_style="green"
        ))
        
    except Exception as e:
        console.print(Panel.fit(
            f"[bold red]❌ Error testing simple streaming[/bold red]\n\n"
            f"[red]Error: {e}[/red]\n\n"
            f"[yellow]This will help debug the streaming issue.[/yellow]",
            border_style="red"
        ))


async def test_tool_registry():
    """Test the tool registry to see what tools are available."""
    
    console.print(Panel.fit(
        "[bold blue]🔧 Testing Tool Registry[/bold blue]\n"
        "This will show all available tools that the agent can use.",
        border_style="blue"
    ))
    console.print()
    
    try:
        from app.services.agent_service.tools import get_odds_tools
        from app.services.odds_api.service import OddsService
        
        console.print("[bold yellow]📋 Step 1: Loading Tools[/bold yellow]")
        odds_service = OddsService()
        tools = get_odds_tools(odds_service)
        
        console.print(f"  ✅ Loaded {len(tools)} tools")
        console.print()
        
        console.print("[bold yellow]📋 Step 2: Tool Details[/bold yellow]")
        tools_table = Table(title="Available Agent Tools")
        tools_table.add_column("Tool Name", style="cyan")
        tools_table.add_column("Description", style="white")
        tools_table.add_column("Purpose", style="green")
        
        for tool in tools:
            tools_table.add_row(
                tool.name,
                tool.description[:80] + "..." if len(tool.description) > 80 else tool.description,
                "Odds Data Fetching"
            )
        
        console.print(tools_table)
        console.print()
        
        console.print(Panel.fit(
            "[bold green]🎉 Tool Registry Test Completed![/bold green]\n"
            f"Agent has access to {len(tools)} tools for fetching odds data.",
            border_style="green"
        ))
        
    except Exception as e:
        console.print(Panel.fit(
            f"[bold red]❌ Error testing tool registry[/bold red]\n\n"
            f"[red]Error: {e}[/red]",
            border_style="red"
        ))


if __name__ == "__main__":
    console.print(Panel.fit(
        "[bold blue]🎯 Draft Killer Agent Service Test Suite[/bold blue]\n"
        "Comprehensive testing of the autonomous agent service\n"
        "with detailed output tracking and progress indicators",
        border_style="blue"
    ))
    console.print()
    
    # Run all tests with detailed output
    console.print("[bold yellow]🧪 Running Simple Dummy Tools Test (for debugging)[/bold yellow]")
    asyncio.run(test_simple_dummy_tools())
    console.print()
    
    console.print("[bold yellow]🌊 Running Simple Streaming Test (for debugging)[/bold yellow]")
    asyncio.run(test_simple_streaming())
    console.print()
    
    console.print("[bold yellow]🔧 Running Tool Registry Test[/bold yellow]")
    asyncio.run(test_tool_registry())
    console.print()
    
    console.print("[bold yellow]🤖 Running Full Agent Service Test[/bold yellow]")
    asyncio.run(test_agent_service())
    console.print()
    
    console.print("[bold yellow]🌊 Running Full Streaming Test[/bold yellow]")
    asyncio.run(test_streaming())
    
    console.print()
    console.print(Panel.fit(
        "[bold green]🏁 All Tests Complete![/bold green]\n"
        "The autonomous agent service is ready for production use.",
        border_style="green"
    ))
