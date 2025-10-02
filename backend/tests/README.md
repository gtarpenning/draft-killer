# Backend Test Suite

Comprehensive testing suite for the Draft Killer backend API, following the pattern established by our ODDS API integration tests.

## 🎯 Philosophy

Our test suite follows these key principles:

1. **Minimize External API Calls**: Like the ODDS API tests, we make ONE real API call per test suite and cache the result
2. **Test Isolation**: Each test is independent and can run in any order
3. **Comprehensive Coverage**: Tests cover health checks, auth, database, inference, and chat functionality
4. **Easy to Run**: Simple commands via Makefile, clear output, helpful error messages

## 📁 Test Structure

Tests are organized by coverage area:

```
tests/
├── conftest.py              # Shared fixtures and configuration
├── test_health.py           # Health check endpoint tests
├── test_auth.py             # Authentication and token tests
├── test_database.py         # Database models and relationships
├── test_inference.py        # LLM inference via Wandb Weave
├── test_chat.py             # Chat endpoints and streaming
└── test_odds_integration.py # Odds API integration (existing)
```

### Test Files Overview

#### `test_health.py`
- Basic service availability
- No external dependencies
- Fast, simple sanity checks

**Coverage:**
- Health endpoint returns 200
- Response structure validation
- Version and environment info
- Response time checks

#### `test_auth.py`
- User registration and login
- JWT token generation and validation
- Authentication middleware

**Coverage:**
- User registration (success and failure cases)
- Login with valid/invalid credentials
- Token validation
- Get current user info
- Duplicate email handling
- Password validation

#### `test_database.py`
- Database models and schemas
- Relationships and constraints
- CRUD operations

**Coverage:**
- User model creation and defaults
- Conversation and message models
- API usage tracking
- Foreign key relationships
- Cascade deletes
- Unique constraints

#### `test_inference.py`
- LLM inference via Wandb Weave
- Prompt generation
- Streaming responses

**Coverage:**
- Prompt template generation
- Model configuration
- Streaming chunk generation
- Response validation
- Integration with odds data
- Error handling

**⚠️ Important:** Makes ONE real inference call (cached across all tests)

#### `test_chat.py`
- Chat streaming endpoints
- Conversation management
- Message history

**Coverage:**
- Anonymous vs authenticated chat
- SSE streaming format
- Conversation creation
- Message persistence
- History retrieval
- Rate limiting

## 🚀 Running Tests

### Quick Start

The easiest way to run tests is from the project root using Make:

```bash
# Run all tests
make test

# Run specific test suites
make test-health        # Health checks only
make test-auth          # Authentication tests
make test-database      # Database tests
make test-inference     # LLM inference tests
make test-chat          # Chat endpoints
make test-odds          # Odds API integration

# Additional options
make test-verbose       # Verbose output (-vv)
make test-coverage      # Generate coverage report
make test-fast          # Skip external API calls
```

### From Backend Directory

You can also run tests directly from the backend directory:

```bash
cd backend

# Run all tests
./run_tests.sh

# Run with options
./run_tests.sh -vv                    # Verbose
./run_tests.sh --coverage             # Coverage report
./run_tests.sh --skip-inference       # Skip inference tests
./run_tests.sh --skip-api             # Skip API tests
./run_tests.sh test_health.py         # Specific test file
```

### Direct pytest

For more control, use pytest directly:

```bash
cd backend
source .venv/bin/activate

# Run all tests
pytest tests/

# Run specific file
pytest tests/test_health.py

# Run specific test
pytest tests/test_auth.py::test_register_new_user

# With coverage
pytest tests/ --cov=app --cov-report=html

# Verbose
pytest tests/ -vv

# Stop on first failure
pytest tests/ -x
```

## 📋 Prerequisites

### Required Services

**Database (PostgreSQL):**
```bash
# Start database
make db-up

# Or with docker-compose
docker-compose up -d postgres
```

**Environment Variables:**
Create a `.env` file in the backend directory:

```env
# Required for all tests
DATABASE_URL=postgresql+asyncpg://draft_killer:draft_killer@localhost:5432/draft_killer
TEST_DATABASE_URL=postgresql+asyncpg://draft_killer:draft_killer@localhost:5432/draft_killer_test
SECRET_KEY=your-secret-key

# Required for inference tests (or set SKIP_INFERENCE_TESTS=1)
WEAVE_PROJECT=your-weave-project
WANDB_API_KEY=your-wandb-key

# Required for odds API tests (or set SKIP_API_TESTS=1)
ODDS_API_KEY=your-odds-api-key
```

### Python Dependencies

```bash
cd backend
source .venv/bin/activate
pip install -e ".[dev]"  # Installs test dependencies
```

## 🎭 Test Patterns

### Following the ODDS API Model

Like `test_odds_integration.py`, our tests minimize external API calls:

```python
@pytest.fixture(scope="module")
async def cached_inference_response(parlay_analyzer):
    """
    Make ONE inference call and cache the result.
    All other tests use this cached response.
    """
    # ... makes single API call ...
    return cached_result

def test_response_not_empty(cached_inference_response):
    """Test using cached data - no API call made"""
    assert cached_inference_response["response"] is not None
```

### Database Test Isolation

Database tests use transactions that rollback after each test:

```python
@pytest.fixture(scope="function")
async def db_session(test_engine):
    """Each test gets a fresh session that rolls back"""
    async with session.begin():
        yield session
        await session.rollback()  # Rollback after test
```

### HTTP Client Testing

Use the `async_client` fixture for endpoint tests:

```python
@pytest.mark.asyncio
async def test_endpoint(async_client: AsyncClient):
    response = await async_client.get("/api/health")
    assert response.status_code == 200
```

