"""
Design system and CSS styles for the ANTAQ Streamlit app.
Provides consistent styling and components for a professional UI.
"""

# CSS Styles
CUSTOM_CSS = """
<style>
/* =============================================================================
   Design System Variables
   ============================================================================= */
:root {
    /* Cores Principais */
    --primary: #0066CC;
    --primary-dark: #004C99;
    --primary-light: #E6F0FF;
    --secondary: #00A651;
    --warning: #FF9500;
    --danger: #DC3545;

    /* Neutros */
    --gray-50: #F8F9FA;
    --gray-100: #F1F3F5;
    --gray-200: #E9ECEF;
    --gray-500: #ADB5BD;
    --gray-700: #495057;
    --gray-900: #212529;

    /* Backgrounds */
    --bg-primary: #FFFFFF;
    --bg-secondary: #F8F9FA;
    --bg-card: #FFFFFF;
    --bg-hover: #F1F3F5;
}

/* =============================================================================
   Global Styles
   ============================================================================= */
/* Hide streamlit footer */
footer {visibility: hidden;}
footer:after {
    content: "ANTAQ - Dados Aquaviários";
    visibility: visible;
    display: block;
    color: var(--gray-500);
    font-size: 0.8rem;
    text-align: center;
    padding: 1rem;
}

/* Hide default menu */
#MainMenu {visibility: hidden;}

/* =============================================================================
   Header Styles
   ============================================================================= */
.main-header {
    background: linear-gradient(135deg, var(--primary) 0%, var(--primary-dark) 100%);
    color: white;
    padding: 1.5rem 2rem;
    border-radius: 0.75rem;
    margin-bottom: 2rem;
    box-shadow: 0 4px 6px rgba(0, 102, 204, 0.1);
}

.main-header h1 {
    margin: 0;
    font-size: 2rem;
    font-weight: 700;
    color: white;
}

.sub-header {
    color: var(--gray-700);
    font-size: 1rem;
    margin-top: 0.5rem;
    margin-bottom: 1.5rem;
}

/* =============================================================================
   Card Styles
   ============================================================================= */
.card {
    background: var(--bg-card);
    border: 1px solid var(--gray-200);
    border-radius: 0.75rem;
    padding: 1.5rem;
    margin-bottom: 1rem;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
}

.card-title {
    font-size: 1.125rem;
    font-weight: 600;
    color: var(--gray-900);
    margin-bottom: 1rem;
}

/* =============================================================================
   Metric Cards
   ============================================================================= */
.overview-metric {
    background: linear-gradient(135deg, var(--gray-50) 0%, var(--bg-card) 100%);
    border: 1px solid var(--gray-200);
    border-radius: 0.75rem;
    padding: 1.25rem;
    text-align: center;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
    transition: transform 0.2s, box-shadow 0.2s;
}

.overview-metric:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
}

.overview-metric .metric-icon {
    font-size: 2rem;
    margin-bottom: 0.5rem;
}

.overview-metric .metric-value {
    font-size: 2rem;
    font-weight: 700;
    color: var(--primary);
}

.overview-metric .metric-label {
    font-size: 0.875rem;
    color: var(--gray-700);
    margin-top: 0.5rem;
}

.overview-metric .metric-delta {
    font-size: 0.875rem;
    margin-top: 0.25rem;
}

.metric-delta.positive {
    color: var(--secondary);
}

.metric-delta.negative {
    color: var(--danger);
}

.metric-delta.neutral {
    color: var(--gray-500);
}

/* =============================================================================
   Status Banner
   ============================================================================= */
.data-status {
    background: var(--primary-light);
    border-left: 4px solid var(--primary);
    padding: 1rem 1.25rem;
    border-radius: 0.5rem;
    margin-bottom: 1.5rem;
}

.data-status .status-icon {
    font-size: 1.25rem;
    margin-right: 0.5rem;
}

.data-status .status-text {
    color: var(--gray-900);
    font-size: 0.9rem;
}

/* =============================================================================
   Info Box
   ============================================================================= */
.info-box {
    padding: 1rem;
    border-radius: 0.5rem;
    margin-bottom: 1rem;
    color: #212529;
}

.info-box.info {
    background: #E3F2FD;
    border-left: 4px solid var(--primary);
    color: #0D47A1;
}

.info-box.info strong {
    color: #0D47A1;
}

.info-box.success {
    background: #E8F5E9;
    border-left: 4px solid var(--secondary);
    color: #1B5E20;
}

.info-box.success strong {
    color: #1B5E20;
}

.info-box.warning {
    background: #FFF3E0;
    border-left: 4px solid var(--warning);
    color: #E65100;
}

.info-box.warning strong {
    color: #E65100;
}

.info-box.error {
    background: #FFEBEE;
    border-left: 4px solid var(--danger);
    color: #B71C1C;
}

.info-box.error strong {
    color: #B71C1C;
}

/* =============================================================================
   Loading Spinner
   ============================================================================= */
.loading-container {
    text-align: center;
    padding: 3rem;
}

.loading-spinner {
    border: 3px solid var(--gray-200);
    border-top: 3px solid var(--primary);
    border-radius: 50%;
    width: 40px;
    height: 40px;
    animation: spin 1s linear infinite;
    margin: 0 auto 1rem;
}

@keyframes spin {
    0% { transform: rotate(0deg); }
    100% { transform: rotate(360deg); }
}

.loading-text {
    color: var(--gray-700);
    font-size: 1rem;
}

/* =============================================================================
   Button Styles
   ============================================================================= */
.stButton > button {
    border-radius: 0.5rem;
    font-weight: 500;
    transition: all 0.2s;
}

.stButton > button:hover {
    transform: translateY(-1px);
    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.15);
}

/* Primary button styling */
.stButton > button[kind="primary"] {
    background: linear-gradient(135deg, var(--primary) 0%, var(--primary-dark) 100%);
}

/* =============================================================================
   Tab Styles
   ============================================================================= */
.stTabs [data-baseweb="tab-list"] {
    gap: 1rem;
}

.stTabs [data-baseweb="tab"] {
    border-radius: 0.5rem 0.5rem 0 0;
    padding: 0.75rem 1.5rem;
    font-weight: 500;
}

/* =============================================================================
   Form Styles
   ============================================================================= */
.stForm {
    border: 1px solid var(--gray-200);
    border-radius: 0.75rem;
    padding: 1.5rem;
    background: var(--bg-card);
}

/* =============================================================================
   Table Styles
   ============================================================================= */
.stDataFrame {
    border-radius: 0.5rem;
    overflow: hidden;
}

.stDataFrame [data-testid="stDataFrame"] {
    border: 1px solid var(--gray-200);
}

/* =============================================================================
   Chat Styles
   ============================================================================= */
.chat-message {
    padding: 1rem;
    border-radius: 0.75rem;
    margin-bottom: 1rem;
}

.chat-message.user {
    background: var(--primary-light);
    border-left: 4px solid var(--primary);
}

.chat-message.assistant {
    background: var(--gray-50);
    border-left: 4px solid var(--gray-500);
}

/* =============================================================================
   Section Divider
   ============================================================================= */
.section-divider {
    border: none;
    border-top: 2px solid var(--gray-200);
    margin: 2rem 0;
}

/* =============================================================================
   Responsive Utilities
   ============================================================================= */
@media (max-width: 768px) {
    .main-header h1 {
        font-size: 1.5rem;
    }

    .overview-metric {
        padding: 1rem;
    }

    .overview-metric .metric-value {
        font-size: 1.5rem;
    }
}
</style>
"""


