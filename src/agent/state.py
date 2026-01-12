"""
Agent state definitions using Pydantic for type safety.
"""
from typing import TypedDict, Annotated, Optional, List, Dict, Any
from langchain_core.messages import BaseMessage

# Use add_messages from langgraph for message accumulation
from langgraph.graph.message import add_messages


class AgentState(TypedDict):
    """
    Main state for the ANTAQ SQL Agent workflow.

    This state is passed between nodes in the LangGraph.
    """
    # Message history (accumulates across conversation turns)
    messages: Annotated[List[BaseMessage], add_messages]

    # BigQuery schema (cached)
    dataset_schema: Optional[str]

    # Current query processing
    question: Optional[str]
    generated_sql: Optional[str]
    validated_sql: Optional[str]
    sql_error: Optional[str]

    # Query execution results
    query_results: Optional[List[Dict[str, Any]]]
    row_count: Optional[int]

    # RAG examples
    retrieved_examples: Optional[List[Dict[str, str]]]

    # Final answer
    final_answer: Optional[str]

    # Metadata
    attempt_count: int
    max_attempts: int


class ValidationResult(TypedDict):
    """Result of SQL validation."""
    is_valid: bool
    errors: List[str]
    warnings: List[str]
    sanitized_query: Optional[str]
