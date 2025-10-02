# Draft Killer - Visual Setup Guide

## 🎯 One-Command Setup Flow

```
                    ./setup.sh
                        │
                        ▼
        ┌───────────────────────────────┐
        │  [1/7] Check Prerequisites    │
        │  ✓ Docker                     │
        │  ✓ Python 3.11+               │
        │  ✓ Node.js 18+                │
        └───────────┬───────────────────┘
                    │
                    ▼
        ┌───────────────────────────────┐
        │  [2/7] Start PostgreSQL       │
        │  - Create container if needed │
        │  - Start if exists            │
        │  - Wait for health check      │
        └───────────┬───────────────────┘
                    │
                    ▼
        ┌───────────────────────────────┐
        │  [3/7] Backend Setup          │
        │  - Create venv/               │
        │  - Install dependencies       │
        │  - Create .env                │
        │  - Generate SECRET_KEY        │
        │  - Run migrations             │
        └───────────┬───────────────────┘
                    │
                    ▼
        ┌───────────────────────────────┐
        │  [4/7] Frontend Setup         │
        │  - Install node_modules/      │
        │  - Create .env.local          │
        └───────────┬───────────────────┘
                    │
                    ▼
        ┌───────────────────────────────┐
        │  [5/7] Create start-dev.sh    │
        │  - Auto-generated helper      │
        └───────────┬───────────────────┘
                    │
                    ▼
        ┌───────────────────────────────┐
        │  [6/7] Display Next Steps     │
        │  - Add WANDB_API_KEY          │
        │  - How to start servers       │
        └───────────┬───────────────────┘
                    │
                    ▼
        ┌───────────────────────────────┐
        │  [7/7] Ready to Code! 🎉      │
        └───────────────────────────────┘
```

---

## 🔄 Development Workflow

### First Time Setup

```
┌──────────────────────────────────────────────────────┐
│                                                      │
│  1. Clone Repository                                 │
│     git clone <repo>                                 │
│                                                      │
│  2. Run Setup                                        │
│     ./setup.sh                                       │
│                                                      │
│  3. Add W&B API Key                                  │
│     Edit backend/.env                                │
│                                                      │
│  4. Start Development                                │
│     ./start-dev.sh                                   │
│                                                      │
│  5. Open Browser                                     │
│     http://localhost:3000                            │
│                                                      │
└──────────────────────────────────────────────────────┘
```

### Daily Development

```
┌──────────────────────────────────────────────────────┐
│                                                      │
│  1. Start Servers                                    │
│     ./start-dev.sh                                   │
│     (or: make start)                                 │
│                                                      │
│  2. Code Away! 💻                                    │
│     - Changes auto-reload                            │
│     - Database persists                              │
│                                                      │
│  3. Stop When Done                                   │
│     Ctrl+C                                          │
│                                                      │
└──────────────────────────────────────────────────────┘
```

---

## 🗂️ File Structure After Setup

```
draft-killer/
│
├── 📁 backend/
│   ├── 📁 venv/                      ⬅ Created by setup
│   │   ├── bin/
│   │   ├── lib/
│   │   └── .dependencies_installed   ⬅ Marker file
│   │
│   ├── 📄 .env                       ⬅ Created by setup
│   ├── 📄 .env.example               ⬅ Template
│   ├── 📁 app/
│   ├── 📁 alembic/
│   │   └── 📁 versions/              ⬅ Migrations created
│   ├── 📄 requirements.txt
│   └── 📄 alembic.ini
│
├── 📁 frontend/
│   ├── 📁 node_modules/              ⬅ Created by setup
│   ├── 📄 .env.local                 ⬅ Created by setup
│   ├── 📄 .env.example               ⬅ Template
│   ├── 📁 src/
│   ├── 📄 package.json
│   └── 📄 next.config.js
│
├── 🐳 docker-compose.yml             ⬅ PostgreSQL config
├── 🔧 setup.sh                       ⬅ Main setup script
├── ▶️  start-dev.sh                  ⬅ Created by setup
├── 📝 Makefile                       ⬅ Convenient commands
│
├── 📚 QUICKSTART.md                  ⬅ Quick reference
├── 📚 SETUP_GUIDE.md                 ⬅ Detailed guide
├── 📚 SETUP_AUTOMATION.md            ⬅ Technical docs
└── 📚 README.md                      ⬅ Project overview
```

---

## 🐳 Docker PostgreSQL Architecture

```
┌─────────────────────────────────────────────────────┐
│  Your Computer                                      │
│                                                     │
│  ┌────────────────────────────────────────────┐    │
│  │  Docker Desktop                            │    │
│  │                                            │    │
│  │  ┌──────────────────────────────────┐     │    │
│  │  │  Container: draft_killer_db      │     │    │
│  │  │                                  │     │    │
│  │  │  PostgreSQL 15                   │     │    │
│  │  │  - Database: draft_killer        │     │    │
│  │  │  - User: draft_killer            │     │    │
│  │  │  - Port: 5432 → 5432            │     │    │
│  │  │                                  │     │    │
│  │  │  📦 Volume: postgres_data        │     │    │
│  │  │     (Persistent storage)         │     │    │
│  │  └──────────────────────────────────┘     │    │
│  │                  ▲                         │    │
│  └──────────────────┼─────────────────────────┘    │
│                     │                              │
│  ┌──────────────────┼─────────────────────────┐    │
│  │  Backend (FastAPI)                         │    │
│  │  Port: 8000                                │    │
│  │  Connects to: localhost:5432               │    │
│  └────────────────────────────────────────────┘    │
│                                                     │
│  ┌────────────────────────────────────────────┐    │
│  │  Frontend (Next.js)                        │    │
│  │  Port: 3000                                │    │
│  │  Connects to: localhost:8000               │    │
│  └────────────────────────────────────────────┘    │
│                                                     │
│  ┌────────────────────────────────────────────┐    │
│  │  Browser                                   │    │
│  │  http://localhost:3000                     │    │
│  └────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────┘
```

