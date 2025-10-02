# Draft Killer - Setup Guide

This guide will walk you through setting up the Draft Killer application for local development.

**Now using `uv` for blazing-fast Python package management! 🚀**

## Prerequisites

Before you begin, ensure you have the following installed:

- **Node.js 18+** and **npm**
- **Python 3.11+**
- **Docker Desktop** (for PostgreSQL)
- **Git**

You'll also need:
- A **Weights & Biases** account and API key (for LLM integration)

**Note:** `uv` will be installed automatically by the setup script if not present.

---

## Step 1: Clone and Navigate to Project

```bash
cd /path/to/draft-killer
```

---

## Step 2: Database Setup

### Option A: Local PostgreSQL

1. Install PostgreSQL if not already installed
2. Create a database:

```bash
createdb draft_killer
```

3. Note your connection string:
```
postgresql://username:password@localhost:5432/draft_killer
```

### Option B: Hosted PostgreSQL (Recommended for Production)

Use one of these services:
- **Neon** (https://neon.tech) - Serverless PostgreSQL
- **Supabase** (https://supabase.com) - PostgreSQL with built-in tools
- **Railway** (https://railway.app) - Simple PostgreSQL hosting

Create a database and note the connection URL.

---

## Step 3: Backend Setup

### 1. Navigate to backend directory

```bash
cd backend
```

### 2. Create virtual environment with uv

```bash
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

### 3. Install dependencies with uv

```bash
uv pip install -e ".[dev]"
```

This installs all production and development dependencies from `pyproject.toml`.

### 4. Create environment file

Create a `.env` file in the `backend/` directory:

```bash
# Copy the example (if it exists) or create new
touch .env
```

Add the following content (replace with your actual values):

```env
# Database Configuration
DATABASE_URL=postgresql://user:password@localhost:5432/draft_killer
DATABASE_URL_ASYNC=postgresql+asyncpg://user:password@localhost:5432/draft_killer

# Security (IMPORTANT: Change this!)
SECRET_KEY=your-very-secure-secret-key-here-use-openssl-rand-hex-32
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440

# Weights & Biases Weave
WANDB_API_KEY=your-wandb-api-key-here
WEAVE_PROJECT=draft-killer

# Application Settings
ENVIRONMENT=development
DEBUG=True
CORS_ORIGINS=http://localhost:3000,http://127.0.0.1:3000

# Rate Limiting
RATE_LIMIT_PER_MINUTE=60
AUTH_RATE_LIMIT_PER_MINUTE=10

# Logging
LOG_LEVEL=INFO
```

**Important:** Generate a secure SECRET_KEY:
```bash
openssl rand -hex 32
```

### 5. Initialize the database

```bash
# Create initial migration
alembic revision --autogenerate -m "Initial schema"

# Apply migrations
alembic upgrade head
```

### 6. Run the backend

```bash
uvicorn app.main:app --reload
```

The backend should now be running at `http://localhost:8000`

Test it by visiting: `http://localhost:8000/health`

---

## Step 4: Frontend Setup

### 1. Open a new terminal and navigate to frontend directory

```bash
cd frontend
```

### 2. Install dependencies

```bash
pnpm install
# or: npm install
```

### 3. Create environment file

Create a `.env.local` file in the `frontend/` directory:

```bash
touch .env.local
```

Add the following:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### 4. Run the frontend

```bash
pnpm dev
# or: npm run dev
```

The frontend should now be running at `http://localhost:3000`

---

## Step 5: Verify Everything Works

1. Open your browser to `http://localhost:3000`
2. Click "Sign up" to create an account
3. Register with an email and password
4. You should be redirected to the chat interface
5. Try submitting a test parlay description:

```
I'm thinking about a 3-leg parlay:
- Lakers to win against the Celtics
- Over 220.5 total points
- LeBron to score 25+ points
```

6. You should see a streaming response with analysis

---

## Common Issues and Solutions

### Backend Issues

**Issue:** `alembic: command not found`
- **Solution:** Make sure your virtual environment is activated

**Issue:** `sqlalchemy.exc.OperationalError: could not connect to server`
- **Solution:** Verify PostgreSQL is running and the DATABASE_URL is correct

**Issue:** `SECRET_KEY validation error`
- **Solution:** Generate a new key with `openssl rand -hex 32`

**Issue:** `ImportError: No module named 'weave'`
- **Solution:** Re-install dependencies: `uv pip install -e ".[dev]"`

### Frontend Issues

**Issue:** `Module not found: Can't resolve '@/...'`
- **Solution:** Ensure you're in the `frontend/` directory and dependencies are installed

**Issue:** `Failed to fetch` when logging in
- **Solution:** Verify the backend is running and NEXT_PUBLIC_API_URL is correct

**Issue:** React hooks errors
- **Solution:** Make sure you're using React 18+ and Next.js 14+

---

## Development Workflow

### Running Both Services

I recommend using two terminal windows:

**Terminal 1 (Backend):**
```bash
cd backend
source .venv/bin/activate
uvicorn app.main:app --reload
```

Or simply use:
```bash
make start-backend
```

**Terminal 2 (Frontend):**
```bash
cd frontend
npm run dev
```

Or simply use:
```bash
make start-frontend
```

### Making Database Changes

1. Modify models in `backend/app/models/database.py`
2. Generate migration:
   ```bash
   cd backend
   source .venv/bin/activate
   alembic revision --autogenerate -m "Description of change"
   ```
3. Review the generated migration in `backend/alembic/versions/`
4. Apply migration:
   ```bash
   alembic upgrade head
   # Or: make db-migrate
   ```

### Adding Python Dependencies

**Add a new package:**
```bash
cd backend
uv add package-name
```

**Add a development dependency:**
```bash
cd backend
uv add --dev package-name
```

**Update all dependencies:**
```bash
cd backend
uv pip install -U -e ".[dev]"
# Or: make update-deps
```

### Styling Changes

All visual styling is in `frontend/src/styles/theme.ts`

To change colors, fonts, spacing, etc., just edit this file. Changes will apply across the entire app.

---

## Next Steps

Once you have the app running locally:

1. **Test the full user flow** - registration, login, chat
2. **Review the code** - familiarize yourself with the architecture
3. **Read DEVELOPMENT_NOTES.md** - understand design decisions
4. **Plan your next feature** - refer to IMPLEMENTATION_OUTLINE.md for roadmap

---

## Getting Help

- Check `DEVELOPMENT_NOTES.md` for architectural decisions
- Review `IMPLEMENTATION_OUTLINE.md` for the full project plan
- Check the backend API docs at `http://localhost:8000/docs`
- Review FastAPI docs: https://fastapi.tiangolo.com/
- Review Next.js docs: https://nextjs.org/docs
- Review Weave docs: https://docs.wandb.ai/guides/inference/

---

## Environment Variables Reference

### Backend (.env)

| Variable | Description | Example |
|----------|-------------|---------|
| DATABASE_URL | Sync PostgreSQL connection | `postgresql://user:pass@localhost/db` |
| DATABASE_URL_ASYNC | Async PostgreSQL connection | `postgresql+asyncpg://user:pass@localhost/db` |
| SECRET_KEY | JWT signing key (32+ chars) | Generate with `openssl rand -hex 32` |
| WANDB_API_KEY | Weights & Biases API key | From your W&B account |
| WEAVE_PROJECT | W&B project name | `draft-killer` |
| CORS_ORIGINS | Allowed origins (comma-separated) | `http://localhost:3000` |
| ENVIRONMENT | Environment name | `development` or `production` |
| DEBUG | Debug mode | `True` or `False` |

### Frontend (.env.local)

| Variable | Description | Example |
|----------|-------------|---------|
| NEXT_PUBLIC_API_URL | Backend API URL | `http://localhost:8000` |

---

**You're all set! Happy coding! 🚀**

