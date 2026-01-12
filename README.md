# ANTAQ AI Agent

Agente AI para consulta em linguagem natural aos dados da ANTAQ (Agência Nacional de Transportes Aquaviários) no BigQuery.

## Características

- Consulta em linguagem natural convertida para SQL
- LangGraph para workflow do agente
- RAG (Retrieval-Augmented Generation) com exemplos few-shot
- Validação de segurança SQL
- Interface Streamlit
- Métricas oficiais ANTAQ com metodologia validada

## Tech Stack

| Componente | Tecnologia |
|------------|------------|
| **Orquestração** | LangGraph |
| **LLM** | OpenAI GPT-4o-mini |
| **Embeddings** | OpenAI text-embedding-3-small |
| **Data Warehouse** | BigQuery |
| **UI** | Streamlit |

## Instalação

```bash
# Criar ambiente virtual
python3 -m venv venv_new
source venv_new/bin/activate  # Windows: venv_new\Scripts\activate

# Instalar dependências
pip install -r requirements.txt
```

## Configuração

Crie o arquivo `.env` com suas credenciais:

```bash
# Google Cloud
GOOGLE_CLOUD_PROJECT=saasimpacto
GOOGLE_CLOUD_REGION=us-central1
GOOGLE_APPLICATION_CREDENTIALS=/path/to/credentials.json

# ANTAQ Dataset
ANTAQ_DATASET=br_antaq_estatistico_aquaviario
ANTAQ_DATASET_LOCATION=US

# OpenAI
LLM_MODEL=gpt-4o-mini
LLM_TEMPERATURE=0
EMBEDDING_MODEL=text-embedding-3-small
OPENAI_API_KEY=sk-proj-...

# Agent Configuration
AGENT_MAX_ROWS=1000
AGENT_TIMEOUT_SECONDS=60
```

## Execução

```bash
# Executar interface Streamlit
source venv_new/bin/activate
GOOGLE_APPLICATION_CREDENTIALS=/path/to/credentials.json streamlit run app/streamlit_app.py
```

Acesse: http://localhost:8501

## Estrutura do Projeto

```
agente_sql_antaq/
├── config/                  # Configurações YAML
│   ├── agent_config.yaml    # Config do agente
│   ├── bigquery_config.yaml # Config BigQuery
│   └── prompts.yaml         # System prompts
├── src/
│   ├── agent/               # LangGraph graph e nodes
│   │   ├── graph.py         # State machine
│   │   ├── nodes.py         # Node implementations
│   │   ├── state.py         # Pydantic models
│   │   └── prompts.py       # Prompt templates
│   ├── bigquery/            # Cliente BigQuery
│   │   ├── client.py        # BQ client wrapper
│   │   ├── schema.py        # Schema retrieval
│   │   └── vector_store.py  # QA examples
│   ├── rag/                 # RAG e retriever
│   │   ├── retriever.py     # Example retrieval
│   │   └── embeddings.py    # OpenAI embeddings
│   └── utils/               # Utilitários
│       └── validation.py    # SQL validation
├── app/                     # Streamlit UI
│   └── streamlit_app.py     # Main interface
├── SCHEMA.md                # Documentação do schema BigQuery
├── .env                     # Variáveis de ambiente
└── requirements.txt         # Dependências Python
```

## Schema BigQuery

**View principal:** `v_carga_metodologia_oficial`

Esta view aplica a metodologia oficial da ANTAQ para estatísticas de carga.

### Colunas principais

| Coluna | Tipo | Descrição |
|--------|------|-----------|
| `ano` | INT64 | Ano (ex: 2024) - SEMPRE filtrar |
| `mes` | INT64 | Mês (1-12) |
| `porto_atracacao` | STRING | Nome do porto |
| `uf` | STRING | Estado |
| **`vlpesocargabruta_oficial`** | FLOAT | **Peso bruto em toneladas - MÉTRICA PRINCIPAL** |
| `qtcarga_oficial` | FLOAT | Quantidade de carga |
| `sentido` | STRING | 'Embarcados' (Exportação) ou 'Desembarcados' (Importação) |
| `tipo_de_navegacao_da_atracacao` | STRING | Tipo de navegação |
| `cdmercadoria` | STRING | Código da mercadoria |
| `isValidoMetodologiaANTAQ` | INT64 | Flag de validação (=1 para dados oficiais) |

### Filtros obrigatórios

```sql
WHERE ano = 2024                    -- INT64, sem aspas
  AND isValidoMetodologiaANTAQ = 1  -- Metodologia oficial
```

> Consulte [SCHEMA.md](SCHEMA.md) para documentação completa do schema.

## Exemplos de Perguntas

| Pergunta | SQL Gerado |
|----------|------------|
| Qual foi o total de carga movimentado em 2024? | `SELECT SUM(vlpesocargabruta_oficial) FROM ... WHERE ano = 2024 AND isValidoMetodologiaANTAQ = 1` |
| Quais são os 10 maiores portos? | `SELECT porto_atracacao, SUM(...) GROUP BY porto_atracacao ORDER BY SUM(...) DESC LIMIT 10` |
| Qual a movimentação do porto de Itaqui? | `WHERE LOWER(porto_atracacao) LIKE '%itaqui%'` |
| Compare importação vs exportação | `GROUP BY sentido` |

## Workflow do Agente

```
         START
           │
           ▼
    ┌─────────────┐
    │ setup_schema│  Cache do schema BigQuery
    └─────────────┘
           │
           ▼
    ┌─────────────┐
    │  retrieve   │  RAG: busca exemplos similares
    │  examples   │
    └─────────────┘
           │
           ▼
    ┌─────────────┐
    │ generate    │  LLM: gera SQL
    │    sql      │
    └─────────────┘
           │
           ▼
    ┌─────────────┐
    │  validate   │  Validação segurança
    │    sql      │  (bloqueia DML/DDL)
    └─────────────┘
           │
           ▼
      ┌────┴────┐
      │  valid  │──── error ──> END
      └────┬────┘
           │
           ▼
    ┌─────────────┐
    │  execute    │  Executa no BigQuery
    │    sql      │
    └─────────────┘
           │
           ▼
    ┌─────────────┐
    │  generate   │  LLM: formata resposta
    │final_answer │  em português
    └─────────────┘
           │
           ▼
          END
```

## Segurança

| Proteção | Descrição |
|----------|-----------|
| **Read-only** | Apenas `SELECT`, `WITH`, `SHOW`, `DESCRIBE` |
| **Keywords bloqueadas** | `DROP`, `DELETE`, `UPDATE`, `INSERT`, `CREATE`, `ALTER`, `TRUNCATE` |
| **SQL Injection** | Detecção de padrões maliciosos |
| **LIMIT automático** | Adiciona `LIMIT 1000` se não especificado |
| **Timeout** | 60 segundos por query |
| **Custo** | Limite de 10 GB processados |

## Troubleshooting

### Erro: Vertex AI API not enabled
Use OpenAI em vez de Vertex AI. Configure `OPENAI_API_KEY` no `.env`.

### Resultados incorretos
Verifique se está usando:
- View: `v_carga_metodologia_oficial`
- Métrica: `vlpesocargabruta_oficial`
- Filtro: `isValidoMetodologiaANTAQ = 1`
- Ano: `2024` (INT64, sem aspas)

### Environment variables não carregam
Adicione no início do `streamlit_app.py`:
```python
from dotenv import load_dotenv
load_dotenv()
```

## Licença

MIT
