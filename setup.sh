#!/bin/bash

# Draft Killer - Automated Setup Script
# This script sets up the entire local development environment with uv

set -e  # Exit on error

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}╔════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║   Draft Killer - Development Setup    ║${NC}"
echo -e "${BLUE}║         Powered by uv 🚀               ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════╝${NC}"
echo

# ============================================================================
# Check Prerequisites
# ============================================================================

echo -e "${BLUE}[1/8] Checking prerequisites...${NC}"

# Check for Docker
if ! command -v docker &> /dev/null; then
    echo -e "${YELLOW}⚠️  Docker not found. Please install Docker Desktop from https://www.docker.com/products/docker-desktop${NC}"
    echo -e "${YELLOW}   We'll use Docker to run PostgreSQL ${NC}"
    exit 1
fi

# Check for Python
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python 3 not found. Please install Python 3.11+${NC}"
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1-2)
echo -e "${GREEN}✓ Python ${PYTHON_VERSION} found${NC}"

# Check for Node.js
if ! command -v node &> /dev/null; then
    echo -e "${RED}❌ Node.js not found. Please install Node.js 18+${NC}"
    exit 1
fi

NODE_VERSION=$(node --version)
echo -e "${GREEN}✓ Node.js ${NODE_VERSION} found${NC}"

# Check for npm (comes with Node)
if ! command -v npm &> /dev/null; then
    echo -e "${RED}❌ npm not found. Please reinstall Node.js${NC}"
    exit 1
fi

echo -e "${GREEN}✓ Docker found${NC}"

# Check for uv (install if missing)
if ! command -v uv &> /dev/null; then
    echo -e "${YELLOW}⚡ uv not found. Installing uv ${NC}"
    curl -LsSf https://astral.sh/uv/install.sh | sh
    # Add uv to PATH for this session
    export PATH="$HOME/.cargo/bin:$PATH"
    echo -e "${GREEN}✓ uv installed${NC}"
else
    UV_VERSION=$(uv --version)
    echo -e "${GREEN}✓ uv ${UV_VERSION} found${NC}"
fi
echo

# ============================================================================
# Start PostgreSQL with Docker
# ============================================================================

echo -e "${BLUE}[2/7] Setting up PostgreSQL database...${NC}"

# Check if container is already running
if docker ps | grep -q draft_killer_db; then
    echo -e "${GREEN}✓ PostgreSQL container already running${NC}"
elif docker ps -a | grep -q draft_killer_db; then
    echo -e "${YELLOW}⚡ Starting existing PostgreSQL container...${NC}"
    docker start draft_killer_db
    sleep 2
else
    echo -e "${YELLOW}⚡ Creating PostgreSQL container...${NC}"
    docker-compose up -d postgres
    echo -e "${YELLOW}   Waiting for PostgreSQL to be ready...${NC}"
    sleep 5
fi

# Wait for PostgreSQL to be healthy
echo -e "${YELLOW}   Checking database health...${NC}"
max_attempts=30
attempt=0
while [ $attempt -lt $max_attempts ]; do
    if docker exec draft_killer_db pg_isready -U draft_killer &> /dev/null; then
        echo -e "${GREEN}✓ PostgreSQL is ready${NC}"
        break
    fi
    attempt=$((attempt + 1))
    if [ $attempt -eq $max_attempts ]; then
        echo -e "${RED}❌ PostgreSQL failed to start${NC}"
        exit 1
    fi
    sleep 1
done

echo

# ============================================================================
# Backend Setup
# ============================================================================

echo -e "${BLUE}[3/8] Setting up backend...${NC}"

cd backend

# Create virtual environment with uv if it doesn't exist
if [ ! -d ".venv" ]; then
    echo -e "${YELLOW}⚡ Creating Python virtual environment with uv...${NC}"
    uv venv
    echo -e "${GREEN}✓ Virtual environment created${NC}"
else
    echo -e "${GREEN}✓ Virtual environment already exists${NC}"
fi

# Activate virtual environment (uv uses .venv by default)
source .venv/bin/activate

# Install dependencies with uv (it's blazing fast! 🚀)
echo -e "${YELLOW}⚡ Installing Python dependencies with uv...${NC}"
uv pip install -e ".[dev]"
echo -e "${GREEN}✓ Python dependencies installed${NC}"

# Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
    echo -e "${YELLOW}⚡ Creating .env file from template...${NC}"
    cp .env.example .env
    
    # Generate a secure SECRET_KEY
    if command -v openssl &> /dev/null; then
        SECRET_KEY=$(openssl rand -hex 32)
        # Replace the placeholder in .env
        if [[ "$OSTYPE" == "darwin"* ]]; then
            # macOS
            sed -i '' "s/your-very-secure-secret-key-here-use-openssl-rand-hex-32/$SECRET_KEY/" .env
        else
            # Linux
            sed -i "s/your-very-secure-secret-key-here-use-openssl-rand-hex-32/$SECRET_KEY/" .env
        fi
        echo -e "${GREEN}✓ Generated secure SECRET_KEY${NC}"
    fi
    
    echo -e "${YELLOW}⚠️  Please edit backend/.env and add your WANDB_API_KEY${NC}"
    echo -e "${YELLOW}   Get it from: https://wandb.ai/authorize${NC}"
else
    echo -e "${GREEN}✓ .env file already exists${NC}"
fi

# Run database migrations
echo -e "${YELLOW}⚡ Running database migrations...${NC}"
if [ ! -d "alembic/versions" ] || [ -z "$(ls -A alembic/versions)" ]; then
    echo -e "${YELLOW}   Creating initial migration...${NC}"
    alembic revision --autogenerate -m "Initial schema"
