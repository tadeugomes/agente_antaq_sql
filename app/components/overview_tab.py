"""
Overview Tab Component - Porto analysis with persistent state.
User-friendly interface without technical details exposed.
"""
import os
from typing import Dict, List, Optional, Tuple
import streamlit as st
import pandas as pd
from google.cloud import bigquery

from ..utils.session import SessionManager
from ..utils.formatting import format_number, format_percentage, format_month
from ..components.base import (
    metric_row, section, divider, primary_button, secondary_button,
    friendly_table, empty_state, loading_spinner, info_box
)
from ..components.styles import Icons
from src.bigquery.referential_helper import get_referential_helper


# =============================================================================
# Data Fetching Functions
# =============================================================================

def get_latest_data_period() -> Optional[Dict[str, int]]:
    """
    Busca o último ano e mês disponível no BigQuery.

    Returns:
        Dict com 'ano', 'mes', 'mes_nome', ou None em caso de erro
    """
    try:
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


def get_available_portos() -> List[str]:
    """
    Retorna lista de portos disponíveis para seleção.
    Inclui "Brasil" como primeira opção para análise agregada.

    Returns:
        Lista de nomes de portos
    """
    try:
        client = bigquery.Client(project=os.getenv("GOOGLE_CLOUD_PROJECT", "saasimpacto"))

        query = """
        SELECT DISTINCT porto_atracacao
        FROM `antaqdados.br_antaq_estatistico_aquaviario.v_carga_metodologia_oficial`
        WHERE isValidoMetodologiaANTAQ = 1
          AND porto_atracacao IS NOT NULL
        ORDER BY porto_atracacao
        """

        result = client.query(query).to_dataframe()
        if not result.empty:
            portos = result['porto_atracacao'].tolist()
            # Add "Brasil" as first option for aggregated analysis
            return ["Brasil"] + portos
    except Exception:
        pass

    return ["Brasil", "Santos", "Itaguaí", "Itaqui", "Paranaguá", "Rio de Janeiro", "Rio Grande"]


