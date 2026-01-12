"""
LangGraph state machine definition for ANTAQ SQL Agent.
"""
from typing import Literal, Optional
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
import os

# Optional Sentry integration
try:
    import sentry_sdk
    SENTRY_AVAILABLE = True
except ImportError:
    SENTRY_AVAILABLE = False

from .state import AgentState
from .nodes import (
    setup_schema_node,
    retrieve_examples_node,
    generate_sql_node,
    validate_sql_node,
    execute_sql_node,
    generate_final_answer_node,
    should_continue_to_execute,
)

# Cache for compiled graph to avoid recreating it on every query
_cached_graph = None


def _get_checkpointer():
    """
    Get the appropriate checkpointer based on configuration.

    Returns:
        MemorySaver or a disk-based checkpointer if available
    """
    # Try to use disk-based checkpointer for better memory management
    try:
        from langgraph.checkpoint.sqlite import SqliteSaver

        # Use a temporary SQLite database for checkpoint storage
        # This persists conversation history to disk instead of memory
        checkpoint_path = os.getenv(
            "LANGCHAIN_CHECKPOINT_PATH",
            os.path.join(os.getcwd(), ".langchain_checkpoint.db")
        )
        return SqliteSaver.from_conn_string(checkpoint_path)
    except ImportError:
        # Fallback to memory-based checkpointer
        return MemorySaver()
    except Exception:
        # If anything goes wrong, fallback to memory
        return MemorySaver()


def create_graph(model_name: str = "gemini-1.5-flash", use_cache: bool = True) -> StateGraph:
    """
    Create and compile the LangGraph state machine.
    Uses caching to avoid recreating the graph on every call.

    Args:
        model_name: Vertex AI model to use (not directly used here, nodes use env var)
        use_cache: Whether to use cached graph (default: True)

    Returns:
        Compiled LangGraph ready for invocation
    """
    global _cached_graph

    # Return cached graph if available
    if use_cache and _cached_graph is not None:
        return _cached_graph

    # Initialize the state graph
    workflow = StateGraph(AgentState)

    # Add all nodes
    workflow.add_node("setup_schema", setup_schema_node)
    workflow.add_node("retrieve_examples", retrieve_examples_node)
    workflow.add_node("generate_sql", generate_sql_node)
    workflow.add_node("validate_sql", validate_sql_node)
    workflow.add_node("execute_sql", execute_sql_node)
    workflow.add_node("generate_final_answer", generate_final_answer_node)

    # Define entry point
    workflow.set_entry_point("setup_schema")

    # Add edges
    workflow.add_edge("setup_schema", "retrieve_examples")
    workflow.add_edge("retrieve_examples", "generate_sql")
    workflow.add_edge("generate_sql", "validate_sql")

    # Conditional routing from validation
    workflow.add_conditional_edges(
        "validate_sql",
        should_continue_to_execute,
        {
            "execute": "execute_sql",
            "retry": "generate_sql",
            "end": END
        }
    )

    workflow.add_edge("execute_sql", "generate_final_answer")
    workflow.add_edge("generate_final_answer", END)

    # Compile with checkpointer (disk-based if available, otherwise memory)
    checkpointer = _get_checkpointer()

    compiled = workflow.compile(
        checkpointer=checkpointer,
        interrupt_before=None,
        interrupt_after=None
    )

    # Cache the compiled graph for future use
    if use_cache:
        _cached_graph = compiled

    return compiled


async def query_agente(
    question: str,
    thread_id: str = "session1",
    max_attempts: int = 3
) -> dict:
    """
    Execute a query through the agent.

    Args:
        question: User's question in natural language
        thread_id: Thread ID for conversation memory
        max_attempts: Maximum SQL generation attempts

    Returns:
        Dictionary with the agent's response
    """
    try:
        return await _query_agente_impl(question, thread_id, max_attempts)
    except Exception as e:
        # Capture exception in Sentry if available
        if SENTRY_AVAILABLE:
            sentry_sdk.capture_exception(e)
            # Add additional context
            sentry_sdk.set_context("agent_query", {
                "question": question[:200],  # Truncate long questions
                "thread_id": thread_id,
                "max_attempts": max_attempts,
            })
        raise


async def _query_agente_impl(
    question: str,
    thread_id: str,
    max_attempts: int
) -> dict:
    """
    Internal implementation of query execution.
    """
    from langchain_core.messages import HumanMessage

    graph = create_graph()

    # Initial state - include the user's question as a message for conversation history
    # Don't set empty messages[] to allow checkpoint to restore history
    initial_state: AgentState = {
        "messages": [HumanMessage(content=question)],  # Add user question to history
        "question": question,
        "dataset_schema": None,  # Will be loaded by setup_schema_node
        "generated_sql": None,
        "validated_sql": None,
        "sql_error": None,
        "query_results": None,
        "row_count": None,
        "retrieved_examples": None,
        "final_answer": None,
        "attempt_count": 0,
        "max_attempts": max_attempts
    }

    config = {
        "configurable": {
            "thread_id": thread_id
        }
    }

    result = await graph.ainvoke(initial_state, config=config)

    return result
