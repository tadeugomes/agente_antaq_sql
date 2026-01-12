"""
Additional security utilities.
"""
import os
from typing import Dict, Optional


def get_credentials_path() -> Optional[str]:
    """
    Get Google Cloud credentials path from environment.

    Returns:
        Path to credentials file or None
    """
    return os.getenv("GOOGLE_APPLICATION_CREDENTIALS")


def validate_environment() -> Dict[str, bool]:
    """
    Validate required environment variables.

    Returns:
        Dictionary of validation results
    """
    required_vars = [
        "GOOGLE_CLOUD_PROJECT",
        "ANTAQ_DATASET"
    ]

    results = {}
    for var in required_vars:
        results[var] = bool(os.getenv(var))

    return results


def sanitize_input(text: str) -> str:
    """
    Basic input sanitization.

    Args:
        text: Input text

    Returns:
        Sanitized text
    """
    # Remove null bytes
    text = text.replace("\x00", "")

    # Limit length
    max_length = 10000
    if len(text) > max_length:
        text = text[:max_length]

    return text.strip()
