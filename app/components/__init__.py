"""
UI components for the ANTAQ Streamlit app.
"""
from .styles import (
    load_styles,
    Colors,
    Icons,
    get_metric_html,
    get_info_box_html,
    get_loading_html
)
from .base import (
    metric_card,
    metric_row,
    info_box,
    status_banner,
    loading_spinner,
    loading_state,
    data_table,
    friendly_table,
    card,
    section,
    divider,
    primary_button,
    secondary_button,
    two_column_layout,
    three_column_layout,
    empty_state,
    error_display,
    main_header,
)

__all__ = [
    # Styles
    "load_styles",
    "Colors",
    "Icons",
    "get_metric_html",
    "get_info_box_html",
    "get_loading_html",
    # Base components
    "metric_card",
    "metric_row",
    "info_box",
    "status_banner",
    "loading_spinner",
    "loading_state",
    "data_table",
    "friendly_table",
    "card",
    "section",
    "divider",
    "primary_button",
    "secondary_button",
    "two_column_layout",
    "three_column_layout",
    "empty_state",
    "error_display",
    "main_header",
]
