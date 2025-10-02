# Development Notes

## Project: Draft Killer
**Started:** October 1, 2025  
**Status:** Phase 1 - Initial Setup

---

## Architecture Decisions

### 1. Monorepo Structure
**Decision:** Use a simple monorepo with separate `frontend/` and `backend/` directories  
**Rationale:**
- Simple to manage for a small team/solo developer
- Easy to deploy both parts to Vercel
- Shared documentation and issue tracking
- No need for complex monorepo tools (Nx, Turborepo) at this stage

**Alternative Considered:** Separate repositories  
**Why Not:** Adds overhead for synchronization and deployment coordination

---

### 2. Centralized Theme Configuration
**Decision:** All styling configuration in `frontend/src/styles/theme.ts`  
**Rationale:**
- Makes it trivial to change entire visual design
- No need to hunt through component files for styling
- Easy to experiment with different aesthetics
- Supports future theming features (dark mode, multiple themes)

**Implementation Pattern:**
```typescript
// theme.ts exports a single configuration object
export const theme = {
  colors: { ... },
  fonts: { ... },
  spacing: { ... },
  animation: { ... }
}

// Components import and use the theme
import { theme } from '@/styles/theme';
```

**Benefits:**
- Single source of truth for all visual properties
- Type-safe with TypeScript
- Easy to extend with new properties
- Can be swapped out entirely for rebrand

---

### 3. Model-Agnostic LLM Integration
**Decision:** Use W&B Weave Inference instead of direct OpenAI/Anthropic SDKs  
**Rationale:**
- Model selection and switching handled by Weave
- Built-in tracing and monitoring
- Prompt versioning and management
- Cost tracking out of the box
- Easy to experiment with different models

**Trade-offs:**
- Additional abstraction layer
- Dependency on W&B infrastructure
- Learning curve for Weave API

**Why It's Worth It:**
- Future-proofs the application
- Better observability for production
- Easier to optimize costs by switching models

---

### 4. Database Schema Design Principles

**Users Table:**
- UUID primary keys for security (not sequential integers)
- Email as unique identifier
- Password hash stored with bcrypt
- Timestamps for audit trail

**Conversations Table:**
- Separate from messages for better organization
- Auto-generated titles (future: from first message)
- Soft delete support (future enhancement)

**Messages Table:**
- JSONB metadata column for extensibility
- Stores token counts, costs, model info
- Role-based (user/assistant) for easy context reconstruction
- Foreign key to conversations for proper relationships