def fetch_overview_data(porto: str, ano: int, mes: int) -> Optional[Dict]:
    """
    Busca todos os dados para o overview do porto ou do Brasil (todos os portos).

    Args:
        porto: Nome do porto ou "Brasil" para análise agregada
        ano: Ano
        mes: Mês (1-12)

    Returns:
        Dicionário com todos os dados do overview, ou None em caso de erro
    """
    try:
        client = bigquery.Client(project=os.getenv("GOOGLE_CLOUD_PROJECT", "saasimpacto"))
        ref_helper = get_referential_helper(client)

        # Filtros oficiais ANTAQ
        tipo_operacao_oficial = (
            "'movimentação de carga', 'apoio', 'longo curso exportação', "
            "'longo curso importação', 'cabotagem', 'interior', "
            "'baldeação de carga nacional', 'baldeação de carga estrangeira de passagem'"
        )

        # Port filter: only apply if not "Brasil"
        is_brasil = porto == "Brasil"
        porto_filter = f"LOWER(c.porto_atracacao) LIKE '%{porto.lower()}%'" if not is_brasil else "1=1"

        # 1. Dados atuais por sentido
        query_atual = f"""
        SELECT c.sentido, SUM(c.vlpesocargabruta_oficial) as carga_total
        FROM `antaqdados.br_antaq_estatistico_aquaviario.v_carga_metodologia_oficial` c
        WHERE c.isValidoMetodologiaANTAQ = 1
          AND c.vlpesocargabruta_oficial > 0
          AND LOWER(c.tipo_operacao_da_carga) IN ({tipo_operacao_oficial})
          AND c.ano = {ano}
          AND c.mes = {mes}
          AND {porto_filter}
        GROUP BY c.sentido
        """

        resultado_atual = client.query(query_atual).to_dataframe()

        # 2. Dados do mesmo mês do ano anterior para comparação
        ano_anterior = ano - 1  # Mesmo mês, ano anterior

        query_anterior = f"""
        SELECT c.sentido, SUM(c.vlpesocargabruta_oficial) as carga_total
        FROM `antaqdados.br_antaq_estatistico_aquaviario.v_carga_metodologia_oficial` c
        WHERE c.isValidoMetodologiaANTAQ = 1
          AND c.vlpesocargabruta_oficial > 0
          AND LOWER(c.tipo_operacao_da_carga) IN ({tipo_operacao_oficial})
          AND c.ano = {ano_anterior}
          AND c.mes = {mes}
          AND {porto_filter}
        GROUP BY c.sentido
        """

        resultado_anterior = client.query(query_anterior).to_dataframe()

        # 3. Top mercadorias exportadas
        query_merc_exp = f"""
        SELECT c.cdmercadoria, SUM(c.vlpesocargabruta_oficial) as carga_total
        FROM `antaqdados.br_antaq_estatistico_aquaviario.v_carga_metodologia_oficial` c
        WHERE c.isValidoMetodologiaANTAQ = 1
          AND c.vlpesocargabruta_oficial > 0
          AND LOWER(c.tipo_operacao_da_carga) IN ({tipo_operacao_oficial})
          AND c.ano = {ano}
          AND c.mes = {mes}
          AND {porto_filter}
          AND c.sentido = 'Embarcados'
        GROUP BY c.cdmercadoria
        ORDER BY carga_total DESC
        LIMIT 5
        """

        mercadorias_exp = client.query(query_merc_exp).to_dataframe()

        # 4. Top mercadorias importadas
        query_merc_imp = f"""
        SELECT c.cdmercadoria, SUM(c.vlpesocargabruta_oficial) as carga_total
        FROM `antaqdados.br_antaq_estatistico_aquaviario.v_carga_metodologia_oficial` c
        WHERE c.isValidoMetodologiaANTAQ = 1
          AND c.vlpesocargabruta_oficial > 0
          AND LOWER(c.tipo_operacao_da_carga) IN ({tipo_operacao_oficial})
          AND c.ano = {ano}
          AND c.mes = {mes}
          AND {porto_filter}
          AND c.sentido = 'Desembarcados'
        GROUP BY c.cdmercadoria
        ORDER BY carga_total DESC
        LIMIT 5
        """

        mercadorias_imp = client.query(query_merc_imp).to_dataframe()

        # 5. Top destinos das exportações
        query_destinos = f"""
        SELECT COALESCE(c.destino, 'Não informado') as destino,
               SUM(c.vlpesocargabruta_oficial) as carga_total
        FROM `antaqdados.br_antaq_estatistico_aquaviario.v_carga_metodologia_oficial` c
        WHERE c.isValidoMetodologiaANTAQ = 1
          AND c.vlpesocargabruta_oficial > 0
          AND LOWER(c.tipo_operacao_da_carga) IN ({tipo_operacao_oficial})
          AND c.ano = {ano}
          AND c.mes = {mes}
          AND {porto_filter}
          AND c.sentido = 'Embarcados'
        GROUP BY c.destino
        ORDER BY carga_total DESC
        LIMIT 5
        """

        destinos = client.query(query_destinos).to_dataframe()

        # 6. UF do porto (não aplicável para Brasil)
        if is_brasil:
            uf = "BR"
        else:
            query_uf = f"""
            SELECT DISTINCT c.uf
            FROM `antaqdados.br_antaq_estatistico_aquaviario.v_carga_metodologia_oficial` c
            WHERE {porto_filter}
              AND c.ano = {ano}
              AND c.isValidoMetodologiaANTAQ = 1
            LIMIT 1
            """

            resultado_uf = client.query(query_uf).to_dataframe()
            uf = resultado_uf.iloc[0]['uf'] if not resultado_uf.empty else 'SP'

        # Processar resultados
        total_atual = 0
        exportacao_atual = 0
        importacao_atual = 0

        for _, row in resultado_atual.iterrows():
            total_atual += row['carga_total']
            if row['sentido'] == 'Embarcados':
                exportacao_atual = row['carga_total']
            elif row['sentido'] == 'Desembarcados':
                importacao_atual = row['carga_total']

        # Totais período anterior
        total_anterior = 0
        exportacao_anterior = 0
        importacao_anterior = 0

        for _, row in resultado_anterior.iterrows():
            total_anterior += row['carga_total']
            if row['sentido'] == 'Embarcados':
                exportacao_anterior = row['carga_total']
            elif row['sentido'] == 'Desembarcados':
                importacao_anterior = row['carga_total']

        # Calcular variações
        variacao_total = ((total_atual - total_anterior) / total_anterior * 100) if total_anterior > 0 else 0
        pct_export = (exportacao_atual / total_atual * 100) if total_atual > 0 else 0
        pct_import = (importacao_atual / total_atual * 100) if total_atual > 0 else 0

        # Enriquecer dados com nomes amigáveis
        nomes_exp_map = {}
        nomes_imp_map = {}

        if not mercadorias_exp.empty:
            nomes_exp_map = ref_helper.batch_get_mercadoria_nomes(
                mercadorias_exp['cdmercadoria'].tolist()
            )

        if not mercadorias_imp.empty:
            nomes_imp_map = ref_helper.batch_get_mercadoria_nomes(
                mercadorias_imp['cdmercadoria'].tolist()
            )

        # Enriquecer destinos
        destinos_enriquecidos = []
        if not destinos.empty:
            for _, row in destinos.iterrows():
                pct = (row['carga_total'] / exportacao_atual * 100) if exportacao_atual > 0 else 0
                destino_nome = ref_helper.enrich_destino_with_info(row['destino'])
                destinos_enriquecidos.append({
                    "nome": destino_nome,
                    "carga": row['carga_total'],
                    "percentual": pct
                })

        return {
            "porto": porto,
            "uf": uf,
            "ano": ano,
            "mes": mes,
            "periodo": f"{format_month(mes)} de {ano}",
            "periodo_anterior": f"{format_month(mes)} de {ano_anterior}",  # Mesmo mês, ano anterior
            "total_atual": total_atual,
            "exportacao_atual": exportacao_atual,
            "importacao_atual": importacao_atual,
            "total_anterior": total_anterior,
            "variacao_total": variacao_total,
            "pct_export": pct_export,
            "pct_import": pct_import,
            "mercadorias_exp": mercadorias_exp,
            "mercadorias_imp": mercadorias_imp,
            "nomes_exp_map": nomes_exp_map,
            "nomes_imp_map": nomes_imp_map,
            "destinos": destinos_enriquecidos,
            "balanco": exportacao_atual - importacao_atual
        }

    except Exception as e:
        return None


