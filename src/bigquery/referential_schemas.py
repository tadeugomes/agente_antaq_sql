"""
Schema definitions for Referential Data Tables (diretórios)
Based on the ER diagram provided
"""
from typing import Dict, Any


class InstalacaoOrigemSchema:
    """
    Schema for INSTALACAO_ORIGEM table
    Reference data for port facilities (origin)
    """

    def __init__(self):
        self.schema: Dict[str, str] = {
            'origem': 'STRING',  # PK
            'cd_tup_origem': 'STRING',
            'nome': 'STRING',
            'cidade': 'STRING',
            'uf': 'STRING',
            'pais': 'STRING',
            'regiao_hidrografica': 'STRING',
            'bloco_economico': 'STRING'
        }

    def get_bigquery_schema(self) -> list:
        """Get BigQuery schema fields"""
        from google.cloud import bigquery

        return [
            bigquery.SchemaField('origem', 'STRING', mode='REQUIRED'),
            bigquery.SchemaField('cd_tup_origem', 'STRING'),
            bigquery.SchemaField('nome', 'STRING'),
            bigquery.SchemaField('cidade', 'STRING'),
            bigquery.SchemaField('uf', 'STRING'),
            bigquery.SchemaField('pais', 'STRING'),
            bigquery.SchemaField('regiao_hidrografica', 'STRING'),
            bigquery.SchemaField('bloco_economico', 'STRING')
        ]


class InstalacaoDestinoSchema:
    """
    Schema for INSTALACAO_DESTINO table
    Reference data for port facilities (destination)
    """

    def __init__(self):
        self.schema: Dict[str, str] = {
            'destino': 'STRING',  # PK
            'cd_tup_destino': 'STRING',
            'nome': 'STRING',
            'cidade': 'STRING',
            'uf': 'STRING',
            'pais': 'STRING',
            'regiao_hidrografica': 'STRING',
            'bloco_economico': 'STRING'
        }

    def get_bigquery_schema(self) -> list:
        """Get BigQuery schema fields"""
        from google.cloud import bigquery

        return [
            bigquery.SchemaField('destino', 'STRING', mode='REQUIRED'),
            bigquery.SchemaField('cd_tup_destino', 'STRING'),
            bigquery.SchemaField('nome', 'STRING'),
            bigquery.SchemaField('cidade', 'STRING'),
            bigquery.SchemaField('uf', 'STRING'),
            bigquery.SchemaField('pais', 'STRING'),
            bigquery.SchemaField('regiao_hidrografica', 'STRING'),
            bigquery.SchemaField('bloco_economico', 'STRING')
        ]


class MercadoriaCargaSchema:
    """
    Schema for MERCADORIA_CARGA table
    Reference data for cargo commodities
    """

    def __init__(self):
        self.schema: Dict[str, str] = {
            'cd_mercadoria': 'STRING',  # PK
            'ncm': 'STRING',
            'tipo_container': 'STRING',
            'grupo_mercadoria': 'STRING',
            'nomenclatura_simplificada': 'STRING'
        }

    def get_bigquery_schema(self) -> list:
        """Get BigQuery schema fields"""
        from google.cloud import bigquery

        return [
            bigquery.SchemaField('cd_mercadoria', 'STRING', mode='REQUIRED'),
            bigquery.SchemaField('ncm', 'STRING'),
            bigquery.SchemaField('tipo_container', 'STRING'),
            bigquery.SchemaField('grupo_mercadoria', 'STRING'),
            bigquery.SchemaField('nomenclatura_simplificada', 'STRING')
        ]


class MercadoriaCargaConteinerSchema:
    """
    Schema for MERCADORIA_CARGA_CONTEIN table
    Reference data for containerized cargo commodities
    """

    def __init__(self):
        self.schema: Dict[str, str] = {
            'cd_mercadoria_conteinerizada': 'STRING',  # PK
            'cd_grupo_mercadoria_conteinerizada': 'STRING',
            'mercadoria_conteinerizada': 'STRING',
            'nomenclatura_simplificada_conteinerizada': 'STRING'
        }

    def get_bigquery_schema(self) -> list:
        """Get BigQuery schema fields"""
        from google.cloud import bigquery

        return [
            bigquery.SchemaField('cd_mercadoria_conteinerizada', 'STRING', mode='REQUIRED'),
            bigquery.SchemaField('cd_grupo_mercadoria_conteinerizada', 'STRING'),
            bigquery.SchemaField('mercadoria_conteinerizada', 'STRING'),
            bigquery.SchemaField('nomenclatura_simplificada_conteinerizada', 'STRING')
        ]


