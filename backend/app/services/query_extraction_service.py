"""
Query Extraction Service for intelligently parsing betting intent from natural language.

Uses an LLM to extract structured betting queries from user messages,
enabling intelligent odds fetching and analysis.
"""

import json
from typing import List, Dict, Any, Optional
import openai

from app.core.config import settings
from app.models.schemas import (
    BettingQuery,
    BettingIntent,
    EntityType,
    ExtractedEntity,
    SuggestedApiQuery,
    ApiQueryType,
)


class QueryExtractionService:
    """
    Service for extracting structured betting queries from natural language using LLM.
    
    This service is the first stage in our two-stage pipeline:
    1. Extract intent and entities from user message
    2. Fetch relevant odds based on extracted queries
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the query extraction service.
        
        Args:
            api_key: OpenAI API key (defaults to settings.OPENAI_API_KEY)
        """
        self.api_key = api_key or settings.OPENAI_API_KEY
        if not self.api_key:
            raise ValueError("OpenAI API key is required for query extraction")
        
        self.client = openai.OpenAI(api_key=self.api_key)
        self.model = "gpt-4o-mini"  # Fast and cost-effective for extraction
        
        # Sport detection mappings (player/team → sport)
        self._sport_mappings = self._build_sport_mappings()
    
    def _build_sport_mappings(self) -> Dict[str, str]:
        """
        Build mappings of well-known teams/players to sports.
        
        This is used for quick lookups before resorting to LLM.
        """
        return {
            # NFL Teams
            "chiefs": "americanfootball_nfl",
            "kansas city": "americanfootball_nfl",
            "cowboys": "americanfootball_nfl",
            "dallas": "americanfootball_nfl",
            "49ers": "americanfootball_nfl",
            "niners": "americanfootball_nfl",
            "san francisco": "americanfootball_nfl",
            "patriots": "americanfootball_nfl",
            "packers": "americanfootball_nfl",
            "eagles": "americanfootball_nfl",
            "bills": "americanfootball_nfl",
            "bengals": "americanfootball_nfl",
            
            # MLB Players (examples)
            "aaron judge": "baseball_mlb",
            "shohei ohtani": "baseball_mlb",
            "mookie betts": "baseball_mlb",
            "yankees": "baseball_mlb",
            "dodgers": "baseball_mlb",
            "red sox": "baseball_mlb",
            
            # NBA Teams (examples)
            "lakers": "basketball_nba",
            "warriors": "basketball_nba",
            "celtics": "basketball_nba",
            "lebron": "basketball_nba",
            "curry": "basketball_nba",
        }
    
    async def extract_betting_intent(
        self,
        message: str,
        conversation_history: Optional[List[Dict[str, Any]]] = None
    ) -> BettingQuery:
        """
        Extract structured betting intent from a user message.
        
        Uses OpenAI GPT-4o-mini with JSON mode for fast, structured extraction.
        
        Args:
            message: User's message
            conversation_history: Optional previous messages for context
            
        Returns:
            Structured BettingQuery with intent, entities, and suggested API queries
        """
        # Build the extraction prompt
        system_prompt = self._get_extraction_system_prompt()
        user_prompt = self._format_extraction_prompt(message, conversation_history)
        
        try:
            # Call OpenAI with JSON mode
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                response_format={"type": "json_object"},
                temperature=0.1,  # Low temperature for consistent extraction
                max_tokens=1000,
            )
            
            # Parse the JSON response
            result = json.loads(response.choices[0].message.content)
            
            # Convert to BettingQuery object
            return self._parse_extraction_result(result, message)
            
        except Exception as e:
            # If extraction fails, return a safe fallback
            print(f"Query extraction failed: {e}")
            return self._create_fallback_query(message)
    
    def _get_extraction_system_prompt(self) -> str:
        """Get the system prompt for query extraction."""
        return """You are a betting query parser. Your job is to extract structured information from user messages about sports betting.

Your task:
1. Identify the user's intent (what they want to do)
2. Extract relevant entities (teams, players, bet types, lines)
3. Infer the sport from context
4. Suggest specific API queries needed to get relevant odds data

Intents:
- "analyze_specific_bets": User has specific bets they want analyzed (e.g., "Chiefs -6.5, Cowboys ML")
- "request_suggestions": User wants betting suggestions (e.g., "what's a good parlay?")
- "lookup_odds": User wants to see odds for something (e.g., "what are the odds for the Yankees game?")
- "general_question": General question about betting (e.g., "how do parlays work?")

Entity types:
- player: Player name (e.g., "Aaron Judge", "Patrick Mahomes")
- team: Team name (e.g., "Chiefs", "Yankees", "Lakers")
- bet_type: Type of bet (e.g., "moneyline", "spread", "over", "under", "props")
- line: Betting line (e.g., "-6.5", "+150", "47.5")
- sport: Sport mentioned (e.g., "NFL", "MLB", "NBA")

Sports mappings (The Odds API keys):
- NFL → "americanfootball_nfl"
- MLB → "baseball_mlb"
- NBA → "basketball_nba"
- NHL → "icehockey_nhl"
- College Football → "americanfootball_ncaaf"

IMPORTANT: Always return valid JSON matching this schema:
{
  "intent": "analyze_specific_bets|request_suggestions|lookup_odds|general_question",
  "sport": "americanfootball_nfl|baseball_mlb|basketball_nba|null",
  "confidence": 0.0-1.0,
  "entities": [
    {
      "type": "player|team|bet_type|line|sport",
      "value": "the extracted value",
      "sport_inferred": "sport key or null",
      "confidence": 0.0-1.0
    }
  ],
  "suggested_queries": [
    {
      "query_type": "player_props|team_odds|game_odds|suggestions",
      "sport": "sport key or null",
      "team_name": "team name or null",
      "player_name": "player name or null",
      "market": "h2h|spreads|totals|null",
      "params": {}
    }
  ],
  "reasoning": "brief explanation of your extraction"
}"""
    
    def _format_extraction_prompt(
        self,
        message: str,
        conversation_history: Optional[List[Dict[str, Any]]] = None
    ) -> str:
        """Format the user prompt for extraction."""
        prompt_parts = []
        
        # Add conversation history if available
        if conversation_history and len(conversation_history) > 0:
            prompt_parts.append("Previous conversation context:")
            for msg in conversation_history[-3:]:  # Last 3 messages for context
                role = msg.get('role', 'unknown')
                content = msg.get('content', '')[:200]  # Truncate long messages
                prompt_parts.append(f"{role.upper()}: {content}")
            prompt_parts.append("")
        
        # Add current message
        prompt_parts.append(f"Current user message: {message}")
        prompt_parts.append("")
        prompt_parts.append("Extract the betting intent and return JSON:")
        
        return "\n".join(prompt_parts)
    
    def _parse_extraction_result(self, result: Dict[str, Any], original_message: str) -> BettingQuery:
        """Parse the LLM's extraction result into a BettingQuery object."""
        try:
            # Parse entities
            entities = []
            for ent in result.get("entities", []):
                entities.append(ExtractedEntity(
                    type=EntityType(ent["type"]),
                    value=ent["value"],
                    sport_inferred=ent.get("sport_inferred"),
                    confidence=ent.get("confidence", 1.0)
                ))
            
            # Parse suggested queries
            suggested_queries = []
            for query in result.get("suggested_queries", []):
                suggested_queries.append(SuggestedApiQuery(
                    query_type=ApiQueryType(query["query_type"]),
                    sport=query.get("sport"),
                    team_name=query.get("team_name"),
                    player_name=query.get("player_name"),
                    market=query.get("market"),
                    params=query.get("params", {})
                ))
            
            # Create BettingQuery
            return BettingQuery(
                intent=BettingIntent(result["intent"]),
                sport=result.get("sport"),
                confidence=result.get("confidence", 1.0),
                entities=entities,
                suggested_queries=suggested_queries,
                reasoning=result.get("reasoning")
            )
            
        except Exception as e:
            print(f"Failed to parse extraction result: {e}")
            return self._create_fallback_query(original_message)
    
    def _create_fallback_query(self, message: str) -> BettingQuery:
        """
        Create a fallback query when extraction fails.
        
        Does basic heuristic parsing as a backup.
        """
        # Check for common patterns
        message_lower = message.lower()
        
        # Check if asking for suggestions
        if any(word in message_lower for word in ["suggest", "good parlay", "recommend", "what should"]):
            intent = BettingIntent.REQUEST_SUGGESTIONS
            sport = self._detect_sport_from_text(message)
            suggested_queries = [
                SuggestedApiQuery(
                    query_type=ApiQueryType.SUGGESTIONS,
                    sport=sport or "americanfootball_nfl",
                    params={"num_legs": 3}
                )
            ]
        # Check if asking about specific odds
        elif any(word in message_lower for word in ["odds", "line", "spread"]):
            intent = BettingIntent.LOOKUP_ODDS
            sport = self._detect_sport_from_text(message)
            suggested_queries = []
        # Check if has specific bets (commas or "and")
        elif ',' in message or ' and ' in message_lower:
            intent = BettingIntent.ANALYZE_SPECIFIC
            sport = self._detect_sport_from_text(message)
            suggested_queries = []
        else:
            # Default to general question
            intent = BettingIntent.GENERAL_QUESTION
            sport = None
            suggested_queries = []
        
        return BettingQuery(
            intent=intent,
            sport=sport,
            confidence=0.5,  # Low confidence for fallback
            entities=[],
            suggested_queries=suggested_queries,
            reasoning="Fallback extraction due to LLM failure"
        )
    
    def _detect_sport_from_text(self, text: str) -> Optional[str]:
        """
        Detect sport from text using keyword matching.
        
        This is a simple fallback when LLM extraction fails.
        """
        text_lower = text.lower()
        
        # Check sport mappings
        for keyword, sport in self._sport_mappings.items():
            if keyword in text_lower:
                return sport
        
        # Check explicit sport mentions
        if "nfl" in text_lower or "football" in text_lower:
            return "americanfootball_nfl"
        elif "mlb" in text_lower or "baseball" in text_lower:
            return "baseball_mlb"
        elif "nba" in text_lower or "basketball" in text_lower:
            return "basketball_nba"
        elif "nhl" in text_lower or "hockey" in text_lower:
            return "icehockey_nhl"
        
        # Default to NFL if nothing detected
        return None


# ============================================================================
# Service Singleton
# ============================================================================

# Global query extraction service instance
_query_extraction_service: Optional[QueryExtractionService] = None


def get_query_extraction_service() -> QueryExtractionService:
    """
    Get or create the global query extraction service instance.
    
    This is used as a FastAPI dependency.
    
    Returns:
        Singleton QueryExtractionService instance
    """
    global _query_extraction_service
    if _query_extraction_service is None:
        _query_extraction_service = QueryExtractionService()
    return _query_extraction_service

