"""
Example usage of the comprehensive Odds API service.

This file demonstrates how to use the new organized odds API service
with minimal API calls and maximum efficiency.
"""

from typing import List, Dict, Any
from .service import OddsService
from .helpers import (
    find_best_moneylines,
    find_best_spreads,
    compare_parlay_across_books,
    get_arbitrage_opportunities,
    find_team_odds
)


def example_basic_usage():
    """Basic usage examples with minimal API calls."""
    
    # Initialize service (uses caching automatically)
    service = OddsService()
    
    # Get active sports (cached for 1 hour)
    sports = service.get_active_sports()
    print(f"Available sports: {[sport.title for sport in sports[:5]]}")
    
    # Get upcoming NFL games (cached for 30 minutes)
    nfl_games = service.get_upcoming_events('americanfootball_nfl')
    print(f"NFL games this week: {len(nfl_games)}")
    
    # Find games for a specific team
    chiefs_games = service.find_events_by_team('americanfootball_nfl', 'Chiefs')
    if chiefs_games:
        print(f"Chiefs game: {chiefs_games[0].home_team} vs {chiefs_games[0].away_team}")


def example_bookmaker_comparison():
    """Compare odds across bookmakers for a specific bet."""
    
    service = OddsService()
    
    # Get an upcoming NFL game
    nfl_games = service.get_upcoming_events('americanfootball_nfl')
    if not nfl_games:
        print("No NFL games found")
        return
    
    game = nfl_games[0]
    
    # Compare moneyline odds for home team across all bookmakers
    comparison = service.compare_bookmaker_odds(
        event_id=game.id,
        sport_key='americanfootball_nfl',
        bet_type='h2h',
        bet_details={
            'bet_type': 'h2h',
            'team': game.home_team
        }
    )
    
    print(f"Moneyline comparison for {game.home_team}:")
    print(f"Best odds: {comparison.best_odds}")
    print(f"Worst odds: {comparison.worst_odds}")
    print(f"Odds range: {comparison.odds_range}")


def example_parlay_comparison():
    """Compare parlay legs across bookmakers."""
    
    service = OddsService()
    
    # Example parlay legs
    parlay_legs = [
        "Chiefs -6.5",
        "Over 47.5", 
        "Cowboys ML"
    ]
    
    # Compare each leg across bookmakers
    for leg in parlay_legs:
        comparison = service.compare_parlay_leg_odds(leg, 'americanfootball_nfl')
        if comparison:
            print(f"\nLeg: {leg}")
            print(f"Best odds: {comparison.best_odds}")
            print(f"Worst odds: {comparison.worst_odds}")
            print(f"Range: {comparison.odds_range}")


def example_helper_functions():
    """Use convenient helper functions for common operations."""
    
    # Find best moneyline odds (uses caching efficiently)
    best_moneylines = find_best_moneylines('americanfootball_nfl', limit=3)
    print("Best moneyline odds:")
    for game in best_moneylines:
        print(f"  {game['game']}: {game['best_moneyline']['team']} {game['best_moneyline']['odds']}")
    
    # Find best spread odds
    best_spreads = find_best_spreads('americanfootball_nfl', limit=2)
    print("\nBest spread odds:")
    for game in best_spreads:
        print(f"  {game['game']}")
        for team, odds in game['best_spreads'].items():
            print(f"    {team}: {odds['point']} @ {odds['odds']}")
    
    # Look for arbitrage opportunities
    arbitrage = get_arbitrage_opportunities('americanfootball_nfl', limit=2)
    print(f"\nArbitrage opportunities: {len(arbitrage)}")
    for opp in arbitrage:
        print(f"  {opp['game']}: {opp['potential_profit']:.2f}% profit potential")


def example_team_analysis():
    """Analyze betting options for a specific team."""
    
    # Find all betting options for the Chiefs
    chiefs_odds = find_team_odds("Chiefs", "americanfootball_nfl")
    
    print("Chiefs betting options:")
    for game_info in chiefs_odds:
        print(f"\nGame: {game_info['game']}")
        for bookmaker, odds in game_info['betting_options'].items():
            print(f"  {bookmaker}:")
            for market, options in odds['markets'].items():
                print(f"    {market}: {options}")


def example_parlay_analysis():
    """Analyze a complete parlay across bookmakers."""
    
    # Example parlay
    parlay_legs = ["Chiefs -6.5", "Over 47.5", "Cowboys ML"]
    
    # Compare entire parlay across bookmakers
    parlay_analysis = compare_parlay_across_books(parlay_legs, 'americanfootball_nfl')
    
    print("Parlay Analysis:")
    print(f"Number of legs: {len(parlay_analysis['legs'])}")
    
    for leg in parlay_analysis['legs']:
        print(f"\nLeg: {leg['description']}")
        print(f"  Best odds: {leg['best_odds']}")
        print(f"  Worst odds: {leg['worst_odds']}")
        print(f"  Odds range: {leg['odds_range']}")
    
    if 'analysis' in parlay_analysis:
        analysis = parlay_analysis['analysis']
        print(f"\nOverall Analysis:")
        print(f"  Best case payout: {analysis['best_case_payout']:.2f}")
        print(f"  Worst case payout: {analysis['worst_case_payout']:.2f}")
        print(f"  Recommendation: {analysis['recommendation']}")


def example_api_usage_monitoring():
    """Monitor API usage and provide recommendations."""
    
    service = OddsService()
    usage = service.get_usage_info()
    
    print("API Usage Summary:")
    print(f"  Requests remaining: {usage.get('requests_remaining', 'Unknown')}")
    print(f"  Requests used: {usage.get('requests_used', 'Unknown')}")
    print(f"  Cache size: {usage.get('cache_size', 0)}")
    
    # Get usage recommendations
    from .helpers import get_api_usage_summary
    summary = get_api_usage_summary()
    
    print("\nRecommendations:")
    for rec in summary['recommendations']:
        print(f"  - {rec}")


if __name__ == "__main__":
    print("=== Odds API Service Examples ===\n")
    
    print("1. Basic Usage:")
    example_basic_usage()
    
    print("\n2. Bookmaker Comparison:")
    example_bookmaker_comparison()
    
    print("\n3. Parlay Comparison:")
    example_parlay_comparison()
    
    print("\n4. Helper Functions:")
    example_helper_functions()
    
    print("\n5. Team Analysis:")
    example_team_analysis()
    
    print("\n6. Parlay Analysis:")
    example_parlay_analysis()
    
    print("\n7. API Usage Monitoring:")
    example_api_usage_monitoring()
    
    print("\n=== Examples Complete ===")
