"""
Chat Tab Component - AI agent interface with clean UX.
No technical SQL exposed to user by default.
Optimized for memory - stores only metadata, not full dataframes.
"""
import asyncio
from typing import Optional, Dict, Any
import streamlit as st

from ..utils.session import SessionManager
from ..components.base import info_box, empty_state, loading_spinner
from ..components.styles import Icons


# Session keys for optimized storage
QUERY_RESULTS_CACHE_KEY = "query_results_cache"
MAX_MESSAGES_IN_HISTORY = 50  # Limit chat history size
MAX_CACHED_RESULTS = 10  # Keep only last N query results in memory


def get_results_cache() -> Dict[str, Any]:
    """Get the query results cache."""
    return st.session_state.get(QUERY_RESULTS_CACHE_KEY, {})


def save_result_to_cache(message_idx: int, results: Any, sql: str = "") -> None:
    """
    Save query results to a separate cache to avoid storing dataframes in chat history.

    Args:
        message_idx: Index of the message in chat history
        results: Query results (dataframe or list)
        sql: SQL query that generated the results
    """
    cache = get_results_cache()

    # Limit cache size - remove oldest entries
    if len(cache) >= MAX_CACHED_RESULTS:
        # Sort by key (message index) and remove oldest
        sorted_keys = sorted(cache.keys())
        for key in sorted_keys[:len(cache) - MAX_CACHED_RESULTS + 1]:
            del cache[key]

    # Store only metadata if results are too large
    row_count = len(results) if results else 0
    cache[str(message_idx)] = {
        "results": results if row_count <= 1000 else None,  # Don't cache large results
        "row_count": row_count,
        "sql": sql,
        "truncated": row_count > 1000
    }

    st.session_state[QUERY_RESULTS_CACHE_KEY] = cache


def get_cached_result(message_idx: int) -> Optional[Dict[str, Any]]:
    """Get cached result for a message."""
    cache = get_results_cache()
    return cache.get(str(message_idx))


def clear_results_cache() -> None:
    """Clear the results cache."""
    if QUERY_RESULTS_CACHE_KEY in st.session_state:
        del st.session_state[QUERY_RESULTS_CACHE_KEY]


