# 06 - Guia de Desenvolvimento

## Implementação do Agente AI para Consulta BigQuery

Este guia fornece as informações técnicas necessárias para desenvolver um protótipo de agente AI que consulta os dados ANTAQ em linguagem natural.

---

## 1. Stack Tecnológico Recomendado

| Componente | Tecnologia | Versão |
|------------|------------|--------|
| **Framework** | LangGraph | >= 0.2.0 |
| **LLM** | Gemini 1.5 Flash/Pro | - |
| **Banco de Dados** | BigQuery | - |
| **Python** | 3.10+ | - |
| **ORM** | SQLAlchemy | 2.0+ |
| **Vector Store** | BigQuery Vector Store | - |

---

## 2. Dependências Python

```txt
# requirements.txt
langgraph>=0.2.0
langchain-google-vertexai>=1.0.0
langchain-google-community>=1.0.0
langchain-anthropic>=0.1.0
sqlalchemy>=2.0.0
google-cloud-bigquery>=3.0.0
pydantic>=2.0.0
python-dotenv>=1.0.0
```

---

## 3. Arquitetura LangGraph

### Grafo de Estados

```
         START
           |
           v
    +-------------+
    | get_schema  |  Recupera schema do BigQuery
    +-------------+
           |
           v
    +-------------+
    | data_chatbot|  LLM gera SQL
    +-------------+
           |
           v
    <conditional>
     /          \
    v            v
execute_sql   END
    |            ^
    v            |
+---------------+  Executa SQL
| ToolNode      |
+---------------+
    |
    v
data_chatbot (loop)
```

### Código Base

