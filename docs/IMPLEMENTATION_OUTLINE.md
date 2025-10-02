# Draft Killer - Implementation Outline

## Project Overview
Draft Killer is a sports betting analysis tool that helps users understand the risks associated with their parlays (combination betting lines). The tool provides comprehensive analysis including risks, potential alternatives, outcomes, and suggestions for improvement.

## MVP Scope

**Core User Flow:**
1. User creates an account (email/password)
2. User loads the chat page (minimal, typewriter-style interface)
3. User writes up a parlay (combination of betting lines)
4. System returns a comprehensive AI-generated response outlining:
   - Risks associated with the parlay
   - Potential alternatives
   - Possible outcomes
   - Suggestions for improvement

**Design Philosophy:**
- Minimal, distraction-free interface
- Old-time text editor aesthetic (white background, typewriter text)
- Simple input field and message display
- Easy to modify styling via centralized theme configuration
- Focus on content and analysis, not flashy UI

---

## Design Decisions - FINALIZED

### 1. Frontend Framework
**Decision:** Next.js
- Optimal Vercel integration
- SSR capabilities
- Built-in routing and API routes

### 2. Database
**Decision:** PostgreSQL
- Robust relational database
- Excellent support for complex queries
- Scalable for future growth

### 3. Authentication Method
**Decision:** Email/Password (Basic)
- Simple implementation for MVP
- Can be enhanced with OAuth later
- Custom implementation using JWT

### 4. Sportsbook APIs
**Decision:** DEFERRED
- Requires additional research
- Will be implemented in Phase 2
- Focus on core chat functionality first

### 5. LLM Model
**Decision:** Weights & Biases Weave Inference
- Model selection handled entirely by W&B Weave
- Reference: https://docs.wandb.ai/guides/inference/
- Flexible model switching through Weave configuration

### 6. UI/UX Design
**Decision:** Minimal "Old-Time Text Editor" Aesthetic
- Simple white background
- Typewriter-style text from bot
- Basic input field
- Monospace or classic serif font
- No distracting UI elements
- **Styling must be factored out** for easy theming/changes later
- CSS variables or theme configuration file for all visual properties

---

## Implementation Phases

## Phase 1: MVP Core Features

### 1. Project Setup & Infrastructure
**Deliverables:**
- Repository structure (monorepo or separate repos)
- Package management setup (pnpm/npm for frontend, poetry/pip for backend)
- Environment variable configuration
- Vercel deployment configuration for both frontend and backend
- Git repository initialization
- `.gitignore` and `.env.example` files

**Files to Create:**
```
draft-killer/
├── frontend/
│   ├── package.json
│   ├── next.config.js (or equivalent)
│   ├── .env.example
│   └── vercel.json
├── backend/
│   ├── requirements.txt
│   ├── pyproject.toml (if using poetry)
│   ├── .env.example
│   └── vercel.json
├── README.md
└── .gitignore
```

---

### 2. Backend (FastAPI)
**Deliverables:**
- FastAPI application structure
- CORS middleware configuration
- Health check endpoint
- Chat/streaming endpoint
- Request/response models with Pydantic
- Error handling middleware

**Files to Create:**
```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── api/
│   │   ├── __init__.py
│   │   ├── routes/
│   │   │   ├── __init__.py
│   │   │   ├── chat.py
│   │   │   ├── auth.py
│   │   │   └── health.py
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py
│   │   └── security.py
│   ├── models/
│   │   ├── __init__.py
│   │   ├── schemas.py
│   │   └── database.py
│   └── services/
│       ├── __init__.py
│       └── llm_service.py
└── requirements.txt
```

**Key Endpoints:**
- `GET /health` - Health check
- `POST /api/chat/stream` - Streaming chat endpoint
- `POST /api/auth/register` - User registration
- `POST /api/auth/login` - User login
- `GET /api/chat/history` - Get chat history

---