def load_styles() -> None:
    """
    Load custom CSS styles into Streamlit.
    Call this once at the beginning of the app.
    """
    import streamlit as st
    st.markdown(CUSTOM_CSS, unsafe_allow_html=True)


# Color constants for use in Python code
class Colors:
    """Color constants for the design system."""

    # Primary colors
    PRIMARY = "#0066CC"
    PRIMARY_DARK = "#004C99"
    PRIMARY_LIGHT = "#E6F0FF"

    # Semantic colors
    SECONDARY = "#00A651"  # Green for success
    WARNING = "#FF9500"    # Orange for warnings
    DANGER = "#DC3545"     # Red for errors

    # Gray scale
    GRAY_50 = "#F8F9FA"
    GRAY_100 = "#F1F3F5"
    GRAY_200 = "#E9ECEF"
    GRAY_500 = "#ADB5BD"
    GRAY_700 = "#495057"
    GRAY_900 = "#212529"


# Icons for use in the UI
class Icons:
    """Icon constants for common UI elements."""

    # Navigation & Actions
    SEARCH = "🔍"
    BACK = "←"
    FORWARD = "→"
    HOME = "🏠"
    REFRESH = "🔄"

    # Data & Metrics
    CHART = "📊"
    TREND_UP = "📈"
    TREND_DOWN = "📉"
    BOX = "📦"
    SHIP = "🚢"
    TRUCK = "🚚"

    # Status
    SUCCESS = "✅"
    WARNING = "⚠️"
    ERROR = "❌"
    INFO = "ℹ️"
    LOADING = "⏳"

    # Chat
    CHAT = "💬"
    USER = "👤"
    BOT = "🤖"

    # Tabs
    CHAT_TAB = "💬"
    OVERVIEW_TAB = "📊"
    SETTINGS_TAB = "⚙️"


def get_metric_html(icon: str, value: str, label: str, delta: str = None) -> str:
    """
    Generate HTML for a metric card.

    Args:
        icon: Icon emoji or character
        value: Main value to display
        label: Label describing the metric
        delta: Optional change indicator (e.g., "+8.5%")

    Returns:
        HTML string for the metric card
    """
    delta_html = ""
    if delta:
        delta_class = "positive" if "+" in delta else ("negative" if "-" in delta else "neutral")
        delta_html = f'<div class="metric-delta {delta_class}">{delta}</div>'

    return f"""
    <div class="overview-metric">
        <div class="metric-icon">{icon}</div>
        <div class="metric-value">{value}</div>
        <div class="metric-label">{label}</div>
        {delta_html}
    </div>
    """


def get_info_box_html(title: str, content: str, box_type: str = "info", icon: str = None) -> str:
    """
    Generate HTML for an info box.

    Args:
        title: Box title
        content: Box content
        box_type: Type of box (info, success, warning, error)
        icon: Optional icon override

    Returns:
        HTML string for the info box
    """
    icons = {
        "info": Icons.INFO,
        "success": Icons.SUCCESS,
        "warning": Icons.WARNING,
        "error": Icons.ERROR,
    }
    icon_html = icon or icons.get(box_type, Icons.INFO)

    return f"""
    <div class="info-box {box_type}">
        <strong>{icon_html} {title}</strong><br>
        {content}
    </div>
    """


def get_loading_html(message: str = "Carregando...") -> str:
    """
    Generate HTML for a loading spinner.

    Args:
        message: Message to display below the spinner

    Returns:
        HTML string for the loading indicator
    """
    return f"""
    <div class="loading-container">
        <div class="loading-spinner"></div>
        <div class="loading-text">{message}</div>
    </div>
    """