```python
"""
Agente AI para consulta BigQuery ANTAQ usando LangGraph
"""
import os
import json
from typing import TypedDict, Annotated, Optional
from google.cloud import bigquery
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langchain_core.tools import tool
from langchain_google_vertexai import ChatVertexAI
from langgraph.graph import StateGraph, END
from langgraph.graph.message import add_messages
from langgraph.checkpoint.memory import MemorySaver

# Configuração
PROJECT_ID = "antaqdados"
DATASET_ID = "br_antaq_estatistico_aquaviario"
MODEL = "gemini-1.5-flash"

# State do Agente
class State(TypedDict):
    """Estado do workflow"""
    messages: Annotated[list, add_messages]
    dataset_schema: Optional[str]
    sql_query: Optional[str]
    query_result: Optional[str]

# Função para recuperar schema
def get_bq_schema() -> str:
    """Recupera schema do BigQuery"""
    client = bigquery.Client(project=PROJECT_ID)
    dataset_ref = client.dataset(DATASET_ID)
    tables = client.list_tables(dataset_ref)

    schemas = []
    tables_to_include = [
        "v_carga_oficial_antaq",
        "v_atracacao_validada",
        "v_carga_validada",
        "instalacao_origem",
        "instalacao_destino",
        "mercadoria_carga"
    ]

    for table in tables:
        if table.table_id not in tables_to_include:
            continue
        table_ref = dataset_ref.table(table.table_id)
        table_obj = client.get_table(table_ref)

        table_schema = {
            "table_name": f"{PROJECT_ID}.{DATASET_ID}.{table.table_id}",
            "description": table_obj.description,
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

# Tool para executar query
@tool
def execute_query_tool(query: str) -> str:
    """Executa SQL no BigQuery e retorna resultados"""
    client = bigquery.Client(project=PROJECT_ID)

    # Validações de segurança
    query_upper = query.upper()
    forbidden = ["DROP", "DELETE", "UPDATE", "INSERT", "CREATE", "ALTER", "TRUNCATE"]
    if any(fw in query_upper for fw in forbidden):
        return json.dumps({"error": "Comando não permitido"})

    # Adiciona LIMIT se não existir
    if "LIMIT" not in query_upper:
        query += " LIMIT 1000"

    try:
        result = client.query_and_wait(query)
        rows = [dict(row) for row in result]
        return json.dumps({
            "rows": rows[:100],  # Max 100 linhas
            "total_rows": len(rows)
        }, ensure_ascii=False, default=str)
    except Exception as e:
        return json.dumps({"error": str(e)})

# Tool para resposta final
class SubmitFinalAnswer:
    """Representa a resposta final do agente"""
    final_answer: str

# Node: recuperar schema
def get_schema_node(state: State) -> State:
    """Recupera schema do BigQuery"""
    if state.get("dataset_schema") is None:
        schema = get_bq_schema()
        return {
            "dataset_schema": schema,
            "messages": [AIMessage(content="Schema recuperado do BigQuery")]
        }
    return {"messages": [AIMessage(content="Schema em memória")]}

# Node: chatbot
def data_chatbot_node(state: State) -> State:
    """Processa pergunta e gera SQL"""
    schema = state["dataset_schema"]

    system_prompt = f"""Você é um assistente especializado em dados da ANTAQ.

RULES IMPORTANTES:
1. SEMPRE filtre por 'ano' quando possível
2. Use 'v_carga_oficial_antaq' para métricas de carga
3. Use 'v_atracacao_validada' para análise de atracação
4. SEMPRE adicione LIMIT nas queries
5. Apenas SELECT queries são permitidas

Schema disponível:
{schema}

Exemplos:
- Pergunta: "Total de carga em 2024?"
  SQL: SELECT SUM(peso_carga) FROM `{PROJECT_ID}.{DATASET_ID}.v_carga_oficial_antaq` WHERE ano = 2024

- Pergunta: "Top 5 portos?"
  SQL: SELECT nm_porto, SUM(peso_carga) FROM `{PROJECT_ID}.{DATASET_ID}.v_carga_oficial_antaq` WHERE ano = 2024 GROUP BY nm_porto ORDER BY SUM(peso_carga) DESC LIMIT 5
"""

    messages = [SystemMessage(content=system_prompt)] + state["messages"]
    llm = ChatVertexAI(model=MODEL, temperature=0)
    response = llm.invoke(messages)

    return {"messages": [response]}

# Node: executar SQL
def execute_sql_node(state: State) -> State:
    """Executa SQL gerado"""
    last_message = state["messages"][-1]

    if hasattr(last_message, "tool_calls") and last_message.tool_calls:
        for tool_call in last_message.tool_calls:
            if tool_call["name"] == "execute_query_tool":
                query = tool_call["args"]["query"]
                result = execute_query_tool.invoke(query)
                return {
                    "sql_query": query,
                    "query_result": result,
                    "messages": [AIMessage(content=f"Resultado: {result}")]
                }

    return state

# Condicao: proximo passo
def should_continue(state: State) -> str:
    """Decide se executa SQL ou termina"""
    last_message = state["messages"][-1]

    if hasattr(last_message, "tool_calls"):
        for tool_call in last_message.tool_calls:
            if tool_call["name"] == "execute_query_tool":
                return "execute_sql"
            elif tool_call["name"] == "submit_final_answer":
                return END

    return END

# Criar grafo
def create_graph():
    """Cria o grafo LangGraph"""
    workflow = StateGraph(State)

    # Adicionar nodes
    workflow.add_node("get_schema", get_schema_node)
    workflow.add_node("data_chatbot", data_chatbot_node)
    workflow.add_node("execute_sql", execute_sql_node)

    # Adicionar edges
    workflow.add_edge("__start__", "get_schema")
    workflow.add_edge("get_schema", "data_chatbot")
    workflow.add_conditional_edges(
        "data_chatbot",
        should_continue,
        {"execute_sql": "execute_sql", END: END}
    )
    workflow.add_edge("execute_sql", "data_chatbot")

    # Compilar com memória
    memory = MemorySaver()
    return workflow.compile(checkpointer=memory)

# Executar
def query_agente(pergunta: str, thread_id: str = "session1"):
    """Executa query no agente"""
    graph = create_graph()
    config = {"configurable": {"thread_id": thread_id}}

    result = graph.invoke(
        {"messages": [HumanMessage(content=pergunta)]},
        config=config
    )

    return result
```

---

## 4. Implementação Simplificada (LangChain)

```python
"""
Versão simplificada usando LangChain SQL Agent
"""
from langchain.agents import create_sql_agent
from langchain_google_vertexai import ChatVertexAI
from langchain_community.utilities import SQLDatabase

# Conexão via SQLAlchemy
db_uri = "bigquery://antaqdados/br_antaq_estatistico_aquaviario"
db = SQLDatabase.from_uri(
    db_uri,
    include_tables=[
        "v_carga_oficial_antaq",
        "v_atracacao_validada",
        "v_carga_validada"
    ],
    sample_rows_in_table_info=3
)

# Criar agente
llm = ChatVertexAI(model="gemini-1.5-flash", temperature=0)
agent = create_sql_agent(
    llm,
    db=db,
    verbose=True,
    agent_type="openai-tools",  # ou "zero-shot-react-description"
    top_k=10
)

# Usar
result = agent.invoke("Qual o total de carga movimentado em 2024?")
print(result)
```

---

## 5. RAG com BigQuery Vector Store

