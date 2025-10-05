"""
Convenience helper functions for common odds operations.

These functions provide simple, high-level interfaces for the most common
betting operations while minimizing API calls through intelligent caching.
"""

from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timedelta
import weave

from .service import OddsService
from .schemas import BookmakerComparison, ParlayLegComparison


# Global service instance for helper functions
_odds_service: Optional[OddsService] = None


def get_odds_service() -> OddsService:
    """Get or create the global odds service instance."""
    global _odds_service
    if _odds_service is None:
        _odds_service = OddsService()
    return _odds_service


@weave.op()
def find_best_moneylines(sport: str = 'americanfootball_nfl', limit: int = 5) -> List[Dict[str, Any]]:
    """
    Find the best moneyline odds for upcoming games.
    
    Args:
        sport: Sport to analyze (default: NFL)
        limit: Maximum number of games to return
        
    Returns:
        List of games with best moneyline odds
    """
    service = get_odds_service()
    events = service.get_upcoming_events(sport, markets=['h2h'])
    
    best_moneylines = []
    for event in events[:limit]:
        best_odds = None
        best_bookmaker = None
        
        for bookmaker in event.bookmakers:
            for market in bookmaker.markets:
                if market.key == 'h2h':
                    for outcome in market.outcomes:
                        if best_odds is None or outcome.price > best_odds:
                            best_odds = outcome.price
                            best_bookmaker = {
                                'bookmaker': bookmaker.title,
                                'team': outcome.name,
                                'odds': outcome.price
                            }
        
        if best_bookmaker:
            best_moneylines.append({
                'game': f"{event.away_team} @ {event.home_team}",
                'commence_time': event.commence_time,
                'best_moneyline': best_bookmaker
            })
    
    return best_moneylines


def find_best_spreads(sport: str = 'americanfootball_nfl', limit: int = 5) -> List[Dict[str, Any]]:
    """
    Find the best spread odds for upcoming games.
    
    Args:
        sport: Sport to analyze (default: NFL)
        limit: Maximum number of games to return
        
    Returns:
        List of games with best spread odds
    """
    service = get_odds_service()
    events = service.get_upcoming_events(sport, markets=['spreads'])
    
    best_spreads = []
    for event in events[:limit]:
        spread_odds = {}
        
        for bookmaker in event.bookmakers:
            for market in bookmaker.markets:
                if market.key == 'spreads':
                    for outcome in market.outcomes:
                        team_key = outcome.name
                        if team_key not in spread_odds or outcome.price > spread_odds[team_key]['odds']:
                            spread_odds[team_key] = {
                                'bookmaker': bookmaker.title,
                                'point': outcome.point,
                                'odds': outcome.price
                            }
        
        if spread_odds:
            best_spreads.append({
                'game': f"{event.away_team} @ {event.home_team}",
                'commence_time': event.commence_time,
                'best_spreads': spread_odds
            })
    
    return best_spreads


def compare_parlay_across_books(legs: List[str], sport: str = 'americanfootball_nfl') -> Dict[str, Any]:
    """
    Compare a parlay across different sportsbooks.
    
    Args:
        legs: List of parlay leg descriptions
        sport: Sport to analyze
        
    Returns:
        Comparison of parlay odds across bookmakers
    """
    service = get_odds_service()
    
    parlay_comparison = {
        'legs': [],
        'total_comparison': {},
        'best_parlay_odds': None,
        'worst_parlay_odds': None
    }
    
    # Analyze each leg
    for leg in legs:
        leg_comparison = service.compare_parlay_leg_odds(leg, sport)
        if leg_comparison:
            parlay_comparison['legs'].append({
                'description': leg,
                'best_odds': leg_comparison.best_odds,
                'worst_odds': leg_comparison.worst_odds,
                'odds_range': leg_comparison.odds_range
            })
    
    # Calculate theoretical parlay odds across different combinations
    if parlay_comparison['legs']:
        parlay_comparison['analysis'] = _analyze_parlay_combinations(parlay_comparison['legs'])
    
    return parlay_comparison


