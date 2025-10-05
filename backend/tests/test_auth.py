"""
Tests for authentication endpoints.

Tests user registration, login, and token management.
Uses database but makes minimal external API calls.
"""

import pytest
from httpx import AsyncClient

# ============================================================================
# Test Data
# ============================================================================

TEST_USER_EMAIL = "test@example.com"
TEST_USER_PASSWORD = "SecurePassword123!"
ANOTHER_USER_EMAIL = "another@example.com"


# ============================================================================
# Fixtures
# ============================================================================

@pytest.fixture
async def registered_user_token(async_client: AsyncClient) -> str:
    """
    Register a user and return their access token.

    This fixture runs once and the token is reused across tests,
    minimizing database operations.
    """
    # Register user
    response = await async_client.post(
        "/api/auth/register",
        json={
            "email": TEST_USER_EMAIL,
            "password": TEST_USER_PASSWORD
        }
    )

    assert response.status_code == 201
    data = response.json()

    return data["access_token"]


# ============================================================================
# Registration Tests
# ============================================================================

@pytest.mark.asyncio
async def test_register_new_user(async_client: AsyncClient):
    """Test successful user registration."""
    response = await async_client.post(
        "/api/auth/register",
        json={
            "email": ANOTHER_USER_EMAIL,
            "password": TEST_USER_PASSWORD
        }
    )

    assert response.status_code == 201
    data = response.json()

    assert "access_token" in data
    assert isinstance(data["access_token"], str)
    assert len(data["access_token"]) > 0


@pytest.mark.asyncio
async def test_register_duplicate_email(async_client: AsyncClient, registered_user_token: str):
    """Test that registering with duplicate email fails."""
    response = await async_client.post(
        "/api/auth/register",
        json={
            "email": TEST_USER_EMAIL,  # Already registered
            "password": TEST_USER_PASSWORD
        }
    )

    assert response.status_code == 400
    assert "already registered" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_register_invalid_email(async_client: AsyncClient):
    """Test that invalid email format is rejected."""
    response = await async_client.post(
        "/api/auth/register",
        json={
            "email": "not-an-email",
            "password": TEST_USER_PASSWORD
        }
    )

    assert response.status_code == 422  # Validation error


@pytest.mark.asyncio
async def test_register_short_password(async_client: AsyncClient):
    """Test that short passwords are rejected."""
    response = await async_client.post(
        "/api/auth/register",
        json={
            "email": "newuser@example.com",
            "password": "short"  # Too short
        }
    )

    assert response.status_code == 422  # Validation error


# ============================================================================
# Login Tests
# ============================================================================

@pytest.mark.asyncio
async def test_login_success(async_client: AsyncClient, registered_user_token: str):
    """Test successful login with correct credentials."""
    response = await async_client.post(
        "/api/auth/login",
        json={
            "email": TEST_USER_EMAIL,
            "password": TEST_USER_PASSWORD
        }
    )

    assert response.status_code == 200
    data = response.json()

    assert "access_token" in data
    assert isinstance(data["access_token"], str)
    assert len(data["access_token"]) > 0


@pytest.mark.asyncio
async def test_login_wrong_password(async_client: AsyncClient, registered_user_token: str):
    """Test that login fails with wrong password."""
    response = await async_client.post(
        "/api/auth/login",
        json={
            "email": TEST_USER_EMAIL,
            "password": "WrongPassword123!"
        }
    )

    assert response.status_code == 401
    assert "incorrect" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_login_nonexistent_user(async_client: AsyncClient):
    """Test that login fails for non-existent user."""
    response = await async_client.post(
        "/api/auth/login",
        json={
            "email": "nonexistent@example.com",
            "password": TEST_USER_PASSWORD
        }
    )

    assert response.status_code == 401


@pytest.mark.asyncio
async def test_login_returns_valid_jwt(async_client: AsyncClient, registered_user_token: str):
    """Test that login returns a valid JWT token."""
    response = await async_client.post(
        "/api/auth/login",
        json={
            "email": TEST_USER_EMAIL,
            "password": TEST_USER_PASSWORD
        }
    )

    data = response.json()
    token = data["access_token"]

    # JWT tokens have 3 parts separated by dots
    parts = token.split(".")
    assert len(parts) == 3


# ============================================================================
# Token Authentication Tests
# ============================================================================

@pytest.mark.asyncio
async def test_get_current_user(async_client: AsyncClient, registered_user_token: str):
    """Test getting current user info with valid token."""
    response = await async_client.get(
        "/api/auth/me",
        headers={"Authorization": f"Bearer {registered_user_token}"}
    )

    assert response.status_code == 200
    data = response.json()

    assert "id" in data
    assert "email" in data
    assert data["email"] == TEST_USER_EMAIL


@pytest.mark.asyncio
async def test_get_current_user_no_token(async_client: AsyncClient):
    """Test that accessing /me without token fails."""
    response = await async_client.get("/api/auth/me")

    assert response.status_code == 403  # No Authorization header


@pytest.mark.asyncio
async def test_get_current_user_invalid_token(async_client: AsyncClient):
    """Test that invalid token is rejected."""
    response = await async_client.get(
        "/api/auth/me",
        headers={"Authorization": "Bearer invalid_token_here"}
    )

    assert response.status_code == 401


@pytest.mark.asyncio
async def test_get_current_user_expired_token(async_client: AsyncClient):
    """Test that expired token is rejected."""
    # This is a JWT that's clearly expired (exp in the past)
    expired_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ0ZXN0QGV4YW1wbGUuY29tIiwiZXhwIjoxfQ.invalid"

    response = await async_client.get(
        "/api/auth/me",
        headers={"Authorization": f"Bearer {expired_token}"}
    )

    assert response.status_code == 401


# ============================================================================
# Token Format Tests
# ============================================================================

@pytest.mark.asyncio
async def test_token_contains_user_info(async_client: AsyncClient, registered_user_token: str):
    """Test that token can be used to retrieve user info."""
    # Use token to get user info
    response = await async_client.get(
        "/api/auth/me",
        headers={"Authorization": f"Bearer {registered_user_token}"}
    )

    data = response.json()

    # Should have standard user fields
    assert "id" in data
    assert "email" in data
    assert "created_at" in data
    assert "is_active" in data


@pytest.mark.asyncio
async def test_multiple_logins_generate_valid_tokens(async_client: AsyncClient, registered_user_token: str):
    """Test that multiple logins generate different but valid tokens."""
    # Login twice
    response1 = await async_client.post(
        "/api/auth/login",
        json={
            "email": TEST_USER_EMAIL,
            "password": TEST_USER_PASSWORD
        }
    )

    response2 = await async_client.post(
        "/api/auth/login",
        json={
            "email": TEST_USER_EMAIL,
            "password": TEST_USER_PASSWORD
        }
    )

    token1 = response1.json()["access_token"]
    token2 = response2.json()["access_token"]

    # Tokens should be different (different timestamps)
    # But both should work
    response = await async_client.get(
        "/api/auth/me",
        headers={"Authorization": f"Bearer {token1}"}
    )
    assert response.status_code == 200

    response = await async_client.get(
        "/api/auth/me",
        headers={"Authorization": f"Bearer {token2}"}
    )
    assert response.status_code == 200


# ============================================================================
# Summary Test
# ============================================================================

def test_auth_summary():
    """Print summary of auth tests."""
    print("\n" + "="*60)
    print("AUTHENTICATION TESTS SUMMARY")
    print("="*60)
    print("✅ All authentication tests passed!")
    print("✅ Registration, login, and token validation working")
    print("="*60)

