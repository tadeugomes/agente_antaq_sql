"""RAG module for example retrieval."""
from .retriever import ExampleRetriever
from .embeddings import get_embeddings_model, embed_text, embed_texts
from .examples_loader import (
    load_examples,
    get_all_examples,
    get_examples_by_category,
    get_example_categories,
)

__all__ = [
    "ExampleRetriever",
    "get_embeddings_model",
    "embed_text",
    "embed_texts",
    "load_examples",
    "get_all_examples",
    "get_examples_by_category",
    "get_example_categories",
]