## 🔧 Configuration

### Environment Variables

Control test behavior with environment variables:

- `SKIP_INFERENCE_TESTS=1` - Skip LLM inference tests (use mock data)
- `SKIP_API_TESTS=1` - Skip external API calls (use mock data)
- `TEST_DATABASE_URL` - Override test database URL

### Pytest Configuration

See `pytest.ini` for pytest settings:

```ini
[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py"]
python_classes = ["Test*"]
python_functions = ["test_*"]
```

## 📊 Coverage Reports

Generate coverage reports to see what's tested:

```bash
# Run with coverage
make test-coverage

# Opens HTML report
open backend/htmlcov/index.html
```

Coverage goals:
- **Critical paths**: 100% (auth, database operations)
- **API endpoints**: 90%+
- **Services**: 85%+
- **Overall**: 80%+

## 🐛 Debugging Tests

### Verbose Output

```bash
# See detailed output
make test-verbose

# Or with pytest
pytest tests/ -vv -s  # -s shows print statements
```

### Run Single Test

```bash
# Run one test file
pytest tests/test_health.py -v

# Run one test function
pytest tests/test_health.py::test_health_endpoint_returns_200 -v
```

### Debug with PDB

```python
def test_something():
    import pdb; pdb.set_trace()  # Breakpoint
    # ... test code ...
```

### Check Database

```bash
# Connect to test database
docker exec -it draft_killer_db psql -U draft_killer -d draft_killer_test

# View tables
\dt

# Query data
SELECT * FROM users;
```

## 🚨 Common Issues

### Database Not Running

```
Error: Database is not running!
```

**Solution:**
```bash
make db-up
# or
docker-compose up -d postgres
```

### Import Errors

```
ImportError: No module named 'app'
```

**Solution:**
```bash
cd backend
source .venv/bin/activate
pip install -e ".[dev]"
```

### Weave/Wandb Errors

```
Error: WEAVE_PROJECT not set
```

**Solution:**
```bash
# Option 1: Set environment variable
export WEAVE_PROJECT=your-project

# Option 2: Skip inference tests
make test-fast
# or
SKIP_INFERENCE_TESTS=1 ./run_tests.sh
```

### Port Already in Use

If tests fail because port is in use:

```bash
# Check what's using the port
lsof -i :8000

# Kill the process
kill -9 <PID>
```

## 📈 Adding New Tests

### 1. Choose the Right File

- Health checks → `test_health.py`
- Auth/tokens → `test_auth.py`
- Database models → `test_database.py`
- LLM inference → `test_inference.py`
- Chat endpoints → `test_chat.py`
- New feature → Create `test_<feature>.py`

### 2. Follow the Pattern

```python
"""
Tests for <feature>.

Brief description of what's being tested.
"""

import pytest
from httpx import AsyncClient

# Test data at module level
TEST_DATA = "..."

# Fixtures if needed
@pytest.fixture
async def my_fixture():
    return something

# Group related tests
# ============================================================================
# <Feature> Tests
# ============================================================================

@pytest.mark.asyncio
async def test_something(async_client: AsyncClient):
    """Test that something works correctly."""
    response = await async_client.get("/api/endpoint")
    assert response.status_code == 200

# Summary test at end
def test_summary():
    """Print summary of tests."""
    print("\n" + "="*60)
    print("<FEATURE> TESTS SUMMARY")
    print("="*60)
    print("✅ All tests passed!")
    print("="*60)
```

### 3. Use Existing Fixtures

Available fixtures from `conftest.py`:
- `db_session` - Database session with rollback
- `async_client` - HTTP client for API testing
- `sample_user_data` - Sample user registration data
- `sample_parlay_message` - Sample parlay for testing
- `sample_enriched_odds` - Sample odds data

### 4. Run and Iterate

```bash
# Run your new test
pytest tests/test_your_feature.py -v

# Check coverage
pytest tests/test_your_feature.py --cov=app.services.your_service
```

## 🎓 Best Practices

1. **Test one thing per test** - Each test should verify a single behavior
2. **Use descriptive names** - `test_login_fails_with_wrong_password` not `test_login_2`
3. **Arrange-Act-Assert** - Setup, execute, verify
4. **Don't test implementation details** - Test behavior, not internal code
5. **Use fixtures for setup** - Keep tests DRY
6. **Mock external services** - Use cached data when possible
7. **Clean up after yourself** - Tests should not affect each other
8. **Document complex tests** - Add comments explaining why

## 📚 Resources

- [Pytest Documentation](https://docs.pytest.org/)
- [FastAPI Testing](https://fastapi.tiangolo.com/tutorial/testing/)
- [SQLAlchemy Testing](https://docs.sqlalchemy.org/en/20/orm/session_transaction.html#joining-a-session-into-an-external-transaction-such-as-for-test-suites)
- [HTTPX Async Client](https://www.python-httpx.org/async/)

## ✅ CI/CD Integration

These tests are designed to run in CI/CD pipelines:

```yaml
# Example GitHub Actions
- name: Run Tests
  run: |
    make db-up
    sleep 3
    make test-fast  # Skip external APIs in CI
```

## 🎉 Summary

This test suite provides comprehensive coverage of the Draft Killer backend:

- ✅ **5 test files** organized by functionality
- ✅ **80+ tests** covering all major features
- ✅ **Minimal API calls** using caching pattern
- ✅ **Easy to run** via Makefile commands
- ✅ **Well documented** with clear patterns
- ✅ **CI/CD ready** for automated testing

Run `make test` and watch everything pass! 🚀

