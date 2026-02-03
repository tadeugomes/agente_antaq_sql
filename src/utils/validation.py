"""
SQL validation and security utilities.
"""
import re
import unicodedata
from typing import Dict, List, Any


class SQLValidator:
    """
    Validate SQL queries for security and correctness.
    """

    # Forbidden SQL keywords
    FORBIDDEN_KEYWORDS = [
        "DROP", "DELETE", "UPDATE", "INSERT", "CREATE",
        "ALTER", "TRUNCATE", "GRANT", "REVOKE", "EXECUTE",
        "CALL", "MERGE", "REPLACE"
    ]

    # Allowed query patterns
    ALLOWED_PREFIXES = ["SELECT", "WITH", "(", "SHOW", "DESCRIBE", "DESC"]

    def __init__(self, max_rows: int = 1000):
        self.max_rows = max_rows

    def validate(self, query: str) -> Dict[str, Any]:
        """
        Comprehensive SQL validation.

        Args:
            query: SQL query to validate

        Returns:
            Dictionary with validation results
        """
        errors = []
        warnings = []
        sanitized_query = query.strip()
        sanitized_query = self._normalize_tipo_carga(sanitized_query)
        sanitized_query = self._normalize_portos_do_parana(sanitized_query)
        sanitized_query = self._normalize_porto_like(sanitized_query)
        sanitized_query = self._normalize_terminal_like(sanitized_query)
        sanitized_query = self._normalize_porto_like_accent_insensitive(sanitized_query)

        # Check for forbidden keywords
        forbidden_found = self._check_forbidden_keywords(sanitized_query)
        if forbidden_found:
            errors.append(
                f"Comandos não permitidos encontrados: {', '.join(forbidden_found)}"
            )

        # Check if query starts with allowed prefix
        if not self._check_allowed_prefix(sanitized_query):
            errors.append(
                "Query deve começar com SELECT, WITH, ou SHOW"
            )

        # Check for LIMIT clause
        if not self._has_limit(sanitized_query):
            warnings.append(
                "Query sem LIMIT pode retornar muitos registros. "
                f"Adicionando LIMIT {self.max_rows}"
            )
            sanitized_query = self._add_limit(sanitized_query)

        # Check for potential SQL injection patterns
        injection_patterns = self._check_injection_patterns(sanitized_query)
        if injection_patterns:
            warnings.append(
                f"Padrões suspeitos detectados: {', '.join(injection_patterns)}"
            )

        # Check for required WHERE clause (for performance)
        if not self._has_where(sanitized_query) and "FROM" in sanitized_query.upper():
            warnings.append(
                "Query sem WHERE pode fazer table scan. "
                "Recomendado adicionar filtro de ano."
            )

        return {
            "is_valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings,
            "sanitized_query": sanitized_query
        }

    def _normalize_porto_like(self, query: str) -> str:
        """
        Normalize port name filters in LIKE patterns.

        Example:
        LOWER(porto_atracacao) LIKE '%porto de itaqui%' -> '%itaqui%'
        """
        pattern = re.compile(
            r"(LIKE\s+')%?porto\s+(?:de|da|do)\s+([^%']+?)%?(')",
            flags=re.IGNORECASE
        )

        def repl(match: re.Match) -> str:
            name = match.group(2).strip()
            return f"{match.group(1)}%{name}%{match.group(3)}"

        return pattern.sub(repl, query)

    def _normalize_terminal_like(self, query: str) -> str:
        """
        Normalize terminal-related filters in LIKE patterns for porto_atracacao.

        Example:
        LOWER(porto_atracacao) LIKE '%terminais de santos%' -> '%santos%'
        """
        pattern = re.compile(
            r"((?:LOWER\()?\s*[\w\.]*porto_atracacao\)?\s+LIKE\s+')([^']+)(')",
            flags=re.IGNORECASE
        )

        def repl(match: re.Match) -> str:
            raw = match.group(2)
            cleaned = re.sub(
                r"\b(terminal(?:es)?|porto|portuário(?:s)?)\b",
                " ",
                raw,
                flags=re.IGNORECASE
            )
            cleaned = re.sub(r"\b(?:de|da|do)\b", " ", cleaned, flags=re.IGNORECASE)
            cleaned = " ".join(cleaned.split()).strip("%")
            if not cleaned:
                return match.group(0)
            return f"{match.group(1)}%{cleaned}%{match.group(3)}"

        return pattern.sub(repl, query)

    def _normalize_tipo_carga(self, query: str) -> str:
        """
        Normalize common "tipo de carga" column names to natureza_carga.

        Example:
        SELECT tipo_carga -> SELECT natureza_carga
        """
        pattern = re.compile(
            r"\b(tipo_carga|tipo_de_carga|tipo_da_carga)\b",
            flags=re.IGNORECASE
        )
        return pattern.sub("natureza_carga", query)

    def _normalize_portos_do_parana(self, query: str) -> str:
        """
        Normalize "Portos do Paraná" queries to include Paranaguá and Antonina.

        Example:
        LOWER(porto_atracacao) LIKE '%portos do parana%' ->
        (LOWER(porto_atracacao) LIKE '%paranagua%' OR LOWER(porto_atracacao) LIKE '%antonina%')
        """
        pattern = re.compile(
            r"(?P<field>(?:LOWER\()?\s*[\w\.]*porto_atracacao\)?)\s+LIKE\s+'(?P<value>[^']+)'",
            flags=re.IGNORECASE
        )

        def repl(match: re.Match) -> str:
            field_expr = match.group("field").strip()
            value_raw = match.group("value")
            value_norm = value_raw.lower().replace("á", "a").replace("ã", "a")
            if re.search(r"\bportos?\s+do\s+parana\b", value_norm):
                if not field_expr.lower().startswith("lower("):
                    field_expr = f"LOWER({field_expr})"
                return (
                    f"({field_expr} LIKE '%paranagua%' "
                    f"OR {field_expr} LIKE '%antonina%')"
                )
            return match.group(0)

        return pattern.sub(repl, query)

    def _normalize_porto_like_accent_insensitive(self, query: str) -> str:
        """
        Make porto_atracacao LIKE filters accent-insensitive.

        Example:
        LOWER(porto_atracacao) LIKE '%paranagua%' ->
        REGEXP_REPLACE(NORMALIZE(LOWER(porto_atracacao), NFD), r'\\pM', '') LIKE '%paranagua%'
        """
        pattern = re.compile(
            r"(?P<field>(?:LOWER\()?\s*[\w\.]*porto_atracacao\)?)\s+LIKE\s+'(?P<value>[^']*)'",
            flags=re.IGNORECASE
        )

        def strip_accents(text: str) -> str:
            return "".join(
                ch for ch in unicodedata.normalize("NFD", text)
                if unicodedata.category(ch) != "Mn"
            )

        def repl(match: re.Match) -> str:
            field_expr = match.group("field").strip()
            value = match.group("value")

            if field_expr.lower().startswith("lower(") and field_expr.endswith(")"):
                field_expr = field_expr[6:-1]

            normalized_field = (
                "REGEXP_REPLACE(NORMALIZE(LOWER("
                + field_expr
                + "), NFD), r'\\pM', '')"
            )
            normalized_value = strip_accents(value)
            return f"{normalized_field} LIKE '{normalized_value}'"

        return pattern.sub(repl, query)

    def _check_forbidden_keywords(self, query: str) -> List[str]:
        """Check for forbidden SQL keywords."""
        query_upper = query.upper()
        found = []

        for keyword in self.FORBIDDEN_KEYWORDS:
            pattern = rf"\b{keyword}\b"
            if re.search(pattern, query_upper):
                found.append(keyword)

        return found

    def _check_allowed_prefix(self, query: str) -> bool:
        """Check if query starts with allowed prefix."""
        query_upper = query.upper().strip()

        for prefix in self.ALLOWED_PREFIXES:
            if query_upper.startswith(prefix):
                return True

        return False

    def _has_limit(self, query: str) -> bool:
        """Check if query has LIMIT clause."""
        return "LIMIT" in query.upper()

    def _add_limit(self, query: str) -> str:
        """Add LIMIT clause to query."""
        # Remove trailing semicolon if present
        query = query.rstrip(";").strip()

        # Add LIMIT
        return f"{query}\nLIMIT {self.max_rows}"

    def _has_where(self, query: str) -> bool:
        """Check if query has WHERE clause."""
        return "WHERE" in query.upper()

    def _check_injection_patterns(self, query: str) -> List[str]:
        """Check for potential SQL injection patterns."""
        patterns = [
            r"';",           # Statement termination
            r"--",           # SQL comment
            r"/\*",          # Multi-line comment start
            r"\bor\s+1\s*=\s*1\b",  # Always true condition
            r"\bxor\b",      # XOR operator
            r"union.*select", # UNION injection
        ]

        found = []
        query_lower = query.lower()

        for pattern in patterns:
            if re.search(pattern, query_lower, re.IGNORECASE):
                found.append(pattern)

        return found


# Singleton instance
_validator_instance: SQLValidator | None = None


def get_sql_validator() -> SQLValidator:
    """Get or create singleton SQLValidator instance."""
    global _validator_instance
    if _validator_instance is None:
        _validator_instance = SQLValidator()
    return _validator_instance
