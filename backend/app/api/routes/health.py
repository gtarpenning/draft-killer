"""
Health check endpoint.

Provides a simple endpoint to verify the service is running
and responding to requests.
"""

from fastapi import APIRouter

from app.core.config import settings
from app.models.schemas import HealthResponse

router = APIRouter()


@router.get("/health", response_model=HealthResponse)
async def health_check() -> HealthResponse:
    """
    Health check endpoint.

    Returns basic service information to verify the API is running.
    This endpoint does not require authentication.

    Returns:
        HealthResponse with status, version, and environment
    """
    return HealthResponse(
        status="healthy",
        version=settings.VERSION,
        environment=settings.ENVIRONMENT
    )


