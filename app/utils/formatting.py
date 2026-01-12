"""
Formatting utilities for displaying data in a user-friendly way.
Translates technical column names to friendly Portuguese names.
"""

# Mapping of technical column names to user-friendly Portuguese names
COLUMN_FRIENDLY_NAMES = {
    # Metrics
    "vlpesocargabruta_oficial": "Carga (toneladas)",
    "pesocarga": "Peso da Carga (t)",
    "teu": "TEU (Contêineres)",
    "unidade_carga": "Unidade de Carga",

    # Identification
    "cdmercadoria": "Mercadoria",
    "cdnaturezacarga": "Natureza da Carga",
    "idcarga": "ID da Carga",
    "idotizacao": "ID da Atracação",

    # Location
    "porto_atracacao": "Porto",
    "uf": "Estado (UF)",
    "regiao_geografica": "Região Geográfica",
    "instalacao_origem": "Instalação de Origem",
    "instalacao_destino": "Instalação de Destino",
    "origem": "Origem",
    "destino": "Destino",

    # Temporal
    "ano": "Ano",
    "mes": "Mês",
    "dataatracacao": "Data da Atracação",
    "periodo": "Período",

    # Operation
    "sentido": "Sentido",
    "tipo_de_navegacao_da_atracacao": "Tipo de Navegação",
    "tipo_operacao_da_carga": "Tipo de Operação",
    "nacionalidade_armador": "Nacionalidade do Armador",
    "nome_navegacao": "Nome da Embarcação",

    # Validation
    "isValidoMetodologiaANTAQ": "Válido pela Metodologia ANTAQ",
}

# Mapping for sentido values
SENTIDO_FRIENDLY_NAMES = {
    "Embarcados": "Exportação",
    "Desembarcados": "Importação",
}

# Mapping for tipo_de_navegacao values
NAVEGACAO_FRIENDLY_NAMES = {
    "Longo Curso": "Longo Curso (Internacional)",
    "Cabotagem": "Cabotagem (Nacional)",
    "Interior": "Navegação Interior",
    "Apoio": "Navegação de Apoio",
}

# User-friendly error messages
ERROR_MESSAGES = {
    "timeout": "A consulta está demorando mais que o esperado. Tente novamente.",
    "connection": "Não foi possível conectar ao servidor. Verifique sua conexão.",
    "no_data": "Nenhum dado encontrado para os filtros selecionados.",
    "invalid_query": "A consulta não pôde ser processada. Tente reformular sua pergunta.",
    "default": "Ocorreu um erro ao processar sua solicitação. Tente novamente.",
}


def get_friendly_column_name(column_name: str) -> str:
    """
    Get user-friendly Portuguese name for a technical column name.

    Args:
        column_name: Technical column name from BigQuery

    Returns:
        User-friendly Portuguese name, or original if not found
    """
    return COLUMN_FRIENDLY_NAMES.get(column_name, column_name)


def get_friendly_sentido(sentido: str) -> str:
    """
    Get user-friendly name for sentido (import/export direction).

    Args:
        sentido: Original sentido value ("Embarcados" or "Desembarcados")

    Returns:
        User-friendly name
    """
    return SENTIDO_FRIENDLY_NAMES.get(sentido, sentido)


def get_friendly_navegacao(navegacao: str) -> str:
    """
    Get user-friendly name for navigation type.

    Args:
        navegacao: Original navigation type value

    Returns:
        User-friendly name
    """
    return NAVEGACAO_FRIENDLY_NAMES.get(navegacao, navegacao)


def format_number(value: float, decimals: int = 1) -> str:
    """
    Format a number for display with thousands separator.

    Args:
        value: Numeric value to format
        decimals: Number of decimal places

    Returns:
        Formatted number string (e.g., "1.23M", "123.5mil", "1.234")
    """
    if value is None or (isinstance(value, float) and value != value):  # NaN check
        return "-"

    try:
        # Convert to float first
        value_float = float(value)

        if abs(value_float) >= 1_000_000:
            # Use millions suffix (one decimal)
            millions = value_float / 1_000_000
            return f"{millions:.1f}M"
        elif abs(value_float) >= 1_000:
            # Use thousands suffix (one decimal)
            thousands = value_float / 1_000
            return f"{thousands:.1f}mil"
        else:
            # Just format with decimals
            return f"{value_float:.{decimals}f}".replace(".", ",")

    except (ValueError, TypeError):
        return str(value)


def format_number_full(value: float) -> str:
    """
    Format a number with full thousands separator.

    Args:
        value: Numeric value to format

    Returns:
        Formatted number string (e.g., "1.234.567")
    """
    if value is None or (isinstance(value, float) and value != value):
        return "-"

    try:
        # Format as integer if it's a whole number, otherwise with decimals
        value_float = float(value)
        if value_float == int(value_float):
            return f"{int(value_float):,}".replace(",", ".")
        else:
            return f"{value_float:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    except (ValueError, TypeError):
        return str(value)


def format_percentage(value: float, decimals: int = 1) -> str:
    """
    Format a percentage value.

    Args:
        value: Numeric value (e.g., 0.085 for 8.5%)
        decimals: Number of decimal places

    Returns:
        Formatted percentage string (e.g., "+8,5%")
    """
    if value is None or (isinstance(value, float) and value != value):
        return "-"

    try:
        value_float = float(value) * 100  # Convert to percentage
        sign = "+" if value_float > 0 else ""
        return f"{sign}{value_float:.{decimals}f}%".replace(".", ",")
    except (ValueError, TypeError):
        return str(value)


def format_month(month: int) -> str:
    """
    Format month number to Portuguese name.

    Args:
        month: Month number (1-12)

    Returns:
        Portuguese month name
    """
    months = [
        "Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho",
        "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"
    ]
    return months[month - 1] if 1 <= month <= 12 else str(month)


def get_error_message(error_type: str) -> str:
    """
    Get user-friendly error message.

    Args:
        error_type: Type of error ("timeout", "connection", etc.)

    Returns:
        User-friendly error message
    """
    return ERROR_MESSAGES.get(error_type, ERROR_MESSAGES["default"])


def sanitize_dataframe(df, columns_map: dict = None) -> dict:
    """
    Sanitize a dataframe by renaming columns to friendly names.

    Args:
        df: DataFrame to sanitize
        columns_map: Optional custom column mapping (uses default if None)

    Returns:
        Dictionary with sanitized data ready for display
    """
    import pandas as pd

    if df is None or df.empty:
        return {"columns": [], "rows": []}

    # Use provided mapping or default
    mapping = columns_map or COLUMN_FRIENDLY_NAMES

    # Rename columns
    df_renamed = df.rename(columns=mapping)

    # Convert to list of dicts for display
    result = {
        "columns": df_renamed.columns.tolist(),
        "rows": df_renamed.to_dict(orient="records")
    }

    return result
