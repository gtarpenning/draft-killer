# Sportsbook API Research & Findings

## Executive Summary

**Recommendation:** Use **The Odds API** (the-odds-api.com) for MVP - it has a generous free tier, excellent documentation, and covers all major sports.

**Backup Option:** OddsJam API or manual scraping using existing open-source tools if API limits are exceeded.

---

## 1. API Options (Recommended Approach)

### Option A: The Odds API ⭐ **RECOMMENDED**
- **Website:** https://the-odds-api.com/
- **Free Tier:** 500 requests/month free
- **Coverage:** 20+ sports, 250+ bookmakers, 500+ markets
- **Data Available:**
  - Pre-match odds (moneyline, spreads, totals)
  - Player props
  - Futures markets
  - Live/in-play odds
  - Historical odds data
- **Response Format:** JSON
- **Latency:** Low (<1s typically)
- **Pricing (Paid Tiers):**
  - Starter: ~$30-50/month for more requests
  - Professional: Custom pricing
- **Pros:**
  - Free tier is generous for MVP testing
  - Excellent documentation with code examples
  - Very popular (widely used, well-maintained)
  - Simple REST API
  - Covers all major US sports (NFL, NBA, MLB, NHL, NCAA)
- **Cons:**
  - Free tier may not be enough for production at scale
  - Need to manage API key securely
- **Best For:** MVP and early development

### Option B: OddsJam API
- **Website:** https://oddsjam.com/odds-api
- **Coverage:** 100+ sportsbooks
- **Data Available:**
  - Real-time odds
  - Player props
  - Alternate markets
  - Injury data
  - Schedules, rankings, scores
- **Pricing:** Contact for pricing (no public free tier mentioned)
- **Pros:**
  - Very comprehensive data
  - Includes injury data (valuable for analysis)
  - Includes schedules and scores
- **Cons:**
  - No obvious free tier
  - May be expensive for MVP
- **Best For:** Production if budget allows

### Option C: Wager API
- **Website:** https://wagerapi.com/
- **Coverage:** NFL, NCAA, NBA
- **Data Available:**
  - Real-time odds (spreads, totals, player props)
  - Futures markets
- **Pricing:** Not publicly listed
- **Pros:**
  - Focus on major US sports
  - Real-time data
- **Cons:**
  - Limited sport coverage
  - No public pricing
- **Best For:** US sports-focused applications with budget

### Option D: SportBet API
- **Website:** https://www.sportapi.net/
- **Coverage:** Multiple sports and championships
- **Data Available:**
  - Pre-match and live odds
  - Sports, championships, matches, teams
  - Odds coefficients
- **Pricing:** Trial available, paid plans
- **Pros:**
  - Fast API
  - Good international coverage
- **Cons:**
  - Less documentation than The Odds API
  - Pricing not transparent
- **Best For:** International sports coverage

### Option E: Odds API (.io)
- **Website:** https://odds-api.io/
- **Coverage:** 250+ bookmakers, 20+ sports
- **Free Trial:** 10-day trial available
- **Data Available:**
  - Real-time odds from 250+ bookmakers
  - Multiple markets
- **Pricing:** Subscription-based after trial
- **Pros:**
  - Extensive bookmaker coverage
  - High uptime
- **Cons:**
  - No permanent free tier (only 10-day trial)
  - May be expensive
- **Best For:** Production with budget for API costs

### Option F: OpticOdds
- **Website:** https://opticodds.com/sports-betting-api/
- **Coverage:** 100+ sportsbooks
- **Data Available:**
  - Real-time odds
  - Player props
  - Alternate markets
  - Injury data
  - Schedules, rankings, scores
- **Pricing:** Contact for pricing
- **Pros:**
  - Comprehensive data similar to OddsJam
  - Includes contextual data (injuries, etc.)
- **Cons:**
  - Pricing not transparent
- **Best For:** Full-featured production app

---

## 2. Web Scraping Options (Fallback Approach)

### Option A: Betting-Scraper (GitHub)
- **Repository:** https://github.com/SishaarGamblr/Betting-Scraper
- **Description:** Service to fetch betting lines from various websites
- **Current Support:** DraftKings
- **Technology:** Python
- **Pros:**
  - Free and open-source
  - Already built for DraftKings
  - Can extend to other sportsbooks
- **Cons:**
  - Legal/ethical concerns (check ToS)
  - Requires maintenance when sites change
  - May get IP blocked
  - Data quality not guaranteed
  - Slower than APIs
