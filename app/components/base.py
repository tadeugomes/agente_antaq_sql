"""
Reusable UI components for the ANTAQ Streamlit app.
Provides consistent, styled components for common UI patterns.
"""
import streamlit as st
from typing import Optional, Any, List, Dict
import pandas as pd
from .styles import Colors, Icons, get_metric_html, get_info_box_html, get_loading_html


# =============================================================================
# Metric Components
# =============================================================================

def metric_card(
    value: str,
    label: str,
    delta: Optional[str] = None,
    icon: str = Icons.CHART,
    color: str = None
) -> None:
    """
    Display a metric card with icon, value, label, and optional delta.

    Args:
        value: Main value to display (e.g., "12.5M")
        label: Label describing the metric
        delta: Optional change indicator (e.g., "+8.5%")
        icon: Icon emoji or character
        color: Optional color override for the value
    """
    delta_html = ""
    if delta:
        delta_class = "positive" if "+" in str(delta) else ("negative" if "-" in str(delta) else "neutral")
        delta_html = f'<div class="metric-delta {delta_class}">{delta}</div>'

    color_style = f'color: {color};' if color else ""

    st.markdown(f"""
    <div class="overview-metric">
        <div class="metric-icon">{icon}</div>
        <div class="metric-value" style="{color_style}">{value}</div>
        <div class="metric-label">{label}</div>
        {delta_html}
    </div>
    """, unsafe_allow_html=True)


def metric_row(metrics: List[Dict[str, Any]]) -> None:
    """
    Display a row of metric cards.

    Args:
        metrics: List of metric dictionaries with keys:
                 - value: Main value to display
                 - label: Label describing the metric
                 - delta: Optional change indicator
                 - icon: Optional icon (default: Icons.CHART)
                 - color: Optional color override
    """
    cols = st.columns(len(metrics))
    for col, metric in zip(cols, metrics):
        with col:
            metric_card(
                value=metric.get("value", "-"),
                label=metric.get("label", ""),
                delta=metric.get("delta"),
                icon=metric.get("icon", Icons.CHART),
                color=metric.get("color")
            )


# =============================================================================
# Info Box Components
# =============================================================================

def info_box(
    title: str,
    content: str,
    box_type: str = "info",
    icon: str = None
) -> None:
    """
    Display an info box with title and content.

    Args:
        title: Box title
        content: Box content
        box_type: Type of box ("info", "success", "warning", "error")
        icon: Optional icon override
    """
    icons = {
        "info": Icons.INFO,
        "success": Icons.SUCCESS,
        "warning": Icons.WARNING,
        "error": Icons.ERROR,
    }
    icon_html = icon or icons.get(box_type, Icons.INFO)

    st.markdown(f"""
    <div class="info-box {box_type}">
        <strong>{icon_html} {title}</strong><br>
        {content}
    </div>
    """, unsafe_allow_html=True)


def status_banner(
    message: str,
    status: str = "info",
    icon: str = None
) -> None:
    """
    Display a status banner message.

    Args:
        message: Message to display
        status: Status type ("info", "success", "warning", "error")
        icon: Optional icon override
    """
    icons = {
        "info": Icons.INFO,
        "success": Icons.SUCCESS,
        "warning": Icons.WARNING,
        "error": Icons.ERROR,
    }
    icon_html = icon or icons.get(status, Icons.INFO)

    st.markdown(f"""
    <div class="data-status">
        <span class="status-icon">{icon_html}</span>
        <span class="status-text">{message}</span>
    </div>
    """, unsafe_allow_html=True)


# =============================================================================
# Loading Components
# =============================================================================

def loading_spinner(message: str = "Carregando...") -> None:
    """
    Display a centered loading spinner with message.

    Args:
        message: Message to display below the spinner
    """
    st.markdown(get_loading_html(message), unsafe_allow_html=True)


def loading_state(message: str = "Processando..."):
    """
    Context manager for showing a loading state.

    Args:
        message: Message to display while loading

    Usage:
        with loading_state("Carregando dados..."):
            # Do expensive operation
            data = fetch_data()
    """
    return st.status(message, expanded=False)


# =============================================================================
# Data Table Components
# =============================================================================

def data_table(
    data: pd.DataFrame,
    columns: Dict[str, str] = None,
    hide_index: bool = True,
    use_container_width: bool = True
) -> None:
    """
    Display a styled data table with optional column renaming.

    Args:
        data: DataFrame to display
        columns: Optional mapping of column names to friendly names
        hide_index: Whether to hide the index column
        use_container_width: Whether to use full container width
    """
    if data is None or data.empty:
        info_box("Sem Dados", "Nenhum dado disponível para exibir.", "warning")
        return

    # Rename columns if mapping provided
    if columns:
        data = data.rename(columns=columns)

    st.dataframe(
        data,
        use_container_width=use_container_width,
        hide_index=hide_index
    )


def friendly_table(
    data: pd.DataFrame,
    use_container_width: bool = True
) -> None:
    """
    Display a table with user-friendly column names.

    Args:
        data: DataFrame to display
        use_container_width: Whether to use full container width
    """
    from ..utils.formatting import COLUMN_FRIENDLY_NAMES

    # Filter column mapping to only include columns that exist in the data
    columns_map = {
        col: COLUMN_FRIENDLY_NAMES[col]
        for col in data.columns
        if col in COLUMN_FRIENDLY_NAMES
    }

    data_table(data, columns_map, use_container_width=use_container_width)


# =============================================================================
# Card Components
# =============================================================================

