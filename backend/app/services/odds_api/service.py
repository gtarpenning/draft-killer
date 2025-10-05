"""
High-level Odds API service with bookmaker comparison and convenience functions.

Provides clean, easy-to-use methods for common betting operations with intelligent
caching to minimize API calls.
"""

from typing import List, Dict, Any, Optional, Union
from datetime import datetime
import re
import weave

from .client import OddsApiClient
from .schemas import (
    Sport, Event, BookmakerComparison, ParlayLegComparison,
    Outcome, Market, Bookmaker
)


class OddsService:
    """
    High-level service for sports betting odds with bookmaker comparison.
    
    Features:
    - Bookmaker odds comparison across sportsbooks
    - Parlay leg analysis and comparison
    - Convenient helper methods for common operations
    - Intelligent caching to minimize API costs
    """
    
    # Common US bookmakers
    US_BOOKMAKERS = [
        'draftkings', 'fanduel', 'betmgm', 'caesars', 'pointsbet',
        'betrivers', 'foxbet', 'twinspires', 'unibet', 'wynnbet'
    ]
    
    # Common markets
    DEFAULT_MARKETS = ['h2h', 'spreads', 'totals']
    
    def __init__(self, api_key: Optional[str] = None):
        self.client = OddsApiClient(api_key)
    
    @weave.op()
    def get_active_sports(self) -> List[Sport]:
        """Get list of currently active sports."""
        sports_data = self.client.get_sports()
        return [Sport(**sport) for sport in sports_data if sport.get('active', False)]
    
    def find_sport_by_name(self, name: str) -> Optional[Sport]:
        """Find sport by partial name match."""
        sports = self.get_active_sports()
        name_lower = name.lower()
        
        for sport in sports:
            if (name_lower in sport.title.lower() or 
                name_lower in sport.description.lower() or
                name_lower in sport.key.lower()):
                return sport
        return None
    
    @weave.op()
    def get_upcoming_events(
        self, 
        sport_key: str, 
        markets: Optional[List[str]] = None,
        bookmakers: Optional[List[str]] = None
    ) -> List[Event]:
        """Get upcoming events for a sport with odds."""
        if markets is None:
            markets = self.DEFAULT_MARKETS
        if bookmakers is None:
            bookmakers = self.US_BOOKMAKERS
            
        events_data = self.client.get_odds(
            sport_key=sport_key,
            markets=markets,
            bookmakers=bookmakers
        )
        
        return [Event(**event) for event in events_data]
    
    @weave.op()
    def find_events_by_team(
        self, 
        sport_key: str, 
        team_name: str,
        markets: Optional[List[str]] = None
    ) -> List[Event]:
        """Find events involving a specific team."""
        events = self.get_upcoming_events(sport_key, markets)
        team_name_lower = team_name.lower()
        
        matching_events = []
        for event in events:
            if (team_name_lower in event.home_team.lower() or 
                team_name_lower in event.away_team.lower()):
                matching_events.append(event)
        
        return matching_events
    
    @weave.op()
    def compare_bookmaker_odds(
        self,
        event_id: str,
        sport_key: str,
        bet_type: str,
        bet_details: Dict[str, Any],
        bookmakers: Optional[List[str]] = None
    ) -> BookmakerComparison:
        """
        Compare odds for a specific bet across all bookmakers.
        
        Args:
            event_id: Event identifier
            sport_key: Sport identifier
            bet_type: Type of bet ('h2h', 'spreads', 'totals')
            bet_details: Bet-specific details (team, side, point, etc.)
            bookmakers: List of bookmakers to compare (default: all US)
            
        Returns:
            BookmakerComparison with odds across all sportsbooks
        """
        if bookmakers is None:
            bookmakers = self.US_BOOKMAKERS
            
        # Get event odds from all bookmakers
        event_data = self.client.get_event_odds(
            sport_key=sport_key,
            event_id=event_id,
            markets=[bet_type],
            bookmakers=bookmakers
        )
        
        event = Event(**event_data)
        bookmaker_odds = []
        
        # Extract odds for this specific bet from each bookmaker
        for bookmaker in event.bookmakers:
            odds_info = self._extract_odds_for_bet(
                bookmaker, bet_type, bet_details
            )
            
            if odds_info:
                bookmaker_odds.append({
                    'bookmaker_key': bookmaker.key,
                    'bookmaker_title': bookmaker.title,
                    'last_update': bookmaker.last_update,
                    **odds_info
                })
        
        # Find best and worst odds
        best_odds = self._find_best_odds(bookmaker_odds, bet_type)
        worst_odds = self._find_worst_odds(bookmaker_odds, bet_type)
        odds_range = self._calculate_odds_range(best_odds, worst_odds)
        
        return BookmakerComparison(
            event_id=event.id,
            sport_key=event.sport_key,
            home_team=event.home_team,
            away_team=event.away_team,
            commence_time=event.commence_time,
            bet_type=bet_type,
            bet_details=bet_details,
            bookmaker_odds=bookmaker_odds,
            best_odds=best_odds,
            worst_odds=worst_odds,
            odds_range=odds_range
        )
    
    def compare_parlay_leg_odds(
        self,
        leg_description: str,
        sport_key: str = 'americanfootball_nfl',
        bookmakers: Optional[List[str]] = None
    ) -> Optional[ParlayLegComparison]:
        """
        Parse and compare odds for a single parlay leg across bookmakers.
        
        Args:
            leg_description: User's bet description (e.g., "Chiefs -6.5", "Over 47.5")
            sport_key: Sport to search in
            bookmakers: List of bookmakers to compare
            
        Returns:
            ParlayLegComparison or None if parsing fails
        """
        parsed_leg = self._parse_parlay_leg(leg_description)
        if not parsed_leg:
            return None
            
        # Find the event for this bet
        events = self.find_events_by_team(
            sport_key, parsed_leg['team'], [parsed_leg['bet_type']]
        )
        
        if not events:
            return None
            
        event = events[0]  # Use first matching event
        
        # Compare odds across bookmakers
        comparison = self.compare_bookmaker_odds(
            event_id=event.id,
            sport_key=sport_key,
            bet_type=parsed_leg['bet_type'],
            bet_details=parsed_leg,
            bookmakers=bookmakers
        )
        
        # Convert to ParlayLegComparison format
        bookmaker_odds = []
        for odds in comparison.bookmaker_odds:
            bookmaker_odds.append({
                'bookmaker_title': odds['bookmaker_title'],
                'odds': odds.get('price'),
                'line': odds.get('point'),
                'last_update': odds['last_update']
            })
        
        best_odds = None
        worst_odds = None
        if comparison.best_odds:
            best_odds = {
                'bookmaker_title': comparison.best_odds['bookmaker_title'],
                'odds': comparison.best_odds.get('price'),
                'line': comparison.best_odds.get('point')
            }
        if comparison.worst_odds:
            worst_odds = {
                'bookmaker_title': comparison.worst_odds['bookmaker_title'],
                'odds': comparison.worst_odds.get('price'),
                'line': comparison.worst_odds.get('point')
            }
        
        return ParlayLegComparison(
            leg_id=f"leg_{datetime.now().timestamp()}",
            bet_description=leg_description,
            event_id=event.id,
            sport_key=sport_key,
            home_team=event.home_team,
            away_team=event.away_team,
            commence_time=event.commence_time,
            bookmaker_odds=bookmaker_odds,
            best_odds=best_odds,
            worst_odds=worst_odds,
            odds_range=comparison.odds_range
        )
    
    def get_best_odds_for_events(
        self,
        sport_key: str,
        markets: Optional[List[str]] = None,
        limit: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Get events with the best available odds for each market.
        
        Args:
            sport_key: Sport to analyze
            markets: Markets to analyze (default: h2h, spreads, totals)
            limit: Maximum number of events to return
            
        Returns:
            List of events with best odds information
        """
        if markets is None:
            markets = self.DEFAULT_MARKETS
            
        events = self.get_upcoming_events(sport_key, markets)
        best_odds_events = []
        
        for event in events[:limit]:
            event_best_odds = {
                'event': event,
                'best_odds_by_market': {}
            }
            
            for market in markets:
                best_odds = self._find_best_odds_for_market(event, market)
                if best_odds:
                    event_best_odds['best_odds_by_market'][market] = best_odds
            
            best_odds_events.append(event_best_odds)
        
        return best_odds_events
    
    def get_usage_info(self) -> Dict[str, Any]:
        """Get current API usage and cache information."""
        return self.client.get_usage_info()
    
    def clear_cache(self) -> None:
        """Clear all cached data."""
        self.client.clear_cache()
    
    def _parse_parlay_leg(self, leg_text: str) -> Optional[Dict[str, Any]]:
        """Parse a parlay leg description into structured data."""
        leg_text = leg_text.strip()
        
        # Moneyline
        if 'ML' in leg_text.upper():
            team = leg_text.replace('ML', '').replace('ml', '').strip()
            return {
                'bet_type': 'h2h',
                'team': team,
                'side': None
            }
        
        # Spread
        spread_match = re.search(r'(.+?)\s*([+-]\d+\.?\d*)', leg_text)
        if spread_match:
            team = spread_match.group(1).strip()
            point = float(spread_match.group(2))
            return {
                'bet_type': 'spreads',
                'team': team,
                'side': 'home' if point < 0 else 'away',
                'point': abs(point)
            }
        
        # Total (Over/Under)
        total_match = re.search(r'(over|under)\s*(\d+\.?\d*)', leg_text.lower())
        if total_match:
            side = total_match.group(1)
            point = float(total_match.group(2))
            return {
                'bet_type': 'totals',
                'team': None,
                'side': side,
                'point': point
            }
        
        return None
    
    def _extract_odds_for_bet(
        self, 
        bookmaker: Bookmaker, 
        bet_type: str, 
        bet_details: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """Extract specific odds from bookmaker data for a bet."""
        for market in bookmaker.markets:
            if market.key != bet_type:
                continue
                
            for outcome in market.outcomes:
                if self._outcome_matches_bet(outcome, bet_details):
                    return {
                        'price': outcome.price,
                        'point': outcome.point,
                        'name': outcome.name,
                        'description': outcome.description
                    }
        
        return None
    
    def _outcome_matches_bet(
        self, 
        outcome: Outcome, 
        bet_details: Dict[str, Any]
    ) -> bool:
        """Check if an outcome matches the bet details."""
        bet_type = bet_details.get('bet_type')
        team = bet_details.get('team', '').lower()
        side = bet_details.get('side', '').lower()
        point = bet_details.get('point')
        
        if bet_type == 'h2h':
            return team in outcome.name.lower()
        elif bet_type == 'spreads':
            return (team in outcome.name.lower() and 
                   point and outcome.point and abs(outcome.point - point) < 0.1)
        elif bet_type == 'totals':
            return (outcome.name.lower() == side and 
                   point and outcome.point and abs(outcome.point - point) < 0.1)
        
        return False
    
    def _find_best_odds(self, bookmaker_odds: List[Dict], bet_type: str) -> Optional[Dict]:
        """Find the best odds from a list of bookmaker odds."""
        if not bookmaker_odds:
            return None
            
        # For positive odds, higher is better; for negative, closer to 0 is better
        best = None
        for odds in bookmaker_odds:
            price = odds.get('price')
            if price is None:
                continue
                
            if best is None:
                best = odds
                continue
            
            best_price = best.get('price')
            
            # Compare odds (higher positive odds or less negative odds are better)
            if (price > 0 and best_price > 0 and price > best_price) or \
               (price < 0 and best_price < 0 and price > best_price) or \
               (price > 0 and best_price < 0):
                best = odds
        
        return best
    
    def _find_worst_odds(self, bookmaker_odds: List[Dict], bet_type: str) -> Optional[Dict]:
        """Find the worst odds from a list of bookmaker odds."""
        if not bookmaker_odds:
            return None
            
        worst = None
        for odds in bookmaker_odds:
            price = odds.get('price')
            if price is None:
                continue
                
            if worst is None:
                worst = odds
                continue
            
            worst_price = worst.get('price')
            
            # Compare odds (lower positive odds or more negative odds are worse)
            if (price > 0 and worst_price > 0 and price < worst_price) or \
               (price < 0 and worst_price < 0 and price < worst_price) or \
               (price < 0 and worst_price > 0):
                worst = odds
        
        return worst
    
    def _calculate_odds_range(self, best: Optional[Dict], worst: Optional[Dict]) -> Optional[float]:
        """Calculate the range between best and worst odds."""
        if not best or not worst:
            return None
            
        best_price = best.get('price')
        worst_price = worst.get('price')
        
        if best_price is None or worst_price is None:
            return None
            
        return abs(best_price - worst_price)
    
    def _find_best_odds_for_market(self, event: Event, market: str) -> Optional[Dict[str, Any]]:
        """Find best odds for a specific market across all bookmakers."""
        best_odds = None
        best_bookmaker = None
        
        for bookmaker in event.bookmakers:
            for market_data in bookmaker.markets:
                if market_data.key != market:
                    continue
                    
                for outcome in market_data.outcomes:
                    if best_odds is None or self._is_better_odds(outcome.price, best_odds):
                        best_odds = outcome.price
                        best_bookmaker = {
                            'bookmaker': bookmaker.title,
                            'odds': outcome.price,
                            'point': outcome.point,
                            'name': outcome.name
                        }
        
        return best_bookmaker
    
    def _is_better_odds(self, new_odds: float, current_odds: float) -> bool:
        """Check if new odds are better than current odds."""
        if new_odds > 0 and current_odds > 0:
            return new_odds > current_odds
        elif new_odds < 0 and current_odds < 0:
            return new_odds > current_odds  # Less negative is better
        elif new_odds > 0 and current_odds < 0:
            return True  # Positive is generally better than negative
        else:
            return False
