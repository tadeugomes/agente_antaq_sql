"""
LLM Factory for creating LLM and Embedding instances.
Supports multiple providers (OpenAI, VertexAI) with easy switching via environment.
"""
import os
from typing import Any, Optional
from .config import LLMConfig
from .providers import OpenAILLM, OpenAIEmbeddingsProvider, VertexAILLM, VertexAIEmbeddingsProvider


class LLMFactory:
    """
    Factory for creating LLM and Embedding instances.

    Usage:
        from src.llm import LLMFactory

        # Simple usage - uses LLM_PROVIDER env var
        llm = LLMFactory.get_llm()
        embeddings = LLMFactory.get_embeddings()

        # With override parameters
        llm = LLMFactory.get_llm(temperature=0.5)
        embeddings = LLMFactory.get_embeddings(model="text-embedding-3-large")

        # Validate configuration
        validation = LLMFactory.validate_configuration()
    """

    _config: Optional[LLMConfig] = None
    _llm_provider: Optional[Any] = None
    _embedding_provider: Optional[Any] = None

    @classmethod
    def _get_config(cls) -> LLMConfig:
        """
        Get or create the cached configuration.

        Returns:
            LLMConfig instance
        """
        if cls._config is None:
            cls._config = LLMConfig.from_env()
        return cls._config

    @classmethod
    def get_llm(
        cls,
        model: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        timeout: Optional[int] = None,
        **kwargs
    ) -> Any:
        """
        Get an LLM instance based on LLM_PROVIDER environment variable.

        Args:
            model: Override model name
            temperature: Override temperature
            max_tokens: Override max tokens
            timeout: Override timeout
            **kwargs: Additional provider-specific parameters

        Returns:
            LLM instance (ChatOpenAI or ChatVertexAI)
        """
        config = cls._get_config()
        provider = config.provider

        # Create provider instance if not cached
        if cls._llm_provider is None:
            if provider == "openai":
                cls._llm_provider = OpenAILLM(
                    api_key=config.openai_api_key,
                    model=config.openai_model,
                    temperature=config.temperature,
                    max_tokens=config.max_tokens,
                    timeout=config.timeout,
                )
            elif provider == "vertexai":
                cls._llm_provider = VertexAILLM(
                    project=config.google_cloud_project,
                    location=config.google_cloud_region,
                    model=config.vertexai_model,
                    temperature=config.temperature,
                    max_tokens=config.max_tokens,
                    timeout=config.timeout,
                )

        # Get LLM instance with overrides
        return cls._llm_provider.get_llm(
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
            timeout=timeout,
            **kwargs
        )

    @classmethod
    def get_embeddings(
        cls,
        model: Optional[str] = None,
        **kwargs
    ) -> Any:
        """
        Get an embeddings instance based on LLM_PROVIDER environment variable.

        Args:
            model: Override model name
            **kwargs: Additional provider-specific parameters

        Returns:
            Embeddings instance (OpenAIEmbeddings or VertexAIEmbeddings)
        """
        config = cls._get_config()
        provider = config.provider

        # Create provider instance if not cached
        if cls._embedding_provider is None:
            if provider == "openai":
                cls._embedding_provider = OpenAIEmbeddingsProvider(
                    api_key=config.openai_api_key,
                    model=config.openai_embedding_model,
                )
            elif provider == "vertexai":
                cls._embedding_provider = VertexAIEmbeddingsProvider(
                    project=config.google_cloud_project,
                    location=config.google_cloud_region,
                    model=config.vertexai_embedding_model,
                )

        # Get embeddings instance with overrides
        return cls._embedding_provider.get_embeddings(
            model=model,
            **kwargs
        )

    @classmethod
    def validate_configuration(cls) -> dict[str, Any]:
        """
        Validate the current LLM configuration.

        Returns:
            Dictionary with validation results:
            {
                "valid": bool,
                "provider": str,
                "errors": list[str],
                "warnings": list[str]
            }
        """
        config = cls._get_config()
        provider = config.provider
        errors = []
        warnings = []

        # Validate provider-specific configuration
        is_valid, provider_errors = config.validate_for_provider(provider)
        errors.extend(provider_errors)

        # Add warnings for optional settings
        if provider == "openai" and not os.getenv("OPENAI_MODEL"):
            warnings.append("OPENAI_MODEL not set, using default: gpt-4o-mini")

        if provider == "vertexai" and not os.getenv("VERTEXAI_MODEL"):
            warnings.append("VERTEXAI_MODEL not set, using default: gemini-1.5-flash")

        if provider == "vertexai" and not os.getenv("GOOGLE_APPLICATION_CREDENTIALS"):
            warnings.append(
                "GOOGLE_APPLICATION_CREDENTIALS not set, relying on Application Default Credentials"
            )

        return {
            "valid": len(errors) == 0,
            "provider": provider,
            "errors": errors,
            "warnings": warnings,
        }

    @classmethod
    def reset(cls):
        """
        Reset cached configuration and providers.

        Useful for testing or when configuration changes.
        """
        cls._config = None
        cls._llm_provider = None
        cls._embedding_provider = None
