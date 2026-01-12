"""
Session state management utilities for Streamlit.
Provides centralized management of session state with type safety.
"""
import streamlit as st
from typing import Any, Optional, Dict


class SessionManager:
    """
    Centralized session state manager.

    Provides methods for saving, retrieving, and clearing
    session state data with consistent key naming.
    """

    # Overview data keys
    OVERVIEW_DATA_KEY = "overview_data"
    OVERVIEW_PARAMS_KEY = "overview_params"

    # Chat state keys
    CHAT_MESSAGES_KEY = "chat_messages"
    CHAT_CONTEXT_KEY = "chat_context"
    ACTIVE_TAB_KEY = "active_tab"
    SESSION_ID_KEY = "session_id"  # Unique session ID for conversation memory

    # UI state keys
    SHOW_SQL_KEY = "show_sql"
    SHOW_RESULTS_KEY = "show_results"
    DEBUG_MODE_KEY = "debug_mode"

    # Cache keys
    LATEST_DATA_INFO_KEY = "latest_data_info"

    @staticmethod
    def init() -> None:
        """
        Initialize all session state variables with default values.
        Call this once at app startup.
        """
        # Initialize overview state
        if SessionManager.OVERVIEW_DATA_KEY not in st.session_state:
            st.session_state[SessionManager.OVERVIEW_DATA_KEY] = None
        if SessionManager.OVERVIEW_PARAMS_KEY not in st.session_state:
            st.session_state[SessionManager.OVERVIEW_PARAMS_KEY] = None

        # Initialize chat state
        if SessionManager.CHAT_MESSAGES_KEY not in st.session_state:
            st.session_state[SessionManager.CHAT_MESSAGES_KEY] = []
        if SessionManager.CHAT_CONTEXT_KEY not in st.session_state:
            st.session_state[SessionManager.CHAT_CONTEXT_KEY] = None
        # Initialize session ID for conversation memory
        if SessionManager.SESSION_ID_KEY not in st.session_state:
            import uuid
            st.session_state[SessionManager.SESSION_ID_KEY] = f"session_{uuid.uuid4().hex[:8]}"

        # Initialize UI state
        if SessionManager.SHOW_SQL_KEY not in st.session_state:
            st.session_state[SessionManager.SHOW_SQL_KEY] = False
        if SessionManager.SHOW_RESULTS_KEY not in st.session_state:
            st.session_state[SessionManager.SHOW_RESULTS_KEY] = True
        if SessionManager.DEBUG_MODE_KEY not in st.session_state:
            st.session_state[SessionManager.DEBUG_MODE_KEY] = False

        # Initialize cache
        if SessionManager.LATEST_DATA_INFO_KEY not in st.session_state:
            st.session_state[SessionManager.LATEST_DATA_INFO_KEY] = None

    # ==========================================================================
    # Overview Methods
    # ==========================================================================

    @staticmethod
    def save_overview(params: Dict[str, Any], data: Dict[str, Any]) -> None:
        """
        Save overview parameters and data to session state.

        Args:
            params: Dictionary with selection parameters (porto, periodo, etc.)
            data: Dictionary with fetched overview data
        """
        st.session_state[SessionManager.OVERVIEW_PARAMS_KEY] = params
        st.session_state[SessionManager.OVERVIEW_DATA_KEY] = data

    @staticmethod
    def get_overview() -> tuple[Optional[Dict[str, Any]], Optional[Dict[str, Any]]]:
        """
        Retrieve overview parameters and data from session state.

        Returns:
            Tuple of (params, data). Both are None if no data is saved.
        """
        params = st.session_state.get(SessionManager.OVERVIEW_PARAMS_KEY)
        data = st.session_state.get(SessionManager.OVERVIEW_DATA_KEY)
        return params, data

    @staticmethod
    def has_overview() -> bool:
        """
        Check if overview data exists in session state.

        Returns:
            True if overview data is saved
        """
        return st.session_state.get(SessionManager.OVERVIEW_DATA_KEY) is not None

    @staticmethod
    def clear_overview() -> None:
        """Clear overview data from session state."""
        if SessionManager.OVERVIEW_DATA_KEY in st.session_state:
            del st.session_state[SessionManager.OVERVIEW_DATA_KEY]
        if SessionManager.OVERVIEW_PARAMS_KEY in st.session_state:
            del st.session_state[SessionManager.OVERVIEW_PARAMS_KEY]

    # ==========================================================================
    # Chat Methods
    # ==========================================================================

    @staticmethod
    def get_chat_messages() -> list:
        """Get chat message history."""
        return st.session_state.get(SessionManager.CHAT_MESSAGES_KEY, [])

    @staticmethod
    def add_chat_message(role: str, content: str) -> None:
        """
        Add a message to chat history.

        Args:
            role: Message role ('user' or 'assistant')
            content: Message content
        """
        messages = SessionManager.get_chat_messages()
        messages.append({"role": role, "content": content})
        st.session_state[SessionManager.CHAT_MESSAGES_KEY] = messages

    @staticmethod
    def clear_chat_messages() -> None:
        """Clear chat message history."""
        st.session_state[SessionManager.CHAT_MESSAGES_KEY] = []

    @staticmethod
    def set_chat_context(context: Optional[Dict[str, Any]]) -> None:
        """Set chat context for passing data between tabs."""
        st.session_state[SessionManager.CHAT_CONTEXT_KEY] = context

    @staticmethod
    def get_chat_context() -> Optional[Dict[str, Any]]:
        """Get chat context."""
        return st.session_state.get(SessionManager.CHAT_CONTEXT_KEY)

    @staticmethod
    def get_or_create_session_id() -> str:
        """
        Get or create unique session ID for conversation memory.

        Returns:
            Unique session ID string (e.g., "session_a1b2c3d4")
        """
        session_id = st.session_state.get(SessionManager.SESSION_ID_KEY)
        if not session_id:
            import uuid
            session_id = f"session_{uuid.uuid4().hex[:8]}"
            st.session_state[SessionManager.SESSION_ID_KEY] = session_id
        return session_id

    @staticmethod
    def clear_session() -> None:
        """
        Clear the current conversation session and create a new one.
        This resets the chat history and generates a new session ID.
        """
        import uuid
        st.session_state[SessionManager.SESSION_ID_KEY] = f"session_{uuid.uuid4().hex[:8]}"
        st.session_state[SessionManager.CHAT_MESSAGES_KEY] = []
        st.session_state[SessionManager.CHAT_CONTEXT_KEY] = None

    # ==========================================================================
    # UI State Methods
    # ==========================================================================

    @staticmethod
    def toggle_sql() -> None:
        """Toggle SQL display visibility."""
        current = st.session_state.get(SessionManager.SHOW_SQL_KEY, False)
        st.session_state[SessionManager.SHOW_SQL_KEY] = not current

    @staticmethod
    def show_sql() -> bool:
        """Check if SQL should be displayed."""
        return st.session_state.get(SessionManager.SHOW_SQL_KEY, False)

    @staticmethod
    def toggle_results() -> None:
        """Toggle results display visibility."""
        current = st.session_state.get(SessionManager.SHOW_RESULTS_KEY, True)
        st.session_state[SessionManager.SHOW_RESULTS_KEY] = not current

    @staticmethod
    def show_results() -> bool:
        """Check if results should be displayed."""
        return st.session_state.get(SessionManager.SHOW_RESULTS_KEY, True)

    @staticmethod
    def is_debug_mode() -> bool:
        """Check if debug mode is enabled."""
        return st.session_state.get(SessionManager.DEBUG_MODE_KEY, False)

    @staticmethod
    def toggle_debug_mode() -> None:
        """Toggle debug mode."""
        current = st.session_state.get(SessionManager.DEBUG_MODE_KEY, False)
        st.session_state[SessionManager.DEBUG_MODE_KEY] = not current

    # ==========================================================================
    # Cache Methods
    # ==========================================================================

    @staticmethod
    def set_latest_data_info(info: Dict[str, Any]) -> None:
        """Cache latest data period information."""
        st.session_state[SessionManager.LATEST_DATA_INFO_KEY] = info

    @staticmethod
    def get_latest_data_info() -> Optional[Dict[str, Any]]:
        """Get cached latest data period information."""
        return st.session_state.get(SessionManager.LATEST_DATA_INFO_KEY)
