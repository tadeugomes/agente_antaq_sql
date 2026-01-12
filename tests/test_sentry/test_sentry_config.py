"""
Test script for Sentry configuration.
Tests the implementation without sending events to actual Sentry.
"""
import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# Set test environment variables BEFORE importing
os.environ["SENTRY_DSN"] = ""  # Empty DSN to test graceful fallback
os.environ["SENTRY_ENVIRONMENT"] = "testing"

def test_init_without_dsn():
    """Test that init_sentry returns False when no DSN is configured."""
    from src.utils.sentry_config import init_sentry

    result = init_sentry()
    assert result is False, "init_sentry should return False without DSN"
    print("✓ Test 1: init_sentry returns False without DSN")


def test_init_with_placeholder_dsn():
    """Test that init_sentry returns False with placeholder DSN."""
    os.environ["SENTRY_DSN"] = "your-sentry-dsn-here"
    from src.utils.sentry_config import init_sentry

    result = init_sentry()
    assert result is False, "init_sentry should return False with placeholder DSN"
    print("✓ Test 2: init_sentry returns False with placeholder DSN")


def test_before_send_filter():
    """Test that before_send_filter removes sensitive data."""
    from src.utils.sentry_config import before_send_filter

    # Create event with sensitive data
    event = {
        "request": {
            "headers": {
                "authorization": "Bearer secret-token-123",
                "content-type": "application/json"
            }
        },
        "extra": {
            "password": "my-secret-password",
            "username": "testuser",
            "api_key": "sk-1234567890"
        },
        "user": {
            "id": "123",
            "email": "test@example.com",
            "ip_address": "192.168.1.1"
        }
    }

    filtered = before_send_filter(event, None)

    # Check that sensitive data is filtered
    assert filtered["request"]["headers"]["authorization"] == "[FILTERED]", \
        "Authorization header should be filtered"
    assert filtered["request"]["headers"]["content-type"] == "application/json", \
        "Non-sensitive header should not be filtered"
    assert filtered["extra"]["password"] == "[FILTERED]", \
        "Password should be filtered"
    assert filtered["extra"]["username"] == "testuser", \
        "Username should not be filtered"
    assert filtered["extra"]["api_key"] == "[FILTERED]", \
        "API key should be filtered"
    assert "email" not in filtered["user"], \
        "Email should be removed"
    assert "ip_address" not in filtered["user"], \
        "IP address should be removed"

    print("✓ Test 3: before_send_filter removes sensitive data")


def test_set_tag():
    """Test that set_tag works without error."""
    from src.utils.sentry_config import set_tag

    # Should not raise even if Sentry is not initialized
    try:
        set_tag("test_key", "test_value")
        print("✓ Test 4: set_tag works without error")
    except Exception as e:
        print(f"✗ Test 4 failed: {e}")
        raise


def test_set_context():
    """Test that set_context works without error."""
    from src.utils.sentry_config import set_context

    try:
        set_context("test", {"key": "value"})
        print("✓ Test 5: set_context works without error")
    except Exception as e:
        print(f"✗ Test 5 failed: {e}")
        raise


def test_capture_exception():
    """Test that capture_exception works without error."""
    from src.utils.sentry_config import capture_exception

    try:
        # Create a test exception
        exc = ValueError("Test exception")
        event_id = capture_exception(exc)
        # Should return None when Sentry is not initialized
        # But should not raise
        print("✓ Test 6: capture_exception works without error")
    except Exception as e:
        print(f"✗ Test 6 failed: {e}")
        raise


def test_capture_message():
    """Test that capture_message works without error."""
    from src.utils.sentry_config import capture_message

    try:
        capture_message("Test message")
        print("✓ Test 7: capture_message works without error")
    except Exception as e:
        print(f"✗ Test 7 failed: {e}")
        raise


def test_logging_config_with_sentry():
    """Test that logging setup works with Sentry integration."""
    from src.utils.logging_config import setup_logging
    import logging

    # Clear any existing handlers
    root_logger = logging.getLogger()
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)

    # Setup logging with Sentry (should not fail even if Sentry is not available)
    try:
        setup_logging(init_sentry=True)
        print("✓ Test 8: setup_logging with Sentry integration works")
    except Exception as e:
        print(f"✗ Test 8 failed: {e}")
        raise


def test_set_user_context():
    """Test that set_user_context works without error."""
    from src.utils.sentry_config import set_user_context

    try:
        set_user_context(user_id="test123", username="testuser")
        print("✓ Test 9: set_user_context works without error")
    except Exception as e:
        print(f"✗ Test 9 failed: {e}")
        raise


def run_all_tests():
    """Run all tests."""
    print("\n" + "=" * 50)
    print("Testing Sentry Configuration")
    print("=" * 50 + "\n")

    tests = [
        test_init_without_dsn,
        test_init_with_placeholder_dsn,
        test_before_send_filter,
        test_set_tag,
        test_set_context,
        test_capture_exception,
        test_capture_message,
        test_logging_config_with_sentry,
        test_set_user_context,
    ]

    passed = 0
    failed = 0

    for test in tests:
        try:
            test()
            passed += 1
        except Exception as e:
            failed += 1
            print(f"✗ {test.__name__} failed: {e}")

    print("\n" + "=" * 50)
    print(f"Results: {passed} passed, {failed} failed")
    print("=" * 50 + "\n")

    return failed == 0


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
