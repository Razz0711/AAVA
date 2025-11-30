# utils/premium_theme.py
# Premium UI Theme for AAVA Application
# Consistent styling across all pages

PREMIUM_CSS = """
<style>
    /* ═══════════════════════════════════════════════════════════════════════════
       AAVA PREMIUM THEME - Consistent Design System
       ═══════════════════════════════════════════════════════════════════════════ */
    
    /* Import Google Font */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    /* Root Variables */
    :root {
        --primary-color: #00d4ff;
        --primary-dark: #0099cc;
        --primary-light: #66e5ff;
        --secondary-color: #667eea;
        --accent-color: #764ba2;
        --bg-dark: #0a0a14;
        --bg-medium: #1a1a2e;
        --bg-light: #16213e;
        --text-primary: #ffffff;
        --text-secondary: #b8c5d6;
        --text-muted: #6b7c93;
        --success-color: #00e676;
        --warning-color: #ffab00;
        --error-color: #ff5252;
        --border-radius: 12px;
        --shadow-sm: 0 2px 8px rgba(0, 0, 0, 0.15);
        --shadow-md: 0 4px 20px rgba(0, 0, 0, 0.25);
        --shadow-lg: 0 8px 40px rgba(0, 0, 0, 0.35);
        --shadow-glow: 0 0 30px rgba(0, 212, 255, 0.3);
    }
    
    /* Global App Styling */
    .stApp {
        background: linear-gradient(135deg, var(--bg-dark) 0%, var(--bg-medium) 50%, var(--bg-light) 100%) !important;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
    }
    
    /* Main Content Area */
    .main .block-container {
        padding: 2rem 3rem !important;
        max-width: 1400px !important;
    }
    
    /* ═══════════════════════════════════════════════════════════════════════════
       TYPOGRAPHY - Consistent Font Sizes
       ═══════════════════════════════════════════════════════════════════════════ */
    
    /* Page Titles */
    h1 {
        font-size: 2rem !important;
        font-weight: 700 !important;
        color: var(--text-primary) !important;
        letter-spacing: -0.02em !important;
    }
    
    /* Section Titles */
    h2 {
        font-size: 1.5rem !important;
        font-weight: 600 !important;
        color: var(--text-primary) !important;
        letter-spacing: -0.01em !important;
    }
    
    /* Subsection Titles */
    h3 {
        font-size: 1.25rem !important;
        font-weight: 600 !important;
        color: var(--text-primary) !important;
    }
    
    /* Card Titles */
    h4 {
        font-size: 1.1rem !important;
        font-weight: 600 !important;
        color: var(--text-primary) !important;
    }
    
    /* Body Text */
    p, .stMarkdown, span, div {
        font-size: 0.95rem !important;
        line-height: 1.6 !important;
    }
    
    /* Small/Caption Text */
    small, .stCaption, caption {
        font-size: 0.85rem !important;
        color: var(--text-muted) !important;
    }
    
    /* ═══════════════════════════════════════════════════════════════════════════
       PAGE HEADERS - Premium Gradient Headers
       ═══════════════════════════════════════════════════════════════════════════ */
    
    .premium-header {
        background: linear-gradient(135deg, var(--primary-color) 0%, var(--secondary-color) 50%, var(--accent-color) 100%);
        padding: 2rem 2.5rem;
        border-radius: 16px;
        color: white;
        margin-bottom: 2rem;
        box-shadow: var(--shadow-glow);
        position: relative;
        overflow: hidden;
    }
    
    .premium-header::before {
        content: '';
        position: absolute;
        top: -50%;
        left: -50%;
        width: 200%;
        height: 200%;
        background: radial-gradient(circle, rgba(255,255,255,0.1) 0%, transparent 60%);
        animation: headerPulse 4s ease-in-out infinite;
    }
    
    @keyframes headerPulse {
        0%, 100% { transform: scale(1); opacity: 0.5; }
        50% { transform: scale(1.1); opacity: 0.8; }
    }
    
    .premium-header h1 {
        margin: 0 !important;
        font-size: 2rem !important;
        font-weight: 700 !important;
        text-shadow: 0 2px 10px rgba(0,0,0,0.3);
        position: relative;
        z-index: 1;
    }
    
    .premium-header p {
        margin: 0.5rem 0 0 0 !important;
        font-size: 1rem !important;
        opacity: 0.95;
        position: relative;
        z-index: 1;
    }
    
    /* ═══════════════════════════════════════════════════════════════════════════
       CARDS & CONTAINERS
       ═══════════════════════════════════════════════════════════════════════════ */
    
    .premium-card {
        background: linear-gradient(135deg, rgba(30, 58, 95, 0.8) 0%, rgba(22, 33, 62, 0.9) 100%);
        padding: 1.5rem;
        border-radius: var(--border-radius);
        border: 1px solid rgba(0, 212, 255, 0.15);
        box-shadow: var(--shadow-md);
        backdrop-filter: blur(10px);
        transition: all 0.3s ease;
    }
    
    .premium-card:hover {
        transform: translateY(-4px);
        border-color: rgba(0, 212, 255, 0.3);
        box-shadow: var(--shadow-lg), var(--shadow-glow);
    }
    
    /* Metric Cards */
    .metric-card {
        background: linear-gradient(135deg, rgba(30, 58, 95, 0.9) 0%, rgba(22, 33, 62, 0.95) 100%);
        padding: 1.5rem;
        border-radius: var(--border-radius);
        border: 1px solid rgba(0, 212, 255, 0.2);
        box-shadow: var(--shadow-md);
        text-align: center;
        transition: all 0.3s ease;
    }
    
    .metric-card:hover {
        transform: translateY(-4px);
        box-shadow: var(--shadow-lg), 0 0 30px rgba(0, 212, 255, 0.2);
    }
    
    .metric-value {
        font-size: 2.5rem !important;
        font-weight: 700 !important;
        color: var(--primary-color) !important;
        line-height: 1 !important;
        text-shadow: 0 0 20px rgba(0, 212, 255, 0.5);
    }
    
    .metric-label {
        font-size: 0.9rem !important;
        color: var(--text-secondary) !important;
        margin-top: 0.5rem !important;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    
    /* Feature Cards */
    .feature-card {
        background: linear-gradient(135deg, rgba(30, 58, 95, 0.8) 0%, rgba(22, 33, 62, 0.9) 100%);
        padding: 1.5rem;
        border-radius: var(--border-radius);
        border: 1px solid rgba(0, 212, 255, 0.15);
        box-shadow: var(--shadow-sm);
        text-align: center;
        transition: all 0.3s ease;
        cursor: pointer;
    }
    
    .feature-card:hover {
        transform: translateY(-6px) scale(1.02);
        border-color: var(--primary-color);
        box-shadow: var(--shadow-lg), var(--shadow-glow);
    }
    
    .feature-card .icon {
        font-size: 2.5rem;
        margin-bottom: 0.75rem;
    }
    
    .feature-card h4 {
        margin: 0.5rem 0 !important;
        color: var(--text-primary) !important;
        font-size: 1.1rem !important;
    }
    
    .feature-card p {
        color: var(--text-secondary) !important;
        font-size: 0.9rem !important;
        margin: 0 !important;
    }
    
    /* ═══════════════════════════════════════════════════════════════════════════
       BUTTONS
       ═══════════════════════════════════════════════════════════════════════════ */
    
    .stButton > button {
        background: linear-gradient(135deg, var(--primary-color) 0%, var(--primary-dark) 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 10px !important;
        padding: 0.6rem 1.5rem !important;
        font-weight: 600 !important;
        font-size: 0.9rem !important;
        box-shadow: 0 4px 15px rgba(0, 212, 255, 0.3) !important;
        transition: all 0.3s ease !important;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 25px rgba(0, 212, 255, 0.5) !important;
    }
    
    .stButton > button[kind="secondary"] {
        background: transparent !important;
        border: 2px solid var(--primary-color) !important;
        color: var(--primary-color) !important;
    }
    
    .stButton > button[kind="secondary"]:hover {
        background: rgba(0, 212, 255, 0.1) !important;
    }
    
    /* ═══════════════════════════════════════════════════════════════════════════
       FORM ELEMENTS
       ═══════════════════════════════════════════════════════════════════════════ */
    
    /* Text Inputs */
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea,
    .stSelectbox > div > div,
    .stMultiSelect > div > div {
        background: rgba(22, 33, 62, 0.8) !important;
        border: 1px solid rgba(0, 212, 255, 0.3) !important;
        border-radius: 10px !important;
        color: var(--text-primary) !important;
        font-size: 0.95rem !important;
        padding: 0.75rem 1rem !important;
    }
    
    .stTextInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus {
        border-color: var(--primary-color) !important;
        box-shadow: 0 0 0 2px rgba(0, 212, 255, 0.2) !important;
    }
    
    /* Labels */
    .stTextInput > label,
    .stTextArea > label,
    .stSelectbox > label,
    .stMultiSelect > label,
    .stNumberInput > label,
    .stDateInput > label {
        color: var(--text-secondary) !important;
        font-size: 0.9rem !important;
        font-weight: 500 !important;
        margin-bottom: 0.5rem !important;
    }
    
    /* ═══════════════════════════════════════════════════════════════════════════
       TABS
       ═══════════════════════════════════════════════════════════════════════════ */
    
    .stTabs [data-baseweb="tab-list"] {
        background: rgba(22, 33, 62, 0.6) !important;
        border-radius: 12px !important;
        padding: 0.5rem !important;
        gap: 0.5rem !important;
    }
    
    .stTabs [data-baseweb="tab"] {
        background: transparent !important;
        color: var(--text-secondary) !important;
        border-radius: 8px !important;
        padding: 0.75rem 1.5rem !important;
        font-size: 0.9rem !important;
        font-weight: 500 !important;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, var(--primary-color) 0%, var(--primary-dark) 100%) !important;
        color: white !important;
    }
    
    /* ═══════════════════════════════════════════════════════════════════════════
       TABLES & DATAFRAMES
       ═══════════════════════════════════════════════════════════════════════════ */
    
    .stDataFrame {
        border-radius: var(--border-radius) !important;
        overflow: hidden !important;
    }
    
    .stDataFrame [data-testid="stDataFrameResizable"] {
        background: rgba(22, 33, 62, 0.8) !important;
        border: 1px solid rgba(0, 212, 255, 0.2) !important;
    }
    
    /* ═══════════════════════════════════════════════════════════════════════════
       SIDEBAR
       ═══════════════════════════════════════════════════════════════════════════ */
    
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, var(--bg-dark) 0%, var(--bg-medium) 100%) !important;
    }
    
    [data-testid="stSidebar"] > div {
        background: transparent !important;
    }
    
    /* ═══════════════════════════════════════════════════════════════════════════
       ALERTS & MESSAGES
       ═══════════════════════════════════════════════════════════════════════════ */
    
    .stSuccess {
        background: rgba(0, 230, 118, 0.15) !important;
        border: 1px solid rgba(0, 230, 118, 0.3) !important;
        color: #00e676 !important;
        border-radius: 10px !important;
    }
    
    .stError {
        background: rgba(255, 82, 82, 0.15) !important;
        border: 1px solid rgba(255, 82, 82, 0.3) !important;
        color: #ff5252 !important;
        border-radius: 10px !important;
    }
    
    .stWarning {
        background: rgba(255, 171, 0, 0.15) !important;
        border: 1px solid rgba(255, 171, 0, 0.3) !important;
        color: #ffab00 !important;
        border-radius: 10px !important;
    }
    
    .stInfo {
        background: rgba(0, 212, 255, 0.15) !important;
        border: 1px solid rgba(0, 212, 255, 0.3) !important;
        color: #00d4ff !important;
        border-radius: 10px !important;
    }
    
    /* ═══════════════════════════════════════════════════════════════════════════
       EXPANDERS
       ═══════════════════════════════════════════════════════════════════════════ */
    
    .streamlit-expanderHeader {
        background: rgba(30, 58, 95, 0.6) !important;
        border: 1px solid rgba(0, 212, 255, 0.2) !important;
        border-radius: 10px !important;
        color: var(--text-primary) !important;
        font-size: 0.95rem !important;
        font-weight: 500 !important;
    }
    
    .streamlit-expanderContent {
        background: rgba(22, 33, 62, 0.6) !important;
        border: 1px solid rgba(0, 212, 255, 0.15) !important;
        border-top: none !important;
        border-radius: 0 0 10px 10px !important;
    }
    
    /* ═══════════════════════════════════════════════════════════════════════════
       DIVIDERS
       ═══════════════════════════════════════════════════════════════════════════ */
    
    hr {
        border: none !important;
        height: 1px !important;
        background: linear-gradient(90deg, transparent, rgba(0, 212, 255, 0.3), transparent) !important;
        margin: 2rem 0 !important;
    }
    
    /* ═══════════════════════════════════════════════════════════════════════════
       BADGES & STATUS INDICATORS
       ═══════════════════════════════════════════════════════════════════════════ */
    
    .badge {
        display: inline-block;
        padding: 0.35rem 0.75rem;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    .badge-primary {
        background: rgba(0, 212, 255, 0.2);
        color: var(--primary-color);
        border: 1px solid rgba(0, 212, 255, 0.3);
    }
    
    .badge-success {
        background: rgba(0, 230, 118, 0.2);
        color: var(--success-color);
        border: 1px solid rgba(0, 230, 118, 0.3);
    }
    
    .badge-warning {
        background: rgba(255, 171, 0, 0.2);
        color: var(--warning-color);
        border: 1px solid rgba(255, 171, 0, 0.3);
    }
    
    .badge-error {
        background: rgba(255, 82, 82, 0.2);
        color: var(--error-color);
        border: 1px solid rgba(255, 82, 82, 0.3);
    }
    
    /* ═══════════════════════════════════════════════════════════════════════════
       PROGRESS BARS
       ═══════════════════════════════════════════════════════════════════════════ */
    
    .stProgress > div > div > div {
        background: linear-gradient(90deg, var(--primary-color), var(--secondary-color)) !important;
    }
    
    /* ═══════════════════════════════════════════════════════════════════════════
       PLOTLY CHARTS (Dark Theme)
       ═══════════════════════════════════════════════════════════════════════════ */
    
    .js-plotly-plot .plotly .modebar {
        background: transparent !important;
    }
    
    /* ═══════════════════════════════════════════════════════════════════════════
       SCROLLBARS
       ═══════════════════════════════════════════════════════════════════════════ */
    
    ::-webkit-scrollbar {
        width: 8px;
        height: 8px;
    }
    
    ::-webkit-scrollbar-track {
        background: var(--bg-dark);
    }
    
    ::-webkit-scrollbar-thumb {
        background: var(--primary-dark);
        border-radius: 4px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: var(--primary-color);
    }
</style>
"""

