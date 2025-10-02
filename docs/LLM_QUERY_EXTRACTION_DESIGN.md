# LLM Query Extraction Design

## Problem Statement

The current odds integration has a critical gap: it doesn't intelligently extract betting intent from natural language. The system only works if users format their messages in very specific ways (e.g., "Chiefs -6.5, Cowboys ML").

### Current Issues

1. **Naive Parsing**: Only triggers if message contains commas or "and"
2. **No Entity Extraction**: Doesn't understand "I want to bet on Aaron Judge" → extract player name
3. **No Intent Recognition**: Can't distinguish between:
   - "What's a good parlay?" (needs suggestions)
   - "Chiefs -6.5, Cowboys ML" (needs analysis of specific bets)
   - "Should I bet on the Yankees game?" (needs odds lookup)
4. **No Sport Detection**: Doesn't infer sport from context (e.g., Aaron Judge → MLB)
5. **Missing Data**: Results in empty odds data being sent to the analysis LLM

### Example of Current Failure

**User Input**: "Hey I want to bet on Aaron Judge"

**Current Behavior**:
```json
{
  "legs": [
    {
      "bet_type": "unknown",
      "original_text": "Hey I want to bet on Aaron Judge"
    }
  ],
  "num_legs": 1,
  "sport": "americanfootball_nfl",
  "fetched_at": "2025-10-01T19:37:37.327713",
  "requests_remaining": 471
}
```

No actual odds data fetched!

---

## Proposed Solution: Two-Stage LLM Pipeline

### Stage 1: Intent & Entity Extraction (LLM)

Use a fast LLM to extract structured betting intent from natural language.

**Input**: User's raw message + conversation history

**Output**: Structured query object
```json
{
  "intent": "analyze_specific_bets|request_suggestions|lookup_odds|general_question",
  "sport": "americanfootball_nfl|baseball_mlb|basketball_nba|...",
  "confidence": 0.95,
  "entities": [
    {
      "type": "player|team|bet_type|line",
      "value": "Aaron Judge",
      "sport_inferred": "baseball_mlb",
      "bet_context": "props|moneyline|spread|total"
    }
  ],
  "suggested_queries": [
    {
      "query_type": "player_props",
      "player_name": "Aaron Judge",
      "sport": "baseball_mlb",
      "market": "home_runs|hits|..."
    }
  ]
}
```

**Prompt Strategy**:
```
You are a betting query parser. Extract structured information from user messages.

User: "I want to bet on Aaron Judge"

Extract:
1. Intent: What does the user want? (analyze, suggest, lookup, question)
2. Sport: Infer from context (Aaron Judge → MLB)
3. Entities: Players, teams, bet types mentioned
4. Queries: Specific API queries needed to get relevant odds

Return JSON with extraction results.
```

### Stage 2: Odds Enrichment (API)

Use the extracted entities to make targeted API calls.

**For player props**:
1. Detect sport from player name
2. Find upcoming games featuring that player
3. Fetch player prop markets (if available)
4. Fallback to team odds if props unavailable

**For team bets**:
1. Find games featuring the team
2. Fetch relevant markets (h2h, spreads, totals)
3. Return current odds

**For suggestions**:
1. Fetch all games in relevant sport
2. Get best odds across bookmakers
3. Let analysis LLM suggest parlays

---

## Implementation Plan

### 1. Create Query Extraction Service

**File**: `backend/app/services/query_extraction_service.py`

```python
class QueryExtractionService:
    """
    Extracts structured betting queries from natural language using LLM.
    """
    
    async def extract_betting_intent(
        self,
        message: str,
        conversation_history: Optional[List[Dict]] = None
    ) -> BettingQuery:
        """
        Parse user message to extract betting intent and entities.
        
        Returns:
            Structured query with intent, entities, and API query suggestions
        """
        pass
    
    async def detect_sport_from_entity(
        self,
        entity: str,
        entity_type: str
    ) -> Optional[str]:
        """
        Detect sport from player/team name.
        
        Examples:
        - "Aaron Judge" → "baseball_mlb"
        - "Chiefs" → "americanfootball_nfl"
        - "Lakers" → "basketball_nba"
        """
        pass
```

### 2. Enhance Odds Service

**File**: `backend/app/services/odds_service.py`

Add new methods:

```python
def find_player_props(
    self,
    player_name: str,
    sport_key: str
) -> Optional[Dict[str, Any]]:
    """
    Find player prop markets for a specific player.
    
    Note: The Odds API has limited player props.
    May need to expand to other APIs in future.
    """
    pass

def get_suggestions_for_sport(
    self,
    sport_key: str,
    num_legs: int = 3
) -> List[Dict[str, Any]]:
    """
    Get suggested parlay legs based on current odds.
    
    Returns popular/favorable bets for parlay building.
    """
    pass
```

