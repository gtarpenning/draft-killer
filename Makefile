# Draft Killer - Makefile
# Convenient commands for common development tasks
# Using uv for blazing-fast Python package management 🚀

.PHONY: help setup start start-backend start-frontend db-up db-down db-reset db-migrate db-connect install-backend install-frontend update-deps clean test test-backend test-verbose test-coverage test-fast test-health test-auth test-database test-inference test-chat test-odds lint lint-backend lint-frontend lint-fix format format-backend format-frontend check-all

# Default target
help:
	@echo "Draft Killer - Development Commands (powered by uv 🚀)"
	@echo ""
	@echo "Setup & Start:"
	@echo "  make setup          - One-time setup (database, .venv, dependencies)"
	@echo "  make start          - Start both backend and frontend"
	@echo "  make start-backend  - Start only the backend"
	@echo "  make start-frontend - Start only the frontend"
	@echo ""
	@echo "Database:"
	@echo "  make db-up          - Start PostgreSQL"
	@echo "  make db-down        - Stop PostgreSQL"
	@echo "  make db-reset       - Reset database (WARNING: deletes all data)"
	@echo "  make db-migrate     - Run pending migrations"
	@echo "  make db-connect     - Connect to database CLI"
	@echo ""
	@echo "Dependencies:"
	@echo "  make install-backend  - Install Python dependencies with uv"
	@echo "  make install-frontend - Install Node dependencies"
	@echo "  make update-deps      - Update all Python packages to latest"
	@echo ""
	@echo "Testing:"
	@echo "  make test           - Run all backend tests"
	@echo "  make test-backend   - Run all backend tests"
	@echo "  make test-verbose   - Run tests with verbose output"
	@echo "  make test-coverage  - Run tests with coverage report"
	@echo "  make test-fast      - Run tests (skip external APIs)"
	@echo "  make test-health    - Run health check tests only"
	@echo "  make test-auth      - Run authentication tests only"
	@echo "  make test-database  - Run database tests only"
	@echo "  make test-inference - Run inference tests only"
	@echo "  make test-chat      - Run chat endpoint tests only"
	@echo "  make test-odds      - Run odds API integration tests"
	@echo ""
	@echo "Linting & Formatting:"
	@echo "  make lint           - Run all linters (backend + frontend)"
	@echo "  make lint-backend   - Run Python linter (ruff)"
	@echo "  make lint-frontend  - Run JavaScript/TypeScript linter (ESLint)"
	@echo "  make lint-fix       - Fix auto-fixable linting issues"
	@echo "  make format         - Format all code (black + prettier)"
	@echo "  make format-backend - Format Python code (black)"
	@echo "  make format-frontend- Format JavaScript/TypeScript (prettier)"
	@echo "  make check-all      - Run all checks (lint + format + type-check)"
	@echo ""
	@echo "Maintenance:"
	@echo "  make clean          - Remove generated files and caches"

# Setup
setup:
	@echo "Running setup script..."
	./setup.sh

# Start services
start:
	@echo "Starting development servers..."
	./start-dev.sh

start-backend:
	@echo "Starting backend..."
	cd backend && source .venv/bin/activate && uvicorn app.main:app --reload

start-frontend:
	@echo "Starting frontend..."
	cd frontend && npm run dev

# Database commands
db-up:
	@echo "Starting PostgreSQL..."
	docker-compose up -d postgres
	@echo "Waiting for database to be ready..."
	@sleep 3

db-down:
	@echo "Stopping PostgreSQL..."
	docker-compose down

db-reset:
	@echo "⚠️  WARNING: This will delete all data!"
	@read -p "Are you sure? [y/N] " -n 1 -r; \
	echo; \
	if [[ $$REPLY =~ ^[Yy]$$ ]]; then \
		docker-compose down -v; \
		docker-compose up -d postgres; \
		sleep 3; \
		cd backend && source .venv/bin/activate && alembic upgrade head; \
		echo "✓ Database reset complete"; \
	fi

db-migrate:
	@echo "Running database migrations..."
	cd backend && source .venv/bin/activate && alembic upgrade head