### 3. Frontend (Chat Interface)
**Deliverables:**
- Minimal chat UI with typewriter aesthetic
- Message input component (simple text field)
- Message display component (user and assistant)
- Streaming response handler with typewriter effect
- Loading states (minimal, text-based)
- Error boundaries and error display
- Theme configuration system for easy style changes

**Files to Create:**
```
frontend/
├── src/
│   ├── app/
│   │   ├── page.tsx (main chat page)
│   │   ├── layout.tsx
│   │   ├── login/
│   │   │   └── page.tsx
│   │   └── register/
│   │       └── page.tsx
│   ├── components/
│   │   ├── Chat/
│   │   │   ├── ChatInterface.tsx
│   │   │   ├── MessageList.tsx
│   │   │   ├── MessageInput.tsx
│   │   │   ├── Message.tsx
│   │   │   └── TypewriterText.tsx
│   │   └── Auth/
│   │       ├── LoginForm.tsx
│   │       └── RegisterForm.tsx
│   ├── styles/
│   │   ├── theme.ts (centralized theme configuration)
│   │   └── globals.css
│   ├── lib/
│   │   ├── api.ts
│   │   └── utils.ts
│   ├── hooks/
│   │   ├── useChat.ts
│   │   ├── useAuth.tsx
│   │   └── useTypewriter.ts
│   └── types/
│       └── index.ts
└── package.json
```

**Design System (Factored Out for Easy Changes):**
```typescript
// theme.ts structure
export const theme = {
  colors: {
    background: '#FFFFFF',
    text: '#000000',
    input: '#F5F5F5',
    border: '#E0E0E0',
  },
  fonts: {
    body: "'Courier Prime', 'Courier New', monospace",
    // Alternative: "'Crimson Text', 'Georgia', serif"
  },
  spacing: {
    page: '2rem',
    message: '1.5rem',
  },
  animation: {
    typewriterSpeed: 30, // ms per character
  }
}
```

**Key Features:**
- Minimalist design with no distractions
- Typewriter animation for bot responses
- Simple text-based loading indicator
- Basic markdown support (optional)
- Auto-scrolling to latest message
- Clean, readable typography

**Styling Architecture (Easy to Modify):**

All visual styling is centralized in a single theme configuration file, making it trivial to change the entire look and feel of the application.

```typescript
// src/styles/theme.ts
export const theme = {
  colors: {
    background: '#FFFFFF',
    text: '#000000',
    textSecondary: '#666666',
    inputBackground: '#F5F5F5',
    inputBorder: '#E0E0E0',
    accent: '#333333',
  },
  fonts: {
    body: "'Courier Prime', 'Courier New', monospace",
    // Can easily swap to: "'Crimson Text', 'Georgia', serif"
    size: {
      base: '16px',
      large: '18px',
      small: '14px',
    },
    lineHeight: '1.6',
  },
  spacing: {
    page: '2rem',
    messageGap: '1.5rem',
    inputPadding: '1rem',
  },
  animation: {
    typewriterSpeed: 30, // milliseconds per character
    fadeIn: '0.3s ease-in',
  },
  layout: {
    maxWidth: '800px', // keep content readable
    inputHeight: '60px',
  }
} as const;

export type Theme = typeof theme;
```

**Usage Example:**
```typescript
// Any component can import and use the theme
import { theme } from '@/styles/theme';

const Message = styled.div`
  color: ${theme.colors.text};
  font-family: ${theme.fonts.body};
  margin-bottom: ${theme.spacing.messageGap};
`;
```

**To Change the Entire Look:**
Simply edit `theme.ts` values - no need to hunt through component files. Want a different color scheme? Update the colors object. Want a different font? Change the fonts.body value. Want faster/slower typewriter effect? Adjust animation.typewriterSpeed.

---

### 4. LLM Integration (Weave Inference)
**Deliverables:**
- Weights & Biases Weave SDK integration
- Weave Inference API setup (model agnostic)
- Prompt templates for parlay analysis
- Streaming response implementation
- Token counting and cost tracking (via Weave)
- Rate limiting
- Error handling and retries