- **Best For:** Proof of concept or backup when APIs fail

### Option B: OddsHarvester (GitHub)
- **Repository:** https://github.com/jordantete/OddsHarvester
- **Description:** Python app to scrape sports betting data from oddsportal.com
- **Technology:** Python, BeautifulSoup/Selenium
- **Pros:**
  - Free and open-source
  - Scrapes from oddsportal.com (aggregates multiple bookmakers)
  - Can get historical data
- **Cons:**
  - Same legal/ethical concerns
  - Website structure changes break scrapers
  - Slower and less reliable than APIs
  - Risk of IP bans
- **Best For:** Historical data collection or research

### Option C: Custom Scraping
- **Approach:** Build your own scraper for specific sportsbooks
- **Target Sites:**
  - DraftKings
  - FanDuel
  - BetMGM
  - Caesars
- **Technology:** Python (BeautifulSoup, Scrapy, Selenium)
- **Pros:**
  - Full control over data collection
  - Free (no API costs)
  - Can customize to exact needs
- **Cons:**
  - **Legal risks:** Most sportsbooks prohibit scraping in ToS
  - High maintenance burden
  - Ethical concerns
  - Can get IP blocked/banned
  - Slow and unreliable
  - Data format inconsistent
- **Best For:** Last resort only

---

## 3. Comparison Matrix

| Provider | Free Tier | Sports Coverage | Data Quality | Ease of Use | Best For |
|----------|-----------|----------------|--------------|-------------|----------|
| **The Odds API** | ✅ 500 req/mo | ⭐⭐⭐⭐⭐ 20+ sports | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | **MVP/Production** |
| OddsJam | ❌ No free tier | ⭐⭐⭐⭐⭐ 100+ books | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | Production |
| Wager API | ❌ No free tier | ⭐⭐⭐ US sports only | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | US-focused apps |
| Odds API (.io) | ⚠️ 10-day trial | ⭐⭐⭐⭐⭐ 250+ books | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | Production |
| Betting-Scraper | ✅ Free/OSS | ⭐⭐ DraftKings only | ⭐⭐⭐ | ⭐⭐ | Proof of concept |
| OddsHarvester | ✅ Free/OSS | ⭐⭐⭐ Via oddsportal | ⭐⭐⭐ | ⭐⭐ | Historical data |
| Custom Scraping | ✅ Free | Varies | ⭐⭐ | ⭐ | Last resort |

---

## 4. Recommended Implementation Plan

### Phase 1: MVP (Use The Odds API Free Tier)
1. Sign up for The Odds API free account
2. Get API key (500 requests/month free)
3. Implement basic integration:
   - Fetch upcoming games for specific sports
   - Get current odds (moneyline, spread, total)
   - Display in chat interface
4. Cache responses aggressively to stay within limits
5. Store fetched data in PostgreSQL to reduce API calls

**500 requests/month = ~16 requests/day**
- This is enough for MVP testing
- Implement smart caching (cache odds for 15-30 minutes)
- One request can fetch multiple games

### Phase 2: Optimize & Scale
1. Implement intelligent caching strategy:
   - Cache odds data for 15-30 minutes
   - Store in Redis or PostgreSQL
   - Only fetch when cache expires
2. Monitor usage with dashboard
3. If hitting limits, upgrade to paid tier (~$30-50/month)

### Phase 3: Production
1. Evaluate if The Odds API paid tier meets needs
2. If not, consider:
   - OddsJam for more comprehensive data
   - Multiple API providers for redundancy
   - Hybrid approach (API + selective scraping for specific data)

---

## 5. Legal & Ethical Considerations

### Using APIs (Recommended)
- ✅ **Legal:** APIs are provided for this purpose
- ✅ **Ethical:** You're paying for the service (or using free tier as intended)
- ✅ **Reliable:** Terms of service are clear
- ✅ **Supportable:** You can get help if issues arise

### Web Scraping (Use with Caution)
- ⚠️ **Legal Gray Area:** Many sites prohibit scraping in ToS
- ⚠️ **Ethical Concerns:** Using data without permission
- ⚠️ **Risk of Blocking:** IP bans, legal threats
- ⚠️ **No Support:** You're on your own if it breaks

**Recommendation:** Only use scraping as a last resort or for data not available via APIs. Always check the website's `robots.txt` and Terms of Service.

---

## 6. Technical Implementation Notes

### The Odds API Integration (Recommended)

