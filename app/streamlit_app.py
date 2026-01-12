"""
Main Streamlit application for ANTAQ AI Agent.
Refactored with new component architecture and clean UX.
"""
import os
import sys

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

# Initialize Sentry and logging
from src.utils.logging_config import setup_logging
setup_logging()

import streamlit as st
import sentry_sdk
from src.agent.graph import create_graph
from src.utils.security import validate_environment

# Import new components
from app.components.styles import load_styles, Icons, Colors
from app.components.base import main_header, info_box
from app.components.chat_tab import show_chat_tab
from app.components.overview_tab import show_overview_tab
from app.utils.session import SessionManager


# =============================================================================
# Configuration
# =============================================================================

st.set_page_config(
    page_title="ANTAQ - Dados Aquaviários",
    page_icon="🚢",
    layout="wide",
    initial_sidebar_state="collapsed"
)


# =============================================================================
# Initialization Functions
# =============================================================================

def init_session_state():
    """Initialize Streamlit session state with SessionManager."""
    # Initialize graph
    if "graph" not in st.session_state:
        st.session_state.graph = create_graph()

    # Initialize session manager
    SessionManager.init()

    # Cache latest data info
    if SessionManager.get_latest_data_info() is None:
        SessionManager.set_latest_data_info(get_latest_data_period())


def get_latest_data_period():
    """Busca o último ano e mês disponível no BigQuery."""
    try:
        from google.cloud import bigquery

        client = bigquery.Client(project=os.getenv("GOOGLE_CLOUD_PROJECT", "saasimpacto"))

        query = """
        SELECT ano, mes, MAX(data_referencia) as ultima_data
        FROM `antaqdados.br_antaq_estatistico_aquaviario.v_carga_metodologia_oficial`
        WHERE isValidoMetodologiaANTAQ = 1
        GROUP BY ano, mes
        ORDER BY ano DESC, mes DESC
        LIMIT 1
        """

        result = client.query(query).to_dataframe()

        if not result.empty:
            meses = ["Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho",
                     "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"]

            return {
                "ano": int(result.iloc[0]['ano']),
                "mes": int(result.iloc[0]['mes']),
                "mes_nome": meses[int(result.iloc[0]['mes']) - 1],
                "ultima_data": str(result.iloc[0]['ultima_data'])
            }
    except Exception:
        pass

    return None


def check_environment():
    """Check if environment is configured."""
    env_status = validate_environment()
    all_ok = all(env_status.values())

    if not all_ok:
        st.error("Variáveis de ambiente não configuradas:")
        for var, status in env_status.items():
            if not status:
                st.error(f"  - {var}")
        st.info("Configure as variáveis de ambiente e reinicie o app.")
        st.stop()

    return all_ok


# =============================================================================
# Main Application
# =============================================================================

def main():
    """Main application entry point."""
    # Set Sentry context for this session
    _set_sentry_context()

    try:
        _run_app()
    except Exception as e:
        # Capture exception in Sentry
        sentry_sdk.capture_exception(e)
        st.error(f"Ocorreu um erro inesperado: {str(e)}")
        if os.getenv("APP_DEBUG", "false").lower() == "true":
            import traceback
            st.code(traceback.format_exc())


def _set_sentry_context():
    """Set Sentry context with session information."""
    try:
        from src.utils.sentry_config import set_tag, set_context

        # Set environment tag
        set_tag("app_environment", os.getenv("SENTRY_ENVIRONMENT", "development"))

        # Set provider context
        set_context("app", {
            "llm_provider": os.getenv("LLM_PROVIDER", "unknown"),
            "dataset": os.getenv("ANTAQ_DATASET", "unknown"),
        })
    except Exception:
        # Don't fail if Sentry is not configured
        pass


def _run_app():
    """Run the main application logic."""
    # Load custom styles
    load_styles()

    # Check environment
    check_environment()

    # Initialize session state
    init_session_state()

    # Main header
    main_header(
        title="ANTAQ - Dados Aquaviários",
        subtitle="Consulta em linguagem natural para dados da ANTAQ"
    )

    # Data status banner
    latest = SessionManager.get_latest_data_info()
    if latest:
        info_box(
            "Dados Disponíveis",
            f"Último mês: **{latest['mes_nome']} de {latest['ano']}**",
            "info"
        )

    # Main tabs
    tab1, tab2 = st.tabs([f"{Icons.CHAT_TAB} Chat", f"{Icons.OVERVIEW_TAB} Overview"])

    with tab1:
        show_chat_tab()

    with tab2:
        show_overview_tab()

    # Footer
    st.markdown("---")
    st.markdown(
        f'<div style="text-align: center; color: {Colors.GRAY_500}; font-size: 0.8rem;">'
        f'Fonte: ANTAQ - Agência Nacional de Transportes Aquaviários | '
        f'Estatística Aquaviária'
        f'</div>',
        unsafe_allow_html=True
    )


if __name__ == "__main__":
    main()