def get_page_header(icon: str, title: str, subtitle: str, gradient_colors: list = None) -> str:
    """Generate a premium page header with custom gradient colors."""
    if gradient_colors is None:
        gradient_colors = ["#00d4ff", "#667eea", "#764ba2"]
    
    gradient = f"linear-gradient(135deg, {gradient_colors[0]} 0%, {gradient_colors[1]} 50%, {gradient_colors[2]} 100%)"
    
    return f"""
    <div class="premium-header" style="background: {gradient};">
        <h1 style="margin: 0; display: flex; align-items: center; gap: 12px;">
            <span style="font-size: 2rem;">{icon}</span> {title}
        </h1>
        <p style="margin: 0.5rem 0 0 0; font-size: 1rem; opacity: 0.95;">{subtitle}</p>
    </div>
    """

def get_metric_card(value: str, label: str, icon: str = "", color: str = "#00d4ff") -> str:
    """Generate a premium metric card."""
    return f"""
    <div class="metric-card">
        <div style="font-size: 1.5rem; margin-bottom: 0.5rem;">{icon}</div>
        <div class="metric-value" style="color: {color};">{value}</div>
        <div class="metric-label">{label}</div>
    </div>
    """

def get_feature_card(icon: str, title: str, description: str, border_color: str = "#00d4ff") -> str:
    """Generate a premium feature card."""
    return f"""
    <div class="feature-card" style="border-left: 4px solid {border_color};">
        <div class="icon">{icon}</div>
        <h4>{title}</h4>
        <p>{description}</p>
    </div>
    """

# Page-specific gradient colors
PAGE_GRADIENTS = {
    "home": ["#00d4ff", "#667eea", "#764ba2"],
    "validation": ["#00e676", "#00c853", "#00a040"],
    "agent": ["#2196F3", "#1976D2", "#0d47a1"],
    "confidence": ["#FF9800", "#F57C00", "#e65100"],
    "admin": ["#9C27B0", "#7B1FA2", "#4a148c"],
    "ai_chat": ["#00d4ff", "#667eea", "#764ba2"]
}