**Design Principles:**
- Normalize data appropriately
- Use JSONB for flexible, schema-less data
- Index frequently queried columns
- Plan for soft deletes (don't hard delete user data)

---

### 5. Authentication Strategy

**Decision:** JWT tokens with simple email/password auth for MVP  
**Rationale:**
- Quick to implement
- Stateless (no session storage needed)
- Works well with serverless deployment
- Can add OAuth later without major refactor

**Security Measures:**
- bcrypt for password hashing (cost factor: 12)
- JWT tokens with expiration (24 hours)
- Refresh tokens for extended sessions (future)
- Rate limiting on auth endpoints
- Email validation before registration

**Future Enhancements:**
- OAuth providers (Google, GitHub)
- 2FA/MFA support
- Password reset flow
- Email verification

---

### 6. API Design Patterns

**RESTful Principles:**
- Predictable URL structure: `/api/{resource}/{action}`
- HTTP verbs match intent (GET, POST, PATCH, DELETE)
- Consistent response format
- Proper status codes

**Streaming Endpoint:**
- Uses Server-Sent Events (SSE) for streaming
- Maintains connection for typewriter effect
- Graceful error handling mid-stream
- Token-by-token or chunk-by-chunk delivery

**Error Handling:**
- Consistent error response format
- Appropriate HTTP status codes
- Detailed error messages in development
- Sanitized messages in production

---

### 7. Frontend Component Architecture

**Component Hierarchy:**
```
ChatInterface (page-level)
├── MessageList
│   └── Message (user/assistant variants)
│       └── TypewriterText (for assistant messages)
└── MessageInput
```

**Component Principles:**
- Single responsibility
- Presentational vs. Container components
- Hooks for shared logic
- Props interface for type safety
- Minimal prop drilling (use context where needed)

**State Management:**
- Local state for UI interactions
- React Context for auth state
- Custom hooks for API calls and streaming

---

### 8. Typewriter Effect Implementation

**Decision:** Client-side typewriter effect with streaming from backend  
**Rationale:**
- Better user experience (character-by-character reveal)
- Backend streams tokens as they arrive from LLM
- Frontend controls display speed for consistent UX

**Implementation:**
```typescript
// Backend: Stream tokens as received from LLM
async function* streamResponse() {
  for token in llm_stream:
    yield token

// Frontend: Display streamed tokens with typewriter delay
useTypewriter(streamedText, speed = 30ms)
```

**Adjustable Parameters:**
- Typewriter speed (ms per character)
- Chunk size from backend
- Animation smoothness

---

### 9. Environment Configuration

**Separate Concerns:**
- Frontend: API URLs, public keys
- Backend: Database URLs, secret keys, API keys

**Security:**
- Never commit `.env` files
- Provide `.env.example` templates
- Use Vercel environment variables in production
- Rotate secrets regularly

**Best Practices:**
- Validate required env vars on startup
- Fail fast if critical configs missing
- Document all environment variables

---

### 10. Deployment Strategy

**Vercel for Everything:**
- Frontend: Next.js optimized deployment
- Backend: Python serverless functions
- Automatic deployments from Git
- Preview deployments for PRs
- Environment management built-in

**Database Hosting Options:**
1. **Neon** - Serverless PostgreSQL, auto-scaling
2. **Supabase** - PostgreSQL with built-in APIs
3. **Railway** - Simple PostgreSQL hosting

**Chosen:** TBD based on testing and pricing

---

## Implementation Checkpoints

### Phase 1: MVP Foundation

**Week 1: Backend + Database** ✅ COMPLETED (Oct 1, 2025)
- [x] Project structure created
- [x] FastAPI application setup
- [x] Database models and schemas
- [x] Alembic migrations configured
- [x] Authentication endpoints
- [x] Health check endpoint
- [x] LLM service with W&B Weave
- [x] Streaming chat endpoint

**Week 2: Frontend + Auth UI** ✅ COMPLETED (Oct 1, 2025)
- [x] Next.js project setup
- [x] Theme configuration (centralized in theme.ts)
- [x] Chat interface components
- [x] Typewriter effect hook
- [x] Login/register UI
- [x] API client with streaming support
- [x] Custom React hooks (useAuth, useChat, useTypewriter)

**Week 3: LLM Integration**
- [ ] W&B Weave SDK integration
- [ ] Streaming endpoint
- [ ] Prompt templates
- [ ] Chat history storage
- [ ] Frontend streaming handler

**Week 4: Deployment + Polish**
- [ ] Vercel configuration
- [ ] Database hosting setup
- [ ] Environment variables
- [ ] End-to-end testing
- [ ] Bug fixes

---

## Code Quality Standards

### Python (Backend)
- **Formatting:** black (line length: 88)
- **Linting:** ruff
- **Type Checking:** mypy (strict mode)
- **Documentation:** Google-style docstrings
- **Testing:** pytest with >80% coverage

### TypeScript (Frontend)
- **Formatting:** Prettier
- **Linting:** ESLint (strict config)
- **Type Checking:** TypeScript strict mode
- **Documentation:** TSDoc comments for public APIs
- **Testing:** Jest + React Testing Library

### General Principles
- **DRY:** Don't Repeat Yourself
- **KISS:** Keep It Simple, Stupid
- **YAGNI:** You Aren't Gonna Need It (yet)
- **Separation of Concerns:** Each module has one job
- **Dependency Injection:** For testability
- **Configuration over Code:** Use config files for settings

---

## Testing Strategy

### Backend Testing
```bash
# Unit tests: services, utilities
pytest tests/unit/

# Integration tests: API endpoints
pytest tests/integration/

# Full test suite with coverage
pytest --cov=app --cov-report=html
```

### Frontend Testing
```bash
# Component tests
pnpm test

# E2E tests (future)
pnpm test:e2e
```

### Manual Testing Checklist
- [ ] User registration flow
- [ ] Login flow
- [ ] Chat message submission
- [ ] Streaming response display
- [ ] Typewriter effect
- [ ] Error handling
- [ ] Loading states
- [ ] Responsive design

---

## Performance Considerations

### Backend
- Database query optimization (indexes, selective loading)
- Connection pooling for PostgreSQL
- Async I/O for all network calls
- Caching for frequent queries (future)

### Frontend
- Code splitting for smaller bundles
- Lazy loading for components
- Optimistic UI updates
- Debouncing for input fields
- Memoization for expensive computations

### LLM Calls
- Stream responses for faster perceived performance
- Token limits to control costs
- Rate limiting to prevent abuse
- Caching for common queries (future)

---

## Security Checklist

- [x] `.gitignore` configured for secrets
- [ ] Password hashing with bcrypt
- [ ] JWT token validation
- [ ] CORS configuration
- [ ] Input validation (Pydantic)
- [ ] SQL injection prevention (ORM)
- [ ] XSS prevention (React default escaping)
- [ ] CSRF protection
- [ ] Rate limiting
- [ ] Environment variable validation

---

## Future Considerations

### Phase 2: Enhanced Features
- Sportsbook API integration (requires research)
- Historical data ingestion pipeline
- Advanced chat history features (search, filter, export)
- Multi-conversation support
- Conversation sharing

### Phase 3: Stretch Goals
- Agentic workflow with tool calling
- Real-time odds display
- Weather API integration
- Advanced analytics engine
- Probability calculators
- Kelly Criterion implementation

---

## Open Questions

1. **Database Hosting:** Neon vs. Supabase vs. Railway?
   - Need to test performance and pricing
   - Consider auto-scaling requirements

2. **Sportsbook API:** Which provider?
   - The Odds API, RapidAPI, or direct integrations?
   - Cost, coverage, and data quality comparison needed

3. **Monitoring:** Which error tracking service?
   - Sentry, LogRocket, or Vercel Analytics?
   - Budget and feature requirements

4. **Testing:** E2E test framework?
   - Playwright vs. Cypress?
   - CI/CD integration requirements

---

## Resources

### Documentation
- [FastAPI Docs](https://fastapi.tiangolo.com/)
- [Next.js Docs](https://nextjs.org/docs)
- [W&B Weave Inference](https://docs.wandb.ai/guides/inference/)
- [SQLAlchemy Docs](https://docs.sqlalchemy.org/)
- [Vercel Python Examples](https://github.com/vercel/examples/tree/main/python/fastapi)

### Design Inspiration
- Minimal text editors
- Typewriter aesthetics
- Monospace typography

---

## Change Log

### 2025-10-01: Initial Setup & MVP Core Implementation
- Created complete project structure (frontend + backend)
- Defined architecture decisions
- Set up comprehensive documentation
- Configured development environment

**Backend Completed:**
- FastAPI application with async SQLAlchemy
- PostgreSQL database models (User, Conversation, Message)
- Alembic migration system
- JWT authentication with bcrypt password hashing
- W&B Weave LLM integration
- Streaming chat endpoint with SSE
- Health check and API routes
- Comprehensive error handling
- CORS middleware configuration

**Frontend Completed:**
- Next.js 14 with App Router
- Centralized theme system (theme.ts) for easy styling changes
- TypeScript types matching backend schemas
- API client with streaming support
- Custom hooks: useAuth, useChat, useTypewriter
- Chat interface with typewriter effect
- Authentication forms (login/register)
- Protected routes with automatic redirects
- Responsive, minimal design

**Key Architecture Decisions Implemented:**
1. ✅ Centralized theme configuration - all styling in one file
2. ✅ Model-agnostic LLM via W&B Weave
3. ✅ Async database operations throughout
4. ✅ Streaming responses with SSE for real-time typewriter effect
5. ✅ JWT-based stateless authentication
6. ✅ Comprehensive TypeScript types
7. ✅ Component-based architecture with separation of concerns

**Files Created:** 50+ files including complete backend and frontend implementations

---

**Note:** This document should be updated regularly as implementation progresses and new decisions are made.