**Reference Documentation:**
- W&B Weave Inference: https://docs.wandb.ai/guides/inference/

**Key Components:**
- Weave client initialization with API key
- Model selection handled by Weave configuration (not hardcoded)
- Prompt engineering for sports betting analysis
- System prompt defining assistant behavior
- User prompt template for parlay input
- Streaming response handling for typewriter effect

**Implementation Notes:**
- Model choice is entirely managed by W&B Weave Inference service
- Application should be model-agnostic
- Use Weave's built-in tracing and logging
- Leverage Weave's prompt versioning for iteration

**Prompt Structure:**
```
System: You are an expert sports betting analyst specializing in risk assessment...
User: Analyze this parlay: [user input]
Assistant: [structured analysis including risks, alternatives, outcomes, suggestions]
```

---

### 5. Authentication System
**Deliverables:**
- User registration flow
- Login flow
- Password hashing (bcrypt or argon2)
- JWT token generation and validation
- Session management
- Protected routes (frontend and backend)
- Logout functionality

**Database Tables:**
```sql
users:
  - id (UUID, primary key)
  - email (unique)
  - password_hash
  - created_at
  - updated_at
  - last_login
```

**Security Features:**
- Password strength validation
- Email validation
- CSRF protection
- XSS protection
- Rate limiting on auth endpoints

---

### 6. Database Schema Design
**Deliverables:**
- Database connection setup
- ORM configuration (SQLAlchemy or similar)
- Migration system (Alembic)
- Initial migrations

**Tables:**

```sql
users:
  - id (UUID, PK)
  - email (unique, indexed)
  - password_hash
  - created_at
  - updated_at
  - last_login

conversations:
  - id (UUID, PK)
  - user_id (FK to users)
  - title (auto-generated from first message)
  - created_at
  - updated_at

messages:
  - id (UUID, PK)
  - conversation_id (FK to conversations)
  - role (enum: 'user', 'assistant')
  - content (text)
  - metadata (JSONB) - for storing tokens, cost, etc.
  - created_at

sportsbook_data (for Phase 2):
  - id (UUID, PK)
  - sport
  - event_name
  - odds_data (JSONB)
  - bookmaker
  - fetched_at
  - created_at
```

---

## Phase 2: Enhanced Features

### 7. Chat History Management
**Deliverables:**
- Save conversations to database
- Retrieve user's conversation history
- Load specific conversation
- Delete conversation
- Archive conversation
- Search through chat history

**API Endpoints:**
- `GET /api/conversations` - List all conversations
- `GET /api/conversations/{id}` - Get specific conversation
- `DELETE /api/conversations/{id}` - Delete conversation
- `PATCH /api/conversations/{id}` - Update conversation (title, archive)

**Frontend Components:**
- Conversation list sidebar
- Search/filter conversations
- Conversation preview
- Delete confirmation modal

---

### 8. Sportsbook Data Integration
**Status:** DEFERRED - Requires Research

**Research Tasks:**
- Evaluate sportsbook API options (The Odds API, RapidAPI, direct integrations)
- Compare pricing, coverage, and data quality
- Determine required data points (lines, props, live odds, etc.)
- Assess rate limits and caching requirements
- Review legal/compliance requirements

**Future Deliverables (Post-Research):**
- API client for chosen sportsbook data provider
- Real-time odds fetching
- Odds display UI components
- Data caching strategy
- Automatic data refresh
- Error handling for API failures

**Planned Features:**
- Display current betting lines in chat interface
- Show odds from multiple bookmakers
- Highlight line movements
- Filter by sport/league
- Search for specific games/events

**Note:** For MVP, users will manually input parlay details. Sportsbook data integration will enhance the experience but is not required for core functionality.

---

