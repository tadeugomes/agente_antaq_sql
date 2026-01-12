#!/usr/bin/env python3
"""
Test script for new metadata tools
Tests explain_column, search_columns, get_official_filters, suggest_query_template
"""
import os
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv
load_dotenv()

from src.agent.tools import (
    explain_column,
    search_columns,
    get_official_filters,
    suggest_query_template
)

print("=" * 70)
print("🧪 TESTING METADATA TOOLS")
print("=" * 70)

# =============================================================================
# Test 1: explain_column
# =============================================================================
print("\n" + "=" * 70)
print("TEST 1: explain_column")
print("=" * 70)

print("\n--- Test 1a: Explain vlpesocargabruta_oficial ---")
result = explain_column.invoke({
    "table": "v_carga_metodologia_oficial",
    "column": "vlpesocargabruta_oficial"
})
print(result)

print("\n--- Test 1b: Explain sentido ---")
result = explain_column.invoke({
    "table": "v_carga_metodologia_oficial",
    "column": "sentido"
})
print(result)

print("\n--- Test 1c: Explain non-existent column ---")
result = explain_column.invoke({
    "table": "v_carga_metodologia_oficial",
    "column": "coluna_inexistente"
})
print(result)

# =============================================================================
# Test 2: search_columns
# =============================================================================
print("\n" + "=" * 70)
print("TEST 2: search_columns")
print("=" * 70)

print("\n--- Test 2a: Search for 'peso' ---")
result = search_columns.invoke({"keywords": "peso"})
print(result)

print("\n--- Test 2b: Search for 'porto exportação' ---")
result = search_columns.invoke({"keywords": "porto exportação"})
print(result)

print("\n--- Test 2c: Search for 'data temporal' ---")
result = search_columns.invoke({"keywords": "data temporal"})
print(result)

# =============================================================================
# Test 3: get_official_filters
# =============================================================================
print("\n" + "=" * 70)
print("TEST 3: get_official_filters")
print("=" * 70)

result = get_official_filters.invoke({})
print(result)

# =============================================================================
# Test 4: suggest_query_template
# =============================================================================
print("\n" + "=" * 70)
print("TEST 4: suggest_query_template")
print("=" * 70)

print("\n--- Test 4a: Suggest 'ranking de portos' ---")
result = suggest_query_template.invoke({"intent": "ranking de portos"})
print(result)

print("\n--- Test 4b: Suggest 'evolução mensal de carga' ---")
result = suggest_query_template.invoke({"intent": "evolução mensal de carga"})
print(result)

print("\n--- Test 4c: Suggest 'análise de peso por mercadoria' ---")
result = suggest_query_template.invoke({"intent": "análise de peso por mercadoria"})
print(result)

print("\n--- Test 4d: Suggest 'unknown intent' ---")
result = suggest_query_template.invoke({"intent": "algo que não existe"})
print(result)

# =============================================================================
# Summary
# =============================================================================
print("\n" + "=" * 70)
print("✅ ALL TESTS COMPLETED")
print("=" * 70)
