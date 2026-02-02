"""
LangChain tools for the agent.
"""
import json
from typing import Optional
from langchain_core.tools import tool
from ..bigquery.client import get_bigquery_client
from .metadata_helper import get_metadata_helper


@tool
async def execute_bigquery_query(query: str) -> str:
    """
    Execute a SQL query on BigQuery ANTAQ dataset.

    Args:
        query: SQL query string

    Returns:
        JSON string with query results
    """
    client = get_bigquery_client()

    try:
        results = client.query(query)
        return json.dumps({
            "success": True,
            "rows": results,
            "count": len(results)
        }, default=str, ensure_ascii=False)

    except Exception as e:
        return json.dumps({
            "success": False,
            "error": str(e)
        })


@tool
async def get_table_info(table_name: str) -> str:
    """
    Get information about a specific table.

    Args:
        table_name: Name of the table

    Returns:
        Table schema and description
    """
    from ..bigquery.schema import get_schema_retriever

    retriever = get_schema_retriever()
    return retriever.get_table_info(table_name)


@tool
async def list_available_tables() -> str:
    """
    List all available tables in the ANTAQ dataset.

    Returns:
        List of table names and descriptions
    """
    tables = [
        "v_carga_metodologia_oficial - Carga segundo metodologia oficial ANTAQ (VIEW PRINCIPAL)",
        "v_atracacao_validada - Atracação com FK validada",
        "v_carga_validada - Carga com relacionamentos validados",
        "instalacao_origem - Catálogo de instalações de origem",
        "instalacao_destino - Catálogo de instalações de destino",
        "mercadoria_carga - Catálogo de mercadorias"
    ]

    return "\n".join(tables)


# =============================================================================
# NEW TOOLS - Metadata-based helpers
# =============================================================================


@tool
def explain_column(table: str, column: str) -> str:
    """
    Explica uma coluna específica do BigQuery com detalhes.

    Use esta ferramenta quando o usuário pedir para explicar uma coluna,
    ou quando precisar entender melhor uma coluna antes de gerar uma query.

    Args:
        table: Nome da tabela (ex: v_carga_metodologia_oficial)
        column: Nome da coluna (ex: vlpesocargabruta_oficial)

    Returns:
        Explicação detalhada da coluna incluindo tipo, descrição, categoria e valores possíveis.
    """
    metadata_helper = get_metadata_helper()
    explanation = metadata_helper.explain_column(table, column)

    if explanation is None:
        return f"""
❌ Coluna não encontrada: {table}.{column}

A coluna '{column}' não foi encontrada na tabela '{table}'.
Verifique se o nome da tabela e coluna estão corretos.

Tabelas disponíveis:
- v_carga_metodologia_oficial (principal view de cargas)

Para ver todas as colunas de uma tabela, use a ferramenta search_columns.
"""

    # Format explanation nicely
    tips = _get_column_tips(explanation)
    # Handle tags properly - convert None to empty list
    tags_val = explanation.get('tags')
    tags = list(tags_val) if tags_val is not None else []
    tags_str = ', '.join(tags) if len(tags) > 0 else 'Nenhuma'
    valores_str = explanation['valores_possiveis'] or 'Sem restrições específicas'

    return f"""
📋 **Coluna: {explanation['coluna']}**

**Tabela:** {explanation['tabela']}
**Tipo de Dado:** {explanation['tipo_dado']}
**Categoria:** {explanation['categoria']}

**Descrição:**
{explanation['descricao']}

**Valores Possíveis:**
{valores_str}

**Tags:**
{tags_str}

---

**💡 Dicas de Uso:**
{tips}
"""


def _get_column_tips(explanation: dict) -> str:
    """Get usage tips based on column metadata"""
    tips = []

    categoria = explanation['categoria']
    # Handle tags properly - convert None to empty list, otherwise use the list
    tags_val = explanation.get('tags')
    tags = list(tags_val) if tags_val is not None else []

    if categoria == 'Temporal':
        tips.extend([
            "• Use funções de data como EXTRACT, DATE_TRUNC para análises temporais",
            "• Para filtros: ano é INT64 (sem aspas), mes é INT64 (1-12)",
            "• Considere sazonalidade nas análises por mês ou trimestre"
        ])

    elif categoria == 'Métrica':
        tips.extend([
            "• Use funções agregadas como SUM, AVG, MAX, MIN",
            "• A métrica principal é vlpesocargabruta_oficial (peso em toneladas)",
            "• Sempre filtre por isValidoMetodologiaANTAQ = 1 para dados oficiais"
        ])

    elif categoria == 'Identificação':
        tips.extend([
            "• Use para JOINs entre tabelas",
            "• Verifique duplicatas usando COUNT DISTINCT",
            "• Em geral, não use em GROUP BY para análises agregadas"
        ])

    elif categoria == 'Localização':
        tips.extend([
            "• Para portos: use LOWER(porto_atracacao) LIKE '%nome%'",
            "• Analise por regiões geográficas ou estados (UF)",
            "• Compare diferentes portos em rankings"
        ])

    elif categoria == 'Operação':
        tips.extend([
            "• **CRITICAL**: sentido = 'Embarcados' é exportação, 'Desembarcados' é importação",
            "• Use GROUP BY sentido para comparar exportação vs importação",
            "• tipo_de_navegacao: 'Longo Curso' (internacional), 'Cabotagem' (doméstico)"
        ])

    # Tag-specific tips
    if 'exportação' in tags or 'importação' in tags:
        tips.append("• Use filtro sentido = 'Embarcados' para exportação, 'Desembarcados' para importação")

    if 'filtro' in tags:
        tips.append("• Sempre inclua esta coluna nos filtros WHERE para performance")

    return '\n'.join(tips) if tips else "• Explore diferentes agrupamentos e filtros para descobrir insights"


