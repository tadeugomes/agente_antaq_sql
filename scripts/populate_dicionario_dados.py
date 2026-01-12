#!/usr/bin/env python3
"""
Populate dicionario_dados table in BigQuery
Runs the SQL to create and populate the metadata dictionary
"""
import os
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from google.cloud import bigquery
from dotenv import load_dotenv

load_dotenv()


def populate_dicionario_dados():
    """
    Create and populate the dicionario_dados table in BigQuery
    Creates in the user's own project (saasimpacto) with reference to antaqdados
    """
    project_id = os.getenv("GOOGLE_CLOUD_PROJECT", "saasimpacto")
    client = bigquery.Client(project=project_id)

    # Create table in the user's project (they have write access here)
    # Dataset will be created if it doesn't exist
    dataset_id = f"{project_id}.antaq_metadados"
    table_id = f"{dataset_id}.dicionario_dados"

    print(f"📊 Working on project: {project_id}")
    print(f"📚 Target table: {table_id}")

    # Create dataset if it doesn't exist
    dataset_ref = bigquery.DatasetReference(project_id, "antaq_metadados")
    try:
        client.get_dataset(dataset_ref)
        print("✅ Dataset already exists.")
    except Exception:
        print("⚠️  Dataset does not exist. Creating...")
        dataset = bigquery.Dataset(dataset_ref)
        dataset.location = "US"
        dataset = client.create_dataset(dataset)
        print(f"✅ Created dataset: {dataset.dataset_id}")

    # Check if table exists
    try:
        client.get_table(table_id)
        print("✅ Table already exists. Skipping creation.")
        print("💡 To recreate, drop the table first:")
        print(f"   DROP TABLE `{table_id}`;")
    except Exception:
        print("⚠️  Table does not exist. Creating...")

        # Create table schema
        schema = [
            bigquery.SchemaField("tabela", "STRING", mode="REQUIRED"),
            bigquery.SchemaField("coluna", "STRING", mode="REQUIRED"),
            bigquery.SchemaField("descricao", "STRING", mode="REQUIRED"),
            bigquery.SchemaField("tipo_dado", "STRING", mode="REQUIRED"),
            bigquery.SchemaField("valores_possiveis", "STRING"),
            bigquery.SchemaField("categoria", "STRING", mode="REQUIRED"),
            bigquery.SchemaField("tags", "STRING", mode="REPEATED"),
        ]

        table = bigquery.Table(table_id, schema=schema)
        table.clustering_fields = ["tabela"]

        table = client.create_table(table)
        print(f"✅ Created table: {table.table_id}")

    # Data to insert
    data = [
        # v_carga_metodologia_oficial - Identificação
        {
            "tabela": "v_carga_metodologia_oficial",
            "coluna": "idcarga",
            "descricao": "Identificador único do registro de carga",
            "tipo_dado": "STRING",
            "valores_possiveis": None,
            "categoria": "Identificação",
            "tags": ["pk", "carga", "id"]
        },
        {
            "tabela": "v_carga_metodologia_oficial",
            "coluna": "idatracacao",
            "descricao": "Identificador da atracação relacionada",
            "tipo_dado": "STRING",
            "valores_possiveis": None,
            "categoria": "Identificação",
            "tags": ["fk", "atracacao", "id"]
        },
        # Temporal
        {
            "tabela": "v_carga_metodologia_oficial",
            "coluna": "ano",
            "descricao": "Ano da operação (formato INT64, usar sem aspas em filtros WHERE)",
            "tipo_dado": "INT64",
            "valores_possiveis": "2015-2025",
            "categoria": "Temporal",
            "tags": ["ano", "periodo", "filtro"]
        },
        {
            "tabela": "v_carga_metodologia_oficial",
            "coluna": "mes",
            "descricao": "Mês da operação (1-12)",
            "tipo_dado": "INT64",
            "valores_possiveis": "1-12",
            "categoria": "Temporal",
            "tags": ["mês", "periodo", "filtro"]
        },
        {
            "tabela": "v_carga_metodologia_oficial",
            "coluna": "data_referencia",
            "descricao": "Data de referência para cálculos oficiais",
            "tipo_dado": "DATE",
            "valores_possiveis": None,
            "categoria": "Temporal",
            "tags": ["data", "referência"]
        },
        {
            "tabela": "v_carga_metodologia_oficial",
            "coluna": "data_atracacao",
            "descricao": "Data da atracação da embarcação",
            "tipo_dado": "TIMESTAMP",
            "valores_possiveis": None,
            "categoria": "Temporal",
            "tags": ["data", "atracacao"]
        },
        # Localização
        {
            "tabela": "v_carga_metodologia_oficial",
            "coluna": "porto_atracacao",
            "descricao": "Nome do porto onde ocorreu a atracação",
            "tipo_dado": "STRING",
            "valores_possiveis": None,
            "categoria": "Localização",
            "tags": ["porto", "local", "uf", "estado"]
        },
        {
            "tabela": "v_carga_metodologia_oficial",
            "coluna": "uf",
            "descricao": "Unidade Federativa (estado) do porto",
            "tipo_dado": "STRING",
            "valores_possiveis": "SP, RJ, ES, etc",
            "categoria": "Localização",
            "tags": ["uf", "estado", "região"]
        },
        {
            "tabela": "v_carga_metodologia_oficial",
            "coluna": "regiao_geografica",
            "descricao": "Região geográfica do porto",
            "tipo_dado": "STRING",
            "valores_possiveis": None,
            "categoria": "Localização",
            "tags": ["região", "geografia"]
        },
        # Mercadoria
        {
            "tabela": "v_carga_metodologia_oficial",
            "coluna": "cdmercadoria",
            "descricao": "Código da mercadoria segundo classificação ANTAQ",
            "tipo_dado": "STRING",
            "valores_possiveis": None,
            "categoria": "Mercadoria",
            "tags": ["mercadoria", "produto", "código"]
        },
        {
            "tabela": "v_carga_metodologia_oficial",
            "coluna": "natureza_carga",
            "descricao": "Natureza da carga (carga geral, granel sólido, granel líquido, etc)",
            "tipo_dado": "STRING",
            "valores_possiveis": None,
            "categoria": "Mercadoria",
            "tags": ["natureza", "tipo", "classificação"]
        },
        # Operação
        {
            "tabela": "v_carga_metodologia_oficial",
            "coluna": "sentido",
            "descricao": "Direção do fluxo da carga. 'Embarcados' = exportação, 'Desembarcados' = importação",
            "tipo_dado": "STRING",
            "valores_possiveis": "Embarcados (exportação), Desembarcados (importação)",
            "categoria": "Operação",
            "tags": ["sentido", "direção", "exportação", "importação"]
        },
        {
            "tabela": "v_carga_metodologia_oficial",
            "coluna": "tipo_de_navegacao_da_atracacao",
            "descricao": "Tipo de navegação da embarcação",
            "tipo_dado": "STRING",
            "valores_possiveis": "Longo Curso, Cabotagem, Interior",
            "categoria": "Operação",
            "tags": ["navegação", "tipo", "classificação"]
        },
        {
            "tabela": "v_carga_metodologia_oficial",
            "coluna": "tipo_operacao_da_carga",
            "descricao": "Tipo da operação de carga",
            "tipo_dado": "STRING",
            "valores_possiveis": None,
            "categoria": "Operação",
            "tags": ["operação", "tipo", "atividade"]
        },
        # Métricas
        {
            "tabela": "v_carga_metodologia_oficial",
            "coluna": "vlpesocargabruta_oficial",
            "descricao": "Peso bruto da carga em toneladas (métrica oficial ANTAQ) - PRINCIPAL MÉTRICA",
            "tipo_dado": "FLOAT64",
            "valores_possiveis": None,
            "categoria": "Métrica",
            "tags": ["peso", "tonelada", "volume", "métrica principal", "oficial"]
        },
        {
            "tabela": "v_carga_metodologia_oficial",
            "coluna": "qtcarga_oficial",
            "descricao": "Quantidade da carga segundo unidade de medida",
            "tipo_dado": "FLOAT64",
            "valores_possiveis": None,
            "categoria": "Métrica",
            "tags": ["quantidade", "unidade"]
        },
        {
            "tabela": "v_carga_metodologia_oficial",
            "coluna": "teu",
            "descricao": "Número de contêineres em TEU (Twenty-foot Equivalent Unit)",
            "tipo_dado": "FLOAT64",
            "valores_possiveis": None,
            "categoria": "Métrica",
            "tags": ["teu", "contêiner", "unidade"]
        },
        # Validação
        {
            "tabela": "v_carga_metodologia_oficial",
            "coluna": "isValidoMetodologiaANTAQ",
            "descricao": "Flag indicando se o registro é válido pela metodologia oficial ANTAQ (usar = 1 para dados oficiais)",
            "tipo_dado": "INT64",
            "valores_possiveis": "0 ou 1",
            "categoria": "Validação",
            "tags": ["validação", "oficial", "filtro", "metodologia"]
        },
        {
            "tabela": "v_carga_metodologia_oficial",
            "coluna": "FlagAutorizacao",
            "descricao": "Flag de autorização da operação (S = autorizado)",
            "tipo_dado": "STRING",
            "valores_possiveis": "S, N",
            "categoria": "Validação",
            "tags": ["autorização", "validação"]
        },
    ]

    # Clear existing data and insert new data
    print(f"🔄 Clearing existing data from {table_id}...")
    client.query(f"DELETE FROM `{table_id}` WHERE TRUE").result()

    print(f"📥 Inserting {len(data)} rows...")
    errors = client.insert_rows_json(table_id, data)

    if errors:
        print(f"❌ Errors encountered: {errors}")
    else:
        print("✅ Data inserted successfully!")

    # Verify data
    print("\n📊 Verifying data...")
    query = f"SELECT COUNT(*) as count FROM `{table_id}`"
    result = client.query(query).to_dataframe()
    print(f"✅ Total rows in table: {result.iloc[0]['count']}")

    # Sample query
    print("\n🔍 Sample data:")
    query = f"""
    SELECT tabela, categoria, COUNT(*) as colunas
    FROM `{table_id}`
    GROUP BY tabela, categoria
    ORDER BY tabela, categoria
    """
    result = client.query(query).to_dataframe()
    print(result.to_string(index=False))


if __name__ == "__main__":
    populate_dicionario_dados()