### 9. Historical Data System
**Deliverables:**
- Historical data schema
- Data ingestion pipeline
- Historical analysis queries
- UI for viewing historical trends
- Data visualization components

**Database Tables:**
```sql
historical_odds:
  - id (UUID, PK)
  - event_id
  - sport
  - league
  - team_home
  - team_away
  - odds_data (JSONB)
  - actual_outcome (JSONB)
  - game_date
  - created_at

betting_results:
  - id (UUID, PK)
  - event_id (FK)
  - bet_type
  - line
  - odds
  - result (win/loss/push)
  - recorded_at
```

**Data Pipeline:**
- Scheduled jobs to fetch and store historical data
- Data normalization and cleaning
- Backfill scripts for historical data
- Data export/import utilities

---

## Phase 3: Stretch Goals

### 10. Agentic Workflow System
**Deliverables:**
- Tool calling framework
- Multiple tool implementations
- Tool orchestration logic
- Logging and monitoring

**Tools to Implement:**

1. **Sportsbook Data Lookup Tool**
   - Input: Team names, sport, date
   - Output: Current odds from multiple bookmakers

2. **Historical Performance Tool**
   - Input: Team/player, time range
   - Output: Historical performance stats

3. **Weather API Tool**
   - Input: Game location, date
   - Output: Weather conditions

4. **Team Stats Tool**
   - Input: Team name, season
   - Output: Season stats, rankings, trends

5. **Player Stats Tool**
   - Input: Player name, sport
   - Output: Recent performance, injury status

**Implementation:**
```python
class AgenticWorkflow:
    - available_tools: List[Tool]
    - tool_selector(query) -> Tool
    - execute_tool(tool, params) -> Result
    - combine_results(results) -> Analysis
```

---

### 11. Advanced Analytics & Recommendations
**Deliverables:**
- Statistical analysis engine
- Alternative bet suggestion algorithm
- Risk scoring system
- Probability calculations
- Value bet identification

**Features:**

1. **Historical Performance Analysis**
   - Win/loss records in similar scenarios
   - Team performance against specific opponents
   - Home/away splits
   - Recent form analysis

2. **Alternative Betting Suggestions**
   - Similar parlays with better odds
   - Lower-risk alternatives
   - Higher-upside alternatives
   - Single bet vs parlay comparison

3. **Risk Scoring**
   - Calculate parlay risk score (0-100)
   - Individual leg risk assessment
   - Correlation analysis (dependent events)
   - Historical success rate of similar parlays

4. **Probability Calculations**
   - Implied probability from odds
   - True probability estimates
   - Expected value calculations
   - Kelly Criterion recommendations

5. **Contextual Factors**
   - Weather impact on games
   - Injury reports
   - Home/away advantages
   - Rest days between games
   - Hot/cold streaks

**Analytics Service:**
```python
class AnalyticsService:
    - calculate_risk_score(parlay) -> float
    - suggest_alternatives(parlay) -> List[Alternative]
    - calculate_probabilities(bet) -> Probability
    - calculate_expected_value(bet) -> float
    - analyze_correlation(legs) -> float
```

---

## Technology Stack Summary

### Frontend
- **Framework:** Next.js 14+ (App Router)
- **Language:** TypeScript
- **Styling:** CSS Modules or plain CSS with theme.ts configuration
- **State Management:** React Context (minimal state needs)
- **HTTP Client:** Fetch API (native)
- **Streaming:** Fetch with ReadableStream for typewriter effect
- **Fonts:** Courier Prime or Crimson Text (configurable)

### Backend
- **Framework:** FastAPI
- **Language:** Python 3.11+
- **Database:** PostgreSQL
- **ORM:** SQLAlchemy 2.0
- **Migrations:** Alembic
- **Auth:** JWT with python-jose
- **Password Hashing:** bcrypt
- **Validation:** Pydantic v2