### 3. Update Chat Flow

**File**: `backend/app/api/routes/chat.py`

Replace naive parsing (lines 255-278) with:

```python
# Stage 1: Extract betting intent using LLM
query_extraction = await query_extraction_service.extract_betting_intent(
    chat_request.message,
    conversation_history=previous_messages
)

# Stage 2: Enrich with odds based on extracted queries
enriched_odds = None
if query_extraction.intent in ['analyze_specific_bets', 'lookup_odds']:
    # Fetch specific odds for mentioned entities
    enriched_odds = await odds_service.enrich_from_queries(
        query_extraction.suggested_queries
    )
elif query_extraction.intent == 'request_suggestions':
    # Get suggestions for parlay building
    enriched_odds = await odds_service.get_suggestions_for_sport(
        query_extraction.sport,
        num_legs=3
    )
# else: general_question → no odds needed

# Stage 3: Send to analysis LLM with enriched odds
async for chunk in stream_parlay_analysis(
    chat_request.message,
    enriched_odds,
    query_context=query_extraction
):
    yield chunk
```

### 4. Models & Schemas

**File**: `backend/app/models/schemas.py`

Add new schema types:

```python
class BettingIntent(str, Enum):
    ANALYZE_SPECIFIC = "analyze_specific_bets"
    REQUEST_SUGGESTIONS = "request_suggestions"
    LOOKUP_ODDS = "lookup_odds"
    GENERAL_QUESTION = "general_question"

class EntityType(str, Enum):
    PLAYER = "player"
    TEAM = "team"
    BET_TYPE = "bet_type"
    LINE = "line"

class ExtractedEntity(BaseModel):
    type: EntityType
    value: str
    sport_inferred: Optional[str] = None
    confidence: float = 1.0

class BettingQuery(BaseModel):
    intent: BettingIntent
    sport: Optional[str] = None
    confidence: float
    entities: List[ExtractedEntity]
    suggested_queries: List[Dict[str, Any]]
```

---

## Example Flows

### Example 1: Player Props

**User**: "I want to bet on Aaron Judge"

**Stage 1 - Query Extraction**:
```json
{
  "intent": "lookup_odds",
  "sport": "baseball_mlb",
  "confidence": 0.95,
  "entities": [
    {
      "type": "player",
      "value": "Aaron Judge",
      "sport_inferred": "baseball_mlb"
    }
  ],
  "suggested_queries": [
    {
      "query_type": "player_props",
      "player_name": "Aaron Judge",
      "sport": "baseball_mlb"
    },
    {
      "query_type": "team_odds",
      "team_name": "New York Yankees",
      "sport": "baseball_mlb"
    }
  ]
}
```

**Stage 2 - Odds Enrichment**:
- Fetch Yankees upcoming games
- Try to get Aaron Judge props (if available)
- Fallback to team odds

**Stage 3 - Analysis**:
LLM receives actual odds data and can provide meaningful analysis.

### Example 2: Parlay Suggestions

**User**: "what's a good parlay for this weekend?"

**Stage 1 - Query Extraction**:
```json
{
  "intent": "request_suggestions",
  "sport": null,
  "confidence": 0.90,
  "entities": [],
  "suggested_queries": [
    {
      "query_type": "suggestions",
      "timeframe": "weekend",
      "num_legs": 3
    }
  ]
}
```

**Stage 2 - Odds Enrichment**:
- Fetch popular games across NFL, NBA, etc.
- Get best odds for favorable bets
- Return suggestions

**Stage 3 - Analysis**:
LLM builds parlay suggestions with real odds.

### Example 3: Specific Parlay Analysis

**User**: "Chiefs -6.5, Cowboys ML, over 47"

**Stage 1 - Query Extraction**:
```json
{
  "intent": "analyze_specific_bets",
  "sport": "americanfootball_nfl",
  "confidence": 0.99,
  "entities": [
    {"type": "team", "value": "Chiefs"},
    {"type": "bet_type", "value": "spread"},
    {"type": "line", "value": "-6.5"},
    {"type": "team", "value": "Cowboys"},
    {"type": "bet_type", "value": "moneyline"},
    {"type": "line", "value": "47"},
    {"type": "bet_type", "value": "total_over"}
  ],
  "suggested_queries": [
    {
      "query_type": "team_odds",
      "team_name": "Chiefs",
      "market": "spreads"
    },
    {
      "query_type": "team_odds",
      "team_name": "Cowboys",
      "market": "h2h"
    }
  ]
}
```

**Stage 2 - Odds Enrichment**:
- Fetch current odds for each bet
- Compare user's lines to current lines
- Get implied probabilities

**Stage 3 - Analysis**:
LLM provides detailed risk analysis with real data.

---

## Technical Considerations

### LLM Model Selection for Query Extraction

