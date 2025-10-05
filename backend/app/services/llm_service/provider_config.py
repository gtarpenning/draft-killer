"""
LLM Provider Configuration

This module handles switching between different LLM providers (OpenAI, W&B Inference)
using a single environment variable. All provider-specific settings are managed
automatically based on the selected provider.
"""

import os
from enum import Enum
from typing import Dict, Any
from dataclasses import dataclass


class LLMProvider(Enum):
    """Supported LLM providers."""
    OPENAI = "openai"
    WANDB = "wandb"


@dataclass
class ProviderConfig:
    """Configuration for a specific LLM provider."""
    name: str
    base_url: str
    api_key_env_var: str
    default_model: str
    description: str


class LLMProviderManager:
    """
    Manages LLM provider configuration and switching.
    
    Usage:
        manager = LLMProviderManager()
        config = manager.get_current_config()
        client = AsyncOpenAI(base_url=config.base_url, api_key=config.api_key)
    """
    
    # Provider configurations
    PROVIDERS: Dict[LLMProvider, ProviderConfig] = {
        LLMProvider.OPENAI: ProviderConfig(
            name="OpenAI",
            base_url="https://api.openai.com/v1",
            api_key_env_var="OPENAI_API_KEY",
            default_model="gpt-4o-mini",
            description="OpenAI's official API"
        ),
        LLMProvider.WANDB: ProviderConfig(
            name="Weights & Biases Inference",
            base_url="https://api.inference.wandb.ai/v1",
            api_key_env_var="WANDB_API_KEY", 
            default_model="gpt-4o-mini",
            description="W&B Inference API (OpenAI-compatible)"
        )
    }
    
    def __init__(self):
        """Initialize the provider manager."""
        self._current_provider = self._detect_provider()
    
    def _detect_provider(self) -> LLMProvider:
        """
        Detect the current provider from environment variables.
        
        Priority:
        1. LLM_PROVIDER env var (explicit)
        2. Auto-detect based on available API keys
        3. Default to OpenAI
        """
        # Check for explicit provider setting
        provider_env = os.getenv("LLM_PROVIDER", "").lower()
        if provider_env in ["openai", "wandb"]:
            return LLMProvider(provider_env)
        
        # Auto-detect based on available API keys
        openai_key = os.getenv("OPENAI_API_KEY")
        wandb_key = os.getenv("WANDB_API_KEY")
        
        if wandb_key and not openai_key:
            return LLMProvider.WANDB
        elif openai_key and not wandb_key:
            return LLMProvider.OPENAI
        elif wandb_key and openai_key:
            # Both available, prefer OpenAI as default
            return LLMProvider.OPENAI
        else:
            # No keys available, default to OpenAI
            return LLMProvider.OPENAI
    
    @property
    def current_provider(self) -> LLMProvider:
        """Get the current provider."""
        return self._current_provider
    
    def get_current_config(self) -> ProviderConfig:
        """Get configuration for the current provider."""
        return self.PROVIDERS[self._current_provider]
    
    def get_api_key(self) -> str:
        """Get the API key for the current provider."""
        config = self.get_current_config()
        api_key = os.getenv(config.api_key_env_var)
        
        if not api_key:
            raise ValueError(
                f"API key not found for {config.name}. "
                f"Please set the {config.api_key_env_var} environment variable."
            )
        
        return api_key
    
    def get_base_url(self) -> str:
        """Get the base URL for the current provider."""
        return self.get_current_config().base_url
    
    def get_default_model(self) -> str:
        """Get the default model for the current provider."""
        return self.get_current_config().default_model
    
    def switch_provider(self, provider: LLMProvider) -> None:
        """
        Switch to a different provider.
        
        Args:
            provider: The provider to switch to
        """
        if provider not in self.PROVIDERS:
            raise ValueError(f"Unknown provider: {provider}")
        
        self._current_provider = provider
    
    def get_provider_info(self) -> Dict[str, Any]:
        """Get information about the current provider."""
        config = self.get_current_config()
        return {
            "provider": self._current_provider.value,
            "name": config.name,
            "base_url": config.base_url,
            "api_key_env_var": config.api_key_env_var,
            "default_model": config.default_model,
            "description": config.description,
            "api_key_available": bool(os.getenv(config.api_key_env_var))
        }
    
    def list_available_providers(self) -> Dict[str, Dict[str, Any]]:
        """List all available providers and their status."""
        providers = {}
        
        for provider, config in self.PROVIDERS.items():
            providers[provider.value] = {
                "name": config.name,
                "base_url": config.base_url,
                "api_key_env_var": config.api_key_env_var,
                "default_model": config.default_model,
                "description": config.description,
                "api_key_available": bool(os.getenv(config.api_key_env_var)),
                "is_current": provider == self._current_provider
            }
        
        return providers


# Global provider manager instance
provider_manager = LLMProviderManager()


def get_current_provider_config() -> ProviderConfig:
    """Get the current provider configuration."""
    return provider_manager.get_current_config()


def get_current_api_key() -> str:
    """Get the current provider's API key."""
    return provider_manager.get_api_key()


def get_current_base_url() -> str:
    """Get the current provider's base URL."""
    return provider_manager.get_base_url()


def get_current_default_model() -> str:
    """Get the current provider's default model."""
    return provider_manager.get_default_model()
