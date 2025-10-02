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
