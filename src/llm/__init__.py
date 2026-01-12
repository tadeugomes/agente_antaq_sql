"""
Multi-LLM Provider Support Module

This module provides a factory pattern for using multiple LLM providers
(OpenAI, Google Vertex AI) with easy switching via environment variables.

Basic Usage:
    from src.llm import LLMFactory

    # Get LLM instance
    llm = LLMFactory.get_llm()
    embeddings = LLMFactory.get_embeddings()

    # Validate configuration
    validation = LLMFactory.validate_configuration()

Configuration:
    Set LLM_PROVIDER environment variable to 'openai' or 'vertexai'

    For OpenAI:
        export OPENAI_API_KEY=sk-...
        export OPENAI_MODEL=gpt-4o-mini

    For VertexAI:
        export GOOGLE_CLOUD_PROJECT=saasimpacto
        export GOOGLE_APPLICATION_CREDENTIALS=/path/to/credentials.json
"""
from .factory import LLMFactory
from .config import LLMConfig

__all__ = [
    "LLMFactory",
    "LLMConfig",
]
