"""
Pytest configuration and shared fixtures for all tests.

Provides database, client, and common test utilities.
"""

import os
import sys
from pathlib import Path
import pytest
import asyncio
from typing import AsyncGenerator

from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.pool import NullPool

# Add backend app to path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

# Ensure .env is loaded for tests
from dotenv import load_dotenv
load_dotenv(backend_dir / ".env")

from app.main import app
from app.models.database import Base
from app.core.database import get_db


# ============================================================================
# Test Database Configuration
# ============================================================================

# Use a test database
TEST_DATABASE_URL = os.getenv(
    "TEST_DATABASE_URL",
    "postgresql+asyncpg://draft_killer:draft_killer@localhost:5432/draft_killer_test"
)


# ============================================================================
# Pytest Configuration
# ============================================================================

def pytest_configure(config):
    """Configure pytest with custom markers."""
    config.addinivalue_line(
        "markers",
        "asyncio: mark test as async"
    )


# ============================================================================
# Event Loop Fixture
# ============================================================================

@pytest.fixture(scope="session")
def event_loop():
    """
    Create an event loop for the entire test session.
    
    This ensures all async tests share the same event loop,
    which is more efficient and prevents issues with async fixtures.
    """
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


# ============================================================================
# Database Fixtures
# ============================================================================

@pytest.fixture(scope="session")
async def test_engine():
    """
    Create a test database engine.
    
    Uses NullPool to avoid connection pooling issues in tests.
    """
    engine = create_async_engine(
        TEST_DATABASE_URL,
        poolclass=NullPool,
        echo=False  # Set to True for SQL debugging
    )
    
    # Create all tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    
    yield engine
    
    # Cleanup
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    
    await engine.dispose()


@pytest.fixture(scope="function")
async def db_session(test_engine) -> AsyncGenerator[AsyncSession, None]:
    """
    Create a database session for a test.
    
    Each test gets a fresh session with a transaction that's rolled back
    after the test completes, ensuring test isolation.
    """
    # Create session factory
    async_session = async_sessionmaker(
        test_engine,
        class_=AsyncSession,
        expire_on_commit=False
    )
    
    async with async_session() as session:
        async with session.begin():
            # Override the get_db dependency
            async def override_get_db():
                yield session
            
            app.dependency_overrides[get_db] = override_get_db
            
            yield session
            
            # Rollback after test
            await session.rollback()
    
    # Clear overrides
    app.dependency_overrides.clear()


# ============================================================================
# HTTP Client Fixtures
# ============================================================================

@pytest.fixture
async def async_client(db_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    """
    Create an async HTTP client for testing API endpoints.
    
    The client is configured to work with the test database session.
    """
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client


# ============================================================================
# Check Dev Environment
# ============================================================================

@pytest.fixture(scope="session", autouse=True)
def check_dev_environment():
    """
    Check if dev environment is running before tests.
    
    This fixture warns if certain services aren't available,
    but doesn't fail tests (some tests can run without external services).
    """
    print("\n" + "="*60)
    print("BACKEND TEST SUITE - Environment Check")
    print("="*60)
    
    # Check database connection
    try:
        import asyncpg
        print("✅ asyncpg available")
    except ImportError:
        print("⚠️  asyncpg not installed - database tests will fail")
    
    # Check if database is running
    db_url = os.getenv("DATABASE_URL")
    if db_url:
        print(f"✅ DATABASE_URL configured")
    else:
        print("⚠️  DATABASE_URL not set - using test database")
    
    # Check Weave configuration
    weave_project = os.getenv("WEAVE_PROJECT")
    if weave_project:
        print(f"✅ WEAVE_PROJECT configured: {weave_project}")
    else:
        print("⚠️  WEAVE_PROJECT not set - inference tests will use mock data")
    
    # Check Odds API
    odds_key = os.getenv("ODDS_API_KEY")
    if odds_key:
        print(f"✅ ODDS_API_KEY configured")
    else:
        print("⚠️  ODDS_API_KEY not set - odds tests will use mock data")
    
    print("="*60)
    print("Starting tests...\n")


# ============================================================================
# Common Test Utilities
# ============================================================================

@pytest.fixture
def sample_user_data():
    """Sample user data for tests."""
    return {
        "email": "test@example.com",
        "password": "TestPassword123!"
    }


@pytest.fixture
def sample_parlay_message():
    """Sample parlay message for tests."""
    return "Chiefs ML, Cowboys -6.5, Over 47.5"


@pytest.fixture
def sample_enriched_odds():
    """Sample enriched odds data for tests."""
    return {
        "num_legs": 2,
        "sport": "americanfootball_nfl",
        "fetched_at": "2024-10-01T12:00:00Z",
        "legs": [
            {
                "bet_type": "moneyline",
                "team": "Chiefs",
                "original_text": "Chiefs ML",
                "game": {
                    "id": "test_game_1",
                    "sport_key": "americanfootball_nfl",
                    "home_team": "Kansas City Chiefs",
                    "away_team": "Las Vegas Raiders",
                    "commence_time": "2024-10-06T17:00:00Z"
                },
                "bookmaker": {
                    "key": "draftkings",
                    "title": "DraftKings",
                    "markets": {
                        "h2h": {
                            "outcomes": [
                                {"name": "Kansas City Chiefs", "price": -250},
                                {"name": "Las Vegas Raiders", "price": 210}
                            ]
                        }
                    }
                }
            }
        ]
    }
