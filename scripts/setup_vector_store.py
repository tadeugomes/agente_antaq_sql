"""
Setup script for BigQuery Vector Store with QA examples.
"""
import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.rag.examples_loader import load_examples, get_all_examples, get_example_categories


def main():
    """Load QA examples into BigQuery Vector Store."""
    print("🚀 Setting up BigQuery Vector Store...")
    print()

    # Show examples
    examples = get_all_examples()
    print(f"📝 Loading {len(examples)} QA examples...")

    # Show categories
    categories = get_example_categories()
    print(f"📁 Categories: {', '.join(categories)}")
    print()

    # Load examples
    try:
        load_examples()
        print("✅ Examples loaded successfully!")
        print()
        print("The vector store is now ready for RAG queries.")
    except Exception as e:
        print(f"❌ Error loading examples: {e}")
        print()
        print("Please check:")
        print("  - BigQuery permissions")
        print("  - Vertex AI API is enabled")
        print("  - Credentials are valid")


if __name__ == "__main__":
    main()