# =============================================================================
# Display Functions
# =============================================================================

def render_metrics(data: Dict) -> None:
    """Renderiza os cards de métricas principais."""
    variacao_str = format_percentage(data["variacao_total"] / 100)
    if data["variacao_total"] >= 0:
        variacao_str = f"+{variacao_str}"

    # Extrair mês e ano do período anterior para exibição
    periodo_anterior = data.get("periodo_anterior", "")
    vs_label = f"vs {periodo_anterior}"

    metrics = [
        {
            "value": format_number(data["total_atual"]),
            "label": "Carga Total",
            "delta": f"{variacao_str} {vs_label}",
            "icon": Icons.SHIP,
            "color": None
        },
        {
            "value": format_number(data["exportacao_atual"]),
            "label": "Exportações",
            "delta": f"{data['pct_export']:.0f}% do total",
            "icon": "📤",
            "color": "#00A651"
        },
        {
            "value": format_number(data["importacao_atual"]),
            "label": "Importações",
            "delta": f"{data['pct_import']:.0f}% do total",
            "icon": "📥",
            "color": "#0066CC"
        },
        {
            "value": "Superávit" if data["balanco"] > 0 else "Déficit",
            "label": "Balança Comercial",
            "delta": format_number(abs(data["balanco"])),
            "icon": Icons.TREND_UP if data["balanco"] > 0 else Icons.TREND_DOWN,
            "color": "#00A651" if data["balanco"] > 0 else "#DC3545"
        }
    ]

    metric_row(metrics)


def render_mercadorias(data: Dict) -> None:
    """Renderiza as seções de mercadorias."""
    col1, col2 = st.columns(2)

    with col1:
        section("Principais Exportações", icon="📤")

        if not data["mercadorias_exp"].empty:
            for _, row in data["mercadorias_exp"].iterrows():
                codigo = str(row['cdmercadoria'])
                nome = data["nomes_exp_map"].get(codigo, codigo)
                carga = format_number(row['carga_total'])
                st.markdown(f"**{nome}** - {carga}")
        else:
            st.info("Nenhum dado disponível.")

    with col2:
        section("Principais Importações", icon="📥")

        if not data["mercadorias_imp"].empty:
            for _, row in data["mercadorias_imp"].iterrows():
                codigo = str(row['cdmercadoria'])
                nome = data["nomes_imp_map"].get(codigo, codigo)
                carga = format_number(row['carga_total'])
                st.markdown(f"**{nome}** - {carga}")
        else:
            st.info("Nenhum dado disponível.")


def render_destinos(data: Dict) -> None:
    """Renderiza a seção de destinos das exportações."""
    section("Principais Destinos", icon=Icons.BOX)

    if data["destinos"]:
        for dest in data["destinos"]:
            st.markdown(f"**{dest['nome']}** - {format_number(dest['carga'])} ({dest['percentual']:.0f}%)")
    else:
        st.info("Nenhum dado disponível.")