db-connect:
	@echo "Connecting to database..."
	docker exec -it draft_killer_db psql -U draft_killer -d draft_killer

# Install dependencies
install-backend:
	@echo "Installing backend dependencies with uv..."
	cd backend && uv pip install -e ".[dev]"

install-frontend:
	@echo "Installing frontend dependencies..."
	cd frontend && npm install

update-deps:
	@echo "Updating all Python dependencies to latest versions..."
	cd backend && uv pip install -U -e ".[dev]"
	@echo "✓ All packages updated!"

# Maintenance
clean:
	@echo "Cleaning up..."
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".next" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".ruff_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "htmlcov" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name ".coverage" -delete 2>/dev/null || true
	@echo "✓ Cleanup complete"

test:
	@echo "Running backend tests..."
	cd backend && ./run_tests.sh

test-backend:
	@echo "Running backend tests..."
	cd backend && ./run_tests.sh

test-verbose:
	@echo "Running backend tests (verbose)..."
	cd backend && ./run_tests.sh -vv

test-coverage:
	@echo "Running backend tests with coverage..."
	cd backend && ./run_tests.sh --coverage

test-fast:
	@echo "Running backend tests (skipping external APIs)..."
	cd backend && SKIP_INFERENCE_TESTS=1 SKIP_API_TESTS=1 ./run_tests.sh

test-health:
	@echo "Running health check tests..."
	cd backend && ./run_tests.sh test_health.py

test-auth:
	@echo "Running authentication tests..."
	cd backend && ./run_tests.sh test_auth.py

test-database:
	@echo "Running database tests..."
	cd backend && ./run_tests.sh test_database.py

test-inference:
	@echo "Running inference tests..."
	cd backend && ./run_tests.sh test_inference.py

test-chat:
	@echo "Running chat endpoint tests..."
	cd backend && ./run_tests.sh test_chat.py

test-odds:
	@echo "Running odds API tests..."
	cd backend && ./run_odds_tests.sh

# Utility targets
.PHONY: logs logs-db logs-backend logs-frontend

logs-db:
	docker logs -f draft_killer_db

logs-backend:
	@echo "Backend logs are in the terminal where you started it"

logs-frontend:
	@echo "Frontend logs are in the terminal where you started it"

# Linting & Formatting
lint:
	@echo "Running all linters..."
	@$(MAKE) lint-backend
	@$(MAKE) lint-frontend

lint-backend:
	@echo "Running Python linter (ruff)..."
	cd backend && source .venv/bin/activate && ruff check app tests
	@echo "✓ Python linting complete"

lint-frontend:
	@echo "Running JavaScript/TypeScript linter (ESLint)..."
	cd frontend && npm run lint
	@echo "✓ Frontend linting complete"

lint-fix:
	@echo "Fixing auto-fixable linting issues..."
	@$(MAKE) lint-fix-backend
	@$(MAKE) lint-fix-frontend

lint-fix-backend:
	@echo "Fixing Python linting issues..."
	cd backend && source .venv/bin/activate && ruff check --fix --unsafe-fixes app tests
	@echo "✓ Python linting fixes complete"

lint-fix-frontend:
	@echo "Fixing JavaScript/TypeScript linting issues..."
	cd frontend && npm run lint:fix
	@echo "✓ Frontend linting fixes complete"

format:
	@echo "Formatting all code..."
	@$(MAKE) format-backend
	@$(MAKE) format-frontend

format-backend:
	@echo "Formatting Python code with black..."
	cd backend && source .venv/bin/activate && black app tests
	@echo "✓ Python formatting complete"

format-frontend:
	@echo "Formatting JavaScript/TypeScript code with prettier..."
	cd frontend && npm run format
	@echo "✓ Frontend formatting complete"

check-all:
	@echo "Running all checks (lint + format + type-check)..."
	@$(MAKE) lint
	@$(MAKE) format
	@echo "Running TypeScript type checking..."
	cd frontend && npm run type-check
	@echo "✓ All checks complete"

