"""
Tests for SQL validation.
"""
import pytest
from src.utils.validation import SQLValidator


@pytest.fixture
def validator():
    return SQLValidator(max_rows=1000)


def test_valid_select_query(validator):
    """Test that valid SELECT query passes."""
    query = "SELECT * FROM table WHERE ano = 2024 LIMIT 100"
    result = validator.validate(query)
    assert result["is_valid"]
    assert len(result["errors"]) == 0


def test_forbidden_keywords_detected(validator):
    """Test that forbidden keywords are blocked."""
    query = "DROP TABLE users"
    result = validator.validate(query)
    assert not result["is_valid"]
    assert "DROP" in " ".join(result["errors"])


def test_delete_blocked(validator):
    """Test that DELETE is blocked."""
    query = "DELETE FROM table WHERE ano = 2024"
    result = validator.validate(query)
    assert not result["is_valid"]


def test_limit_auto_added(validator):
    """Test that LIMIT is added automatically."""
    query = "SELECT * FROM table WHERE ano = 2024"
    result = validator.validate(query)
    assert "LIMIT 1000" in result["sanitized_query"]


def test_sql_injection_pattern_detection(validator):
    """Test SQL injection pattern detection."""
    query = "SELECT * FROM users WHERE id = 1 OR 1=1"
    result = validator.validate(query)
    assert len(result["warnings"]) > 0


def test_valid_with_cte(validator):
    """Test that WITH (CTE) queries are allowed."""
    query = "WITH cte AS (SELECT * FROM table) SELECT * FROM cte LIMIT 100"
    result = validator.validate(query)
    assert result["is_valid"]


def test_valid_subquery(validator):
    """Test that subqueries starting with parentheses are allowed."""
    query = "(SELECT * FROM table) LIMIT 100"
    result = validator.validate(query)
    assert result["is_valid"]


def test_missing_limit_adds_warning(validator):
    """Test that missing LIMIT adds a warning."""
    query = "SELECT * FROM table WHERE ano = 2024"
    result = validator.validate(query)
    assert len(result["warnings"]) > 0
    assert "LIMIT" in result["warnings"][0]


def test_missing_where_adds_warning(validator):
    """Test that missing WHERE adds a warning."""
    query = "SELECT * FROM table LIMIT 100"
    result = validator.validate(query)
    assert len(result["warnings"]) > 0
    assert any("WHERE" in w for w in result["warnings"])