def render_summary(data: Dict) -> None:
    """Renderiza o resumo narrativo."""
    periodo = data["periodo"]
    total = format_number(data["total_atual"])
    variacao = format_percentage(data["variacao_total"] / 100)
    if data["variacao_total"] > 0:
        variacao = f"+{variacao}"

    balanca_tipo = "superávit" if data["balanco"] > 0 else "déficit"

    # Check if it's Brasil (aggregated) or specific port
    is_brasil = data["porto"] == "Brasil"
    localizacao = "Brasil" if is_brasil else f"porto de **{data['porto']}**"

    texto = f"""
    ### 📊 Resumo Executivo

    Em **{periodo}**, {localizacao} movimentou **{total} toneladas** de carga,
    apresentando {variacao} em relação ao mês de {data['periodo_anterior']}.

    {"O país" if is_brasil else "O porto"} registrou **{balanca_tipo}** na balança comercial, com destaque para o movimento
    de contêineres e granéis sólidos.
    """

    st.markdown(texto)


def show_overview_form():
    """Exibe o formulário de seleção de porto."""
    st.title("📊 Análise de Porto")

    # Get available portos
    portos = get_available_portos()

    # Get latest period
    latest = get_latest_data_period()

    with st.form("overview_form"):
        col1, col2 = st.columns(2)

        with col1:
            porto = st.selectbox(
                "Selecione o Porto",
                options=portos,
                index=0,
                label_visibility="visible"
            )

        with col2:
            latest = get_latest_data_period()

            # Opções de ano - dinâmico até o ano atual
            import datetime
            ano_atual = datetime.datetime.now().year
            anos = list(range(ano_atual, 2019, -1))  # [2025, 2024, 2023, 2022, 2021, 2020]
            default_ano = latest['ano'] if latest else ano_atual

            # Opções de mês
            meses = [
                "Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho",
                "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"
            ]
            default_mes_idx = (latest['mes'] - 1) if latest else 0

            col2a, col2b = st.columns(2)
            with col2a:
                idx_ano = anos.index(default_ano) if default_ano in anos else 0
                ano = st.selectbox("Ano", options=anos, index=idx_ano)
            with col2b:
                mes_nome = st.selectbox("Mês", options=meses, index=default_mes_idx)
                mes = meses.index(mes_nome) + 1

        submitted = st.form_submit_button(
            f"{Icons.SEARCH} Gerar Análise Completa",
            use_container_width=True,
            type="primary"
        )

        if submitted:
            loading_spinner("Carregando dados do BigQuery...")

            # Fetch data
            data = fetch_overview_data(porto, ano, mes)

            if data:
                SessionManager.save_overview(
                    params={"porto": porto, "ano": ano, "mes": mes},
                    data=data
                )
                st.rerun()
            else:
                info_box(
                    "Erro ao Carregar Dados",
                    "Não foi possível carregar os dados. Tente novamente.",
                    "error"
                )


def show_overview_results(params: Dict, data: Dict) -> None:
    """Exibe os resultados da análise."""
    col1, col2 = st.columns([3, 1])

    with col1:
        # Show flag emoji for Brasil
        emoji = "🇧🇷 " if params['porto'] == "Brasil" else ""
        st.title(f"📊 {emoji}{params['porto']}")

    with col2:
        if secondary_button("Nova Análise", icon=Icons.BACK):
            SessionManager.clear_overview()
            st.rerun()

    # Data period banner
    info_box(
        "Período Analisado",
        f"**{data['periodo']}** | Comparado com {data['periodo_anterior']}",
        "info",
        Icons.CHART
    )

    # Metric explanation
    st.caption("💡 **Métrica:** Dados em toneladas de peso bruto da carga movimentada (não confundir com valor em dólares do comércio exterior).")

    divider()

    # Executive summary
    render_summary(data)

    divider()

    # Main metrics
    render_metrics(data)

    divider()

    # Detailed sections
    col1, col2 = st.columns(2)

    with col1:
        render_mercadorias(data)

    with col2:
        render_destinos(data)

    divider()

    # Call to action for Chat
    st.markdown("---")

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if primary_button("Fazer pergunta sobre estes dados", icon=Icons.CHAT):
            # Set chat context
            contexto = f"""
            Contexto: Análise do porto de {params['porto']} em {data['periodo']}.
            - Carga total: {format_number(data['total_atual'])} toneladas
            - Exportações: {format_number(data['exportacao_atual'])} toneladas
            - Importações: {format_number(data['importacao_atual'])} toneladas
            """

            SessionManager.set_chat_context({"context": contexto, "porto": params['porto']})
            st.info("💡 Clique na aba **Chat** acima para fazer perguntas sobre estes dados.")


# =============================================================================
# Main Entry Point
# =============================================================================

def show_overview_tab():
    """
    Entry point for the Overview tab.

    Checks if overview data exists in session state:
    - If yes: displays the results
    - If no: displays the selection form
    """
    saved_params, saved_data = SessionManager.get_overview()

    if saved_data is not None:
        show_overview_results(saved_params, saved_data)
    else:
        show_overview_form()
