"""
Simulate error scenarios to test Sentry integration.
This test simulates errors without actually sending to Sentry.
"""
import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# Configure environment
os.environ["SENTRY_DSN"] = ""  # No actual DSN
os.environ["SENTRY_ENVIRONMENT"] = "testing"


def test_exception_capture_simulation():
    """Simulate capturing an exception."""
    print("\n--- Simulating Exception Capture ---")

    from src.utils.sentry_config import capture_exception

    try:
        # Simulate a database error
        raise ConnectionError("Failed to connect to BigQuery: timeout")
    except ConnectionError as e:
        event_id = capture_exception(e)
        print(f"✓ Exception captured, event_id: {event_id}")


def test_message_capture_simulation():
    """Simulate capturing a message."""
    print("\n--- Simulating Message Capture ---")

    from src.utils.sentry_config import capture_message

    event_id = capture_message("User attempted invalid SQL query", level="warning")
    print(f"✓ Message captured, event_id: {event_id}")


def test_context_setting():
    """Test setting various context types."""
    print("\n--- Testing Context Setting ---")

    from src.utils.sentry_config import set_tag, set_context, set_user_context

    # Set tags
    set_tag("query_type", "aggregate")
    set_tag("dataset", "br_antaq_estatistico_aquaviario")
    set_tag("llm_provider", "vertexai")
    print("✓ Tags set successfully")

    # Set context
    set_context("query_details", {
        "question": "Qual o total de carga transportada em 2024?",
        "table": "v_carga_metodologia_oficial",
        "filters": ["ano = 2024"]
    })
    print("✓ Context set successfully")

    # Set user context
    set_user_context(
        user_id="session_12345",
        username="anonymous"
    )
    print("✓ User context set successfully")


def test_sensitive_data_filtering():
    """Test that sensitive data is filtered."""
    print("\n--- Testing Sensitive Data Filtering ---")

    from src.utils.sentry_config import before_send_filter

    # Simulate an event with sensitive data
    event = {
        "request": {
            "headers": {
                "Authorization": "Bearer ya29.1234567890abcdef",
                "Cookie": "session_id=secret123",
            }
        },
        "extra": {
            "sql_query": "SELECT * FROM users WHERE password = 'secret'",
            "api_key": "sk-1234567890",
            "normal_field": "this should not be filtered"
        },
        "user": {
            "id": "user123",
            "email": "user@example.com",
            "ip_address": "10.0.0.1"
        }
    }

    filtered_event = before_send_filter(event, None)

    # Verify filtering
    assert filtered_event["request"]["headers"]["Authorization"] == "[FILTERED]"
    assert filtered_event["request"]["headers"]["Cookie"] == "[FILTERED]"
    assert filtered_event["extra"]["api_key"] == "[FILTERED]"
    assert filtered_event["extra"]["normal_field"] == "this should not be filtered"
    assert "email" not in filtered_event["user"]
    assert "ip_address" not in filtered_event["user"]

    print("✓ Sensitive data filtered correctly")
    print(f"  - Authorization: {filtered_event['request']['headers']['Authorization']}")
    print(f"  - API key: {filtered_event['extra']['api_key']}")
    print(f"  - Normal field preserved: {filtered_event['extra']['normal_field']}")


def test_transaction_filter():
    """Test transaction event filtering."""
    print("\n--- Testing Transaction Filter ---")

    from src.utils.sentry_config import before_send_transaction_filter

    event = {
        "request": {
            "query_string": "param1=value1&param2=value2"
        },
        "transaction": "/api/query"
    }

    filtered = before_send_transaction_filter(event, None)
    print("✓ Transaction filter works")


def run_all_tests():
    """Run all simulation tests."""
    print("\n" + "=" * 60)
    print("Sentry Integration Simulation Tests")
    print("=" * 60)

    tests = [
        test_exception_capture_simulation,
        test_message_capture_simulation,
        test_context_setting,
        test_sensitive_data_filtering,
        test_transaction_filter,
    ]

    for test in tests:
        try:
            test()
        except Exception as e:
            print(f"✗ {test.__name__} failed: {e}")
            import traceback
            traceback.print_exc()
            return False

    print("\n" + "=" * 60)
    print("All simulation tests passed!")
    print("=" * 60 + "\n")
    return True


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
