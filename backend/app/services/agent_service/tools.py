"""
Tool registry for the autonomous agent.

This module defines tools that the agent can use to interact with external services
like the odds API, providing real-time data for sports betting analysis.
"""

from typing import List, Dict, Any, Optional, Callable
from agents import FunctionTool
from agents.tool import ToolContext
from rich.console import Console
import json
import weave

from app.core.weave_config import get_weave_op_decorator

console = Console()


def get_odds_tools(odds_service) -> List[FunctionTool]:
    """
    Get all available tools for odds data fetching.
    
    Args:
        odds_service: OddsService instance for API calls
        
    Returns:
        List of FunctionTool objects that can be used by the agent
    """
    if not odds_service:
        return []
    
    return [
        _create_get_odds_tool(odds_service),
        _create_find_team_odds_tool(odds_service),
        _create_get_suggestions_tool(odds_service),
        _create_get_sports_tool(odds_service),
    ]


def _create_get_odds_tool(odds_service) -> FunctionTool:
    """Create tool for getting odds for a specific sport."""
    
    @get_weave_op_decorator()
    async def get_odds_for_sport(context: ToolContext, arguments: str) -> str:
        """
        Get current odds for all upcoming games in a sport.
        """
        try:
            # Parse arguments
            args = json.loads(arguments)
            sport_key = args.get("sport_key", "")
            markets = args.get("markets")
            bookmakers = args.get("bookmakers")
            
            markets_list = markets.split(',') if markets else None
            bookmakers_list = bookmakers.split(',') if bookmakers else None
            
            events = odds_service.get_upcoming_events(
                sport_key=sport_key,
                markets=markets_list,
                bookmakers=bookmakers_list
            )
            
            # Convert Event objects to dictionaries for JSON serialization
            games = []
            for event in events:
                game_dict = {
                    "id": event.id,
                    "sport_key": event.sport_key,
                    "commence_time": event.commence_time,
                    "home_team": event.home_team,
                    "away_team": event.away_team,
                    "bookmakers": []
                }
                
                for bookmaker in event.bookmakers:
                    bookmaker_dict = {
                        "key": bookmaker.key,
                        "title": bookmaker.title,
                        "last_update": bookmaker.last_update,
                        "markets": []
                    }
                    
                    for market in bookmaker.markets:
                        market_dict = {
                            "key": market.key,
                            "last_update": market.last_update,
                            "outcomes": [
                                {
                                    "name": outcome.name,
                                    "price": outcome.price,
                                    "point": outcome.point,
                                    "description": outcome.description
                                }
                                for outcome in market.outcomes
                            ]
                        }
                        bookmaker_dict["markets"].append(market_dict)
                    
                    game_dict["bookmakers"].append(bookmaker_dict)
                
                games.append(game_dict)
            
            result = {
                "success": True,
                "sport": sport_key,
                "games_count": len(games),
                "games": games[:5],  # Limit to first 5 games for response size
                "message": f"Found {len(games)} games for {sport_key}"
            }
            
            return json.dumps(result)
        
        except Exception as e:
            result = {
                "success": False,
                "error": str(e),
                "message": f"Failed to fetch odds for {sport_key}"
            }
            return json.dumps(result)
    
    # Define the JSON schema for the tool parameters
    params_schema = {
        "type": "object",
        "properties": {
            "sport_key": {
                "type": "string",
                "description": "Sport identifier (e.g., 'americanfootball_nfl', 'basketball_nba')"
            },
            "markets": {
                "type": "string",
                "description": "Comma-separated markets (e.g., 'h2h,spreads,totals')",
                "default": None
            },
            "bookmakers": {
                "type": "string", 
                "description": "Comma-separated bookmakers (optional)",
                "default": None
            }
        },
        "required": ["sport_key"]
    }
    
    return FunctionTool(
        name="get_odds_for_sport",
        description="Get current odds for all upcoming games in a specific sport. Use this when users ask about odds for a sport like NFL, NBA, etc.",
        params_json_schema=params_schema,
        on_invoke_tool=get_odds_for_sport
    )