def show_chat_tab():
    """
    Entry point for the Chat tab.

    Displays:
    - Chat message history
    - Chat input for user questions
    - AI responses (without SQL unless debug mode)
    - Example questions (below input when chat is empty)

    Memory optimizations:
    - Limits chat history size
    - Stores query results separately from messages
    - Doesn't cache large result sets (>1000 rows)
    """
    # Header with "Nova Conversa" button
    col1, col2 = st.columns([4, 1])
    with col1:
        st.markdown("### 💬 Chat")
    with col2:
        if st.button("Nova Conversa", key="new_conversation", use_container_width=True):
            SessionManager.clear_session()
            clear_results_cache()
            st.rerun()

    # Display chat history
    messages = SessionManager.get_chat_messages()

    if not messages:
        show_empty_state()
    else:
        for idx, message in enumerate(messages):
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

                # Show SQL only in debug mode
                if "sql" in message and SessionManager.is_debug_mode():
                    with st.expander(f"{Icons.SEARCH} SQL Gerado"):
                        st.code(message["sql"], language="sql")

                # Show results if enabled - fetch from cache
                if message.get("has_results") and SessionManager.show_results():
                    cached = get_cached_result(idx)
                    if cached:
                        row_count = cached["row_count"]
                        title = f"{Icons.CHART} Resultados ({row_count} linhas)"
                        if cached.get("truncated"):
                            title += " [muitos resultados para exibir]"

                        with st.expander(title):
                            if cached["results"] is not None:
                                st.dataframe(cached["results"])
                            else:
                                st.info(
                                    f"Query retornou {row_count} linhas. "
                                    "Resultado muito grande para exibir em cache."
                                )

    # Chat input
    if prompt := st.chat_input("Faça sua pergunta sobre os dados ANTAQ..."):
        # Limit message history size before adding new message
        messages = SessionManager.get_chat_messages()
        if len(messages) >= MAX_MESSAGES_IN_HISTORY:
            # Remove oldest messages (keep pairs of user/assistant)
            messages_to_remove = (len(messages) - MAX_MESSAGES_IN_HISTORY + 2)
            st.session_state[SessionManager.CHAT_MESSAGES_KEY] = messages[messages_to_remove:]

        # Add user message
        SessionManager.add_chat_message("user", prompt)

        # Display user message
        with st.chat_message("user"):
            st.markdown(prompt)

        # Generate response
        with st.chat_message("assistant"):
            with st.spinner("Processando..."):
                try:
                    # Run async query
                    from src.agent.graph import query_agente

                    # Get unique session ID for conversation memory
                    session_id = SessionManager.get_or_create_session_id()

                    result = asyncio.run(query_agente(
                        question=prompt,
                        thread_id=session_id
                    ))

                    # Extract answer - handle None or empty responses
                    answer = result.get("final_answer", None)

                    if not answer or answer.strip() == "":
                        # If no answer was generated, provide a fallback response
                        sql = result.get("validated_sql", "")
                        results = result.get("query_results", [])
                        row_count = len(results) if results else 0

                        if results:
                            answer = f"Encontrei {row_count} resultados para sua consulta."
                        elif sql:
                            answer = "A query foi executada mas não retornou resultados. Tente reformular sua pergunta."
                        else:
                            answer = "Não foi possível processar sua solicitação. Tente reformular sua pergunta."
                    else:
                        sql = result.get("validated_sql", "")
                        results = result.get("query_results", [])
                        row_count = len(results) if results else 0

                    # Display answer
                    st.markdown(answer)

                    # Display SQL only in debug mode
                    if sql and SessionManager.is_debug_mode():
                        with st.expander(f"{Icons.SEARCH} SQL Gerado"):
                            st.code(sql, language="sql")

                    # Display results if enabled
                    if results and SessionManager.show_results():
                        with st.expander(f"{Icons.CHART} Resultados ({row_count} linhas)"):
                            st.dataframe(results)

                    # Get current message index
                    messages = SessionManager.get_chat_messages()
                    message_idx = len(messages)  # Index of the message we're about to add

                    # Add assistant message to history (without full results)
                    assistant_message = {
                        "role": "assistant",
                        "content": answer,
                        "has_results": bool(results),
                        "row_count": row_count
                    }

                    if sql:
                        assistant_message["sql"] = sql

                    SessionManager.add_chat_message("assistant", answer)
                    # Update with full message data
                    st.session_state[SessionManager.CHAT_MESSAGES_KEY][-1] = assistant_message

                    # Save results to separate cache
                    if results:
                        save_result_to_cache(message_idx, results, sql)

                except Exception as e:
                    import traceback
                    error_message = "Ocorreu um erro ao processar sua solicitação. Tente novamente."
                    error_detail = str(e)

                    # Show user-friendly error
                    info_box("Erro", error_message, "error")

                    # Show error details in expander
                    with st.expander("Ver detalhes do erro"):
                        st.code(f"{error_detail}\n\n{traceback.format_exc()}", language="text")

                    # Add error to history
                    SessionManager.add_chat_message("assistant", error_message)

    # Example questions (show when chat is empty, above input)
    if not messages:
        st.markdown("---")
        st.markdown("**💡 Exemplos de perguntas:**")

        example_questions = [
            "Qual foi o total de carga movimentado em 2024?",
            "Quais são os 10 maiores portos do Brasil?",
            "Quanto foi exportado pelo porto de Santos em janeiro?",
            "Compare as exportações e importações de 2024",
        ]

        for question in example_questions:
            if st.button(question, key=f"example_{question}", use_container_width=True):
                SessionManager.add_chat_message("user", question)
                st.rerun()


def show_empty_state():
    """Display empty state when no messages exist."""
    empty_state(
        title="Comece uma conversa",
        message="Faça uma pergunta sobre os dados da ANTAQ em linguagem natural.",
        icon=Icons.CHAT
    )