**Endpoint Examples:**
```
GET https://api.the-odds-api.com/v4/sports
GET https://api.the-odds-api.com/v4/sports/{sport}/odds
GET https://api.the-odds-api.com/v4/sports/{sport}/events
```

**Authentication:**
- API key in query parameter: `?apiKey=YOUR_KEY`

**Sports Available:**
- americanfootball_nfl
- basketball_nba
- baseball_mlb
- icehockey_nhl
- americanfootball_ncaaf
- basketball_ncaab
- And many more...

**Markets Available:**
- h2h (moneyline)
- spreads
- totals (over/under)
- player_props
- futures

**Response Format:**
```json
{
  "id": "event_id",
  "sport_key": "americanfootball_nfl",
  "sport_title": "NFL",
  "commence_time": "2024-10-06T17:00:00Z",
  "home_team": "Kansas City Chiefs",
  "away_team": "Las Vegas Raiders",
  "bookmakers": [
    {
      "key": "draftkings",
      "title": "DraftKings",
      "markets": [
        {
          "key": "h2h",
          "outcomes": [
            {
              "name": "Kansas City Chiefs",
              "price": -250
            },
            {
              "name": "Las Vegas Raiders",
              "price": +210
            }
          ]
        }
      ]
    }
  ]
}
```

### Caching Strategy

**Cache Timing:**
- Pre-game odds: Cache for 30 minutes
- Live odds: Cache for 1-5 minutes (if needed)
- Historical data: Cache indefinitely

**Implementation:**
```python
# Pseudo-code for caching
def get_odds(sport, event_id):
    cache_key = f"odds:{sport}:{event_id}"
    cached = redis.get(cache_key)
    
    if cached:
        return cached
    
    # Fetch from API
    data = fetch_from_odds_api(sport, event_id)
    
    # Cache for 30 minutes
    redis.setex(cache_key, 1800, data)
    
    return data
```

**Database Storage:**
Store fetched odds in PostgreSQL for:
- Historical analysis
- Reducing API calls
- Offline functionality
- Cost tracking

---

## 7. Cost Projections

### The Odds API Costs

**Free Tier:**
- 500 requests/month
- Good for: MVP, testing, low-volume apps
- Limitations: ~16 requests/day

**Paid Tiers (Estimated):**
- Starter: $30-50/month for ~5,000-10,000 requests
- Professional: $100-300/month for ~50,000+ requests
- Enterprise: Custom pricing for unlimited

**Cost Optimization:**
- Aggressive caching (30 min for pre-game odds)
- Batch requests when possible
- Only fetch data when users request it
- Store data in database for reuse

**Example:** 
- 1,000 active users/month
- Each user checks 5 parlays
- Each parlay checks 3 games
- = 15,000 API calls without caching
- With 30-min caching: ~500-1,000 calls (most users check similar games)
- **Cost: Free tier or ~$30-50/month**

---

## 8. Next Steps

1. ✅ **Research Complete** (this document)
2. **Test The Odds API:**
   - Sign up for free account
   - Get API key
   - Run test script (see `test_sportsbook_api.py`)
   - Verify data quality and response times
3. **Implement in Backend:**
   - Create FastAPI service for odds fetching
   - Implement caching layer (Redis or PostgreSQL)
   - Add rate limiting to stay within free tier
4. **Integrate with LLM:**
   - Pass odds data to Weave prompts
   - Enhance parlay analysis with real-time odds
   - Show alternatives based on current lines
5. **Monitor Usage:**
   - Track API calls per day
   - Alert when approaching limit
   - Decide when to upgrade to paid tier

---

## 9. Alternative Data Sources (Future Consideration)

- **ESPN API:** Scores, schedules, stats (no odds)
- **SportsData.io:** Stats and scores (some odds data)
- **MySportsFeeds:** Historical stats and data
- **Weather APIs:** For weather-based analysis (AccuWeather, OpenWeather)
- **Injury APIs:** RotoWire, ESPN

---

## Final Recommendation

**For MVP: Use The Odds API**
- Free tier is perfect for getting started
- Excellent documentation and support
- Easy integration
- Can upgrade when needed
- No legal/ethical concerns

**Implementation Timeline:**
- Week 1: Sign up, test API, implement basic integration
- Week 2: Add caching and database storage
- Week 3: Integrate with LLM for enhanced analysis
- Week 4: Monitor usage and optimize

**Budget:** $0 for MVP, $30-50/month when scaling to production

---

**Document created:** October 1, 2024  
**Last updated:** October 1, 2024  
**Status:** Ready for implementation