def card(title: str, content: str = None, icon: str = None) -> None:
    """
    Display a card with title and optional content.

    Args:
        title: Card title
        content: Optional card content (markdown supported)
        icon: Optional icon to display before title
    """
    icon_html = f"{icon} " if icon else ""
    st.markdown(f"""
    <div class="card">
        <div class="card-title">{icon_html}{title}</div>
        {content if content else ""}
    </div>
    """, unsafe_allow_html=True)


# =============================================================================
# Section Components
# =============================================================================

def section(title: str, subtitle: str = None, icon: str = None) -> None:
    """
    Display a section header with title and optional subtitle.

    Args:
        title: Section title
        subtitle: Optional subtitle
        icon: Optional icon to display before title
    """
    icon_html = f"{icon} " if icon else ""
    st.markdown(f"### {icon_html}{title}")
    if subtitle:
        st.markdown(f"<div class='sub-header'>{subtitle}</div>", unsafe_allow_html=True)


def divider() -> None:
    """Display a horizontal section divider."""
    st.markdown("<hr class='section-divider'>", unsafe_allow_html=True)


# =============================================================================
# Button Components
# =============================================================================

def primary_button(
    label: str,
    icon: str = None,
    on_click: callable = None,
    key: str = None,
    use_container_width: bool = True
) -> bool:
    """
    Display a primary action button.

    Args:
        label: Button label
        icon: Optional icon to display before label
        on_click: Optional callback function
        key: Optional unique key for the button
        use_container_width: Whether to use full container width

    Returns:
        True if button was clicked
    """
    label_with_icon = f"{icon} {label}" if icon else label
    return st.button(
        label_with_icon,
        on_click=on_click,
        key=key,
        type="primary",
        use_container_width=use_container_width
    )


def secondary_button(
    label: str,
    icon: str = None,
    on_click: callable = None,
    key: str = None,
    use_container_width: bool = False
) -> bool:
    """
    Display a secondary action button.

    Args:
        label: Button label
        icon: Optional icon to display before label
        on_click: Optional callback function
        key: Optional unique key for the button
        use_container_width: Whether to use full container width

    Returns:
        True if button was clicked
    """
    label_with_icon = f"{icon} {label}" if icon else label
    return st.button(
        label_with_icon,
        on_click=on_click,
        key=key,
        use_container_width=use_container_width
    )


# =============================================================================
# Layout Components
# =============================================================================

def two_column_layout(left_content: callable = None, right_content: callable = None,
                      ratio: List[int] = None) -> None:
    """
    Display a two-column layout.

    Args:
        left_content: Function that renders left column content
        right_content: Function that renders right column content
        ratio: Optional ratio for column widths (default: [1, 1])
    """
    if ratio is None:
        ratio = [1, 1]

    col1, col2 = st.columns(ratio)
    with col1:
        if left_content:
            left_content()
    with col2:
        if right_content:
            right_content()


def three_column_layout(left: callable = None, center: callable = None,
                        right: callable = None, ratio: List[int] = None) -> None:
    """
    Display a three-column layout.

    Args:
        left: Function that renders left column content
        center: Function that renders center column content
        right: Function that renders right column content
        ratio: Optional ratio for column widths (default: [1, 2, 1])
    """
    if ratio is None:
        ratio = [1, 2, 1]

    col1, col2, col3 = st.columns(ratio)
    with col1:
        if left:
            left()
    with col2:
        if center:
            center()
    with col3:
        if right:
            right()


# =============================================================================
# Empty State Components
# =============================================================================

def empty_state(
    title: str = "Nenhum dado encontrado",
    message: str = "Selecione filtros para carregar os dados.",
    icon: str = Icons.BOX
) -> None:
    """
    Display an empty state message.

    Args:
        title: Empty state title
        message: Descriptive message
        icon: Icon to display
    """
    st.markdown(f"""
    <div style="text-align: center; padding: 3rem; color: var(--gray-500);">
        <div style="font-size: 4rem; margin-bottom: 1rem;">{icon}</div>
        <div style="font-size: 1.25rem; font-weight: 600; margin-bottom: 0.5rem; color: var(--gray-700);">
            {title}
        </div>
        <div style="font-size: 1rem;">{message}</div>
    </div>
    """, unsafe_allow_html=True)


# =============================================================================
# Error Components
# =============================================================================

def error_display(
    title: str = "Erro",
    message: str = "Ocorreu um erro inesperado.",
    show_details: bool = False,
    details: str = None
) -> None:
    """
    Display an error message with optional details.

    Args:
        title: Error title
        message: User-friendly error message
        show_details: Whether to show technical details
        details: Technical error details (only shown if show_details=True)
    """
    info_box(title, message, "error")

    if show_details and details:
        with st.expander("Ver detalhes técnicos"):
            st.code(details, language="text")


# =============================================================================
# Header Components
# =============================================================================

def main_header(title: str = "ANTAQ - Dados Aquaviários",
                subtitle: str = None) -> None:
    """
    Display the main application header.

    Args:
        title: Header title
        subtitle: Optional subtitle
    """
    st.markdown(f"""
    <div class="main-header">
        <h1>{title}</h1>
        {f'<p style="margin: 0.5rem 0 0 0; opacity: 0.9;">{subtitle}</p>' if subtitle else ''}
    </div>
    """, unsafe_allow_html=True)


# =============================================================================
# Export all components
# =============================================================================

__all__ = [
    # Metric components
    "metric_card",
    "metric_row",
    # Info box components
    "info_box",
    "status_banner",
    # Loading components
    "loading_spinner",
    "loading_state",
    # Data table components
    "data_table",
    "friendly_table",
    # Card components
    "card",
    # Section components
    "section",
    "divider",
    # Button components
    "primary_button",
    "secondary_button",
    # Layout components
    "two_column_layout",
    "three_column_layout",
    # Empty state
    "empty_state",
    # Error display
    "error_display",
    # Header
    "main_header",
]
