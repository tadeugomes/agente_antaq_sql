"""
Performance test for the ANTAQ AI Agent.
Tests graph caching, memory usage, and query execution time.
"""
import os
import sys
import time
import tracemalloc

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Set environment
os.environ["LLM_PROVIDER"] = "vertexai"
os.environ["GOOGLE_CLOUD_PROJECT"] = "saasimpacto"
os.environ["SENTRY_DSN"] = ""


def test_graph_cache_performance():
    """Test that graph caching improves performance."""
    print("\n" + "=" * 60)
    print("TEST 1: Graph Cache Performance")
    print("=" * 60)

    from src.agent.graph import create_graph

    # First creation - should take longer
    start = time.perf_counter()
    g1 = create_graph(use_cache=True)
    first_time = time.perf_counter() - start

    # Second creation - should be instant (cached)
    start = time.perf_counter()
    g2 = create_graph(use_cache=True)
    cached_time = time.perf_counter() - start

    # Verify same object
    is_same = g1 is g2

    print(f"First creation:  {first_time*1000:.2f} ms")
    print(f"Cached creation: {cached_time*1000:.2f} ms")
    print(f"Same object: {is_same}")
    print(f"Speedup: {first_time/cached_time:.1f}x faster")

    if is_same and cached_time < first_time:
        print("✓ Graph cache working correctly!")
        return True
    else:
        print("✗ Graph cache not working as expected")
        return False


def test_memory_overhead():
    """Test memory usage of the agent components."""
    print("\n" + "=" * 60)
    print("TEST 2: Memory Overhead")
    print("=" * 60)

    tracemalloc.start()

    # Baseline
    baseline = tracemalloc.get_traced_memory()[0]

    # Create graph
    from src.agent.graph import create_graph
    graph = create_graph()
    graph_memory = tracemalloc.get_traced_memory()[0] - baseline

    # Simulate session state with messages
    from app.utils.session import SessionManager
    import streamlit as st

    # Mock session state
    if not hasattr(st, 'session_state'):
        from collections import defaultdict
        st.session_state = defaultdict(dict)

    SessionManager.init()
    init_memory = tracemalloc.get_traced_memory()[0] - baseline

    # Add messages
    for i in range(10):
        SessionManager.add_chat_message("user", f"Test message {i}")
        SessionManager.add_chat_message("assistant", f"Response {i}" * 10)

    messages_memory = tracemalloc.get_traced_memory()[0] - baseline

    print(f"Graph overhead:     {graph_memory/1024:.1f} KB")
    print(f"Session init:       {init_memory/1024:.1f} KB")
    print(f"10 msg pairs:       {messages_memory/1024:.1f} KB")
    print(f"Per message:        {(messages_memory-init_memory)/10/1024:.1f} KB")

    tracemalloc.stop()

    # Check that per-message overhead is reasonable (< 10KB per message pair)
    per_msg_kb = (messages_memory - init_memory) / 10 / 1024
    if per_msg_kb < 10:
        print("✓ Memory usage is reasonable!")
        return True
    else:
        print("⚠ Memory usage is high")
        return False


def test_results_cache():
    """Test the results cache functionality."""
    print("\n" + "=" * 60)
    print("TEST 3: Results Cache")
    print("=" * 60)

    from app.components.chat_tab import (
        save_result_to_cache,
        get_cached_result,
        get_results_cache,
        clear_results_cache,
        MAX_CACHED_RESULTS
    )

    # Mock session state
    import streamlit as st
    from collections import defaultdict
    st.session_state = defaultdict(dict)

    # Add some results
    for i in range(15):
        results = list(range(100))  # Mock 100 rows
        save_result_to_cache(i, results, f"SELECT * FROM table_{i}")

    cache = get_results_cache()

    print(f"Added 15 results to cache")
    print(f"Cache size limit: {MAX_CACHED_RESULTS}")
    print(f"Actual cache size: {len(cache)}")
    print(f"Cache properly limited: {len(cache) <= MAX_CACHED_RESULTS}")

    # Check first result was removed (LRU eviction)
    first_removed = "0" not in cache
    print(f"Oldest entry evicted: {first_removed}")

    # Check a cached result
    cached = get_cached_result(14)
    print(f"Latest result retrievable: {cached is not None}")
    if cached:
        print(f"  - Row count: {cached['row_count']}")
        print(f"  - SQL stored: {bool(cached.get('sql'))}")

    clear_results_cache()

    if len(cache) <= MAX_CACHED_RESULTS and first_removed:
        print("✓ Results cache working correctly!")
        return True
    else:
        print("✗ Results cache not working as expected")
        return False


def test_large_results_handling():
    """Test handling of large result sets."""
    print("\n" + "=" * 60)
    print("TEST 4: Large Results Handling")
    print("=" * 60)

    from app.components.chat_tab import save_result_to_cache, get_cached_result

    # Mock session state
    import streamlit as st
    from collections import defaultdict
    st.session_state = defaultdict(dict)

    # Small result - should be cached
    small_results = list(range(100))
    save_result_to_cache(0, small_results, "SELECT * FROM small_table")

    # Large result - should NOT be fully cached
    large_results = list(range(2000))
    save_result_to_cache(1, large_results, "SELECT * FROM large_table")

    small_cached = get_cached_result(0)
    large_cached = get_cached_result(1)

    print(f"Small result (100 rows):")
    print(f"  - Cached data: {small_cached['results'] is not None}")
    print(f"  - Row count: {small_cached['row_count']}")
    print(f"  - Truncated: {small_cached.get('truncated', False)}")

    print(f"\nLarge result (2000 rows):")
    print(f"  - Cached data: {large_cached['results'] is not None}")
    print(f"  - Row count: {large_cached['row_count']}")
    print(f"  - Truncated: {large_cached.get('truncated', False)}")

    if small_cached['results'] is not None and large_cached['results'] is None:
        print("\n✓ Large results handling working correctly!")
        return True
    else:
        print("\n✗ Large results handling not working as expected")
        return False


def run_all_tests():
    """Run all performance tests."""
    print("\n" + "=" * 60)
    print("ANTAQ AI Agent - Performance Tests")
    print("=" * 60)

    results = []

    try:
        results.append(("Graph Cache", test_graph_cache_performance()))
    except Exception as e:
        print(f"✗ Graph cache test failed: {e}")
        results.append(("Graph Cache", False))

    try:
        results.append(("Memory Overhead", test_memory_overhead()))
    except Exception as e:
        print(f"✗ Memory test failed: {e}")
        results.append(("Memory Overhead", False))

    try:
        results.append(("Results Cache", test_results_cache()))
    except Exception as e:
        print(f"✗ Results cache test failed: {e}")
        results.append(("Results Cache", False))

    try:
        results.append(("Large Results", test_large_results_handling()))
    except Exception as e:
        print(f"✗ Large results test failed: {e}")
        results.append(("Large Results", False))

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
    success = run_all_tests()
    sys.exit(0 if success else 1)