fi

alembic upgrade head
echo -e "${GREEN}✓ Database migrations complete${NC}"

cd ..
echo

# ============================================================================
# Frontend Setup
# ============================================================================

echo -e "${BLUE}[4/8] Setting up frontend...${NC}"

cd frontend

# Create .env.local if it doesn't exist
if [ ! -f ".env.local" ]; then
    echo -e "${YELLOW}⚡ Creating .env.local file...${NC}"
    cp .env.example .env.local
    echo -e "${GREEN}✓ .env.local created${NC}"
else
    echo -e "${GREEN}✓ .env.local already exists${NC}"
fi

# Install dependencies
if [ ! -d "node_modules" ]; then
    echo -e "${YELLOW}⚡ Installing frontend dependencies...${NC}"
    npm install --silent
    echo -e "${GREEN}✓ Frontend dependencies installed${NC}"
else
    echo -e "${GREEN}✓ Frontend dependencies already installed${NC}"
fi

cd ..
echo

# ============================================================================
# Summary
# ============================================================================

echo -e "${BLUE}[5/8] Setup complete! 🎉${NC}"
echo
echo -e "${GREEN}╔════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║          Setup Successful!             ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════╝${NC}"
echo
echo -e "${BLUE}📋 What was set up:${NC}"
echo -e "   ${GREEN}✓${NC} PostgreSQL database (running in Docker)"
echo -e "   ${GREEN}✓${NC} Python virtual environment"
echo -e "   ${GREEN}✓${NC} Backend dependencies installed"
echo -e "   ${GREEN}✓${NC} Database migrations applied"
echo -e "   ${GREEN}✓${NC} Frontend dependencies installed"
echo -e "   ${GREEN}✓${NC} Environment files created"
echo

# ============================================================================
# Next Steps
# ============================================================================

echo -e "${BLUE}[6/8] Next steps:${NC}"
echo
echo -e "${YELLOW}1. Add your Weights & Biases API key:${NC}"
echo -e "   Edit: ${BLUE}backend/.env${NC}"
echo -e "   Add: ${GREEN}WANDB_API_KEY=your-key-here${NC}"
echo -e "   Get key from: ${BLUE}https://wandb.ai/authorize${NC}"
echo
echo -e "${YELLOW}2. Start the development servers:${NC}"
echo

# ============================================================================
# Create convenience start script
# ============================================================================

echo -e "${BLUE}[7/8] Creating convenience scripts...${NC}"

# Create start script
cat > start-dev.sh << 'EOF'
#!/bin/bash

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}Starting Draft Killer development servers...${NC}"
echo

# Check if PostgreSQL is running
if ! docker ps | grep -q draft_killer_db; then
    echo -e "${BLUE}Starting PostgreSQL...${NC}"
    docker start draft_killer_db
    sleep 2
fi

# Function to run backend
run_backend() {
    cd backend
    source .venv/bin/activate
    echo -e "${GREEN}🚀 Backend running on http://localhost:8000${NC}"
    echo -e "${BLUE}   API docs: http://localhost:8000/docs${NC}"
    uvicorn app.main:app --reload
}

# Function to run frontend
run_frontend() {
    cd frontend
    echo -e "${GREEN}🚀 Frontend running on http://localhost:3000${NC}"
    npm run dev
}

# Export functions for parallel execution
export -f run_backend
export -f run_frontend

# Run both in parallel using background jobs
echo -e "${BLUE}Starting backend and frontend...${NC}"
echo

# Start backend in background
(run_backend) &
BACKEND_PID=$!

# Wait a bit for backend to start
sleep 3

# Start frontend in background
(run_frontend) &
FRONTEND_PID=$!

# Wait for both processes
wait $BACKEND_PID $FRONTEND_PID
EOF

chmod +x start-dev.sh

echo -e "${GREEN}✓ Created start-dev.sh${NC}"
echo

# Display final instructions
echo -e "${GREEN}╔════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║      🚀 Ready to start coding!         ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════╝${NC}"
echo
echo -e "${BLUE}To start development:${NC}"
echo
echo -e "   ${GREEN}./start-dev.sh${NC}"
echo
echo -e "${BLUE}Or manually:${NC}"
echo
echo -e "   Terminal 1 (Backend):"
echo -e "   ${GREEN}cd backend && source .venv/bin/activate && uvicorn app.main:app --reload${NC}"
echo
echo -e "   Terminal 2 (Frontend):"
echo -e "   ${GREEN}cd frontend && npm run dev${NC}"
echo
echo -e "${BLUE}Documentation:${NC}"
echo -e "   ${GREEN}docs/QUICKSTART.md${NC} - Quick reference guide"
echo -e "   ${GREEN}docs/SETUP_VISUAL_GUIDE.md${NC} - Visual diagrams"
echo
echo -e "${BLUE}To stop PostgreSQL:${NC}"
echo -e "   ${GREEN}docker-compose down${NC}"
echo
echo -e "${BLUE}[8/8] Package management info:${NC}"
echo -e "   ${GREEN}✓${NC} Using uv for Python packages (10-100x faster than pip!)"
echo -e "   ${GREEN}✓${NC} All dependencies are in pyproject.toml"
echo -e "   ${GREEN}✓${NC} To add packages: ${BLUE}cd backend && uv add package-name${NC}"
echo -e "   ${GREEN}✓${NC} To update all: ${BLUE}cd backend && uv pip install -U -e ".[dev]"${NC}"
echo
echo -e "${YELLOW}⚠️  Don't forget to add your WANDB_API_KEY to backend/.env${NC}"
echo

