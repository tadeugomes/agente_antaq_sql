"""
Result formatting utilities.
"""
import json
from typing import List, Dict, Any


def enrich_results_with_mercadoria_names(results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Enrich query results with mercadoria names instead of codes.

    Args:
        results: Query results

    Returns:
        Enriched results with mercadoria names
    """
    if not results:
        return results

    # Collect unique mercadoria codes
    mercadoria_codes = set()
    for row in results:
        if 'cdmercadoria' in row and row['cdmercadoria']:
            mercadoria_codes.add(str(row['cdmercadoria']))

    if not mercadoria_codes:
        return results

    # Batch lookup mercadoria names
    try:
        from src.bigquery.referential_helper import get_referential_helper
        helper = get_referential_helper()
        nome_map = helper.batch_get_mercadoria_nomes(list(mercadoria_codes))

        # Create enriched results
        enriched = []
        for row in results:
            new_row = dict(row)
            if 'cdmercadoria' in row and row['cdmercadoria']:
                code = str(row['cdmercadoria'])
                nome = nome_map.get(code, code)
                # Add formatted column with both code and name
                new_row['mercadoria_nome'] = f"{nome} ({code})" if nome != code else code
            enriched.append(new_row)

        return enriched
    except Exception as e:
        # If enrichment fails, return original results
        import logging
        logging.warning(f"Could not enrich mercadoria names: {e}")
        return results


def format_results_for_llm(results: List[Dict[str, Any]], enrich: bool = True) -> str:
    """
    Format query results for LLM consumption.
    Optionally enriches mercadoria codes with names.

    Args:
        results: Query results
        enrich: Whether to enrich mercadoria codes with names

    Returns:
        Formatted string
    """
    if not results:
        return "Nenhum resultado encontrado."

    # Enrich results with mercadoria names if requested
    if enrich:
        results = enrich_results_with_mercadoria_names(results)

    if len(results) > 100:
        results = results[:100]
        header = f"Primeiros 100 de {len(results)} resultados:\n"
    else:
        header = f"{len(results)} resultados:\n"

    # Format as table
    lines = [header]

    # Get headers - use mercadoria_nome if available
    headers = list(results[0].keys())
    # Prefer mercadoria_nome over cdmercadoria for display
    if 'mercadoria_nome' in headers:
        headers.remove('cdmercadoria')

    lines.append(" | ".join(headers))
    lines.append("-" * min(100, len(" | ".join(headers))))

    # Add rows
    for row in results[:20]:  # Limit to 20 rows for display
        values = []
        for h in headers:
            val = row.get(h, "")
            # Truncate long values
            val_str = str(val)[:50] if val is not None else ""
            values.append(val_str)
        lines.append(" | ".join(values))

    if len(results) > 20:
        lines.append(f"... e mais {len(results) - 20} linhas")

    return "\n".join(lines)


def format_results_for_display(results: List[Dict[str, Any]]) -> str:
    """
    Format results for Streamlit display.

    Args:
        results: Query results

    Returns:
        Formatted string
    """
    if not results:
        return "Nenhum resultado encontrado."

    return json.dumps(results, indent=2, ensure_ascii=False, default=str)


def format_sql_query(query: str) -> str:
    """
    Format SQL query for display.

    Args:
        query: SQL query

    Returns:
        Formatted query
    """
    # Basic formatting
    query = query.strip()

    # Normalize whitespace
    import re
    query = re.sub(r'\s+', ' ', query)

    # Add newlines before keywords
    keywords = ["SELECT", "FROM", "WHERE", "GROUP BY", "ORDER BY", "HAVING", "LIMIT"]
    for kw in keywords:
        query = re.sub(rf'\b{kw}\b', f'\n{kw}', query, flags=re.IGNORECASE)

    return query.strip()
