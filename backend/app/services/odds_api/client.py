"""
Base API client for The Odds API with intelligent caching and rate limiting.

Optimized to minimize API calls while providing comprehensive coverage of all endpoints.
"""

import time
import hashlib
from typing import Dict, Any, Optional, List, Union
from datetime import datetime, timedelta
from dataclasses import dataclass
import requests
from fastapi import HTTPException
import weave

from app.core.config import settings


@dataclass
class CacheEntry:
    """Cache entry with timestamp and data."""
    data: Any
    timestamp: datetime
    ttl: int  # seconds


@dataclass
class ApiUsage:
    """Track API usage and remaining requests."""
    requests_remaining: Optional[int] = None
    requests_used: Optional[int] = None
    requests_last_cost: Optional[int] = None
    last_reset: Optional[datetime] = None


class OddsApiClient:
    """
    Efficient base client for The Odds API with smart caching.
    
    Features:
    - Intelligent caching to minimize API calls
    - Rate limiting and usage tracking
    - Comprehensive error handling
    - Request deduplication
    """
    
    BASE_URL = "https://api.the-odds-api.com/v4"
    CACHE_DEFAULT_TTL = 1800  # 30 minutes
    CACHE_SPORTS_TTL = 3600   # 1 hour (sports list changes rarely)
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or settings.ODDS_API_KEY
        self._cache: Dict[str, CacheEntry] = {}
        self._usage = ApiUsage()
        self._request_cache: Dict[str, Any] = {}  # For request deduplication
        
    def _make_cache_key(self, endpoint: str, params: Dict[str, Any]) -> str:
        """Generate cache key from endpoint and parameters."""
        param_str = "&".join(f"{k}={v}" for k, v in sorted(params.items()))
        content = f"{endpoint}?{param_str}"
        return hashlib.md5(content.encode()).hexdigest()
    
    def _is_cache_valid(self, cache_key: str) -> bool:
        """Check if cache entry is still valid."""
        if cache_key not in self._cache:
            return False
            
        entry = self._cache[cache_key]
        return datetime.now() - entry.timestamp < timedelta(seconds=entry.ttl)
    
    def _update_usage_from_response(self, response: requests.Response) -> None:
        """Update usage tracking from response headers."""
        headers = response.headers
        
        if 'x-requests-remaining' in headers:
            self._usage.requests_remaining = int(headers['x-requests-remaining'])
        
        if 'x-requests-used' in headers:
            self._usage.requests_used = int(headers['x-requests-used'])
            
        if 'x-requests-last' in headers:
            self._usage.requests_last_cost = int(headers['x-requests-last'])
    
    @weave.op()
    def _make_request(
        self, 
        endpoint: str, 
        params: Dict[str, Any],
        cache_ttl: Optional[int] = None,
        use_cache: bool = True
    ) -> Any:
        """
        Make API request with caching and error handling.
        
        Args:
            endpoint: API endpoint path
            params: Request parameters
            cache_ttl: Cache time-to-live in seconds
            use_cache: Whether to use caching
            
        Returns:
            API response data
            
        Raises:
            HTTPException: If request fails or quota exceeded
        """
        cache_key = self._make_cache_key(endpoint, params)
        
        # Check cache first
        if use_cache and self._is_cache_valid(cache_key):
            return self._cache[cache_key].data
        
        # Check if we're already making this request (deduplication)
        if cache_key in self._request_cache:
            return self._request_cache[cache_key]
        
        # Make the actual request
        url = f"{self.BASE_URL}{endpoint}"
        params['apiKey'] = self.api_key
        
        try:
            response = requests.get(url, params=params, timeout=15)
            
            # Handle rate limiting
            if response.status_code == 429:
                raise HTTPException(
                    status_code=429,
                    detail="Rate limit exceeded. Please wait before making more requests."
                )
            
            # Handle quota exceeded
            if response.status_code == 401:
                raise HTTPException(
                    status_code=401,
                    detail="API quota exceeded or invalid API key."
                )
            
            response.raise_for_status()
            
            data = response.json()
            
            # Update usage tracking
            self._update_usage_from_response(response)
            
            # Cache the response
            ttl = cache_ttl or self.CACHE_DEFAULT_TTL
            self._cache[cache_key] = CacheEntry(
                data=data,
                timestamp=datetime.now(),
                ttl=ttl
            )
            
            # Store in request cache for deduplication
            self._request_cache[cache_key] = data
            
            return data
            
        except requests.exceptions.RequestException as e:
            raise HTTPException(
                status_code=500,
                detail=f"API request failed: {str(e)}"
            )
    
    @weave.op()
    def get_sports(self, include_all: bool = False) -> List[Dict[str, Any]]:
        """
        Get list of available sports.
        
        Args:
            include_all: Include inactive sports (default: False)
            
        Returns:
            List of sport objects
        """
        params = {}
        if include_all:
            params['all'] = 'true'
            
        return self._make_request(
            "/sports",
            params,
            cache_ttl=self.CACHE_SPORTS_TTL
        )
    
    @weave.op()
    def get_odds(
        self,
        sport_key: str,
        regions: List[str] = None,
        markets: List[str] = None,
        odds_format: str = "american",
        date_format: str = "iso",
        bookmakers: List[str] = None,
        event_ids: List[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Get current odds for a sport.
        
        Args:
            sport_key: Sport identifier
            regions: List of regions (default: ['us'])
            markets: List of markets (default: ['h2h', 'spreads', 'totals'])
            odds_format: Odds format - 'american' or 'decimal'
            date_format: Date format - 'iso' or 'unix'
            bookmakers: Specific bookmakers to fetch
            event_ids: Specific event IDs to fetch
            
        Returns:
            List of events with odds
        """
        if regions is None:
            regions = ['us']
        if markets is None:
            markets = ['h2h', 'spreads', 'totals']
            
        params = {
            'regions': ','.join(regions),
            'markets': ','.join(markets),
            'oddsFormat': odds_format,
            'dateFormat': date_format
        }
        
        if bookmakers:
            params['bookmakers'] = ','.join(bookmakers)
        if event_ids:
            params['eventIds'] = ','.join(event_ids)
        
        return self._make_request(f"/sports/{sport_key}/odds", params)
    
    @weave.op()
    def get_scores(
        self,
        sport_key: str,
        days_from: int = 1,
        date_format: str = "iso"
    ) -> List[Dict[str, Any]]:
        """
        Get live and final scores for a sport.
        
        Args:
            sport_key: Sport identifier
            days_from: Days to look back (default: 1)
            date_format: Date format - 'iso' or 'unix'
            
        Returns:
            List of events with scores
        """
        params = {
            'daysFrom': str(days_from),
            'dateFormat': date_format
        }
        
        return self._make_request(f"/sports/{sport_key}/scores", params)
    
    def get_events(
        self,
        sport_key: str,
        regions: List[str] = None,
        markets: List[str] = None,
        date_format: str = "iso"
    ) -> List[Dict[str, Any]]:
        """
        Get upcoming events for a sport.
        
        Args:
            sport_key: Sport identifier
            regions: List of regions (default: ['us'])
            markets: List of markets (default: ['h2h'])
            date_format: Date format - 'iso' or 'unix'
            
        Returns:
            List of upcoming events
        """
        if regions is None:
            regions = ['us']
        if markets is None:
            markets = ['h2h']
            
        params = {
            'regions': ','.join(regions),
            'markets': ','.join(markets),
            'dateFormat': date_format
        }
        
        return self._make_request(f"/sports/{sport_key}/events", params)
    
    def get_event_odds(
        self,
        sport_key: str,
        event_id: str,
        regions: List[str] = None,
        markets: List[str] = None,
        odds_format: str = "american",
        date_format: str = "iso",
        bookmakers: List[str] = None
    ) -> Dict[str, Any]:
        """
        Get odds for a specific event.
        
        Args:
            sport_key: Sport identifier
            event_id: Event identifier
            regions: List of regions (default: ['us'])
            markets: List of markets (default: ['h2h', 'spreads', 'totals'])
            odds_format: Odds format - 'american' or 'decimal'
            date_format: Date format - 'iso' or 'unix'
            bookmakers: Specific bookmakers to fetch
            
        Returns:
            Event with odds data
        """
        if regions is None:
            regions = ['us']
        if markets is None:
            markets = ['h2h', 'spreads', 'totals']
            
        params = {
            'regions': ','.join(regions),
            'markets': ','.join(markets),
            'oddsFormat': odds_format,
            'dateFormat': date_format
        }
        
        if bookmakers:
            params['bookmakers'] = ','.join(bookmakers)
        
        return self._make_request(f"/sports/{sport_key}/events/{event_id}/odds", params)
    
    def get_event_markets(
        self,
        sport_key: str,
        event_id: str,
        regions: List[str] = None
    ) -> Dict[str, Any]:
        """
        Get available markets for a specific event.
        
        Args:
            sport_key: Sport identifier
            event_id: Event identifier
            regions: List of regions (default: ['us'])
            
        Returns:
            Available markets for the event
        """
        if regions is None:
            regions = ['us']
            
        params = {
            'regions': ','.join(regions)
        }
        
        return self._make_request(f"/sports/{sport_key}/events/{event_id}/markets", params)
    
    def get_participants(
        self,
        sport_key: str,
        event_id: str
    ) -> Dict[str, Any]:
        """
        Get participants for a specific event.
        
        Args:
            sport_key: Sport identifier
            event_id: Event identifier
            
        Returns:
            Event with participant details
        """
        return self._make_request(f"/sports/{sport_key}/events/{event_id}/participants", {})
    
    def get_historical_odds(
        self,
        sport_key: str,
        regions: List[str] = None,
        markets: List[str] = None,
        odds_format: str = "american",
        date_format: str = "iso",
        bookmakers: List[str] = None,
        date: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Get historical odds for a sport.
        
        Args:
            sport_key: Sport identifier
            regions: List of regions (default: ['us'])
            markets: List of markets (default: ['h2h'])
            odds_format: Odds format - 'american' or 'decimal'
            date_format: Date format - 'iso' or 'unix'
            bookmakers: Specific bookmakers to fetch
            date: Specific date to fetch (ISO format)
            
        Returns:
            List of historical events with odds
        """
        if regions is None:
            regions = ['us']
        if markets is None:
            markets = ['h2h']
            
        params = {
            'regions': ','.join(regions),
            'markets': ','.join(markets),
            'oddsFormat': odds_format,
            'dateFormat': date_format
        }
        
        if bookmakers:
            params['bookmakers'] = ','.join(bookmakers)
        if date:
            params['date'] = date
        
        return self._make_request(f"/historical/sports/{sport_key}/odds", params)
    
    def get_historical_events(
        self,
        sport_key: str,
        regions: List[str] = None,
        markets: List[str] = None,
        date_format: str = "iso",
        date: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Get historical events for a sport.
        
        Args:
            sport_key: Sport identifier
            regions: List of regions (default: ['us'])
            markets: List of markets (default: ['h2h'])
            date_format: Date format - 'iso' or 'unix'
            date: Specific date to fetch (ISO format)
            
        Returns:
            List of historical events
        """
        if regions is None:
            regions = ['us']
        if markets is None:
            markets = ['h2h']
            
        params = {
            'regions': ','.join(regions),
            'markets': ','.join(markets),
            'dateFormat': date_format
        }
        
        if date:
            params['date'] = date
        
        return self._make_request(f"/historical/sports/{sport_key}/events", params)
    
    def get_historical_event_odds(
        self,
        sport_key: str,
        event_id: str,
        regions: List[str] = None,
        markets: List[str] = None,
        odds_format: str = "american",
        date_format: str = "iso",
        bookmakers: List[str] = None,
        date: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get historical odds for a specific event.
        
        Args:
            sport_key: Sport identifier
            event_id: Event identifier
            regions: List of regions (default: ['us'])
            markets: List of markets (default: ['h2h'])
            odds_format: Odds format - 'american' or 'decimal'
            date_format: Date format - 'iso' or 'unix'
            bookmakers: Specific bookmakers to fetch
            date: Specific date to fetch (ISO format)
            
        Returns:
            Historical odds snapshot for the event
        """
        if regions is None:
            regions = ['us']
        if markets is None:
            markets = ['h2h']
            
        params = {
            'regions': ','.join(regions),
            'markets': ','.join(markets),
            'oddsFormat': odds_format,
            'dateFormat': date_format
        }
        
        if bookmakers:
            params['bookmakers'] = ','.join(bookmakers)
        if date:
            params['date'] = date
        
        return self._make_request(f"/historical/sports/{sport_key}/events/{event_id}/odds", params)
    
    def get_usage_info(self) -> Dict[str, Any]:
        """Get current API usage information."""
        return {
            "requests_remaining": self._usage.requests_remaining,
            "requests_used": self._usage.requests_used,
            "requests_last_cost": self._usage.requests_last_cost,
            "cache_size": len(self._cache)
        }
    
    def clear_cache(self) -> None:
        """Clear all cached data."""
        self._cache.clear()
        self._request_cache.clear()
    
    def clear_cache_for_sport(self, sport_key: str) -> None:
        """Clear cache entries for a specific sport."""
        keys_to_remove = [
            key for key in self._cache.keys() 
            if sport_key in key
        ]
        for key in keys_to_remove:
            del self._cache[key]
            if key in self._request_cache:
                del self._request_cache[key]
