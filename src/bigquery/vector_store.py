"""
BigQuery Vector Store setup for RAG implementation.
"""
import os
from typing import Optional, List, Dict, Any
from langchain_google_community import BigQueryVectorStore
from langchain_core.documents import Document


def create_vector_store(
    project_id: str | None = None,
    dataset_id: str | None = None,
    table_name: str = "qa_embeddings",
    location: str = "US"
) -> BigQueryVectorStore:
    """
    Create or connect to BigQuery Vector Store.

    Note: Uses embeddings from LLMFactory based on LLM_PROVIDER.
    BigQueryVectorStore works best with VertexAI embeddings when using
    Google Cloud infrastructure, but can support other providers.

    Args:
        project_id: GCP project ID
        dataset_id: Dataset ID for vector store
        table_name: Table name for embeddings
        location: BigQuery location

    Returns:
        BigQueryVectorStore instance
    """
    from ..llm import LLMFactory

    project_id = project_id or os.getenv("GOOGLE_CLOUD_PROJECT", "antaqdados")
    dataset_id = dataset_id or os.getenv("ANTAQ_DATASET", "br_antaq_estatistico_aquaviario")

    # Initialize embeddings using LLMFactory
    embeddings = LLMFactory.get_embeddings()

    # Create vector store
    vector_store = BigQueryVectorStore(
        project_id=project_id,
        dataset_name=dataset_id,
        table_name=table_name,
        location=location,
        embedding=embeddings,
        content_field="question",
        metadata_fields=["sql", "category", "difficulty"]
    )

    return vector_store


def load_examples_to_vector_store(
    examples: List[Dict[str, Any]],
    table_name: str = "qa_embeddings"
) -> None:
    """
    Load QA examples into BigQuery Vector Store.

    Args:
        examples: List of example dictionaries
        table_name: Table name for embeddings
    """
    vector_store = create_vector_store(table_name=table_name)

    # Prepare documents
    texts = [ex["question"] for ex in examples]
    metadatas = [
        {
            "sql": ex["sql"],
            "category": ex.get("category", ""),
            "difficulty": ex.get("difficulty", "")
        }
        for ex in examples
    ]

    # Add to vector store
    vector_store.add_texts(texts=texts, metadatas=metadatas)

    print(f"Loaded {len(examples)} examples to vector store")