---

## 🔐 Environment Variables Flow

### Backend (.env)

```
┌─────────────────────────────────────────┐
│  .env.example (Template)                │
│  - Placeholder values                   │
│  - Documentation                        │
└──────────────┬──────────────────────────┘
               │
               │ setup.sh copies and modifies
               ▼
┌─────────────────────────────────────────┐
│  .env (Your config)                     │
│  - Real database URL                    │
│  - Generated SECRET_KEY                 │
│  - Needs: WANDB_API_KEY (manual)        │
└──────────────┬──────────────────────────┘
               │
               │ Loaded by FastAPI
               ▼
┌─────────────────────────────────────────┐
│  app/core/config.py                     │
│  - Validates all settings               │
│  - Provides to app                      │
└─────────────────────────────────────────┘
```

### Frontend (.env.local)

```
┌─────────────────────────────────────────┐
│  .env.example (Template)                │
│  - NEXT_PUBLIC_API_URL                  │
└──────────────┬──────────────────────────┘
               │
               │ setup.sh copies
               ▼
┌─────────────────────────────────────────┐
│  .env.local (Your config)               │
│  - Points to localhost:8000             │
└──────────────┬──────────────────────────┘
               │
               │ Used by Next.js
               ▼
┌─────────────────────────────────────────┐
│  Browser                                │
│  - API calls to localhost:8000          │
└─────────────────────────────────────────┘
```

---

## 🔄 Database Migration Flow

```
┌─────────────────────────────────────────────────────┐
│  1. Models defined in:                              │
│     backend/app/models/database.py                  │
│     - User                                          │
│     - Conversation                                  │
│     - Message                                       │
└──────────────┬──────────────────────────────────────┘
               │
               │ alembic revision --autogenerate
               ▼
┌─────────────────────────────────────────────────────┐
│  2. Migration created in:                           │
│     backend/alembic/versions/xxxx_initial.py        │
│     - Auto-generated SQL                            │
└──────────────┬──────────────────────────────────────┘
               │
               │ alembic upgrade head
               ▼
┌─────────────────────────────────────────────────────┐
│  3. Applied to database:                            │
│     PostgreSQL in Docker                            │
│     - Tables created                                │
│     - Indexes created                               │
│     - Constraints added                             │
└─────────────────────────────────────────────────────┘
```

---

## 🎮 Command Reference

### Quick Commands

| Command | Description |
|---------|-------------|
| `./setup.sh` | One-time setup |
| `./start-dev.sh` | Start both servers |
| `make setup` | Same as ./setup.sh |
| `make start` | Same as ./start-dev.sh |
| `make db-up` | Start PostgreSQL |
| `make db-down` | Stop PostgreSQL |
| `make db-reset` | Reset database |

### Manual Commands

**Backend:**
```bash
cd backend
source venv/bin/activate
uvicorn app.main:app --reload
```

**Frontend:**
```bash
cd frontend
npm run dev
```

**Database:**
```bash
docker-compose up -d postgres      # Start
docker-compose down                # Stop
docker logs draft_killer_db        # View logs
docker exec -it draft_killer_db psql -U draft_killer  # Connect
```

---

## 🎯 Quick Troubleshooting

```
Problem: Setup fails
└─→ Check: Docker running?
    └─→ Start Docker Desktop

Problem: Port 5432 in use
└─→ Check: Other PostgreSQL?
    └─→ Stop it: brew services stop postgresql

Problem: Backend won't start
└─→ Check: WANDB_API_KEY set?
    └─→ Edit backend/.env

Problem: Frontend can't connect
└─→ Check: Backend running?
    └─→ Visit http://localhost:8000/health
```

---

## 📊 Setup Time Comparison

### Without Automation
```
Manual Setup: ████████████████████ (15-20 min)
- Install PostgreSQL
- Configure database
- Create virtualenv
- Install dependencies
- Configure environment
- Run migrations
- Install frontend deps
- Multiple terminals
- Error-prone
```

### With Automation
```
Automated Setup: ███ (2-3 min)
- ./setup.sh
- Add W&B key
- ./start-dev.sh
- Done! ✨
```

---

## 🎓 What You Get

After running `./setup.sh`, you have:

✅ **Working PostgreSQL** - In Docker, isolated, persistent
✅ **Backend Ready** - Virtual environment, dependencies installed
✅ **Database Schema** - Tables created via migrations
✅ **Frontend Ready** - Dependencies installed, configured
✅ **Environment Files** - Created with secure defaults
✅ **Start Script** - One command to run everything
✅ **Make Commands** - Convenient shortcuts
✅ **Documentation** - Multiple guides for reference

All you need to add: **Your W&B API key!**

---

**🚀 From zero to coding in under 3 minutes!**

