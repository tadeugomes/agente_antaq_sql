"""
Metadata Helper for ANTAQ AI Agent
Integrates with BigQuery metadata dictionary for enhanced SQL generation
"""
import os
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta, date
import pandas as pd


class MetadataHelper:
    """
    Helper for querying and using metadata from BigQuery
    Enhances the agent with schema-aware SQL generation
    """

    def __init__(self, client=None):
        """
        Initialize the metadata helper

        Args:
            client: BigQuery client (optional, will create if not provided)
        """
        if client is None:
            from google.cloud import bigquery
            project_id = os.getenv("GOOGLE_CLOUD_PROJECT", "saasimpacto")
            self.client = bigquery.Client(project=project_id)
        else:
            self.client = client

        self.dataset_id = "antaqdados.br_antaq_estatistico_aquaviario"
        self.metadata_project_id = os.getenv("GOOGLE_CLOUD_PROJECT", "saasimpacto")
        self.metadata_dataset_id = f"{self.metadata_project_id}.antaq_metadados"

        # Official data lag (45 days for ANTAQ official publication)
        self.official_publication_lag_days = 45
        self.official_cutoff_date = (
            date.today() - timedelta(days=self.official_publication_lag_days)
        )

        # Cache for column existence checks
        self._column_cache: Dict[tuple, bool] = {}

        # Cached metadata
        self._metadata_df: Optional[pd.DataFrame] = None

    def has_column(self, table: str, column: str) -> bool:
        """
        Check if column exists in table using INFORMATION_SCHEMA

        Args:
            table: Table/view name
            column: Column name

        Returns:
            True if column exists
        """
        key = (table.lower(), column.lower())
        if key in self._column_cache:
            return self._column_cache[key]

        query = f"""
            SELECT 1
            FROM `{self.dataset_id.replace('br_antaq_estatistico_aquaviario', '')}`.INFORMATION_SCHEMA.COLUMNS
            WHERE table_name = @table
              AND LOWER(column_name) = @column
            LIMIT 1
        """

        try:
            job_config = {
                "query_parameters": [
                    {"name": "table", "parameter_type": "STRING", "parameter_value": table},
                    {"name": "column", "parameter_type": "STRING", "parameter_value": column.lower()},
                ]
            }
            df = self.client.query(query, job_config=job_config).to_dataframe()
            exists = not df.empty
        except Exception:
            exists = False

        self._column_cache[key] = exists
        return exists

    def get_official_period_filter_sql(self, alias: str = 'c') -> str:
        """
        Generate SQL filter for official ANTAQ publication period (45-day lag)
        Uses data_desatracacao or data_referencia when available

        Args:
            alias: Table alias for the SQL query

        Returns:
            SQL filter string
        """
        cutoff_str = self.official_cutoff_date.isoformat()

        # Check if data_referencia exists in carga view
        if alias == 'c' and self.has_column('v_carga_metodologia_oficial', 'data_referencia'):
            return f"SAFE_CAST({alias}.data_referencia AS DATE) <= DATE '{cutoff_str}'"
        else:
            # Fallback to data_atracacao
            return f"DATE(SAFE_CAST({alias}.data_atracacao AS TIMESTAMP)) <= DATE '{cutoff_str}'"

    def get_official_methodology_filters_sql(self, alias: str = 'c') -> str:
        """
        Generate SQL filters for official ANTAQ methodology
        - isValidoMetodologiaANTAQ = 1
        - vlpesocargabruta_oficial > 0
        - Official operation types only

        Args:
            alias: Table alias for the SQL query

        Returns:
            SQL filter string
        """
        # Official operation types
        tipos_oficiais = (
            "'movimentação de carga', 'apoio', 'longo curso exportação', 'longo curso importação', "
            "'longo curso exportação com baldeação de carga estrangeira', 'longo curso importação com baldeação de carga estrangeira', "
            "'cabotagem', 'interior', 'baldeação de carga nacional', 'baldeação de carga estrangeira de passagem'"
        )

        # Check if FlagAutorizacao exists
        flag_filter = ""
        if self.has_column('v_carga_metodologia_oficial', 'FlagAutorizacao'):
            flag_filter = f" AND {alias}.FlagAutorizacao = 'S'"

        return (
            f"{alias}.isValidoMetodologiaANTAQ = 1"
            f" AND {alias}.vlpesocargabruta_oficial > 0"
            f" AND LOWER({alias}.tipo_operacao_da_carga) IN ({tipos_oficiais})"
            f"{flag_filter}"
        )

    def load_metadata(self) -> pd.DataFrame:
        """
        Load metadata from dicionario_dados table

        Returns:
            DataFrame with metadata or empty DataFrame if table doesn't exist
        """
        if self._metadata_df is not None:
            return self._metadata_df

        query = f"""
        SELECT
            tabela,
            coluna,
            descricao,
            tipo_dado,
            valores_possiveis,
            categoria,
            tags
        FROM `{self.metadata_dataset_id}.dicionario_dados`
        ORDER BY tabela, categoria, coluna
        """

        try:
            df = self.client.query(query).to_dataframe()
            self._metadata_df = df
            return df
        except Exception as e:
            # Table might not exist - return empty DataFrame
            print(f"Warning: Could not load metadata table: {e}")
            self._metadata_df = pd.DataFrame()
            return pd.DataFrame()

    def search_columns(self, keywords: List[str], table: Optional[str] = None,
                       category: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Search columns by keywords in metadata

        Args:
            keywords: List of keywords to search for
            table: Optional table filter
            category: Optional category filter

        Returns:
            List of matching column dictionaries
        """
        df = self.load_metadata()

        if df.empty:
            return []

        # Convert keywords to lowercase
        keywords_lower = [kw.lower() for kw in keywords if kw]

        # Filter by keywords in description
        if keywords_lower:
            pattern = '|'.join(keywords_lower)
            mask = df['descricao'].str.lower().str.contains(pattern, na=False)
            df = df[mask]

        # Filter by table
        if table:
            df = df[df['tabela'].str.upper() == table.upper()]

        # Filter by category
        if category:
            df = df[df['categoria'].str.lower() == category.lower()]

        # Convert to list of dicts
        return df.to_dict('records')

    def explain_column(self, table: str, column: str) -> Optional[Dict[str, Any]]:
        """
        Get detailed explanation for a specific column

        Args:
            table: Table name
            column: Column name

        Returns:
            Dictionary with column details or None if not found
        """
        df = self.load_metadata()

        if df.empty:
            return None

        result = df[
            (df['tabela'].str.upper() == table.upper()) &
            (df['coluna'].str.upper() == column.upper())
        ]

        if result.empty:
            return None

        row = result.iloc[0]
        return {
            'tabela': row['tabela'],
            'coluna': row['coluna'],
            'tipo_dado': row['tipo_dado'],
            'descricao': row['descricao'],
            'categoria': row['categoria'],
            'valores_possiveis': row['valores_possiveis'],
            'tags': row['tags']
        }

    def get_schema_for_prompt(self) -> str:
        """
        Generate schema description for use in LLM prompts

        Returns:
            Formatted string with schema information
        """
        df = self.load_metadata()

        if df.empty:
            # Fallback to hardcoded schema
            return self._get_fallback_schema()

        # Group by table
        result = []
        for table in sorted(df['tabela'].unique()):
            table_df = df[df['tabela'] == table]
            result.append(f"\n## Tabela: {table}\n")

            for category in sorted(table_df['categoria'].unique()):
                cat_df = table_df[table_df['categoria'] == category]
                result.append(f"\n### {category}\n")

                for _, row in cat_df.iterrows():
                    # Handle tags: check if None or empty, avoiding array ambiguity
                    tags_val = row['tags']
                    tags_str = ""
                    if tags_val is not None:
                        # Use scalar check for single values
                        try:
                            if pd.notna(tags_val):
                                if hasattr(tags_val, '__len__') and len(tags_val) > 0:
                                    tags_list = list(tags_val) if isinstance(tags_val, (list, tuple)) else tags_val.tolist()
                                    tags_str = f" [{', '.join(tags_list)}]"
                        except (ValueError, TypeError):
                            # Fallback for array-like values that cause issues with pd.notna
                            if hasattr(tags_val, '__len__') and len(tags_val) > 0:
                                try:
                                    tags_list = list(tags_val) if isinstance(tags_val, (list, tuple)) else tags_val.tolist()
                                    tags_str = f" [{', '.join(tags_list)}]"
                                except:
                                    pass

                    # Handle valores_possiveis
                    valores_val = row['valores_possiveis']
                    valores_str = ""
                    try:
                        if valores_val is not None and pd.notna(valores_val) and valores_val:
                            valores_str = f" - Valores: {valores_val}"
                    except (ValueError, TypeError):
                        if valores_val:
                            valores_str = f" - Valores: {valores_val}"

                    result.append(f"- {row['coluna']}: {row['descricao']}{tags_str}{valores_str}")

        return "\n".join(result)

    def _get_fallback_schema(self) -> str:
        """
        Fallback schema description when metadata table is not available
        """
        return """
## Tabela: v_carga_metodologia_oficial

### Identificação
- idcarga: Identificador único da carga
- idatracacao: Identificador da atracação relacionada

### Temporal
- ano: Ano da operação (INT64)
- mes: Mês da operação (INT64)
- data_atracacao: Data da atracação
- data_referencia: Data de referência para cálculos

### Localização
- porto_atracacao: Nome do porto de atracação
- uf: Unidade Federativa (estado)
- regiao_geografica: Região geográfica

### Mercadoria
- cdmercadoria: Código da mercadoria
- natureza_carga: Natureza da carga

### Operação
- sentido: Direção ('Embarcados' para exportação, 'Desembarcados' para importação)
- tipo_de_navegacao_da_atracacao: Tipo de navegação (Longo Curso, Cabotagem, Interior)
- tipo_operacao_da_carga: Tipo da operação

### Métricas
- vlpesocargabruta_oficial: Peso bruto da carga em toneladas (métrica oficial)

### Validação
- isValidoMetodologiaANTAQ: Flag de validação pela metodologia ANTAQ (use = 1 para dados oficiais)
"""

    def suggest_query_template(self, intent: str) -> Optional[Dict[str, str]]:
        """
        Suggest query template based on user intent

        Args:
            intent: User's query intent description

        Returns:
            Dictionary with template and description or None
        """
        intent_lower = intent.lower()

        # Weight/volume analysis
        if any(word in intent_lower for word in ['peso', 'tonelada', 'carga', 'volume', 'total']):
            return {
                'template': 'weight_analysis',
                'description': 'Análise de peso/volume de cargas',
                'sql_pattern': '''
SELECT
    {group_by_columns},
    SUM(c.vlpesocargabruta_oficial) AS peso_total_toneladas,
    COUNT(*) AS total_operacoes
FROM `{dataset}.v_carga_metodologia_oficial` c
WHERE {official_filters}
  AND c.ano = {ano}
  {additional_filters}
GROUP BY {group_by_columns}
ORDER BY peso_total_toneladas DESC
LIMIT 100
                '''.strip()
            }

        # Temporal analysis
        if any(word in intent_lower for word in ['evolução', 'tendência', 'mensal', 'série temporal', 'histórico']):
            return {
                'template': 'temporal_analysis',
                'description': 'Análise temporal/evolução',
                'sql_pattern': '''
SELECT
    c.ano,
    c.mes,
    SUM(c.vlpesocargabruta_oficial) AS peso_total_toneladas
FROM `{dataset}.v_carga_metodologia_oficial` c
WHERE {official_filters}
  AND c.ano >= {ano_inicio}
  {additional_filters}
GROUP BY c.ano, c.mes
ORDER BY c.ano, c.mes
                '''.strip()
            }

        # Ranking
        if any(word in intent_lower for word in ['ranking', 'top', 'maiores', 'principais']):
            return {
                'template': 'ranking',
                'description': 'Ranking por métrica',
                'sql_pattern': '''
SELECT
    {ranking_column},
    SUM(c.vlpesocargabruta_oficial) AS total_toneladas
FROM `{dataset}.v_carga_metodologia_oficial` c
WHERE {official_filters}
  AND c.ano = {ano}
  {additional_filters}
GROUP BY {ranking_column}
ORDER BY total_toneladas DESC
LIMIT {limit}
                '''.strip()
            }

        return None


# Singleton instance
_cached_metadata_helper: Optional[MetadataHelper] = None


def get_metadata_helper(client=None) -> MetadataHelper:
    """
    Get cached MetadataHelper instance

    Args:
        client: BigQuery client (optional)

    Returns:
        MetadataHelper instance
    """
    global _cached_metadata_helper

    if _cached_metadata_helper is None:
        _cached_metadata_helper = MetadataHelper(client)

    return _cached_metadata_helper