# QA examples from documentation - Updated with correct BigQuery schema
# Using v_carga_metodologia_oficial view with official methodology
# IMPORTANT: sentido column values are 'Embarcados' (export) and 'Desembarcados' (import)
#
# CRITICAL TERM MAPPING:
# - User says "exportadas/exportação/exportar" → use sentido = 'Embarcados'
# - User says "importadas/importação/importar" → use sentido = 'Desembarcados'
QA_EXAMPLES = [
    {
        "question": "Qual foi o total de carga movimentado em 2024?",
        "sql": "SELECT SUM(vlpesocargabruta_oficial) AS carga_total FROM `antaqdados.br_antaq_estatistico_aquaviario.v_carga_metodologia_oficial` WHERE ano = 2024 AND isValidoMetodologiaANTAQ = 1",
        "category": "total_geral",
        "difficulty": "basico"
    },
    {
        "question": "Qual a carga movimentada por tipo de navegação em 2024?",
        "sql": "SELECT tipo_de_navegacao_da_atracacao, SUM(vlpesocargabruta_oficial) AS carga_total FROM `antaqdados.br_antaq_estatistico_aquaviario.v_carga_metodologia_oficial` WHERE ano = 2024 AND isValidoMetodologiaANTAQ = 1 GROUP BY tipo_de_navegacao_da_atracacao ORDER BY carga_total DESC",
        "category": "por_navegacao",
        "difficulty": "basico"
    },
    {
        "question": "Quanto foi exportado em 2024?",
        "sql": "SELECT SUM(vlpesocargabruta_oficial) AS carga_total FROM `antaqdados.br_antaq_estatistico_aquaviario.v_carga_metodologia_oficial` WHERE ano = 2024 AND isValidoMetodologiaANTAQ = 1 AND sentido = 'Embarcados'",
        "category": "por_sentido",
        "difficulty": "basico"
    },
    {
        "question": "Quanto foi importado em 2024?",
        "sql": "SELECT SUM(vlpesocargabruta_oficial) AS carga_total FROM `antaqdados.br_antaq_estatistico_aquaviario.v_carga_metodologia_oficial` WHERE ano = 2024 AND isValidoMetodologiaANTAQ = 1 AND sentido = 'Desembarcados'",
        "category": "por_sentido",
        "difficulty": "basico"
    },
    {
        "question": "Quantas toneladas foram exportadas pelo porto de Santos em janeiro de 2025?",
        "sql": "SELECT SUM(vlpesocargabruta_oficial) AS carga_total FROM `antaqdados.br_antaq_estatistico_aquaviario.v_carga_metodologia_oficial` WHERE ano = 2025 AND mes = 1 AND isValidoMetodologiaANTAQ = 1 AND LOWER(porto_atracacao) LIKE '%santos%' AND sentido = 'Embarcados'",
        "category": "por_porto",
        "difficulty": "intermediario"
    },
    {
        "question": "Compare as exportações de Santos entre janeiro de 2024 e janeiro de 2025",
        "sql": "SELECT ano, SUM(vlpesocargabruta_oficial) AS carga_total FROM `antaqdados.br_antaq_estatistico_aquaviario.v_carga_metodologia_oficial` WHERE ((ano = 2024 AND mes = 1) OR (ano = 2025 AND mes = 1)) AND isValidoMetodologiaANTAQ = 1 AND LOWER(porto_atracacao) LIKE '%santos%' AND sentido = 'Embarcados' GROUP BY ano ORDER BY ano",
        "category": "comparacao",
        "difficulty": "intermediario"
    },
    {
        "question": "Compare a importação e exportação em 2024",
        "sql": "SELECT sentido, SUM(vlpesocargabruta_oficial) AS carga_total FROM `antaqdados.br_antaq_estatistico_aquaviario.v_carga_metodologia_oficial` WHERE ano = 2024 AND isValidoMetodologiaANTAQ = 1 GROUP BY sentido ORDER BY carga_total DESC",
        "category": "por_sentido",
        "difficulty": "basico"
    },
    {
        "question": "Quais são os 10 maiores portos por movimentação de carga em 2024?",
        "sql": "SELECT porto_atracacao, uf, SUM(vlpesocargabruta_oficial) AS carga_total FROM `antaqdados.br_antaq_estatistico_aquaviario.v_carga_metodologia_oficial` WHERE ano = 2024 AND isValidoMetodologiaANTAQ = 1 GROUP BY porto_atracacao, uf ORDER BY carga_total DESC LIMIT 10",
        "category": "ranking",
        "difficulty": "basico"
    },
    {
        "question": "Qual foi a evolução mensal da carga em 2024?",
        "sql": "SELECT mes, SUM(vlpesocargabruta_oficial) AS carga_total FROM `antaqdados.br_antaq_estatistico_aquaviario.v_carga_metodologia_oficial` WHERE ano = 2024 AND isValidoMetodologiaANTAQ = 1 GROUP BY mes ORDER BY mes",
        "category": "serie_temporal",
        "difficulty": "basico"
    },
    {
        "question": "Qual a movimentação do porto de Itaguaí em 2024?",
        "sql": "SELECT SUM(vlpesocargabruta_oficial) AS carga_total FROM `antaqdados.br_antaq_estatistico_aquaviario.v_carga_metodologia_oficial` WHERE ano = 2024 AND isValidoMetodologiaANTAQ = 1 AND LOWER(porto_atracacao) LIKE '%itagua%'",
        "category": "por_porto",
        "difficulty": "intermediario"
    },
    {
        "question": "Qual foi a movimentação total dos terminais de Santos em agosto de 2025?",
        "sql": "SELECT SUM(vlpesocargabruta_oficial) AS carga_total FROM `antaqdados.br_antaq_estatistico_aquaviario.v_carga_metodologia_oficial` WHERE ano = 2025 AND mes = 8 AND isValidoMetodologiaANTAQ = 1 AND LOWER(porto_atracacao) LIKE '%santos%'",
        "category": "por_porto",
        "difficulty": "intermediario"
    },
    {
        "question": "Quais são as 10 principais mercadorias movimentadas em 2024?",
        "sql": "SELECT cdmercadoria, SUM(vlpesocargabruta_oficial) AS carga_total FROM `antaqdados.br_antaq_estatistico_aquaviario.v_carga_metodologia_oficial` WHERE ano = 2024 AND isValidoMetodologiaANTAQ = 1 GROUP BY cdmercadoria ORDER BY carga_total DESC LIMIT 10",
        "category": "por_mercadoria",
        "difficulty": "basico"
    },
    {
        "question": "Qual a carga por estado em 2024?",
        "sql": "SELECT uf, SUM(vlpesocargabruta_oficial) AS carga_total FROM `antaqdados.br_antaq_estatistico_aquaviario.v_carga_metodologia_oficial` WHERE ano = 2024 AND isValidoMetodologiaANTAQ = 1 GROUP BY uf ORDER BY carga_total DESC",
        "category": "por_regiao",
        "difficulty": "intermediario"
    },
    {
        "question": "Compare exportações e importações por região geográfica em 2024",
        "sql": "SELECT regiao_geografica, sentido, SUM(vlpesocargabruta_oficial) AS carga_total FROM `antaqdados.br_antaq_estatistico_aquaviario.v_carga_metodologia_oficial` WHERE ano = 2024 AND isValidoMetodologiaANTAQ = 1 AND sentido IN ('Embarcados', 'Desembarcados') GROUP BY regiao_geografica, sentido ORDER BY regiao_geografica, sentido",
        "category": "por_regiao",
        "difficulty": "intermediario"
    }
]
