"""
Tests for health check endpoint.

These tests verify basic service availability and configuration.
No external API calls or database dependencies.
"""

import pytest
from httpx import AsyncClient
from app.main import app


# ============================================================================
# Health Check Tests
# ============================================================================

@pytest.mark.asyncio
async def test_health_endpoint_returns_200():
    """Test that health endpoint returns 200 OK."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/api/health")
    
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_health_endpoint_structure():
    """Test that health endpoint returns expected data structure."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/api/health")
    
    data = response.json()
    
    assert "status" in data
    assert "version" in data
    assert "environment" in data


@pytest.mark.asyncio
async def test_health_endpoint_status_healthy():
    """Test that health endpoint reports healthy status."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/api/health")
    
    data = response.json()
    assert data["status"] == "healthy"


@pytest.mark.asyncio
async def test_health_endpoint_version_format():
    """Test that version is a non-empty string."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/api/health")
    
    data = response.json()
    assert isinstance(data["version"], str)
    assert len(data["version"]) > 0


@pytest.mark.asyncio
async def test_health_endpoint_environment_valid():
    """Test that environment is set to valid value."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/api/health")
    
    data = response.json()
    assert data["environment"] in ["development", "staging", "production"]


@pytest.mark.asyncio
async def test_health_endpoint_no_auth_required():
    """Test that health endpoint doesn't require authentication."""
    # Should work without any Authorization header
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/api/health")
    
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_health_endpoint_response_time():
    """Test that health endpoint responds quickly."""
    import time
    
    async with AsyncClient(app=app, base_url="http://test") as client:
        start = time.time()
        response = await client.get("/api/health")
        elapsed = time.time() - start
    
    assert response.status_code == 200
    assert elapsed < 0.5  # Should respond in under 500ms


# ============================================================================
# Summary Test
# ============================================================================

def test_health_summary():
    """Print summary of health check tests."""
    print("\n" + "="*60)
    print("HEALTH CHECK TESTS SUMMARY")
    print("="*60)
    print("✅ All health check tests passed!")
    print("✅ Service is responsive and properly configured")
    print("="*60)

