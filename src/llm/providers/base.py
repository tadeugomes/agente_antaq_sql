"""
Abstract base classes for LLM and Embedding providers.
All provider implementations must inherit from these base classes.
"""
from abc import ABC, abstractmethod
from typing import Any, Optional


class LLMProvider(ABC):
    """
    Abstract base class for LLM providers.

    All LLM providers (OpenAI, VertexAI, etc.) must implement this interface.
    """

    @abstractmethod
    def get_llm(
        self,
        model: Optional[str] = None,
        temperature: float = 0,
        max_tokens: Optional[int] = None,
        timeout: Optional[int] = None,
        **kwargs
    ) -> Any:
        """
        Get an LLM instance configured with the specified parameters.

        Args:
            model: Model name (uses provider default if None)
            temperature: Sampling temperature (0-1)
            max_tokens: Maximum tokens in response
            timeout: Request timeout in seconds
            **kwargs: Additional provider-specific parameters

        Returns:
            Configured LLM instance (e.g., ChatOpenAI, ChatVertexAI)
        """
        pass

    @abstractmethod
    def validate_credentials(self) -> tuple[bool, list[str]]:
        """
        Validate that required credentials and configuration are present.

        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        pass


class EmbeddingProvider(ABC):
    """
    Abstract base class for embedding providers.

    All embedding providers must implement this interface.
    """

    @abstractmethod
    def get_embeddings(
        self,
        model: Optional[str] = None,
        **kwargs
    ) -> Any:
        """
        Get an embeddings instance configured with the specified parameters.

        Args:
            model: Model name (uses provider default if None)
            **kwargs: Additional provider-specific parameters

        Returns:
            Configured embeddings instance
        """
        pass

    @abstractmethod
    def validate_credentials(self) -> tuple[bool, list[str]]:
        """
        Validate that required credentials and configuration are present.

        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        pass
