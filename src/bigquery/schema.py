"""
Schema retrieval and formatting for BigQuery tables.
"""
import json
from typing import List, Dict, Any
from .client import BigQueryClient, get_bigquery_client


class SchemaRetriever:
    """
    Retrieve and format BigQuery table schemas for LLM context.
    """

    # IMPORTANT: Use v_carga_metodologia_oficial for official cargo metrics
    # This view applies ANTAQ's official methodology (isValidoMetodologiaANTAQ = 1)
    TABLES_TO_INCLUDE = [
        "v_carga_metodologia_oficial",  # PRIMARY: Official cargo methodology view
        "v_atracacao_validada",         # Docking/berthing analysis
        "v_carga_validada",             # Validated cargo data
        "instalacao_origem",            # Origin port catalog
        "instalacao_destino",           # Destination port catalog
        "mercadoria_carga"              # Commodity catalog
    ]

    def __init__(self, client: BigQueryClient | None = None):
        self.client = client or get_bigquery_client()

    def get_formatted_schema(self) -> str:
        """
        Get formatted schema for all included tables.

        Returns:
            Formatted schema string for LLM
        """
        schemas = []

        for table_name in self.TABLES_TO_INCLUDE:
            table_info = self._get_table_schema(table_name)
            schemas.append(self._format_table_schema(table_info))

        return "\n\n".join(schemas)

    def _get_table_schema(self, table_name: str) -> Dict[str, Any]:
        """Get schema for a single table."""
        # Use the client's get_table which already handles cross-project access
        table = self.client.get_table(table_name)

        return {
            "name": table_name,
            "description": table.description or f"Table: {table_name}",
            "columns": [
                {
                    "name": field.name,
                    "type": field.field_type,
                    "mode": field.mode,
                    "description": field.description or ""
                }
                for field in table.schema
            ]
        }

    def _format_table_schema(self, table_info: Dict[str, Any]) -> str:
        """Format table schema for LLM consumption."""
        lines = [
            f"### {table_info['name']}",
            table_info['description'],
            "\nColumns:"
        ]

        for col in table_info['columns']:
            desc = f" - {col['description']}" if col['description'] else ""
            lines.append(f"  - {col['name']} ({col['type']}){desc}")

        return "\n".join(lines)

    def get_schema_json(self) -> str:
        """
        Get schema as JSON string.

        Returns:
            JSON string with table schemas
        """
        schemas = []

        for table_name in self.TABLES_TO_INCLUDE:
            table_info = self._get_table_schema(table_name)
            schemas.append(table_info)

        return json.dumps({"tables": schemas}, indent=2, ensure_ascii=False)

    def get_table_info(self, table_name: str) -> str:
        """
        Get detailed information about a specific table.

        Args:
            table_name: Name of the table

        Returns:
            Formatted table information
        """
        table_info = self._get_table_schema(table_name)
        return self._format_table_schema(table_info)


# Singleton instance
_schema_retriever_instance: SchemaRetriever | None = None


def get_schema_retriever() -> SchemaRetriever:
    """Get or create singleton SchemaRetriever instance."""
    global _schema_retriever_instance
    if _schema_retriever_instance is None:
        _schema_retriever_instance = SchemaRetriever()
    return _schema_retriever_instance