class TaxaOcupacaoSchema:
    """
    Schema for TAXA_OCUPACAO table
    Berth occupation rates
    """

    def __init__(self):
        self.schema: Dict[str, str] = {
            'idberco': 'STRING',  # FK
            'dia_taxa_ocupacao': 'DATE',
            'min_taxa_ocupacao': 'FLOAT64',
            'max_taxa_ocupacao': 'FLOAT64',
            'media_taxa_ocupacao': 'FLOAT64',
            'tempo_em_minutos': 'INT64',
            'ano_taxa_ocupacao': 'INT64'
        }

    def get_bigquery_schema(self) -> list:
        """Get BigQuery schema fields"""
        from google.cloud import bigquery

        return [
            bigquery.SchemaField('idberco', 'STRING', mode='REQUIRED'),
            bigquery.SchemaField('dia_taxa_ocupacao', 'DATE', mode='REQUIRED'),
            bigquery.SchemaField('min_taxa_ocupacao', 'FLOAT64'),
            bigquery.SchemaField('max_taxa_ocupacao', 'FLOAT64'),
            bigquery.SchemaField('media_taxa_ocupacao', 'FLOAT64'),
            bigquery.SchemaField('tempo_em_minutos', 'INT64'),
            bigquery.SchemaField('ano_taxa_ocupacao', 'INT64')
        ]


class TaxaOcupacaoComCargaSchema:
    """
    Schema for TAXA_OCUPACAO_COM_CARGA table
    Berth occupation rates with cargo
    """

    def __init__(self):
        self.schema: Dict[str, str] = {
            'idberco': 'STRING',  # FK
            'dia_taxa_ocupacao_com_carga': 'DATE',
            'media_taxa_ocupacao_com_carga': 'FLOAT64',
            'tempo_em_minutos_dia': 'INT64',
            'ano_taxa_ocupacao_com_carga': 'INT64'
        }

    def get_bigquery_schema(self) -> list:
        """Get BigQuery schema fields"""
        from google.cloud import bigquery

        return [
            bigquery.SchemaField('idberco', 'STRING', mode='REQUIRED'),
            bigquery.SchemaField('dia_taxa_ocupacao_com_carga', 'DATE', mode='REQUIRED'),
            bigquery.SchemaField('media_taxa_ocupacao_com_carga', 'FLOAT64'),
            bigquery.SchemaField('tempo_em_minutos_dia', 'INT64'),
            bigquery.SchemaField('ano_taxa_ocupacao_com_carga', 'INT64')
        ]


class TaxaOcupacaoTipoOperAtracSchema:
    """
    Schema for TAXA_OCUPACAO_TIPO_OPER_ATRAC table
    Berth occupation rates by operation type
    """

    def __init__(self):
        self.schema: Dict[str, str] = {
            'idberco': 'STRING',  # FK
            'ds_tipo_operacao_atracacao': 'STRING',
            'media_taxa_ocupacao_tipo_atracacao': 'FLOAT64',
            'tempo_em_minutos_tipo_atracacao': 'INT64',
            'ano_taxa_ocupacao_tipo_atracacao': 'INT64'
        }

    def get_bigquery_schema(self) -> list:
        """Get BigQuery schema fields"""
        from google.cloud import bigquery

        return [
            bigquery.SchemaField('idberco', 'STRING', mode='REQUIRED'),
            bigquery.SchemaField('ds_tipo_operacao_atracacao', 'STRING', mode='REQUIRED'),
            bigquery.SchemaField('media_taxa_ocupacao_tipo_atracacao', 'FLOAT64'),
            bigquery.SchemaField('tempo_em_minutos_tipo_atracacao', 'INT64'),
            bigquery.SchemaField('ano_taxa_ocupacao_tipo_atracacao', 'INT64')
        ]


class CargaAreasSchema:
    """
    Schema for CARGA_AREAS table
    Cargo areas/companies information
    """

    def __init__(self):
        self.schema: Dict[str, str] = {
            'idcarga': 'STRING',  # FK
            'codigo_area': 'STRING',
            'nome_area': 'STRING',
            'cnpj': 'STRING',
            'empresa': 'STRING'
        }

    def get_bigquery_schema(self) -> list:
        """Get BigQuery schema fields"""
        from google.cloud import bigquery

        return [
            bigquery.SchemaField('idcarga', 'STRING', mode='REQUIRED'),
            bigquery.SchemaField('codigo_area', 'STRING'),
            bigquery.SchemaField('nome_area', 'STRING'),
            bigquery.SchemaField('cnpj', 'STRING'),
            bigquery.SchemaField('empresa', 'STRING')
        ]
