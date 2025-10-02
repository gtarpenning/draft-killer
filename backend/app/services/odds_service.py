"""
Odds API Service for fetching sports betting data.

Integrates with The Odds API to provide real-time odds for parlay analysis.
Includes caching to minimize API calls and stay within rate limits.
"""

from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import requests
import json
from fastapi import HTTPException

from app.core.config import settings


class OddsService:
    """
    Service for fetching and managing sportsbook odds data from The Odds API.
    
    Features:
    - Real-time odds from 250+ bookmakers
    - Support for moneyline, spreads, and totals
    - Intelligent caching to minimize API calls
    - Parlay parsing and enrichment
    """
    
    def __init__(self, api_key: Optional[str] = None, cache_ttl: int = 1800):
        """
        Initialize the odds service.
        
        Args:
            api_key: The Odds API key (defaults to settings.ODDS_API_KEY)
            cache_ttl: Cache time-to-live in seconds (default: 30 minutes)
        """
        self.api_key = api_key or settings.ODDS_API_KEY
        self.base_url = 'https://api.the-odds-api.com/v4'
        self.cache_ttl = cache_ttl
        # In production, use Redis or PostgreSQL for caching
        self._cache: Dict[str, Any] = {}
        self._last_requests_remaining: Optional[int] = None
    
    def get_available_sports(self) -> List[Dict[str, Any]]:
        """
        Get list of available sports from The Odds API.
        
        Returns:
            List of sports with their keys, titles, and status
            
        Raises:
            HTTPException: If API request fails
        """
        cache_key = "sports_list"
        
        # Check cache
        if cache_key in self._cache:
            cached_data, cached_time = self._cache[cache_key]
            if datetime.now() - cached_time < timedelta(seconds=self.cache_ttl):
                return cached_data
        
        # Fetch from API
        url = f"{self.base_url}/sports"
        params = {'apiKey': self.api_key}
        
        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            sports = response.json()
            
            # Cache the result
            self._cache[cache_key] = (sports, datetime.now())
            
            # Track remaining requests
            self._update_remaining_requests(response)
            
            return sports
            
        except requests.exceptions.RequestException as e:
            raise HTTPException(status_code=500, detail=f"Failed to fetch sports: {str(e)}")
    
    def get_odds_for_sport(
        self, 
        sport_key: str, 
        markets: Optional[List[str]] = None,
        bookmakers: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """
        Get current odds for all upcoming games in a sport.
        
        Args:
            sport_key: Sport identifier (e.g., 'americanfootball_nfl')
            markets: List of markets to fetch (default: ['h2h', 'spreads', 'totals'])
            bookmakers: Specific bookmakers to fetch (default: all US bookmakers)
        
        Returns:
            List of games with odds data
            
        Raises:
            HTTPException: If API request fails
        """
        if markets is None:
            markets = ['h2h', 'spreads', 'totals']
        
        cache_key = f"odds:{sport_key}:{','.join(markets)}"
        
        # Check cache
        if cache_key in self._cache:
            cached_data, cached_time = self._cache[cache_key]
            if datetime.now() - cached_time < timedelta(seconds=self.cache_ttl):
                return cached_data
        
        # Fetch from API
        url = f"{self.base_url}/sports/{sport_key}/odds"
        params = {
            'apiKey': self.api_key,
            'regions': 'us',
            'markets': ','.join(markets),
            'oddsFormat': 'american',
        }
        
        if bookmakers:
            params['bookmakers'] = ','.join(bookmakers)
        
        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            games = response.json()
            
            # Cache the result
            self._cache[cache_key] = (games, datetime.now())
            
            # Track remaining requests
            self._update_remaining_requests(response)
            
            return games
            
        except requests.exceptions.RequestException as e:
            raise HTTPException(status_code=500, detail=f"Failed to fetch odds: {str(e)}")
    
    def find_game_odds(
        self, 
        sport_key: str, 
        team_name: str
    ) -> Optional[Dict[str, Any]]:
        """
        Find odds for a specific game by team name.
        
        Uses fuzzy matching to find games even if team name is partial.
        
        Args:
            sport_key: Sport identifier
            team_name: Name of team to search for
        
        Returns:
            Game data with odds, or None if not found
        """
        games = self.get_odds_for_sport(sport_key)
        
        team_name_lower = team_name.lower()
        
        for game in games:
            home = game['home_team'].lower()
            away = game['away_team'].lower()
            
            if team_name_lower in home or team_name_lower in away:
                return game
        
        return None
    
    def parse_parlay_leg(self, leg_text: str) -> Dict[str, Any]:
        """
        Parse a single parlay leg from user input.
        
        Supports multiple formats:
        - "Chiefs -6.5" -> spread bet
        - "Cowboys ML" -> moneyline bet
        - "Over 47.5" -> total over
        - "Under 44" -> total under
        
        Args:
            leg_text: User's bet description
        
        Returns:
            Parsed bet information with type, team, and value
        """
        leg_text = leg_text.strip()
        
        # Moneyline
        if 'ML' in leg_text.upper():
            team = leg_text.replace('ML', '').replace('ml', '').strip()
            return {
                'bet_type': 'moneyline',
                'team': team,
                'original_text': leg_text
            }
        
        # Spread
        parts = leg_text.split()
        for i, part in enumerate(parts):
            if part.startswith(('+', '-')) and any(c.isdigit() for c in part):
                team = ' '.join(parts[:i])
                try:
                    value = float(part)
                    return {
                        'bet_type': 'spread',
                        'team': team,
                        'value': value,
                        'original_text': leg_text
                    }
                except ValueError:
                    continue
        
        # Total (Over/Under)
        if 'OVER' in leg_text.upper() or 'UNDER' in leg_text.upper():
            side = 'over' if 'OVER' in leg_text.upper() else 'under'
            # Extract number
            for part in leg_text.split():
                try:
                    value = float(part)
                    return {
                        'bet_type': 'total',
                        'side': side,
                        'value': value,
                        'original_text': leg_text
                    }
                except ValueError:
                    continue
        
        # If we can't parse it, return as-is and let LLM handle it
        return {
            'bet_type': 'unknown',
            'original_text': leg_text
        }
    
    def enrich_parlay_with_odds(
        self, 
        parlay_legs: List[Dict[str, Any]], 
        sport_key: str = 'americanfootball_nfl'
    ) -> Dict[str, Any]:
        """
        Enrich parsed parlay legs with current odds data from The Odds API.
        
        This is the key function that connects user input with live market data.
        
        Args:
            parlay_legs: List of parsed bet legs
            sport_key: Sport to fetch odds for (default: NFL)
        
        Returns:
            Enriched parlay data with current odds, lines, and bookmaker info
        """
        # Get all games for this sport (uses caching, so only 1 API call)
        games = self.get_odds_for_sport(sport_key)
        
        enriched_legs = []
        
        for leg in parlay_legs:
            enriched_leg = leg.copy()
            
            # Find the game if team is specified
            if leg.get('team'):
                game = None
                team_name_lower = leg['team'].lower()
                
                # Find matching game
                for g in games:
                    home = g['home_team'].lower()
                    away = g['away_team'].lower()
                    if team_name_lower in home or team_name_lower in away:
                        game = g
                        break
                
                if game:
                    enriched_leg['game'] = {
                        'home_team': game['home_team'],
                        'away_team': game['away_team'],
                        'commence_time': game['commence_time'],
                    }
                    
                    # Add current odds from first available bookmaker
                    if game.get('bookmakers'):
                        bookmaker = game['bookmakers'][0]
                        enriched_leg['bookmaker'] = bookmaker['title']
                        
                        # Find the specific odds for this bet
                        for market in bookmaker['markets']:
                            if leg['bet_type'] == 'moneyline' and market['key'] == 'h2h':
                                for outcome in market['outcomes']:
                                    if leg['team'].lower() in outcome['name'].lower():
                                        enriched_leg['current_odds'] = outcome['price']
                            
                            elif leg['bet_type'] == 'spread' and market['key'] == 'spreads':
                                for outcome in market['outcomes']:
                                    if leg['team'].lower() in outcome['name'].lower():
                                        enriched_leg['current_odds'] = outcome['price']
                                        enriched_leg['current_line'] = outcome['point']
                            
                            elif leg['bet_type'] == 'total' and market['key'] == 'totals':
                                for outcome in market['outcomes']:
                                    if outcome['name'].lower() == leg['side']:
                                        enriched_leg['current_odds'] = outcome['price']
                                        enriched_leg['current_line'] = outcome['point']
                else:
                    enriched_leg['error'] = f"Game not found for team: {leg['team']}"
            
            enriched_legs.append(enriched_leg)
        
        return {
            'legs': enriched_legs,
            'num_legs': len(enriched_legs),
            'sport': sport_key,
            'fetched_at': datetime.now().isoformat(),
            'requests_remaining': self._last_requests_remaining,
        }
    
    def enrich_from_api_queries(
        self,
        api_queries: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Enrich with odds data based on structured API queries from query extraction.
        
        This is the new method that works with the query extraction service.
        
        Args:
            api_queries: List of SuggestedApiQuery objects (as dicts)
        
        Returns:
            Enriched odds data with relevant games and markets
        """
        all_games = []
        sports_fetched = set()
        
        for query in api_queries:
            query_type = query.get('query_type')
            sport = query.get('sport', 'americanfootball_nfl')
            
            try:
                if query_type == 'team_odds':
                    # Fetch odds for a specific team
                    team_name = query.get('team_name', '')
                    game = self.find_game_odds(sport, team_name)
                    if game:
                        all_games.append({
                            'game': game,
                            'query_type': 'team_odds',
                            'team_name': team_name,
                        })
                
                elif query_type == 'suggestions':
                    # Get suggestions for this sport
                    suggestions = self.get_suggestions_for_sport(
                        sport,
                        num_legs=query.get('params', {}).get('num_legs', 3)
                    )
                    return suggestions  # Return suggestions directly
                
                elif query_type in ['player_props', 'game_odds']:
                    # Fetch general game odds for the sport
                    if sport not in sports_fetched:
                        games = self.get_odds_for_sport(sport)
                        for game in games[:5]:  # Limit to top 5 games
                            all_games.append({
                                'game': game,
                                'query_type': query_type,
                            })
                        sports_fetched.add(sport)
            
            except Exception as e:
                print(f"Failed to fetch odds for query {query}: {e}")
                continue
        
        # Format the results
        if not all_games:
            return {
                'games': [],
                'message': 'No odds data found for your query.',
                'fetched_at': datetime.now().isoformat(),
                'requests_remaining': self._last_requests_remaining,
            }
        
        return {
            'games': all_games,
            'num_games': len(all_games),
            'fetched_at': datetime.now().isoformat(),
            'requests_remaining': self._last_requests_remaining,
        }
    
    def get_suggestions_for_sport(
        self,
        sport_key: str = 'americanfootball_nfl',
        num_legs: int = 3
    ) -> Dict[str, Any]:
        """
        Get suggested parlay legs based on current odds.
        
        Returns popular/favorable bets for parlay building.
        
        Args:
            sport_key: Sport to get suggestions for
            num_legs: Number of legs to suggest (default: 3)
        
        Returns:
            Suggested parlay legs with odds data
        """
        # Get all games for this sport
        games = self.get_odds_for_sport(sport_key)
        
        if not games:
            return {
                'suggestions': [],
                'message': f'No games available for {sport_key}',
                'sport': sport_key,
                'fetched_at': datetime.now().isoformat(),
            }
        
        suggestions = []
        
        # Strategy: Pick favorites from different games
        # This is a simple strategy - can be made more sophisticated
        for game in games[:num_legs]:
            if not game.get('bookmakers'):
                continue
            
            bookmaker = game['bookmakers'][0]
            
            # Find moneyline market
            for market in bookmaker['markets']:
                if market['key'] == 'h2h':
                    # Get the favorite (lower odds = favorite in American odds)
                    outcomes = market['outcomes']
                    favorite = min(outcomes, key=lambda x: abs(x['price']))
                    
                    suggestions.append({
                        'bet_type': 'moneyline',
                        'team': favorite['name'],
                        'current_odds': favorite['price'],
                        'game': {
                            'home_team': game['home_team'],
                            'away_team': game['away_team'],
                            'commence_time': game['commence_time'],
                        },
                        'bookmaker': bookmaker['title'],
                        'reasoning': f"{favorite['name']} is favored at {favorite['price']}"
                    })
                    break
        
        return {
            'suggestions': suggestions[:num_legs],
            'num_suggestions': len(suggestions[:num_legs]),
            'sport': sport_key,
            'strategy': 'Favorites from different games (safer parlay)',
            'fetched_at': datetime.now().isoformat(),
            'requests_remaining': self._last_requests_remaining,
        }
    
    def _update_remaining_requests(self, response: requests.Response) -> None:
        """Track remaining API requests from response headers."""
        if 'x-requests-remaining' in response.headers:
            self._last_requests_remaining = int(response.headers['x-requests-remaining'])
    
    def get_remaining_requests(self) -> Optional[int]:
        """Get the last known count of remaining API requests."""
        return self._last_requests_remaining
    
    def clear_cache(self) -> None:
        """Clear the odds cache (useful for testing)."""
        self._cache = {}


# ============================================================================
# Service Singleton
# ============================================================================

# Global odds service instance
_odds_service: Optional[OddsService] = None


def get_odds_service() -> OddsService:
    """
    Get or create the global odds service instance.
    
    This is used as a FastAPI dependency.
    
    Returns:
        Singleton OddsService instance
    """
    global _odds_service
    if _odds_service is None:
        _odds_service = OddsService()
    return _odds_service

