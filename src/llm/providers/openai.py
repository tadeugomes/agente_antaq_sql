"""
OpenAI provider implementation for LLM and Embeddings.
"""
import os
from typing import Any, Optional
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from .base import LLMProvider, EmbeddingProvider


class OpenAILLM(LLMProvider):
    """
    OpenAI LLM provider using LangChain's ChatOpenAI.
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = "gpt-4o-mini",
        temperature: float = 0,
        max_tokens: Optional[int] = None,
        timeout: int = 60,
    ):
        """
        Initialize OpenAI LLM provider.

        Args:
            api_key: OpenAI API key (uses OPENAI_API_KEY env var if None)
            model: Model name (default: gpt-4o-mini)
            temperature: Sampling temperature (0-1)
            max_tokens: Maximum tokens in response
            timeout: Request timeout in seconds
        """
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.timeout = timeout

    def get_llm(
        self,
        model: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        timeout: Optional[int] = None,
        **kwargs
    ) -> ChatOpenAI:
        """
        Get a configured ChatOpenAI instance.

        Args:
            model: Override model name
            temperature: Override temperature
            max_tokens: Override max tokens
            timeout: Override timeout
            **kwargs: Additional ChatOpenAI parameters

        Returns:
            Configured ChatOpenAI instance
        """
        return ChatOpenAI(
            model=model or self.model,
            temperature=temperature if temperature is not None else self.temperature,
            max_tokens=max_tokens or self.max_tokens,
            request_timeout=timeout or self.timeout,
            api_key=self.api_key,
            **kwargs
        )

    def validate_credentials(self) -> tuple[bool, list[str]]:
        """
        Validate OpenAI API key is present.

        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        errors = []

        if not self.api_key:
            errors.append("OPENAI_API_KEY is not set")

        return len(errors) == 0, errors


class OpenAIEmbeddingsProvider(EmbeddingProvider):
    """
    OpenAI embeddings provider using LangChain's OpenAIEmbeddings.
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = "text-embedding-3-small",
    ):
        """
        Initialize OpenAI embeddings provider.

        Args:
            api_key: OpenAI API key (uses OPENAI_API_KEY env var if None)
            model: Embedding model name (default: text-embedding-3-small)
        """
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.model = model

    def get_embeddings(
        self,
        model: Optional[str] = None,
        **kwargs
    ) -> OpenAIEmbeddings:
        """
        Get a configured OpenAIEmbeddings instance.

        Args:
            model: Override model name
            **kwargs: Additional OpenAIEmbeddings parameters

        Returns:
            Configured OpenAIEmbeddings instance
        """
        return OpenAIEmbeddings(
            model=model or self.model,
            api_key=self.api_key,
            **kwargs
        )

    def validate_credentials(self) -> tuple[bool, list[str]]:
        """
        Validate OpenAI API key is present.

        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        errors = []

        if not self.api_key:
            errors.append("OPENAI_API_KEY is not set")

        return len(errors) == 0, errors
