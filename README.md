# Draft Killer

A sports analysis tool that provides comprehensive risk assessment, alternatives, and suggestions for parlays.

![killr-2](https://github.com/user-attachments/assets/0f37bfa2-8e96-463c-8c59-998ada4062b4)


## Overview

Draft Killer helps users understand the risks associated with their parlays through AI-powered analysis. The tool features a minimal, typewriter-style chat interface that provides:
- Risk assessment for betting lines
- Alternative betting suggestions
- Outcome analysis
- Parlay improvement recommendations

## Tech Stack

### Frontend
- **Framework:** Next.js 14+ (App Router)
- **Language:** TypeScript
- **Styling:** Centralized theme configuration (CSS Modules)
- **Deployment:** Vercel

### Backend
- **Framework:** FastAPI
- **Language:** Python 3.11+
- **Package Manager:** uv (blazing fast! 🚀)
- **Database:** PostgreSQL
- **ORM:** SQLAlchemy 2.0
- **Migrations:** Alembic
- **Authentication:** JWT with bcrypt
- **Deployment:** Vercel Serverless

### AI/LLM
- **Provider:** Weights & Biases Weave Inference
- **Model:** Managed by W&B Weave (model-agnostic)
- **Documentation:** [W&B Weave Inference](https://docs.wandb.ai/guides/inference/)

## Project Structure

```
draft-killer/
├── frontend/          # Next.js application
│   ├── src/
│   │   ├── app/      # App router pages
│   │   ├── components/ # React components
│   │   ├── styles/   # Theme configuration
│   │   ├── lib/      # Utilities and API client
│   │   ├── hooks/    # Custom React hooks
│   │   └── types/    # TypeScript type definitions
│   └── package.json
│
├── backend/           # FastAPI application
│   ├── app/
│   │   ├── api/      # API routes
│   │   ├── core/     # Core configuration
│   │   ├── models/   # Database models
│   │   └── services/ # Business logic
│   ├── alembic/      # Database migrations
│   └── pyproject.toml # Dependencies & config
│
├── IMPLEMENTATION_OUTLINE.md  # Detailed implementation plan
├── DEVELOPMENT_NOTES.md       # Implementation decisions and notes
└── README.md                  # This file
```

## Getting Started

### 🚀 Quick Start (Recommended)

**One command to set everything up:**

```bash
./setup.sh
```

This will:
- Install `uv` if not present (fastest Python package manager)
- Start PostgreSQL in Docker
- Create Python virtual environment with `uv`
- Install all dependencies (super fast!)
- Run database migrations
- Create environment files

Then add your W&B API key to `backend/.env` and run:

```bash
./start-dev.sh
```

**Full instructions:** See [docs/QUICKSTART.md](docs/QUICKSTART.md)

---

### Manual Setup

If you prefer to set things up manually, see [docs/SETUP_GUIDE.md](docs/SETUP_GUIDE.md) for detailed instructions.

**Prerequisites:**
- Docker Desktop (for PostgreSQL)
- Python 3.11+
- Node.js 18+
- W&B API key for Weave Inference

## Environment Variables

### Frontend (.env.local)
```
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### Backend (.env)
```
DATABASE_URL=postgresql://user:password@localhost:5432/draft_killer
SECRET_KEY=your-secret-key-here
WANDB_API_KEY=your-wandb-api-key
WEAVE_PROJECT=draft-killer
```

## Development Workflow

### Phase 1: MVP (Current)
- ✅ Project structure and configuration
- 🔄 Backend API with authentication
- 🔄 Database models and migrations
- 🔄 LLM integration with W&B Weave
- 🔄 Minimal chat interface
- 🔄 Typewriter effect for responses
- 🔄 Deployment to Vercel

### Phase 2: Enhanced Features
- Chat history management
- Sportsbook data integration (research required)
- Historical data system

### Phase 3: Stretch Goals
- Agentic workflow with tool calling
- Advanced analytics and recommendations

## Design Philosophy

**Minimal, Distraction-Free Interface**
- Old-time text editor aesthetic
- White background with typewriter text
- Centralized theme configuration for easy style changes
- Focus on content and analysis, not flashy UI

All visual styling is centralized in `frontend/src/styles/theme.ts`, making it trivial to modify the entire look and feel by editing a single configuration file.

## API Documentation

Once the backend is running, visit:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Key Endpoints

- `POST /api/auth/register` - User registration
- `POST /api/auth/login` - User login
- `POST /api/chat/stream` - Streaming chat endpoint for parlay analysis
- `GET /api/chat/history` - Get user's chat history
- `GET /health` - Health check

## Deployment

Both frontend and backend deploy to Vercel:

### Frontend Deployment
```bash
cd frontend
vercel
```

### Backend Deployment
Vercel automatically detects Python and deploys FastAPI as serverless functions.
See [Vercel + FastAPI examples](https://github.com/vercel/examples/tree/main/python/fastapi)

## Testing

### Backend Tests
```bash
cd backend
pytest
```

### Frontend Tests
```bash
cd frontend
pnpm test
```

## Documentation

All documentation is organized in the `docs/` folder:

- **[Quick Start Guide](docs/QUICKSTART.md)** - Get up and running in minutes
- **[Setup Guide](docs/SETUP_GUIDE.md)** - Detailed manual setup instructions
- **[Setup Automation](docs/AUTOMATION_README.md)** - Overview of automation tools
- **[Visual Setup Guide](docs/SETUP_VISUAL_GUIDE.md)** - Diagrams and flowcharts
- **[Development Notes](docs/DEVELOPMENT_NOTES.md)** - Architecture decisions
- **[Implementation Outline](docs/IMPLEMENTATION_OUTLINE.md)** - Complete project roadmap
- **[Implementation Status](docs/IMPLEMENTATION_STATUS.md)** - Current progress
- **[Sportsbook Research](docs/SPORTSBOOK_RESEARCH_COMPLETE.md)** - API research findings