```python
"""
RAG para melhorar geração de SQL usando exemplos
"""
from langchain_google_community import BigQueryVectorStore

# Configurar Vector Store
vector_store = BigQueryVectorStore(
    project_id="antaqdados",
    dataset_name="br_antaq_estatistico_aquaviario",
    table_name="qa_embeddings",
    embedding_model="textembedding-gecko@003",
    location="US"
)

# Buscar exemplos similares
def get_similar_examples(question: str, k: int = 3):
    """Recupera exemplos similares"""
    results = vector_store.similarity_search(question, k=k)
    return results

# Usar no prompt
def augment_prompt_with_examples(question: str) -> str:
    """Adiciona exemplos ao prompt"""
    examples = get_similar_examples(question)

    examples_text = "\n\n".join([
        f"Exemplo:\nPergunta: {ex.metadata['question']}\nSQL: {ex.metadata['sql']}"
        for ex in examples
    ])

    return f"""Considere estes exemplos:

{examples_text}

Pergunta atual: {question}
"""
```

---

## 6. Validação de Segurança

```python
import re

def validate_sql(query: str) -> tuple[bool, str]:
    """Valida se SQL é seguro para executar"""

    # Converter para maiúsculo
    query_upper = query.upper()

    # Comandos proibidos
    forbidden_patterns = [
        r'\bDROP\b',
        r'\bDELETE\b',
        r'\bTRUNCATE\b',
        r'\bINSERT\b',
        r'\bUPDATE\b',
        r'\bALTER\b',
        r'\bCREATE\b',
        r'\bGRANT\b',
        r'\bREVOKE\b'
    ]

    for pattern in forbidden_patterns:
        if re.search(pattern, query_upper):
            return False, f"Comando não permitido: {pattern}"

    # Verificar se é SELECT
    if not query_upper.strip().startswith('SELECT'):
        return False, "Apenas comandos SELECT são permitidos"

    # Verificar se tem LIMIT
    if 'LIMIT' not in query_upper:
        return False, "Queries devem ter LIMIT"

    # Verificar se tem WHERE (para evitar table scans)
    if 'WHERE' not in query_upper and 'FROM' in query_upper:
        return True, "WARNING: Query sem WHERE pode ser lenta"

    return True, "OK"
```

---

## 7. Interface de Usuário (Streamlit)

```python
"""
Interface simples com Streamlit
"""
import streamlit as st
from vertex_preview import vertex_ai

st.title("🚢 Assistente ANTAQ - Consulta em Linguagem Natural")

st.markdown("""
Faça perguntas sobre os dados de navegação e carga da ANTAQ.
Exemplos:
- Qual o total de carga em 2024?
- Quais os 5 maiores portos?
- Compare importação vs exportação
""")

# Input
user_question = st.text_input("Sua pergunta:")

if st.button("Consultar"):
    if user_question:
        with st.spinner("Processando..."):
            result = query_agente(user_question)
            st.write(result)
```

---

## 8. Estrutura de Arquivos

```
ai_agent_antaq/
├── config/
│   ├── bigquery_config.yaml
│   └── agent_config.yaml
├── src/
│   ├── __init__.py
│   ├── agent/
│   │   ├── __init__.py
│   │   ├── graph.py         # LangGraph
│   │   ├── nodes.py         # Nodes do grafo
│   │   └── tools.py         # Tools
│   ├── bigquery/
│   │   ├── __init__.py
│   │   ├── client.py        # Cliente BQ
│   │   └── schema.py        # Schema retrieval
│   └── utils/
│       ├── __init__.py
│       ├── validation.py    # Validação SQL
│       └── security.py      # Segurança
├── app/
│   └── streamlit_app.py     # Interface
├── tests/
│   ├── test_agent.py
│   └── test_security.py
├── requirements.txt
└── README.md
```

---

## 9. Variáveis de Ambiente

```bash
# .env
GOOGLE_CLOUD_PROJECT=antaqdados
GOOGLE_CLOUD_REGION=us-central1
GOOGLE_APPLICATION_CREDENTIALS=/path/to/credentials.json

# Vertex AI
VERTEX_AI_MODEL=gemini-1.5-flash
VERTEX_AI_TEMPERATURE=0
VERTEX_AI_MAX_TOKENS=2048

# Agente
AGENT_MAX_ROWS=1000
AGENT_TIMEOUT_SECONDS=60
```

---

## 10. Custos Estimados

| Operação | Custo |
|----------|------|
| Gemini 1.5 Flash (Input) | $0.075 por 1M tokens |
| Gemini 1.5 Flash (Output) | $0.30 por 1M tokens |
| BigQuery (On-demand) | $5 por TB |
| BigQuery Vector Search | $1 por 10K queries |

**Estimativa mensal (1.000 queries):**
- LLM: ~$2-5
- BigQuery: ~$1-2
- **Total:** ~$3-7/mês

---

## 11. Próximos Passos

1. Criar novo repositório para o protótipo
2. Configurar ambiente virtual Python
3. Instalar dependências
4. Implementar versão simplificada (LangChain SQL Agent)
5. Testar com perguntas básicas
6. Evoluir para LangGraph se necessário
7. Adicionar RAG com exemplos
8. Implementar interface web
