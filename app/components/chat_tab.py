"""
Chat Tab Component - AI agent interface with clean UX.
No technical SQL exposed to user by default.
Optimized for memory - stores only metadata, not full dataframes.
"""
import asyncio
import logging
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
    - Example questions (at top when chat is empty)
    - Chat input for user questions
    - Header with title and clear button
    - Chat message history
    - AI responses (without SQL unless debug mode)

    Memory optimizations:
    - Limits chat history size
    - Stores query results separately from messages
    - Doesn't cache large result sets (>1000 rows)
    """
    # Get chat messages
    messages = SessionManager.get_chat_messages()

    if "pergunta" not in st.session_state:
        st.session_state["pergunta"] = ""

    if st.session_state.get("pergunta_pending"):
        st.session_state["pergunta"] = st.session_state["pergunta_pending"]
        st.session_state["pergunta_pending"] = ""

    if st.session_state.get("_clear_pergunta"):
        st.session_state["pergunta"] = ""
        st.session_state["_clear_pergunta"] = False

    with st.container(border=True):
        col1, col2 = st.columns([4, 1])
        with col1:
            st.markdown("### Chat com os dados da ANTAQ")
            st.caption("Faça uma pergunta em linguagem natural sobre os dados do Estatístico Aquaviário da ANTAQ.")
        with col2:
            if messages:
                if st.button("Nova conversa", key="new_conversation", use_container_width=True):
                    SessionManager.clear_session()
                    clear_results_cache()
                    st.session_state["pergunta"] = ""
                    st.rerun()

        # Display chat history
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

                    # Show error details when available
                    if message.get("error_detail") or message.get("error_trace"):
                        with st.expander("Ver detalhes do erro"):
                            detail = message.get("error_detail", "")
                            trace = message.get("error_trace", "")
                            st.code(f"{detail}\n\n{trace}".strip(), language="text")

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
        prompt = st.text_area(
            "Faça uma pergunta em linguagem natural sobre os dados do Estatístico Aquaviário da ANTAQ.",
            placeholder="Ex.: Quanto foi exportado em toneladas pelo porto de Santos em janeiro de 2024?",
            height=80,
            key="pergunta",
        )

        submit = st.button("Consultar", type="primary", use_container_width=True)
        if submit:
            if not prompt or not prompt.strip():
                st.info("Digite uma pergunta para iniciar.")
                return

            prompt = prompt.strip()

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
                with st.spinner("Consultando dados..."):
                    try:
                        # Run async query
                        from src.agent.graph import query_agente

                        # Get unique session ID for conversation memory
                        session_id = SessionManager.get_or_create_session_id()

                        result = asyncio.run(query_agente(
                            question=prompt,
                            thread_id=session_id
                        ))

                        sql = result.get("validated_sql", "")
                        results = result.get("query_results", [])
                        row_count = len(results) if results else 0
                        answer = result.get("final_answer", "") or ""

                        if not answer.strip():
                            if results:
                                answer = f"Encontrei {row_count} resultados para sua consulta."
                            else:
                                answer = "Nenhum dado encontrado para o critério informado."

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
                        error_detail = str(e)
                        error_trace = traceback.format_exc()
                        logging.exception(
                            "Erro ao executar consulta no chat",
                            extra={
                                "prompt_len": len(prompt) if prompt else 0
                            }
                        )
                        print(f"[chat] erro: {error_detail}\n{error_trace}")
                        error_message = (
                            "Ocorreu um erro ao consultar os dados. "
                            "Tente novamente ou ajuste o período/porto."
                        )

                        # Show user-friendly error
                        info_box("Erro", error_message, "error")

                        # Show error details in expander
                        with st.expander("Ver detalhes do erro"):
                            st.code(f"{error_detail}\n\n{error_trace}", language="text")

                        # Add error to history
                        SessionManager.add_chat_message("assistant", error_message)
                        st.session_state[SessionManager.CHAT_MESSAGES_KEY][-1].update({
                            "error_detail": error_detail,
                            "error_trace": error_trace
                        })

            st.session_state["_clear_pergunta"] = True
            st.rerun()


def show_empty_state():
    """Display empty state when no messages exist."""
    empty_state(
        title="Digite uma pergunta para iniciar",
        message="Faça uma pergunta em linguagem natural sobre os dados do Estatístico Aquaviário da ANTAQ.",
        icon=Icons.CHAT
    )