### LLM & AI
- **LLM Integration:** Weights & Biases Weave Inference
- **Model:** Managed by Weave (model-agnostic implementation)
- **Prompt Management:** Weave prompts and versioning
- **Monitoring:** Weave tracing and logging
- **Documentation:** https://docs.wandb.ai/guides/inference/

### External APIs
- **Sportsbook Data:** DEFERRED to Phase 2 (research required)
- **Other APIs:** To be determined based on Phase 3 requirements

### Deployment
- **Hosting:** Vercel (both frontend and backend)
- **Database Hosting:** Neon, Supabase, or Railway (PostgreSQL)
- **Environment Management:** Vercel Environment Variables
- **CI/CD:** Vercel Git integration

### Development Tools
- **Version Control:** Git
- **Package Manager:** npm or pnpm (frontend), pip or poetry (backend)
- **Linting:** ESLint (frontend), ruff (backend)
- **Formatting:** Prettier (frontend), black (backend)
- **Type Checking:** TypeScript (frontend), mypy (backend)

---

## Deployment Architecture

```
User Browser
    ↓
Vercel Edge Network
    ↓
Next.js Frontend (Vercel)
    ↓
FastAPI Backend (Vercel Serverless)
    ↓
┌─────────────┬────────────────────┐
│  PostgreSQL │  W&B Weave API     │
│  Database   │  (LLM Inference)   │
└─────────────┴────────────────────┘
```

**MVP Architecture Notes:**
- Simple, serverless architecture
- No caching layer for MVP (can add Redis later if needed)
- No external sportsbook APIs initially
- PostgreSQL for all persistent data
- Weave handles LLM inference and monitoring

---

## Development Workflow

### Phase 1: MVP (Weeks 1-4)
1. Week 1: Setup + Backend foundation + Database
2. Week 2: Frontend chat interface + Auth
3. Week 3: LLM integration + Streaming
4. Week 4: Testing + Deployment + Bug fixes

### Phase 2: Enhanced Features (Weeks 5-8)
1. Week 5: Chat history + UI improvements
2. Week 6: Sportsbook API integration
3. Week 7: Historical data system
4. Week 8: Testing + Performance optimization

### Phase 3: Stretch Goals (Weeks 9-12)
1. Weeks 9-10: Agentic workflow implementation
2. Weeks 11-12: Advanced analytics + Recommendations

---

## Testing Strategy

### Backend Testing
- Unit tests for services and utilities
- Integration tests for API endpoints
- Database migration tests
- Load testing for streaming endpoints

### Frontend Testing
- Component unit tests (Jest + React Testing Library)
- Integration tests for user flows
- E2E tests (Playwright or Cypress)
- Visual regression tests

### LLM Testing
- Prompt evaluation with test cases
- Response quality monitoring
- Cost tracking
- Latency benchmarks

---

## Security Considerations

1. **Authentication & Authorization**
   - Secure password storage
   - JWT token expiration
   - Refresh token rotation
   - Rate limiting on auth endpoints

2. **API Security**
   - CORS configuration
   - API key management
   - Rate limiting
   - Input validation and sanitization

3. **Data Security**
   - Encrypted database connections
   - Sensitive data encryption at rest
   - Secure environment variable management
   - API key rotation policy

4. **Frontend Security**
   - XSS protection
   - CSRF tokens
   - Content Security Policy
   - Secure cookie settings

---

## Monitoring & Observability

1. **Application Monitoring**
   - Error tracking (Sentry or similar)
   - Performance monitoring
   - User analytics

2. **LLM Monitoring**
   - Weave tracing for all LLM calls
   - Token usage tracking
   - Cost monitoring
   - Response quality metrics

3. **Infrastructure Monitoring**
   - Vercel deployment status
   - Database performance
   - API endpoint latency
   - Cache hit rates

---

## Open Questions for Product Owner

