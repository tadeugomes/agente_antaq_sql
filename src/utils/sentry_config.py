"""
Sentry configuration for error monitoring and performance tracking.
"""
import os
from typing import Optional

import sentry_sdk
from sentry_sdk.integrations.logging import LoggingIntegration
from sentry_sdk.integrations.stdlib import StdlibIntegration


def init_sentry(
    dsn: Optional[str] = None,
    environment: Optional[str] = None,
    traces_sample_rate: Optional[float] = None,
    debug: bool = False
) -> bool:
    """
    Initialize Sentry SDK for error monitoring.

    Args:
        dsn: Sentry DSN (defaults to SENTRY_DSN env var)
        environment: Environment name (defaults to SENTRY_ENVIRONMENT env var)
        traces_sample_rate: Sample rate for performance tracing (0-1)
        debug: Enable debug mode for Sentry

    Returns:
        True if Sentry was initialized, False otherwise
    """
    dsn = dsn or os.getenv("SENTRY_DSN")
    if not dsn or dsn == "your-sentry-dsn-here":
        # Sentry not configured, skip initialization
        return False

    environment = environment or os.getenv("SENTRY_ENVIRONMENT", "development")

    # Parse traces_sample_rate from env if not provided
    if traces_sample_rate is None:
        traces_sample_rate_str = os.getenv("SENTRY_TRACES_SAMPLE_RATE", "0.1")
        try:
            traces_sample_rate = float(traces_sample_rate_str)
        except ValueError:
            traces_sample_rate = 0.1

    # Configure Sentry integrations
    logging_integration = LoggingIntegration(
        level=logging.INFO,  # Capture info and above as breadcrumbs
        event_level=logging.ERROR  # Send only errors as events
    )

    sentry_sdk.init(
        dsn=dsn,
        environment=environment,
        traces_sample_rate=traces_sample_rate,
        debug=debug,
        integrations=[
            logging_integration,
            StdlibIntegration(),
        ],
        # Filter sensitive data
        before_send_transaction=before_send_transaction_filter,
        before_send=before_send_filter,
        # Ignore specific errors
        ignore_errors=[
            KeyboardInterrupt,
            SystemExit,
        ],
    )

    return True


def before_send_filter(event, hint):
    """
    Filter events before sending to Sentry.

    Removes sensitive data like passwords, API keys, tokens, etc.
    """
    # Filter request data
    if "request" in event:
        request = event["request"]
        # Filter headers (case-insensitive matching)
        if "headers" in request:
            headers = request["headers"]
            for header in ["authorization", "cookie", "set-cookie"]:
                # Check both lowercase and original case
                if header in headers:
                    headers[header] = "[FILTERED]"
                # Also check for uppercase variants
                for key in list(headers.keys()):
                    if key.lower() == header:
                        headers[key] = "[FILTERED]"

    # Filter extra data
    if "extra" in event:
        extra = event["extra"]
        for key in list(extra.keys()):
            if any(sensitive in key.lower() for sensitive in
                   ["password", "secret", "token", "api_key", "apikey", "credential"]):
                extra[key] = "[FILTERED]"

    # Filter user data
    if "user" in event and event["user"]:
        user = event["user"]
        for sensitive_key in ["email", "ip_address", "password"]:
            if sensitive_key in user:
                del user[sensitive_key]

    return event


def before_send_transaction_filter(event, hint):
    """
    Filter transaction events before sending to Sentry.
    """
    # Filter sensitive query parameters
    if "request" in event and "query_string" in event["request"]:
        # You can add specific query params to filter here
        pass

    return event


def set_user_context(
    user_id: Optional[str] = None,
    username: Optional[str] = None,
    email: Optional[str] = None,
    **kwargs
) -> None:
    """
    Set user context for Sentry events.

    Args:
        user_id: User identifier
        username: Username
        email: User email (will be filtered)
        **kwargs: Additional user data
    """
    user_data = {}

    if user_id:
        user_data["id"] = user_id
    if username:
        user_data["username"] = username
    # Email is filtered in before_send_filter, but we don't store it

    user_data.update(kwargs)

    if user_data:
        sentry_sdk.set_user(user_data)


def set_tag(key: str, value: str) -> None:
    """
    Set a tag for Sentry events.

    Args:
        key: Tag key
        value: Tag value
    """
    sentry_sdk.set_tag(key, value)


def set_context(key: str, value: dict) -> None:
    """
    Set additional context for Sentry events.

    Args:
        key: Context key
        value: Context data
    """
    sentry_sdk.set_context(key, value)


def capture_exception(exception: Exception, level: str = "error") -> str:
    """
    Capture an exception and send to Sentry.

    Args:
        exception: The exception to capture
        level: Event level (error, warning, info)

    Returns:
        Event ID
    """
    return sentry_sdk.capture_exception(exception)


def capture_message(message: str, level: str = "info") -> str:
    """
    Capture a message and send to Sentry.

    Args:
        message: The message to capture
        level: Event level (error, warning, info)

    Returns:
        Event ID
    """
    return sentry_sdk.capture_message(message, level=level)


# Import logging for the LoggingIntegration
import logging
