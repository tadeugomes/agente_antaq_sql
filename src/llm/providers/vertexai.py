"""
Google Vertex AI provider implementation for LLM and Embeddings.
"""
import os
from typing import Any, Optional
from langchain_google_vertexai import ChatVertexAI, VertexAIEmbeddings
from .base import LLMProvider, EmbeddingProvider


class VertexAILLM(LLMProvider):
    """
    Google Vertex AI LLM provider using LangChain's ChatVertexAI.
    """

    def __init__(
        self,
        project: Optional[str] = None,
        location: str = "us-central1",
        model: str = "gemini-1.5-flash",
        temperature: float = 0,
        max_tokens: Optional[int] = None,
        timeout: int = 60,
    ):
        """
        Initialize VertexAI LLM provider.

        Args:
            project: Google Cloud project ID (uses GOOGLE_CLOUD_PROJECT env var if None)
            location: Cloud region (default: us-central1)
            model: Model name (default: gemini-1.5-flash)
            temperature: Sampling temperature (0-1)
            max_tokens: Maximum tokens in response
            timeout: Request timeout in seconds
        """
        self.project = project or os.getenv("GOOGLE_CLOUD_PROJECT")
        self.location = location
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
    ) -> ChatVertexAI:
        """
        Get a configured ChatVertexAI instance.

        Args:
            model: Override model name
            temperature: Override temperature
            max_tokens: Override max tokens
            timeout: Override timeout
            **kwargs: Additional ChatVertexAI parameters

        Returns:
            Configured ChatVertexAI instance
        """
        return ChatVertexAI(
            model=model or self.model,
            temperature=temperature if temperature is not None else self.temperature,
            max_tokens=max_tokens or self.max_tokens,
            timeout=timeout or self.timeout,
            project=self.project,
            location=self.location,
            **kwargs
        )

    def validate_credentials(self) -> tuple[bool, list[str]]:
        """
        Validate VertexAI credentials are configured.

        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        errors = []

        if not self.project:
            errors.append("GOOGLE_CLOUD_PROJECT is not set")

        # Check if credentials are configured
        creds_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
        if not creds_path:
            # Try to detect if Application Default Credentials are available
            try:
                import google.auth
                google.auth.default()
            except Exception:
                errors.append(
                    "GOOGLE_APPLICATION_CREDENTIALS or Application Default Credentials not configured"
                )

        return len(errors) == 0, errors


class VertexAIEmbeddingsProvider(EmbeddingProvider):
    """
    Google Vertex AI embeddings provider using LangChain's VertexAIEmbeddings.
    """

    def __init__(
        self,
        project: Optional[str] = None,
        location: str = "us-central1",
        model: str = "textembedding-gecko@003",
    ):
        """
        Initialize VertexAI embeddings provider.

        Args:
            project: Google Cloud project ID (uses GOOGLE_CLOUD_PROJECT env var if None)
            location: Cloud region (default: us-central1)
            model: Embedding model name (default: textembedding-gecko@003)
        """
        self.project = project or os.getenv("GOOGLE_CLOUD_PROJECT")
        self.location = location
        self.model = model

    def get_embeddings(
        self,
        model: Optional[str] = None,
        **kwargs
    ) -> VertexAIEmbeddings:
        """
        Get a configured VertexAIEmbeddings instance.

        Args:
            model: Override model name
            **kwargs: Additional VertexAIEmbeddings parameters

        Returns:
            Configured VertexAIEmbeddings instance
        """
        return VertexAIEmbeddings(
            model=model or self.model,
            project=self.project,
            location=self.location,
            **kwargs
        )

    def validate_credentials(self) -> tuple[bool, list[str]]:
        """
        Validate VertexAI credentials are configured.

        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        errors = []

        if not self.project:
            errors.append("GOOGLE_CLOUD_PROJECT is not set")

        # Check if credentials are configured
        creds_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
        if not creds_path:
            # Try to detect if Application Default Credentials are available
            try:
                import google.auth
                google.auth.default()
            except Exception:
                errors.append(
                    "GOOGLE_APPLICATION_CREDENTIALS or Application Default Credentials not configured"
                )

        return len(errors) == 0, errors