def get_arbitrage_opportunities(sport: str = 'americanfootball_nfl', limit: int = 3) -> List[Dict[str, Any]]:
    """
    Find potential arbitrage opportunities across bookmakers.
    
    Args:
        sport: Sport to analyze
        limit: Maximum number of opportunities to return
        
    Returns:
        List of potential arbitrage opportunities
    """
    service = get_odds_service()
    events = service.get_upcoming_events(sport, markets=['h2h'])
    
    arbitrage_ops = []
    
    for event in events[:limit]:
        home_odds = {}
        away_odds = {}
        
        # Collect all odds for home and away teams
        for bookmaker in event.bookmakers:
            for market in bookmaker.markets:
                if market.key == 'h2h':
                    for outcome in market.outcomes:
                        if event.home_team in outcome.name:
                            home_odds[bookmaker.title] = outcome.price
                        elif event.away_team in outcome.name:
                            away_odds[bookmaker.title] = outcome.price
        
        # Check for arbitrage opportunity
        if home_odds and away_odds:
            best_home = max(home_odds.values())
            best_away = max(away_odds.values())
            
            # Simple arbitrage check: if both odds are positive and high enough
            if best_home > 100 and best_away > 100:
                # Calculate implied probabilities
                home_prob = 100 / (best_home + 100) if best_home > 0 else 0
                away_prob = 100 / (best_away + 100) if best_away > 0 else 0
                total_prob = home_prob + away_prob
                
                if total_prob < 0.95:  # Potential arbitrage if total prob < 95%
                    arbitrage_ops.append({
                        'game': f"{event.away_team} @ {event.home_team}",
                        'commence_time': event.commence_time,
                        'best_home_odds': best_home,
                        'best_away_odds': best_away,
                        'total_implied_probability': total_prob,
                        'potential_profit': (1 - total_prob) * 100
                    })
    
    return arbitrage_ops[:limit]


def get_live_scores(sport: str = 'americanfootball_nfl', days_back: int = 1) -> List[Dict[str, Any]]:
    """
    Get live and recent scores for a sport.
    
    Args:
        sport: Sport to get scores for
        days_back: How many days back to look
        
    Returns:
        List of games with scores
    """
    service = get_odds_service()
    scores_data = service.client.get_scores(sport, days_from=days_back)
    
    return [
        {
            'game': f"{score['away_team']} @ {score['home_team']}",
            'commence_time': score['commence_time'],
            'completed': score.get('completed', False),
            'scores': score.get('scores', []),
            'last_update': score.get('last_update')
        }
        for score in scores_data
    ]


def find_team_odds(team_name: str, sport: str = 'americanfootball_nfl') -> List[Dict[str, Any]]:
    """
    Find all betting odds for a specific team.
    
    Args:
        team_name: Name of the team to find
        sport: Sport to search in
        
    Returns:
        List of betting options for the team
    """
    service = get_odds_service()
    events = service.find_events_by_team(sport, team_name)
    
    team_odds = []
    
    for event in events:
        event_odds = {
            'game': f"{event.away_team} @ {event.home_team}",
            'commence_time': event.commence_time,
            'betting_options': {}
        }
        
        for bookmaker in event.bookmakers:
            bookmaker_odds = {
                'bookmaker': bookmaker.title,
                'markets': {}
            }
            
            for market in bookmaker.markets:
                market_odds = []
                for outcome in market.outcomes:
                    if team_name.lower() in outcome.name.lower():
                        market_odds.append({
                            'outcome': outcome.name,
                            'odds': outcome.price,
                            'point': outcome.point
                        })
                
                if market_odds:
                    bookmaker_odds['markets'][market.key] = market_odds
            
            if bookmaker_odds['markets']:
                event_odds['betting_options'][bookmaker.title] = bookmaker_odds
        
        if event_odds['betting_options']:
            team_odds.append(event_odds)
    
    return team_odds


def get_api_usage_summary() -> Dict[str, Any]:
    """Get a summary of API usage and recommendations."""
    service = get_odds_service()
    usage = service.get_usage_info()
    
    summary = {
        'current_usage': usage,
        'recommendations': []
    }
    
    remaining = usage.get('requests_remaining', 0)
    
    if remaining < 100:
        summary['recommendations'].append("Low API quota remaining - consider caching more aggressively")
    elif remaining < 500:
        summary['recommendations'].append("Moderate API quota remaining - monitor usage")
    else:
        summary['recommendations'].append("Good API quota remaining")
    
    cache_size = usage.get('cache_size', 0)
    if cache_size > 50:
        summary['recommendations'].append("Large cache size - consider clearing unused entries")
    
    return summary


def _analyze_parlay_combinations(legs: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Analyze different parlay combinations for optimal odds."""
    if not legs:
        return {}
    
    # Simple analysis - in reality you'd want more sophisticated combinations
    best_case_odds = 1.0
    worst_case_odds = 1.0
    
    for leg in legs:
        if leg.get('best_odds') and leg['best_odds'].get('odds'):
            best_odds = leg['best_odds']['odds']
            # Convert American odds to decimal for calculation
            if best_odds > 0:
                decimal_odds = (best_odds / 100) + 1
            else:
                decimal_odds = (100 / abs(best_odds)) + 1
            best_case_odds *= decimal_odds
        
        if leg.get('worst_odds') and leg['worst_odds'].get('odds'):
            worst_odds = leg['worst_odds']['odds']
            if worst_odds > 0:
                decimal_odds = (worst_odds / 100) + 1
            else:
                decimal_odds = (100 / abs(worst_odds)) + 1
            worst_case_odds *= decimal_odds
    
    return {
        'best_case_payout': best_case_odds,
        'worst_case_payout': worst_case_odds,
        'odds_spread': best_case_odds - worst_case_odds,
        'recommendation': 'Best case' if best_case_odds > worst_case_odds * 1.1 else 'Odds are similar across books'
    }
