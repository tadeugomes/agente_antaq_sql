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
from app.components.styles import load_styles, Colors
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

def _render_help_tab() -> None:
    """Render the help tab with onboarding content and examples."""
    st.markdown("### Ajuda")
    st.markdown(
        "Faça perguntas em linguagem natural sobre os dados do Estatístico Aquaviário da ANTAQ. "
        "Inclua o porto, o período e, se possível, o sentido da operação (exportação/importação)."
    )

    st.markdown("#### Exemplos de perguntas")
    example_questions = [
        "Qual foi o total de carga movimentado em agosto de 2024 pelo porto de Paranaguá?",
        "Quais são os 10 principais portos por tonelagem em 2024?",
        "Compare exportações e importações por região geográfica em 2024.",
        "Quanto foi exportado de soja pelo porto de Santos em agosto de 2024?",
        "Quanto foi importado de fertilizantes pelo porto de Itaqui em novembro de 2024?",
    ]

    for idx, question in enumerate(example_questions):
        if st.button(question, key=f"help_example_{idx}", use_container_width=True):
            st.session_state["pergunta_pending"] = question
            st.info("Pergunta preenchida na aba Chat. Clique em Consultar.")

    st.markdown("---")
    st.markdown(
        "Dica: padronize o período como \"mês de ano\" e o nome do porto como \"porto de X\" "
        "para obter respostas mais consistentes."
    )


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
        subtitle="Consulta em linguagem natural para dados do Estatístico Aquaviário da ANTAQ"
    )

    # Data status banner
    latest = SessionManager.get_latest_data_info()
    if latest:
        cobertura = f"{latest['mes_nome'].lower()} de {latest['ano']}"
        info_box(
            "Dados disponíveis",
            f"Cobertura: até {cobertura} (dados mensais do Estatístico Aquaviário da ANTAQ).",
            "info"
        )
    else:
        info_box(
            "Dados disponíveis",
            "Cobertura: dados mensais do Estatístico Aquaviário da ANTAQ.",
            "info"
        )

    # Main tabs
    tab_chat, tab_overview, tab_help = st.tabs(["Chat", "Overview", "Ajuda"])

    with tab_chat:
        show_chat_tab()

    with tab_overview:
        show_overview_tab()

    with tab_help:
        _render_help_tab()

    # Footer
    st.markdown("---")
    st.markdown(
        f'<div style="text-align: center; color: {Colors.GRAY_500}; font-size: 0.8rem;">'
        f'Fonte: ANTAQ - Agência Nacional de Transportes Aquaviários | '
        f'<a href="https://web3.antaq.gov.br/ea/sense/index.html#" '
        f'target="_blank" rel="noopener noreferrer">Estatística Aquaviária</a>'
        f'</div>',
        unsafe_allow_html=True
    )


if __name__ == "__main__":
    main()
