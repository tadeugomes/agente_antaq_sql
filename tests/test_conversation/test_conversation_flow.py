"""
Test conversation context and follow-up questions.
"""
import os
import sys
import asyncio

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# Set environment
os.environ["LLM_PROVIDER"] = "vertexai"
os.environ["GOOGLE_CLOUD_PROJECT"] = "saasimpacto"
os.environ["SENTRY_DSN"] = ""


async def test_followup_question():
    """Test that follow-up questions use conversation context."""
    print("\n" + "=" * 60)
    print("TEST: Follow-up Questions with Context")
    print("=" * 60)

    from src.agent.graph import query_agente

    # Use same thread_id to simulate same conversation
    thread_id = "test_conversation_001"

    # First question
    print("\n📝 Question 1: quantas toneladas foram importadas por santos em julho de 2025?")
    print("-" * 60)

    result1 = await query_agente(
        question="quantas toneladas foram importadas por santos em julho de 2025?",
        thread_id=thread_id
    )

    answer1 = result1.get("final_answer", "No answer")
    sql1 = result1.get("validated_sql", "")
    results1 = result1.get("query_results", [])

    print(f"✓ Answer 1: {answer1[:200]}...")
    print(f"✓ SQL 1: {sql1[:100]}...")
    print(f"✓ Results: {len(results1)} rows")

    # Check if it used the correct filter (Desembarcados = import)
    has_import_filter = "desembarcados" in sql1.lower() or "sentido" in sql1.lower()
    print(f"✓ Has import filter: {has_import_filter}")

    # Second question - follow-up
    print("\n📝 Question 2: e exportadas?")
    print("-" * 60)

    result2 = await query_agente(
        question="e exportadas?",
        thread_id=thread_id  # Same thread to continue conversation
    )

    answer2 = result2.get("final_answer", "No answer")
    sql2 = result2.get("validated_sql", "")
    results2 = result2.get("query_results", [])

    print(f"✓ Answer 2: {answer2[:200]}...")
    print(f"✓ SQL 2: {sql2[:100]}...")
    print(f"✓ Results: {len(results2)} rows")

    # Check if it used the correct filter (Embarcados = export)
    has_export_filter = "embarcados" in sql2.lower() or "sentido" in sql2.lower()
    print(f"✓ Has export filter: {has_export_filter}")

    # Check if it maintained context (Santos, julho 2025)
    has_santos = "santos" in sql2.lower()
    has_julho = "julho" in sql2.lower() or "mes = 7" in sql2.lower()
    has_2025 = "ano = 2025" in sql2.lower() or "2025" in sql2.lower()

    print(f"\n✓ Context maintained:")
    print(f"  - Porto Santos: {has_santos}")
    print(f"  - Mês Julho: {has_julho}")
    print(f"  - Ano 2025: {has_2025}")

    # Evaluate results
    success = (
        answer1 and answer1 != "No answer" and
        answer2 and answer2 != "No answer" and
        has_export_filter and
        (has_santos or has_julho or has_2025)  # At least some context maintained
    )

    print("\n" + "=" * 60)
    if success:
        print("✓ TEST PASSED: Follow-up question worked correctly!")
    else:
        print("✗ TEST FAILED: Follow-up question did not maintain context")
    print("=" * 60 + "\n")

    return success


async def test_multiple_followups():
    """Test multiple follow-up questions in sequence."""
    print("\n" + "=" * 60)
    print("TEST: Multiple Follow-up Questions")
    print("=" * 60)

    from src.agent.graph import query_agente

    thread_id = "test_conversation_002"

    questions = [
        "quantas toneladas passaram pelo porto de Santos em 2024?",
        "e em 2023?",
        "e pelo porto do Rio de Janeiro em 2024?"
    ]

    answers = []

    for i, question in enumerate(questions, 1):
        print(f"\n📝 Question {i}: {question}")
        print("-" * 40)

        result = await query_agente(
            question=question,
            thread_id=thread_id
        )

        answer = result.get("final_answer", "No answer")
        sql = result.get("validated_sql", "")

        print(f"✓ Answer: {answer[:150]}...")
        print(f"✓ SQL: {sql[:80]}...")

        answers.append(answer)

    # Check if all questions got answers
    all_answered = all(a and a != "No answer" for a in answers)

    print("\n" + "=" * 60)
    if all_answered:
        print("✓ TEST PASSED: All follow-up questions got answers!")
    else:
        print("✗ TEST FAILED: Some questions returned 'No answer'")
    print("=" * 60 + "\n")

    return all_answered


async def test_context_with_mercadorias():
    """Test conversation about mercadorias with proper names."""
    print("\n" + "=" * 60)
    print("TEST: Mercadorias with Names in Conversation")
    print("=" * 60)

    from src.agent.graph import query_agente

    thread_id = "test_conversation_003"

    # First question
    print("\n📝 Question 1: quais as principais mercadorias importadas em 2024?")
    print("-" * 60)

    result1 = await query_agente(
        question="quais as principais mercadorias importadas em 2024?",
        thread_id=thread_id
    )

    answer1 = result1.get("final_answer", "No answer")
    print(f"✓ Answer: {answer1[:300]}...")

    # Check if mercadoria names are mentioned
    has_names = any(name in answer1 for name in [
        "Minerios", "Sementes", "Combustíveis", "Cereais", "Trigo"
    ])

    # Follow-up
    print("\n📝 Question 2: e as exportadas?")
    print("-" * 60)

    result2 = await query_agente(
        question="e as exportadas?",
        thread_id=thread_id
    )

    answer2 = result2.get("final_answer", "No answer")
    print(f"✓ Answer: {answer2[:300]}...")

    has_names_2 = any(name in answer2 for name in [
        "Minerios", "Sementes", "Combustíveis", "Cereais", "Trigo", "Minérios"
    ])

    print(f"\n✓ Mercadoria names in answer 1: {has_names}")
    print(f"✓ Mercadoria names in answer 2: {has_names_2}")

    success = (
        answer1 and answer1 != "No answer" and
        answer2 and answer2 != "No answer"
    )

    print("\n" + "=" * 60)
    if success:
        print("✓ TEST PASSED: Mercadorias conversation works!")
    else:
        print("✗ TEST FAILED: Mercadorias conversation failed")
    print("=" * 60 + "\n")

    return success


async def run_all_tests():
    """Run all conversation tests."""
    print("\n" + "=" * 60)
    print("CONVERSATION CONTEXT TESTS")
    print("=" * 60)

    results = []

    try:
        results.append(("Follow-up Questions", await test_followup_question()))
    except Exception as e:
        print(f"✗ Follow-up test failed: {e}")
        import traceback
        traceback.print_exc()
        results.append(("Follow-up Questions", False))

    try:
        results.append(("Multiple Follow-ups", await test_multiple_followups()))
    except Exception as e:
        print(f"✗ Multiple follow-ups test failed: {e}")
        import traceback
        traceback.print_exc()
        results.append(("Multiple Follow-ups", False))

    try:
        results.append(("Mercadorias Context", await test_context_with_mercadorias()))
    except Exception as e:
        print(f"✗ Mercadorias test failed: {e}")
        import traceback
        traceback.print_exc()
        results.append(("Mercadorias Context", False))

    # Summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)

    passed = sum(1 for _, r in results if r)
    total = len(results)

    for name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status}: {name}")

    print("=" * 60)
    print(f"Results: {passed}/{total} tests passed")
    print("=" * 60 + "\n")

    return passed == total


if __name__ == "__main__":
    success = asyncio.run(run_all_tests())
    sys.exit(0 if success else 1)