**Requirements**:
- Fast (< 500ms response time)
- Good at structured output / JSON
- Cost-effective (called on every message)

**Options**:
1. **OpenAI GPT-4o-mini** - Fast, cheap, great JSON mode
2. **Anthropic Claude Haiku** - Fast, good reasoning
3. **Local/Self-hosted** - Llama 3.1 8B (if hosting cost < API cost)

**Recommendation**: Start with GPT-4o-mini for speed and structured output.

### Caching Strategy

- Cache sport detection (player name → sport) in Redis
- Cache query extractions for identical messages (1 hour TTL)
- Reuse existing odds caching (already implemented)

### Error Handling

1. **Query extraction fails**: Fallback to naive parsing (current behavior)
2. **Odds API fails**: Continue with empty odds, let LLM explain limitation
3. **Sport detection fails**: Default to NFL or ask user to specify

### Cost Estimation

**Per request**:
- Query extraction LLM: ~$0.001 (1K tokens @ GPT-4o-mini pricing)
- Odds API: Free tier = 500 requests/month
- Analysis LLM: ~$0.01 (W&B Inference)

**Total**: ~$0.011 per analyzed parlay

**For 1000 users/month at 10 requests each**:
- Query extraction: $10
- Odds API: Free (5,000 requests < 10,000 limit)
- Analysis: $100

**Total**: ~$110/month (very affordable)

---

## Testing Strategy

### Unit Tests

1. **Query Extraction**:
   - Test various natural language inputs
   - Verify correct intent classification
   - Check entity extraction accuracy
   - Test sport inference

2. **Odds Enrichment**:
   - Test player props lookup
   - Test team odds lookup
   - Test suggestion generation
   - Test error handling

### Integration Tests

1. **End-to-End Flow**:
   - Send natural language → verify odds fetched
   - Test different intents
   - Test conversation context

### Manual Testing Scenarios

```python
test_messages = [
    "I want to bet on Aaron Judge",
    "what's a good parlay for this weekend?",
    "Chiefs -6.5, Cowboys ML",
    "Should I bet on the Lakers game tonight?",
    "Give me a 3-leg NFL parlay",
    "What are the odds for the Yankees game?",
]
```

---

## Migration Plan

### Phase 1: Add Query Extraction (No Breaking Changes)

1. Implement `QueryExtractionService`
2. Add alongside existing parsing (both run)
3. Log comparison of results
4. Gather metrics on accuracy

### Phase 2: Integrate with Odds Service

1. Add new odds service methods
2. Update chat endpoint to use extraction
3. Keep fallback to naive parsing

### Phase 3: Enhanced Analysis

1. Pass query context to analysis LLM
2. Improve prompts with structured data
3. Add conversation memory

### Phase 4: Remove Naive Parsing

1. Remove old comma-splitting logic
2. Fully rely on LLM extraction
3. Monitor for regressions

---

## Future Enhancements

### 1. Multi-Sport Intelligence

- Detect sport automatically from context
- Support NBA, MLB, NHL in addition to NFL
- Cross-sport parlays

### 2. Advanced Entity Resolution

- Team nickname resolution ("Niners" → "San Francisco 49ers")
- Player team lookup (fetch from sports API)
- Historical context (remember user's favorite teams)

### 3. Conversation Memory

- Track betting preferences
- Remember previous parlays
- Personalized suggestions

### 4. Line Shopping

- Compare odds across multiple bookmakers
- Show best available odds
- Alert on line movements

### 5. Player Props Expansion

- Integrate additional player props APIs
- Support complex prop bets
- Same-game parlays

---

## Success Metrics

### Accuracy Metrics

- **Intent classification accuracy**: > 95%
- **Entity extraction accuracy**: > 90%
- **Sport detection accuracy**: > 95%
- **Odds enrichment success rate**: > 80%

### User Experience Metrics

- **Response time**: < 2 seconds for full analysis
- **User satisfaction**: > 4.5/5 stars
- **Conversion rate**: % of messages that get meaningful analysis

### System Metrics

- **API usage efficiency**: Stay within free tier limits
- **Cache hit rate**: > 50% for odds data
- **Error rate**: < 5%

---

## Summary

The two-stage LLM pipeline solves the critical gap in our odds integration:

1. **Stage 1**: LLM extracts structured intent and entities from natural language
2. **Stage 2**: API fetches relevant odds based on extracted queries
3. **Stage 3**: Analysis LLM provides data-driven insights

This enables users to interact naturally while ensuring the system fetches actual, relevant odds data for meaningful analysis.

**Next Steps**:
1. Implement `QueryExtractionService` with OpenAI GPT-4o-mini
2. Add new methods to `OddsService` for player props and suggestions
3. Update chat endpoint to use extraction pipeline
4. Add comprehensive tests
5. Monitor and iterate based on user feedback

