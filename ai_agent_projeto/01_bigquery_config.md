# 01 - Configuração BigQuery

## Conexão BigQuery para o Agente AI

### Configuração Básica

```yaml
# config/bigquery_config.yaml
project_id: antaqdados
dataset_name: br_antaq_estatistico_aquaviario
location: US
```

### Autenticação

O projeto usa autenticação via Service Account do Google Cloud. O arquivo de credenciais deve ser configurado via variável de ambiente:

```bash
export GOOGLE_APPLICATION_CREDENTIALS="/path/to/service-account-key.json"
export GOOGLE_CLOUD_PROJECT="antaqdados"
```

### Conexão Python

```python
from google.cloud import bigquery
import os

# Cliente BigQuery
client = bigquery.Client(
    project=os.getenv("GOOGLE_CLOUD_PROJECT", "antaqdados")
)

# Dataset completo
DATASET_ID = "antaqdados.br_antaq_estatistico_aquaviario"

# Exemplo: listar tabelas
tables = client.list_tables("br_antaq_estatistico_aquaviario")
for table in tables:
    print(f"{table.table_id}")
```

### Conexão via SQLAlchemy (para LangChain)

```python
from sqlalchemy import create_engine
from langchain_community.utilities import SQLDatabase

# URI de conexão BigQuery para SQLAlchemy
# Formato: bigquery://project_id/dataset_id
db_uri = "bigquery://antaqdados/br_antaq_estatistico_aquaviario"

# Criar database para LangChain
db = SQLDatabase.from_uri(
    db_uri,
    include_tables=[
        "atracacao",
        "carga",
        "instalacao_origem",
        "instalacao_destino",
        "mercadoria_carga",
        "mercadoria_carga_conteiner",
        "taxa_ocupacao"
    ],
    sample_rows_in_table_info=3
)
```

### Obter Schema via Python (para LangGraph)

```python
import json
from google.cloud import bigquery

def get_bq_schema(dataset_id: str) -> str:
    """
    Recupera e retorna o schema do dataset BigQuery em formato JSON.

    Args:
        dataset_id: ID do dataset (ex: 'br_antaq_estatistico_aquaviario')

    Returns:
        JSON string com schema das tabelas
    """
    client = bigquery.Client()
    dataset_ref = client.dataset(dataset_id)
    tables = client.list_tables(dataset_ref)

    schemas = []
    for table in tables:
        table_ref = dataset_ref.table(table.table_id)
        table_obj = client.get_table(table_ref)

        table_schema = {
            "table_name": f"{table.project}.{table.dataset_id}.{table.table_id}",
            "description": table.description,
            "schema": [
                {
                    "name": field.name,
                    "type": field.field_type,
                    "mode": field.mode,
                    "description": field.description
                }
                for field in table_obj.schema
            ]
        }
        schemas.append(table_schema)

    return json.dumps({"tables": schemas}, indent=2, ensure_ascii=False)


# Uso no LangGraph
def get_schema_node(state: Dict) -> Dict:
    """Recupera o schema e armazena no estado do agente."""
    if state.get("dataset_schema") is None:
        schema = get_bq_schema("br_antaq_estatistico_aquaviario")
        return {
            "dataset_schema": schema,
            "messages": [AIMessage(content="Schema recuperado do BigQuery")]
        }
    return {"messages": [AIMessage(content="Schema recuperado da memória")]}
```

### Conexão Direta via BigQuery Python Client

```python
from google.cloud import bigquery

def execute_query(query: str) -> list:
    """
    Executa uma query SQL no BigQuery e retorna os resultados.

    Args:
        query: String SQL query

    Returns:
        Lista de dicionários com os resultados
    """
    client = bigquery.Client()
    job = client.query(query)
    results = job.result()

    return [dict(row) for row in results]
```

### Configuração de Segurança

```python
from google.cloud import bigquery

# Configurar cliente com limites de segurança
client = bigquery.Client(
    project="antaqdados",
    location="US",
    default_query_job_config=bigquery.QueryJobConfig(
        maximum_bytes_billed=10_000_000_000,  # 10 GB max
        timeout=60  # 60 segundos timeout
    )
)
```

### Variáveis de Ambiente Necessárias

```bash
# .env file
GOOGLE_CLOUD_PROJECT=antaqdados
GOOGLE_CLOUD_REGION=us-central1
GOOGLE_APPLICATION_CREDENTIALS=/path/to/credentials.json

# Vertex AI (para Gemini)
VERTEX_AI_PROJECT=antaqdados
VERTEX_AI_LOCATION=us-central1
VERTEX_AI_MODEL=gemini-1.5-flash
```

### Partições e Clustering

As tabelas principais são particionadas e clusterizadas para performance:

```yaml
# Colunas de partição
partition_columns:
  - ano
  - mes

# Colunas de clustering
cluster_columns:
  - cd_porto
  - tipo_operacao
  - tipo_navegacao
```

**Dica:** O agente deve SEMPRE filtrar por `ano` quando possível para aproveitar as partições.

### Views Disponíveis para Consulta

| View | Descrição | Uso Recomendado |
|------|-----------|-----------------|
| `v_carga_oficial_antaq` | Carga metodologia oficial ANTAQ | Consultas de carga totais |
| `v_carga_metodologia_oficial` | Carga com regras oficiais | Análises oficiais |
| `v_atracacao_validada` | Atracação com FK validada | Consultas de atracação |
| `v_carga_validada` | Carga com relacionamentos validados | Consultas de carga |
| `v_analise_portuaria_1semestre_2025` | Análise portuária específica | Exemplo de análise |

### Validação de Conexão

```python
def validate_connection() -> bool:
    """Valida se a conexão com BigQuery está funcionando."""
    try:
        client = bigquery.Client()
        query = "SELECT 1 as test"
        result = client.query(query).result()
        return list(result)[0].test == 1
    except Exception as e:
        print(f"Erro de conexão: {e}")
        return False
```
