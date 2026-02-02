"""
Node implementations for the LangGraph workflow.
"""
import json
import re
import os
from typing import Dict, Any, List

from langchain_core.messages import AIMessage, HumanMessage, SystemMessage

from ..bigquery.client import get_bigquery_client
from ..bigquery.schema import get_schema_retriever
from ..rag.retriever import ExampleRetriever
from ..utils.validation import get_sql_validator
from ..utils.formatting import format_results_for_llm
from .state import AgentState
from .prompts import get_system_prompt, get_sql_generation_prompt, get_final_answer_prompt
from .metadata_helper import get_metadata_helper


# Initialize dependencies
bq_client = get_bigquery_client()
schema_retriever = get_schema_retriever()
sql_validator = get_sql_validator()
metadata_helper = None  # Lazy initialization


def get_llm():
    """Get the LLM instance based on LLM_PROVIDER configuration."""
    from ..llm import LLMFactory
    return LLMFactory.get_llm()


async def setup_schema_node(state: AgentState) -> Dict[str, Any]:
    """
    Initialize: Retrieve and cache BigQuery schema.
    Uses MetadataHelper to get schema from dicionario_dados table or fallback.
    Only runs once per conversation.
    """
    global metadata_helper

    if state.get("dataset_schema") is None:
        # Initialize metadata helper with BigQuery client
        if metadata_helper is None:
            metadata_helper = get_metadata_helper(bq_client.client)

        # Get schema from metadata helper (tries dicionario_dados first, then fallback)
        schema = metadata_helper.get_schema_for_prompt()

        return {
            "dataset_schema": schema,
            "messages": [AIMessage(content="Schema BigQuery carregado (usando MetadataHelper).")]
        }

    return {
        "messages": [AIMessage(content="Schema já em memória.")]
    }


async def retrieve_examples_node(state: AgentState) -> Dict[str, Any]:
    """
    Retrieve relevant QA examples using RAG.
    Uses BigQuery Vector Store for semantic search.
    """
    question = state.get("question") or state["messages"][-1].content

    # Get similar examples from vector store
    try:
        retriever = ExampleRetriever()
        examples = await retriever.retrieve(
            question=question,
            top_k=3
        )
    except Exception:
        # If RAG fails, continue without examples
        examples = []

    return {
        "retrieved_examples": examples,
        "messages": [AIMessage(content=f"Recuperados {len(examples)} exemplos similares.")]
    }


async def generate_sql_node(state: AgentState) -> Dict[str, Any]:
    """
    Generate SQL query using LLM with schema and examples.
    Uses conversation history for context on follow-up questions.
    """
    # Build system prompt with schema and examples
    system_prompt = get_system_prompt(
        schema=state["dataset_schema"],
        examples=state.get("retrieved_examples", [])
    )

    # Build messages with conversation history
    messages = [SystemMessage(content=system_prompt)]

    # Add conversation history (excluding internal AIMessages from nodes)
    history = state.get("messages", [])
    for msg in history:
        # Include all human messages and AI responses, but skip internal node messages
        # Internal messages typically don't have content meant for the user
        if msg.type == "human":
            messages.append(msg)
        elif msg.type in ["ai", "assistant"]:
            # Only include AI messages that look like actual responses (not node status)
            content = msg.content if hasattr(msg, 'content') else ""
            # Skip short status messages from internal nodes
            if content and len(content) > 50:  # Actual responses are longer
                messages.append(msg)

    # Invoke LLM
    llm = get_llm()
    response = await llm.ainvoke(messages)

    # Extract SQL from response
    sql_query = extract_sql_from_response(response.content)

    # Increment attempt count
    attempt_count = state.get("attempt_count", 0) + 1

    return {
        "generated_sql": sql_query,
        "attempt_count": attempt_count,
        "messages": [response]
    }


async def validate_sql_node(state: AgentState) -> Dict[str, Any]:
    """
    Validate the generated SQL for security and correctness.
    """
    sql_query = state.get("generated_sql", "")

    if not sql_query:
        return {
            "validated_sql": None,
            "sql_error": "Nenhuma query foi gerada."
        }

    # Run validation
    validation_result = sql_validator.validate(sql_query)

    if not validation_result["is_valid"]:
        error_msg = "Erros de validação: " + "; ".join(validation_result["errors"])
        return {
            "validated_sql": None,
            "sql_error": error_msg,
            "messages": [AIMessage(content=error_msg)]
        }

    # Check if we've exceeded max attempts
    if state.get("attempt_count", 0) >= state.get("max_attempts", 3):
        return {
            "validated_sql": None,
            "sql_error": "Número máximo de tentativas atingido.",
            "messages": [AIMessage(content="Maximum retry limit reached.")]
        }

    return {
        "validated_sql": validation_result.get("sanitized_query", sql_query),
        "sql_error": None
    }


async def execute_sql_node(state: AgentState) -> Dict[str, Any]:
    """
    Execute validated SQL against BigQuery.
    """
    sql_query = state["validated_sql"]

    try:
        results = await bq_client.aquery(sql_query)
        row_count = len(results) if results else 0

        result_message = f"Query executado com sucesso. {row_count} linhas retornadas."

        return {
            "query_results": results,
            "row_count": row_count,
            "messages": [AIMessage(content=result_message)]
        }

    except Exception as e:
        error_message = f"Erro ao executar query: {str(e)}"
        return {
            "query_results": None,
            "row_count": 0,
            "sql_error": error_message,
            "messages": [AIMessage(content=error_message)]
        }


async def generate_final_answer_node(state: AgentState) -> Dict[str, Any]:
    """
    Generate natural language answer from query results.
    """
    question = state.get("question") or state["messages"][-1].content
    results = state.get("query_results", [])
    sql_query = state.get("validated_sql", "")

    # Format results for LLM
    results_text = format_results_for_llm(results)

    # Generate final answer
    prompt = get_final_answer_prompt(
        question=question,
        sql_query=sql_query,
        results=results_text
    )

    llm = get_llm()
    response = await llm.ainvoke([HumanMessage(content=prompt)])

    # Ensure we have a valid response
    answer_content = response.content if response and response.content else ""

    if not answer_content or not answer_content.strip():
        # Fallback response if LLM didn't generate anything
        if results:
            row_count = len(results)
            answer_content = f"Query executada com sucesso. {row_count} registros encontrados."
        elif sql_query:
            answer_content = "Query executada mas não retornou resultados."
        else:
            answer_content = "Não foi possível processar sua solicitação. Tente reformular sua pergunta."

    return {
        "final_answer": answer_content,
        "messages": [response]
    }


# Conditional edge functions

def should_continue_to_execute(state: AgentState) -> str:
    """Decide next step after SQL validation."""
    if state.get("sql_error"):
        # If we have an error and haven't exceeded attempts, retry
        if state.get("attempt_count", 0) < state.get("max_attempts", 3):
            return "retry"
        return "end"

    if state.get("validated_sql"):
        return "execute"

    return "end"


def extract_sql_from_response(response: str) -> str:
    """Extract SQL query from LLM response."""
    # Look for code blocks
    if "```sql" in response:
        start = response.find("```sql") + 6
        end = response.find("```", start)
        return response[start:end].strip()

    if "```" in response:
        start = response.find("```") + 3
        end = response.find("```", start)
        return response[start:end].strip()

    # Return whole response if no code blocks
    return response.strip()
