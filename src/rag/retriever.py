"""
Example retrieval for few-shot learning.
"""
from typing import List, Dict, Any
from ..rag.examples_loader import QA_EXAMPLES


class ExampleRetriever:
    """
    Retrieve relevant QA examples using simple matching.
    """

    def __init__(self, table_name: str = "qa_embeddings"):
        # Not using vector store, using local examples
        self.examples = QA_EXAMPLES

    async def retrieve(
        self,
        question: str,
        top_k: int = 3,
        score_threshold: float = 0.0
    ) -> List[Dict[str, str]]:
        """
        Retrieve similar QA examples using keyword matching.

        Args:
            question: User question
            top_k: Number of examples to retrieve
            score_threshold: Minimum similarity score (not used, returns top_k)

        Returns:
            List of example dictionaries
        """
        # Simple keyword-based matching
        question_lower = question.lower()

        # Score each example based on keyword overlap
        scored_examples = []
        for ex in self.examples:
            example_question_lower = ex["question"].lower()
            # Count matching words
            question_words = set(question_lower.split())
            example_words = set(example_question_lower.split())
            overlap = len(question_words & example_words)
            scored_examples.append({
                **ex,
                "similarity": overlap
            })

        # Sort by overlap and return top_k
        scored_examples.sort(key=lambda x: x["similarity"], reverse=True)
        return scored_examples[:top_k]
