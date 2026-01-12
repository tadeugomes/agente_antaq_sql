"""
Embedding generation for RAG.
"""
from typing import List, Any
from ..llm import LLMFactory


def get_embeddings_model(
    model_name: str | None = None
) -> Any:
    """
    Get embeddings model based on LLM_PROVIDER configuration.

    Args:
        model_name: Embedding model name (uses provider default if None)

    Returns:
        Embeddings instance (OpenAIEmbeddings or VertexAIEmbeddings)
    """
    if model_name:
        return LLMFactory.get_embeddings(model=model_name)
    return LLMFactory.get_embeddings()


async def embed_text(text: str) -> List[float]:
    """
    Embed a single text.

    Args:
        text: Text to embed

    Returns:
        Embedding vector
    """
    embeddings = get_embeddings_model()
    return await embeddings.aembed_query(text)


async def embed_texts(texts: List[str]) -> List[List[float]]:
    """
    Embed multiple texts.

    Args:
        texts: List of texts to embed

    Returns:
        List of embedding vectors
    """
    embeddings = get_embeddings_model()
    return await embeddings.aembed_documents(texts)