1. What is the target user base size for MVP?
2. What is the budget for LLM API calls?
3. Are there specific sports/leagues to focus on initially?
4. Should we support mobile devices from day one?
5. What level of sports betting knowledge should we assume users have?
6. Are there any compliance/legal considerations for sports betting analysis?
7. Should we store actual bet outcomes for learning/improvement?
8. What are the privacy requirements for user data?

---

## Success Metrics

### MVP Success Criteria
- User can create account and log in
- User can submit parlay and receive analysis within 10 seconds
- Chat interface properly displays streaming responses
- 99% uptime
- User can view saved chat history

### Phase 2 Success Criteria
- Real-time odds data displayed accurately
- Historical data available for major sports
- Chat history searchable and filterable
- Sub-3-second page load times

### Phase 3 Success Criteria
- Agentic workflow provides enhanced analysis
- Alternative bet suggestions improve user outcomes
- Risk scoring correlates with actual outcomes
- User engagement increases by 50%

---

## Summary of Key Decisions

### ✅ Finalized Choices
- **Frontend:** Next.js 14+ with TypeScript
- **Backend:** FastAPI with Python 3.11+
- **Database:** PostgreSQL
- **Auth:** Email/password with JWT (basic implementation)
- **LLM:** W&B Weave Inference (model-agnostic)
- **Deployment:** Vercel for both frontend and backend
- **UI Style:** Minimal typewriter aesthetic with centralized theme

### 🚧 Deferred/TBD
- **Sportsbook APIs:** Requires research - deferred to Phase 2
- **Caching Layer:** Not needed for MVP
- **OAuth/Social Login:** Can add later
- **Mobile App:** Not in scope for MVP

### 🎯 MVP Scope (Phase 1)
1. User authentication (register/login)
2. Minimal chat interface with typewriter effect
3. LLM integration via Weave for parlay analysis
4. Basic chat history storage
5. Deploy to Vercel

## Immediate Next Steps for Implementation

### Step 1: Environment Setup
```bash
# Create project structure
mkdir -p frontend backend
cd frontend && npx create-next-app@latest . --typescript --app --no-tailwind
cd ../backend && poetry init (or pip)
```

### Step 2: Backend Foundation
- Set up FastAPI project structure
- Configure PostgreSQL connection
- Create database models (User, Conversation, Message)
- Implement authentication endpoints
- Set up Alembic for migrations

### Step 3: W&B Weave Integration
- Install Weave SDK
- Configure API credentials
- Create chat/streaming endpoint
- Test LLM inference

### Step 4: Frontend Development
- Create theme.ts configuration
- Build minimal chat interface
- Implement typewriter effect
- Connect to backend API
- Add authentication UI

### Step 5: Deployment
- Configure Vercel for frontend
- Configure Vercel for backend (Python runtime)
- Set up PostgreSQL hosting (Neon/Supabase/Railway)
- Configure environment variables
- Deploy and test

### Step 6: Testing & Polish
- Test authentication flow
- Test chat streaming
- Verify typewriter effect
- Ensure responsive design
- Fix any bugs

## Development Priorities

**Priority 1 (Week 1):**
- Backend API structure
- Database setup and migrations
- Basic authentication
- Weave integration

**Priority 2 (Week 2):**
- Frontend chat interface
- Typewriter animation
- Auth UI (login/register)
- API integration

**Priority 3 (Week 3):**
- Chat history
- UI polish
- Error handling
- Deployment configuration

**Priority 4 (Week 4):**
- Testing
- Bug fixes
- Performance optimization
- Documentation

## Reference Documentation

- Next.js: https://nextjs.org/docs
- FastAPI: https://fastapi.tiangolo.com/
- W&B Weave Inference: https://docs.wandb.ai/guides/inference/
- Vercel Deployment: https://vercel.com/docs
- Vercel + FastAPI: https://github.com/vercel/examples/tree/main/python/fastapi
- PostgreSQL + SQLAlchemy: https://docs.sqlalchemy.org/

---

**This document is ready for implementation. All critical design decisions have been made. Begin with Step 1 above.**