@tool
def search_columns(keywords: str) -> str:
    """
    Busca colunas por palavras-chave nos metadados.

    Use esta ferramenta quando o usuário perguntar sobre colunas
    relacionadas a um tema específico (ex: peso, data, porto).

    Args:
        keywords: Palavras-chave para buscar (ex: "peso tonelada", "porto", "exportação")

    Returns:
        Lista de colunas encontradas com suas descrições.
    """
    # Split keywords by comma or space
    keyword_list = [k.strip() for k in keywords.replace(',', ' ').split() if k.strip()]

    metadata_helper = get_metadata_helper()
    results = metadata_helper.search_columns(keyword_list)

    if not results:
        return f"""
❌ Nenhuma coluna encontrada para: {keywords}

Tente palavras-chave diferentes como:
- peso, tonelada, volume (para métricas)
- porto, uf, estado (para localização)
- data, ano, mês (para temporal)
- exportação, importação, sentido (para operação)
"""

    # Format results
    output = f"🔍 Encontradas {len(results)} colunas para '{keywords}':\n\n"

    for i, col in enumerate(results, 1):
        # Handle tags properly
        tags_val = col.get('tags')
        tags = list(tags_val) if tags_val is not None else []
        tags_str = f" [{', '.join(tags)}]" if len(tags) > 0 else ""
        output += f"{i}. **{col['tabela']}.{col['coluna']}** ({col['categoria']}){tags_str}\n"
        output += f"   {col['descricao']}\n"

    return output


@tool
def get_official_filters() -> str:
    """
    Retorna os filtros SQL oficiais que devem ser usados em todas as queries.

    Os filtros oficiais garantem que apenas dados válidos pela metodologia
    ANTAQ sejam retornados.

    Returns:
        Template SQL com os filtros oficiais.
    """
    return """
## Filtros Oficiais ANTAQ

Todas as queries devem incluir estes filtros para garantir dados oficiais:

```sql
WHERE c.isValidoMetodologiaANTAQ = 1              -- Metodologia oficial
  AND c.vlpesocargabruta_oficial > 0               -- Apenas cargas com peso
  AND LOWER(c.tipo_operacao_da_carga) IN (        -- Tipos de operação válidos
      'movimentação de carga', 'apoio',
      'longo curso exportação', 'longo curso importação',
      'cabotagem', 'interior',
      'baldeação de carga nacional', 'baldeação de carga estrangeira de passagem'
  )
  AND c.ano = 2024                                 -- Filtro de ano (obrigatório)
```

**Importância:**
- Apenas dados válidos pela metodologia oficial ANTAQ
- Exclui operações não-oficiais
- Garante consistência com dados publicados
- Evita duplicatas e registros inválidos
"""


@tool
def suggest_query_template(intent: str) -> str:
    """
    Sugere um template de query baseado na intenção do usuário.

    Use esta ferramenta quando o usuário descrever o tipo de análise
    que deseja fazer (ex: ranking, evolução temporal, comparação).

    Args:
        intent: Descrição da intenção da análise (ex: "ranking de portos", "evolução mensal")

    Returns:
        Template de query SQL com explicações.
    """
    metadata_helper = get_metadata_helper()
    template = metadata_helper.suggest_query_template(intent)

    if template is None:
        return f"""
❌ Não foi possível sugerir um template para: {intent}

Tente descrever a análise com termos como:
- "ranking" ou "top" - para ordenar por métrica
- "evolução" ou "série temporal" - para análise temporal
- "peso" ou "volume" - para análise de quantidade
- "porto" ou "mercadoria" - para análise específica
"""

    return f"""
## {template['template']}

**Descrição:** {template['description']}

```sql
{template['sql_pattern']}
```

**Parâmetros para substituir:**
- {{dataset}}: `antaqdados.br_antaq_estatistico_aquaviario`
- {{ano}}: Ano desejado (ex: 2024)
- {{ano_inicio}}: Ano inicial (ex: 2023)
- {{group_by_columns}}: Colunas para agrupar (ex: c.porto_atracacao)
- {{ranking_column}}: Coluna para ordenar (ex: c.porto_atracacao)
- {{limit}}: Limite de resultados (ex: 100)
- {{additional_filters}}: Filtros adicionais (ex: AND c.sentido = 'Embarcados')
- {{official_filters}}: Use a ferramenta get_official_filters

**Tags:** weight_analysis, temporal_analysis, ranking
"""


# Export all tools
def get_all_metadata_tools():
    """
    Get all metadata-based LangChain tools for the agent.

    Returns:
        List of LangChain tools
    """
    return [
        explain_column,
        search_columns,
        get_official_filters,
        suggest_query_template,
    ]
