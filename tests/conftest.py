"""
Pytest configuration for ANTAQ AI Agent tests.
"""
import os
import sys

# Add src to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest


@pytest.fixture
def sample_sql_query():
    """Sample SQL query for testing."""
    return "SELECT nm_porto, SUM(peso_carga) FROM `antaqdados.br_antaq_estatistico_aquaviario.v_carga_oficial_antaq` WHERE ano = 2024 GROUP BY nm_porto LIMIT 10"


@pytest.fixture
def sample_question():
    """Sample question for testing."""
    return "Qual foi o total de carga movimentado em 2024?"


@pytest.fixture
def sample_results():
    """Sample query results for testing."""
    return [
        {"nm_porto": "Santos", "carga_total": 50000000},
        {"nm_porto": "Itaguaí", "carga_total": 30000000},
    ]