def _create_find_team_odds_tool(odds_service) -> FunctionTool:
    """Create tool for finding odds for a specific team."""
    
    @get_weave_op_decorator()
    async def find_team_odds(context: ToolContext, arguments: str) -> str:
        """
        Find odds for a specific team's upcoming game.
        """
        try:
            # Parse arguments
            args = json.loads(arguments)
            sport_key = args.get("sport_key", "")
            team_name = args.get("team_name", "")
            
            events = odds_service.find_events_by_team(sport_key, team_name)
            
            if events:
                # Convert Event objects to dictionaries for JSON serialization
                games = []
                for event in events:
                    game_dict = {
                        "id": event.id,
                        "sport_key": event.sport_key,
                        "commence_time": event.commence_time,
                        "home_team": event.home_team,
                        "away_team": event.away_team,
                        "bookmakers": []
                    }
                    
                    for bookmaker in event.bookmakers:
                        bookmaker_dict = {
                            "key": bookmaker.key,
                            "title": bookmaker.title,
                            "last_update": bookmaker.last_update,
                            "markets": []
                        }
                        
                        for market in bookmaker.markets:
                            market_dict = {
                                "key": market.key,
                                "last_update": market.last_update,
                                "outcomes": [
                                    {
                                        "name": outcome.name,
                                        "price": outcome.price,
                                        "point": outcome.point,
                                        "description": outcome.description
                                    }
                                    for outcome in market.outcomes
                                ]
                            }
                            bookmaker_dict["markets"].append(market_dict)
                        
                        game_dict["bookmakers"].append(bookmaker_dict)
                    
                    games.append(game_dict)
                
                result = {
                    "success": True,
                    "team": team_name,
                    "sport": sport_key,
                    "games": games,
                    "games_count": len(games),
                    "message": f"Found {len(games)} game(s) for {team_name}"
                }
            else:
                result = {
                    "success": False,
                    "team": team_name,
                    "sport": sport_key,
                    "message": f"No upcoming games found for {team_name}"
                }
            
            return json.dumps(result)
        
        except Exception as e:
            result = {
                "success": False,
                "error": str(e),
                "message": f"Failed to find odds for {team_name}"
            }
            return json.dumps(result)
    
    # Define the JSON schema for the tool parameters
    params_schema = {
        "type": "object",
        "properties": {
            "sport_key": {
                "type": "string",
                "description": "Sport identifier (e.g., 'americanfootball_nfl')"
            },
            "team_name": {
                "type": "string",
                "description": "Name of the team to search for"
            }
        },
        "required": ["sport_key", "team_name"]
    }
    
    return FunctionTool(
        name="find_team_odds",
        description="Find odds for a specific team's upcoming game. Use this when users mention a specific team.",
        params_json_schema=params_schema,
        on_invoke_tool=find_team_odds
    )


def _create_get_suggestions_tool(odds_service) -> FunctionTool:
    """Create tool for getting parlay suggestions."""
    
    @get_weave_op_decorator()
    async def get_parlay_suggestions(context: ToolContext, arguments: str) -> str:
        """
        Get suggested parlay legs based on current odds.
        """
        try:
            # Parse arguments
            args = json.loads(arguments)
            sport_key = args.get("sport_key", "americanfootball_nfl")
            num_legs = args.get("num_legs", 3)
            
            # Get best odds for events and create suggestions
            best_odds_events = odds_service.get_best_odds_for_events(
                sport_key=sport_key,
                limit=num_legs * 2  # Get more events to choose from
            )
            
            suggestions = []
            for i, event_data in enumerate(best_odds_events[:num_legs]):
                event = event_data['event']
                best_odds_by_market = event_data['best_odds_by_market']
                
                suggestion = {
                    "leg_number": i + 1,
                    "event": {
                        "id": event.id,
                        "home_team": event.home_team,
                        "away_team": event.away_team,
                        "commence_time": event.commence_time
                    },
                    "best_odds": best_odds_by_market
                }
                suggestions.append(suggestion)
            
            result = {
                "success": True,
                "sport": sport_key,
                "suggestions": suggestions,
                "message": f"Generated {num_legs} parlay suggestions for {sport_key}"
            }
            
            return json.dumps(result)
        
        except Exception as e:
            result = {
                "success": False,
                "error": str(e),
                "message": f"Failed to get suggestions for {sport_key}"
            }
            return json.dumps(result)
    
    # Define the JSON schema for the tool parameters
    params_schema = {
        "type": "object",
        "properties": {
            "sport_key": {
                "type": "string",
                "description": "Sport identifier (default: 'americanfootball_nfl')",
                "default": "americanfootball_nfl"
            },
            "num_legs": {
                "type": "integer",
                "description": "Number of legs to suggest (default: 3)",
                "default": 3
            }
        },
        "required": []
    }
    
    return FunctionTool(
        name="get_parlay_suggestions",
        description="Get suggested parlay legs for a sport. Use this when users ask for parlay suggestions or recommendations.",
        params_json_schema=params_schema,
        on_invoke_tool=get_parlay_suggestions
    )


def _create_get_sports_tool(odds_service) -> FunctionTool:
    """Create tool for getting available sports."""
    
    @get_weave_op_decorator()
    async def get_available_sports(context: ToolContext, arguments: str) -> str:
        """
        Get list of available sports from the odds API.
        """
        try:
            sports = odds_service.get_active_sports()
            
            # Convert Sport objects to dictionaries for JSON serialization
            active_sports = []
            for sport in sports:
                sport_dict = {
                    "key": sport.key,
                    "group": sport.group,
                    "title": sport.title,
                    "description": sport.description,
                    "active": sport.active,
                    "has_outrights": sport.has_outrights
                }
                active_sports.append(sport_dict)
            
            result = {
                "success": True,
                "sports": active_sports,
                "count": len(active_sports),
                "message": f"Found {len(active_sports)} active sports"
            }
            
            return json.dumps(result)
        
        except Exception as e:
            result = {
                "success": False,
                "error": str(e),
                "message": "Failed to fetch available sports"
            }
            return json.dumps(result)
    
    # Define the JSON schema for the tool parameters (no parameters needed)
    params_schema = {
        "type": "object",
        "properties": {},
        "required": []
    }
    
    return FunctionTool(
        name="get_available_sports",
        description="Get list of available sports for betting. Use this when users ask what sports are available or want to see options.",
        params_json_schema=params_schema,
        on_invoke_tool=get_available_sports
    )
