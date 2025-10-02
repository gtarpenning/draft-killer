# Sports Betting API Testing Guide

This directory contains everything you need to test and integrate sports betting data into Draft Killer.

## 📁 Files Created

1. **SPORTSBOOK_API_RESEARCH.md** - Comprehensive research on all available APIs
2. **test_sportsbook_api.py** - Test script to validate The Odds API
3. **sample_api_response.json** - Example API response structure
4. **requirements_test.txt** - Python dependencies for testing

## 🚀 Quick Start

### Step 1: Get API Key (Free)

1. Go to https://the-odds-api.com/
2. Sign up for a free account
3. Get your API key (500 requests/month free)

### Step 2: Setup Environment

```bash
# Create .env file
echo "ODDS_API_KEY=your_api_key_here" > .env

# Install dependencies
pip install -r requirements_test.txt
```

### Step 3: Run Tests

```bash
python test_sportsbook_api.py
```

This will:
- ✅ Validate your API key
- ✅ Fetch available sports
- ✅ Get upcoming NFL games with odds
- ✅ Compare odds across multiple bookmakers
- ✅ Simulate a parlay analysis scenario
- ✅ Show data structure for backend integration

## 📊 What You'll See

The test script will display:

1. **Available Sports** - All sports you can bet on
2. **Upcoming Games** - Real games with current odds
3. **Multiple Bookmakers** - Compare DraftKings, FanDuel, BetMGM, etc.
4. **Parlay Simulation** - How to analyze a 3-leg parlay
5. **API Usage** - Remaining requests in your quota

## 💰 API Costs

- **Free Tier:** 500 requests/month (~16 per day)
- **Paid Tier:** ~$30-50/month for 5,000-10,000 requests
- **Optimization:** With caching, free tier can support 100s of users

## 🔧 Integration Tips

### Caching Strategy

```python
# Cache odds for 30 minutes
CACHE_TTL = 1800  # seconds

def get_odds_with_cache(sport, event_id):
    cache_key = f"odds:{sport}:{event_id}"
    
    # Try cache first
    cached = redis.get(cache_key)
    if cached:
        return json.loads(cached)
    
    # Fetch from API
    odds = fetch_from_api(sport, event_id)
    
    # Cache it
    redis.setex(cache_key, CACHE_TTL, json.dumps(odds))
    
    return odds
```

### Database Storage

Store fetched odds in PostgreSQL to:
- Reduce API calls
- Enable historical analysis
- Support offline functionality
- Track odds movements

### Rate Limiting

```python
# Track API usage
def track_api_call():
    today = datetime.now().date()
    key = f"api_calls:{today}"
    
    calls = redis.incr(key)
    redis.expire(key, 86400)  # 24 hours
    
    if calls > 16:  # Daily limit on free tier
        raise RateLimitError("Daily API limit reached")
```

## 📝 Sample API Response

Check `sample_api_response.json` to see:
- Full response structure
- All available data fields
- Bookmaker format
- Market types (moneyline, spreads, totals)

## 🎯 Next Steps for Draft Killer

1. **Backend Service**
   ```
   backend/app/services/odds_service.py
   - OddsService class
   - Caching layer
   - Parlay parsing
   ```

2. **Database Schema**
   ```sql
   CREATE TABLE sportsbook_odds (
     id UUID PRIMARY KEY,
     event_id VARCHAR,
     sport VARCHAR,
     home_team VARCHAR,
     away_team VARCHAR,
     commence_time TIMESTAMP,
     odds_data JSONB,
     fetched_at TIMESTAMP
   );
   ```

3. **LLM Integration**
   - Fetch odds for user's parlay
   - Pass to Weave LLM with prompt
   - Return analysis with alternatives

4. **Frontend Display**
   - Show current odds in chat
   - Highlight line movements
   - Display odds comparison

## 🔍 Testing Without API Key

If you want to explore the code without an API key:
- Review `sample_api_response.json` for data structure
- Read `SPORTSBOOK_API_RESEARCH.md` for full analysis
- Check the test script code to see implementation examples

## ⚠️ Important Notes

- **Free Tier Limit:** 500 requests/month
- **Caching is Critical:** Cache for 30 minutes minimum
- **Batch Requests:** Fetch all games for a sport at once
- **Monitor Usage:** Track API calls to avoid overages
- **Upgrade When Ready:** ~$30-50/month for production scale

## 📚 Additional Resources

- The Odds API Docs: https://the-odds-api.com/liveapi/guides/v4/
- Draft Killer Implementation: See IMPLEMENTATION_OUTLINE.md
- Sports Coverage: 20+ sports, 250+ bookmakers
- Markets: Moneyline, spreads, totals, props, futures

## 🎉 Success Criteria

After running tests, you should have:
- ✅ Validated API key works
- ✅ Seen real betting odds data
- ✅ Understood response structure
- ✅ Confirmed API meets project needs
- ✅ Ready to integrate into FastAPI backend

---

**Status:** Ready for implementation  
**Recommended API:** The Odds API (free tier)  
**Cost for MVP:** $0  
**Cost for Production:** $0-50/month depending on scale


