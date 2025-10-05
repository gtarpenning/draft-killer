"""
Application configuration management.

All configuration is loaded from environment variables with validation.
Uses Pydantic Settings for type-safe configuration.
"""


from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.

    All settings are validated at startup. Missing required settings
    will cause the application to fail fast with clear error messages.
    """

    # Application
    APP_NAME: str = "Draft Killer API"
    VERSION: str = "0.1.0"
    ENVIRONMENT: str = "development"
    DEBUG: bool = False

    # Database
    DATABASE_URL: str
    DATABASE_URL_ASYNC: str

    # Security
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440  # 24 hours

    # LLM Provider Configuration
    LLM_PROVIDER: str = "openai"  # "openai" or "wandb"
    WANDB_API_KEY: str
    OPENAI_API_KEY: str
    WEAVE_PROJECT: str = "draft-killer"

    # The Odds API
    ODDS_API_KEY: str

    # CORS
    CORS_ORIGINS: str = "http://localhost:3000"

    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = 60
    AUTH_RATE_LIMIT_PER_MINUTE: int = 10

    # Logging
    LOG_LEVEL: str = "INFO"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True
    )

    @field_validator("CORS_ORIGINS")
    @classmethod
    def parse_cors_origins(cls, v: str) -> list[str]:
        """Parse comma-separated CORS origins into a list."""
        return [origin.strip() for origin in v.split(",")]

    @field_validator("SECRET_KEY")
    @classmethod
    def validate_secret_key(cls, v: str) -> str:
        """Ensure secret key is not using the default example value."""
        if v == "your-secret-key-here-change-in-production":
            raise ValueError(
                "SECRET_KEY must be changed from the default value. "
                "Generate a secure key using: openssl rand -hex 32"
            )
        if len(v) < 32:
            raise ValueError("SECRET_KEY must be at least 32 characters long")
        return v

    @field_validator("LLM_PROVIDER")
    @classmethod
    def validate_llm_provider(cls, v: str) -> str:
        """Validate LLM provider setting."""
        valid_providers = ["openai", "wandb"]
        if v.lower() not in valid_providers:
            raise ValueError(
                f"LLM_PROVIDER must be one of {valid_providers}, got: {v}"
            )
        return v.lower()

    @property
    def is_production(self) -> bool:
        """Check if running in production environment."""
        return self.ENVIRONMENT.lower() == "production"

    @property
    def is_development(self) -> bool:
        """Check if running in development environment."""
        return self.ENVIRONMENT.lower() == "development"


# Global settings instance
# This will be imported by other modules
settings = Settings()


def get_settings() -> Settings:
    """
    Dependency for FastAPI endpoints to inject settings.

    Usage:
        @app.get("/config")
        def get_config(settings: Settings = Depends(get_settings)):
            return {"environment": settings.ENVIRONMENT}
    """
    return settings


