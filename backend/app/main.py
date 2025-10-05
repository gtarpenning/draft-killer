"""
Main FastAPI application entry point.

This module initializes the FastAPI application, configures middleware,
and registers all API routes.
"""

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.routes import admin, auth, chat, health
from app.core.config import settings
from app.core.database import init_db


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """
    Lifespan context manager for startup and shutdown events.

    Handles initialization and cleanup tasks:
    - Database initialization
    - Resource cleanup
    """
    # Startup
    await init_db()
    print(f"🚀 {settings.APP_NAME} v{settings.VERSION} starting...")
    print(f"📍 Environment: {settings.ENVIRONMENT}")
    print(f"🔧 Debug mode: {settings.DEBUG}")

    yield

    # Shutdown
    print("👋 Shutting down...")


# Initialize FastAPI application
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.VERSION,
    description="Sports betting parlay analysis API",
    docs_url="/docs" if settings.is_development else None,
    redoc_url="/redoc" if settings.is_development else None,
    lifespan=lifespan,
)


# ============================================================================
# Middleware Configuration
# ============================================================================

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================================
# Exception Handlers
# ============================================================================

@app.exception_handler(ValueError)
async def value_error_handler(request, exc):
    """Handle ValueError exceptions with a 400 Bad Request response."""
    return JSONResponse(
        status_code=400,
        content={"detail": str(exc), "code": "VALUE_ERROR"}
    )


@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """Handle unexpected exceptions with a 500 Internal Server Error response."""
    if settings.is_development:
        # In development, show detailed error
        return JSONResponse(
            status_code=500,
            content={
                "detail": str(exc),
                "code": "INTERNAL_ERROR",
                "type": type(exc).__name__
            }
        )
    else:
        # In production, hide error details
        return JSONResponse(
            status_code=500,
            content={
                "detail": "An internal error occurred",
                "code": "INTERNAL_ERROR"
            }
        )


# ============================================================================
# Route Registration
# ============================================================================

# Register API routes
app.include_router(health.router, tags=["Health"])
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(chat.router, prefix="/api/chat", tags=["Chat"])
app.include_router(admin.router, prefix="/api/admin", tags=["Admin"])


# ============================================================================
# Root Endpoint
# ============================================================================

@app.get("/")
async def root():
    """Root endpoint - API information."""
    return {
        "name": settings.APP_NAME,
        "version": settings.VERSION,
        "environment": settings.ENVIRONMENT,
        "docs": "/docs" if settings.is_development else "disabled",
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower(),
    )


