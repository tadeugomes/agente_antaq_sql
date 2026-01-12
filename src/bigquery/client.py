"""
BigQuery client wrapper with connection pooling and error handling.
"""
import os
import asyncio
from typing import List, Dict, Any, Optional
from google.cloud import bigquery
from google.cloud.bigquery import QueryJobConfig


class BigQueryClient:
    """
    Wrapper for Google Cloud BigQuery client.
    """

    def __init__(
        self,
        project_id: Optional[str] = None,
        dataset_id: Optional[str] = None,
        location: str = "US",
        data_project_id: str = "antaqdados"
    ):
        """
        Initialize BigQuery client.

        Args:
            project_id: GCP project ID for the client (credentials project)
            dataset_id: Dataset ID (defaults to br_antaq_estatistico_aquaviario)
            location: Dataset location
            data_project_id: Project where the dataset is located (antaqdados)
        """
        self.project_id = project_id or os.getenv("GOOGLE_CLOUD_PROJECT", "saasimpacto")
        self.dataset_id = dataset_id or os.getenv("ANTAQ_DATASET", "br_antaq_estatistico_aquaviario")
        self.location = location
        self.data_project_id = data_project_id

        # Initialize client with default credentials
        self.client = bigquery.Client(
            project=self.project_id,
            location=self.location
        )

        # Default job config for safety
        self.default_job_config = QueryJobConfig(
            maximum_bytes_billed=10_000_000_000,  # 10 GB
            use_query_cache=True,
            use_legacy_sql=False
        )

    def query(
        self,
        sql: str,
        job_config: Optional[QueryJobConfig] = None
    ) -> List[Dict[str, Any]]:
        """
        Execute a SQL query.

        Args:
            sql: SQL query string
            job_config: Optional job configuration

        Returns:
            List of dictionaries representing rows
        """
        config = job_config or self.default_job_config

        try:
            # Run query
            query_job = self.client.query(sql, job_config=config)
            results = query_job.result()

            # Convert to list of dicts
            rows = [dict(row) for row in results]

            return rows

        except Exception as e:
            raise RuntimeError(f"Query execution failed: {str(e)}") from e

    async def aquery(
        self,
        sql: str,
        job_config: Optional[QueryJobConfig] = None
    ) -> List[Dict[str, Any]]:
        """
        Execute a SQL query asynchronously.

        Args:
            sql: SQL query string
            job_config: Optional job configuration

        Returns:
            List of dictionaries representing rows
        """
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self.query, sql, job_config)

    def test_connection(self) -> bool:
        """
        Test BigQuery connection.

        Returns:
            True if connection successful
        """
        try:
            query = "SELECT 1 as test"
            result = self.client.query(query).result()
            return list(result)[0].test == 1
        except Exception:
            return False

    def get_table(self, table_name: str):
        """
        Get BigQuery table object.

        Args:
            table_name: Name of the table

        Returns:
            bigquery.Table object
        """
        full_table_id = f"{self.data_project_id}.{self.dataset_id}.{table_name}"
        return self.client.get_table(full_table_id)

    def list_tables(self) -> List[str]:
        """
        List all tables in the dataset.

        Returns:
            List of table names
        """
        dataset_ref = self.client.dataset(self.dataset_id, project=self.data_project_id)
        tables = self.client.list_tables(dataset_ref)
        return [table.table_id for table in tables]


# Singleton instance for easy import
_client_instance: Optional[BigQueryClient] = None


def get_bigquery_client() -> BigQueryClient:
    """Get or create singleton BigQuery client instance."""
    global _client_instance
    if _client_instance is None:
        _client_instance = BigQueryClient()
    return _client_instance
