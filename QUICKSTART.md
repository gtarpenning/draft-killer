# Draft Killer - Quick Start Guide

**Get up and running in one command! 🚀**

**Now powered by `uv` - the fastest Python package manager! ⚡**

---

## One-Command Setup

```bash
./setup.sh
```

That's it! The script will:
- ✅ Check prerequisites (Docker, Python, Node.js)
- ✅ Install `uv` automatically if not present
- ✅ Start PostgreSQL in Docker
- ✅ Create Python virtual environment with `uv`
- ✅ Install all backend dependencies (blazing fast!)
- ✅ Run database migrations
- ✅ Install all frontend dependencies
- ✅ Create environment files
- ✅ Generate secure SECRET_KEY

---

## Prerequisites

You only need these installed:

1. **Docker Desktop** - https://www.docker.com/products/docker-desktop
2. **Python 3.11+** - https://www.python.org/downloads/
3. **Node.js 18+** - https://nodejs.org/

---

## First Time Setup

### 1. Run the setup script

```bash
./setup.sh
```

### 2. Add your W&B API key

Edit `backend/.env` and add your Weights & Biases API key:

```bash
WANDB_API_KEY=your-actual-key-here
```

Get your key from: https://wandb.ai/authorize

### 3. Start development servers

**Option A: Use the convenience script (recommended)**

```bash
./start-dev.sh
```

This starts both backend and frontend together!

**Option B: Manual (two terminals)**

Terminal 1 (Backend):
```bash
cd backend
source .venv/bin/activate
uvicorn app.main:app --reload
```

Terminal 2 (Frontend):
```bash
cd frontend
npm run dev
```

### 4. Open your browser

- **Frontend:** http://localhost:3000
- **Backend API Docs:** http://localhost:8000/docs
- **Health Check:** http://localhost:8000/health

### 5. Create an account and test!

1. Click "Sign up" on the login page
2. Create an account with email/password
3. Try analyzing a parlay:

```
I'm thinking about a 3-leg parlay:
- Lakers to win against the Celtics
- Over 220.5 total points
- LeBron to score 25+ points
```

---

## Subsequent Runs

After the initial setup, just run:

```bash
./start-dev.sh
```

The script automatically:
- Starts PostgreSQL if it's not running
- Activates the Python virtual environment
- Starts both backend and frontend

---

## Useful Commands

### Database Management

**View database logs:**
```bash
docker logs draft_killer_db
```

**Connect to database:**
```bash
docker exec -it draft_killer_db psql -U draft_killer -d draft_killer
```

**Stop database:**
```bash
docker-compose down
```

**Reset database (WARNING: deletes all data):**
```bash
docker-compose down -v
./setup.sh
```

### Database Migrations

**Create a new migration:**
```bash
cd backend
source .venv/bin/activate
alembic revision --autogenerate -m "Description of changes"
```

**Apply migrations:**
```bash
alembic upgrade head
```

**Rollback migration:**
```bash
alembic downgrade -1
```

### Python Dependencies (with uv 🚀)

**Add a new package:**
```bash
cd backend
uv add package-name
```

**Add a dev dependency:**
```bash
cd backend
uv add --dev package-name
```

**Update all dependencies to latest:**
```bash
cd backend
uv pip install -U -e ".[dev]"
# Or use the make command:
make update-deps
```

**Install dependencies manually:**
```bash
cd backend
uv pip install -e ".[dev]"
```

> **Why uv?** It's 10-100x faster than pip, handles all the venv management, and uses modern `pyproject.toml` instead of `requirements.txt`!

### Frontend Dependencies

**Add a new package:**
```bash
cd frontend
npm install package-name
```

**Update dependencies:**
```bash
npm install
```

---

## Environment Variables

### Backend (`backend/.env`)

| Variable | Description | Where to Get |
|----------|-------------|--------------|
| `DATABASE_URL` | PostgreSQL connection (set automatically) | N/A |
| `SECRET_KEY` | JWT signing key (generated automatically) | N/A |
| `WANDB_API_KEY` | W&B API key for LLM | https://wandb.ai/authorize |
| `WEAVE_PROJECT` | W&B project name | Default: `draft-killer` |

### Frontend (`frontend/.env.local`)

