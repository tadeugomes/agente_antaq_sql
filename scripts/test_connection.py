"""
Test BigQuery connection script.
"""
import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.bigquery.client import get_bigquery_client
from src.bigquery.schema import get_schema_retriever


def test_connection():
    """Test BigQuery connection."""
    print("🔍 Testing BigQuery connection...")

    # Get client
    client = get_bigquery_client()

    # Test connection
    if client.test_connection():
        print("✅ BigQuery connection successful!")

        # List tables
        print("\n📋 Available tables:")
        tables = client.list_tables()
        for table in tables:
            print(f"  - {table}")

        # Test schema retrieval
        print("\n🔧 Testing schema retrieval...")
        retriever = get_schema_retriever()
        schema = retriever.get_formatted_schema()
        print(f"✅ Schema retrieved ({len(schema)} characters)")

        return True
    else:
        print("❌ BigQuery connection failed!")
        print("\nPlease check:")
        print("  - GOOGLE_APPLICATION_CREDENTIALS is set")
        print("  - Service account has BigQuery access")
        print("  - Project ID is correct")
        return False


if __name__ == "__main__":
    test_connection()
