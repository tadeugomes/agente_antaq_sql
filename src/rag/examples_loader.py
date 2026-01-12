"""
Load QA examples from documentation into BigQuery Vector Store.
"""
from typing import List, Dict, Any
from ..bigquery.vector_store import QA_EXAMPLES, load_examples_to_vector_store


def load_examples(
    examples: List[Dict[str, Any]] | None = None,
    table_name: str = "qa_embeddings"
) -> None:
    """
    Load QA examples into BigQuery Vector Store.

    Args:
        examples: List of example dictionaries (defaults to QA_EXAMPLES)
        table_name: Table name for embeddings
    """
    examples = examples or QA_EXAMPLES
    load_examples_to_vector_store(examples, table_name)


def get_all_examples() -> List[Dict[str, Any]]:
    """
    Get all QA examples.

    Returns:
        List of example dictionaries
    """
    return QA_EXAMPLES


def get_examples_by_category(category: str) -> List[Dict[str, Any]]:
    """
    Get QA examples filtered by category.

    Args:
        category: Category to filter by

    Returns:
        List of example dictionaries
    """
    return [ex for ex in QA_EXAMPLES if ex.get("category") == category]


def get_example_categories() -> List[str]:
    """
    Get all unique categories from QA examples.

    Returns:
        List of category names
    """
    categories = set(ex.get("category", "") for ex in QA_EXAMPLES)
    categories.discard("")
    return sorted(list(categories))