| Variable | Description | Default |
|----------|-------------|---------|
| `NEXT_PUBLIC_API_URL` | Backend API URL | `http://localhost:8000` |

---

## Troubleshooting

### "Docker not found"
Install Docker Desktop: https://www.docker.com/products/docker-desktop

### "Port 5432 already in use"
Another PostgreSQL instance is running. Either:
- Stop it: `brew services stop postgresql` (on macOS)
- Or change the port in `docker-compose.yml`

### "Port 8000 already in use"
Another service is using port 8000. Stop it or change the backend port.

### "Database connection failed"
Check if PostgreSQL is running:
```bash
docker ps | grep draft_killer_db
```

If not running, start it:
```bash
docker start draft_killer_db
```

### "Module not found" errors (Python)
Make sure virtual environment is activated:
```bash
cd backend
source .venv/bin/activate
```

Or reinstall dependencies:
```bash
cd backend
uv pip install -e ".[dev]"
```

### "Module not found" errors (Node)
Reinstall dependencies:
```bash
cd frontend
rm -rf node_modules
npm install
```

### Backend crashes immediately
Check if you've added your `WANDB_API_KEY` to `backend/.env`

### Frontend can't connect to backend
1. Check backend is running: http://localhost:8000/health
2. Check `NEXT_PUBLIC_API_URL` in `frontend/.env.local`

---

## Architecture Quick Reference

```
draft-killer/
├── backend/          # FastAPI + PostgreSQL
│   ├── app/         # Application code
│   ├── alembic/     # Database migrations
│   └── venv/        # Python virtual environment
│
├── frontend/        # Next.js + React
│   └── src/         # Source code
│
├── docker-compose.yml   # PostgreSQL configuration
├── setup.sh            # One-command setup
└── start-dev.sh        # Start development servers
```

---

## What the Setup Script Does

1. **Checks prerequisites** - Docker, Python 3.11+, Node.js 18+, and installs `uv` if missing
2. **Starts PostgreSQL** - In Docker container (persisted data)
3. **Backend setup:**
   - Creates virtual environment with `uv` (`backend/.venv/`)
   - Installs Python dependencies using `uv` (super fast!)
   - Generates secure `SECRET_KEY`
   - Creates `backend/.env` from template
   - Runs database migrations
4. **Frontend setup:**
   - Installs npm dependencies
   - Creates `frontend/.env.local` from template
5. **Creates `start-dev.sh`** - Convenience script to start both servers

### Why uv?

- ⚡ **10-100x faster** than pip
- 🦀 Written in Rust (blazingly fast)
- 📦 Uses modern `pyproject.toml`
- 🔒 Better dependency resolution
- 🎯 Drop-in replacement for pip
- 🚀 Made by Astral (creators of Ruff)

---

## Why Docker for PostgreSQL?

**Benefits:**
- ✅ Works on any OS (macOS, Linux, Windows)
- ✅ No complex PostgreSQL installation
- ✅ Isolated from system packages
- ✅ Easy to reset/delete
- ✅ Consistent across team members
- ✅ Data persists between restarts

**The database data is stored in a Docker volume**, so your data persists even if you restart the container.

---

## Development Workflow

1. **First time:** `./setup.sh`
2. **Every day:** `./start-dev.sh`
3. **Add features:** Edit code, changes auto-reload
4. **Database changes:** Create migration, run `alembic upgrade head`
5. **Done for the day:** `Ctrl+C` to stop servers

---

## Next Steps

Once you have it running:

1. ✅ Read the full [SETUP_GUIDE.md](SETUP_GUIDE.md) for detailed information
2. ✅ Check [DEVELOPMENT_NOTES.md](DEVELOPMENT_NOTES.md) for architecture decisions
3. ✅ Review [IMPLEMENTATION_OUTLINE.md](IMPLEMENTATION_OUTLINE.md) for the roadmap
4. ✅ Explore the code and start building!

---

## Getting Help

- **Setup issues?** Check [SETUP_GUIDE.md](SETUP_GUIDE.md)
- **Architecture questions?** See [DEVELOPMENT_NOTES.md](DEVELOPMENT_NOTES.md)
- **API documentation?** Visit http://localhost:8000/docs

---

**Happy coding! 🚀**

