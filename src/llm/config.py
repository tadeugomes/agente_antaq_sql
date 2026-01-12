"""
Configuration management for LLM providers.
Uses Pydantic for validation and environment variable loading.
"""
import os
from typing import Literal, Optional
from pydantic import BaseModel, Field, field_validator


class LLMConfig(BaseModel):
    """
    Configuration for LLM providers with validation.

    Environment variables:
        LLM_PROVIDER: Provider name ('openai' or 'vertexai')
        OPENAI_API_KEY: OpenAI API key
        OPENAI_MODEL: OpenAI model name (default: gpt-4o-mini)
        OPENAI_EMBEDDING_MODEL: OpenAI embedding model (default: text-embedding-3-small)
        GOOGLE_CLOUD_PROJECT: Google Cloud project ID
        GOOGLE_CLOUD_REGION: Google Cloud region (default: us-central1)
        GOOGLE_APPLICATION_CREDENTIALS: Path to service account credentials
        VERTEXAI_MODEL: VertexAI model name (default: gemini-1.5-flash)
        VERTEXAI_EMBEDDING_MODEL: VertexAI embedding model (default: textembedding-gecko@003)
        LLM_TEMPERATURE: Default temperature (default: 0)
        LLM_MAX_TOKENS: Default max tokens (default: 1000)
        LLM_TIMEOUT: Default timeout in seconds (default: 60)
    """

    # Provider selection
    provider: Literal["openai", "vertexai"] = Field(
        default="openai",
        description="LLM provider to use"
    )

    # Common parameters
    temperature: float = Field(default=0, ge=0, le=2)
    max_tokens: Optional[int] = Field(default=1000, ge=1)
    timeout: int = Field(default=60, ge=1)

    # OpenAI configuration
    openai_api_key: Optional[str] = Field(default=None)
    openai_model: str = Field(default="gpt-4o-mini")
    openai_embedding_model: str = Field(default="text-embedding-3-small")

    # VertexAI configuration
    google_cloud_project: Optional[str] = Field(default=None)
    google_cloud_region: str = Field(default="us-central1")
    google_application_credentials: Optional[str] = Field(default=None)
    vertexai_model: str = Field(default="gemini-1.5-flash")
    vertexai_embedding_model: str = Field(default="textembedding-gecko@003")

    @field_validator("provider")
    @classmethod
    def validate_provider(cls, v: str) -> str:
        """Validate provider name and normalize to lowercase."""
        if v not in ("openai", "vertexai"):
            raise ValueError(f"Invalid provider: {v}. Must be 'openai' or 'vertexai'")
        return v.lower()

    @classmethod
    def from_env(cls) -> "LLMConfig":
        """
        Create configuration from environment variables.

        Returns:
            LLMConfig instance with values from environment
        """
        return cls(
            provider=os.getenv("LLM_PROVIDER", "openai"),
            temperature=float(os.getenv("LLM_TEMPERATURE", "0")),
            max_tokens=int(os.getenv("LLM_MAX_TOKENS", "1000")) if os.getenv("LLM_MAX_TOKENS") else None,
            timeout=int(os.getenv("LLM_TIMEOUT", "60")),
            # OpenAI
            openai_api_key=os.getenv("OPENAI_API_KEY"),
            openai_model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
            openai_embedding_model=os.getenv("OPENAI_EMBEDDING_MODEL", "text-embedding-3-small"),
            # VertexAI
            google_cloud_project=os.getenv("GOOGLE_CLOUD_PROJECT"),
            google_cloud_region=os.getenv("GOOGLE_CLOUD_REGION", "us-central1"),
            google_application_credentials=os.getenv("GOOGLE_APPLICATION_CREDENTIALS"),
            vertexai_model=os.getenv("VERTEXAI_MODEL", "gemini-1.5-flash"),
            vertexai_embedding_model=os.getenv("VERTEXAI_EMBEDDING_MODEL", "textembedding-gecko@003"),
        )

    def validate_for_provider(self, provider: Optional[str] = None) -> tuple[bool, list[str]]:
        """
        Validate configuration for a specific provider.

        Args:
            provider: Provider to validate (uses default if None)

        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        provider = provider or self.provider
        errors = []

        if provider == "openai":
            if not self.openai_api_key:
                errors.append("OPENAI_API_KEY is required for OpenAI provider")

        elif provider == "vertexai":
            if not self.google_cloud_project:
                errors.append("GOOGLE_CLOUD_PROJECT is required for VertexAI provider")

            # Check if credentials are set (either via env var or Application Default Credentials)
            if not self.google_application_credentials:
                # Try to detect if ADC is configured
                try:
                    import google.auth
                    google.auth.default()
                except Exception:
                    errors.append(
                        "GOOGLE_APPLICATION_CREDENTIALS or Application Default Credentials required"
                    )

        return len(errors) == 0, errors

    def get_model_name(self, provider: Optional[str] = None) -> str:
        """Get the model name for a provider."""
        provider = provider or self.provider
        if provider == "openai":
            return self.openai_model
        elif provider == "vertexai":
            return self.vertexai_model
        raise ValueError(f"Unknown provider: {provider}")

    def get_embedding_model_name(self, provider: Optional[str] = None) -> str:
        """Get the embedding model name for a provider."""
        provider = provider or self.provider
        if provider == "openai":
            return self.openai_embedding_model
        elif provider == "vertexai":
            return self.vertexai_embedding_model
        raise ValueError(f"Unknown provider: {provider}")
