"""
utils/ui.py
Dark luxury theme CSS + reusable Streamlit UI components.
"""

import streamlit as st

# ── Theme CSS ──────────────────────────────────────────────────────────────
DARK_LUXURY_CSS = """
<style>
/* ── Google Fonts ── */
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;600;700&family=DM+Sans:wght@300;400;500;600&display=swap');

/* ── CSS Variables ── */
:root {
    --bg-primary: #0a0e1a;
    --bg-secondary: #111827;
    --bg-card: #1a2235;
    --bg-card-hover: #1e2a40;
    --accent-gold: #d4a843;
    --accent-teal: #2dd4bf;
    --accent-blue: #3b82f6;
    --text-primary: #f1f5f9;
    --text-secondary: #94a3b8;
    --text-muted: #64748b;
    --border: rgba(255,255,255,0.08);
    --border-accent: rgba(212,168,67,0.3);
    --shadow: 0 4px 24px rgba(0,0,0,0.4);
    --radius: 12px;
    --radius-lg: 20px;
}

/* ── Base ── */
.stApp {
    background: var(--bg-primary) !important;
    font-family: 'DM Sans', sans-serif !important;
    color: var(--text-primary) !important;
}

/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background: var(--bg-secondary) !important;
    border-right: 1px solid var(--border) !important;
}
[data-testid="stSidebar"] * { color: var(--text-primary) !important; }

/* ── Headers ── */
h1, h2 { font-family: 'Playfair Display', serif !important; }
h1 { color: var(--accent-gold) !important; font-size: 2rem !important; }
h2 { color: var(--text-primary) !important; }
h3 { color: var(--accent-teal) !important; font-size: 1.1rem !important; }

/* ── Metric cards ── */
[data-testid="metric-container"] {
    background: var(--bg-card) !important;
    border: 1px solid var(--border) !important;
    border-radius: var(--radius) !important;
    padding: 1rem !important;
}
[data-testid="stMetricValue"] {
    color: var(--accent-gold) !important;
    font-size: 1.8rem !important;
    font-weight: 700 !important;
}
[data-testid="stMetricLabel"] { color: var(--text-secondary) !important; }

/* ── Buttons ── */
.stButton > button {
    background: linear-gradient(135deg, var(--accent-gold), #b8862e) !important;
    color: #0a0e1a !important;
    border: none !important;
    border-radius: 8px !important;
    font-weight: 600 !important;
    font-family: 'DM Sans', sans-serif !important;
    padding: 0.5rem 1.5rem !important;
    transition: all 0.2s ease !important;
}
.stButton > button:hover {
    transform: translateY(-1px) !important;
    box-shadow: 0 6px 20px rgba(212,168,67,0.4) !important;
}

/* ── Text inputs ── */
.stTextInput > div > div > input,
.stTextArea > div > div > textarea,
.stSelectbox > div > div {
    background: var(--bg-card) !important;
    border: 1px solid var(--border) !important;
    border-radius: 8px !important;
    color: var(--text-primary) !important;
    font-family: 'DM Sans', sans-serif !important;
}
.stTextInput > div > div > input:focus,
.stTextArea > div > div > textarea:focus {
    border-color: var(--accent-teal) !important;
    box-shadow: 0 0 0 2px rgba(45,212,191,0.2) !important;
}

/* ── Chat messages ── */
.user-bubble {
    background: linear-gradient(135deg, #1e3a5f, #1a2e4a);
    border: 1px solid rgba(59,130,246,0.3);
    border-radius: 18px 18px 4px 18px;
    padding: 12px 16px;
    margin: 8px 0 8px 60px;
    color: #e2e8f0;
    font-size: 0.95rem;
    line-height: 1.6;
    box-shadow: var(--shadow);
}
.bot-bubble {
    background: var(--bg-card);
    border: 1px solid var(--border-accent);
    border-radius: 18px 18px 18px 4px;
    padding: 14px 18px;
    margin: 8px 60px 8px 0;
    color: var(--text-primary);
    font-size: 0.95rem;
    line-height: 1.6;
    box-shadow: var(--shadow);
}
.chat-avatar-user {
    float: right;
    margin-left: 10px;
    background: var(--accent-blue);
    border-radius: 50%;
    width: 36px; height: 36px;
    display: flex; align-items: center; justify-content: center;
    font-size: 1rem;
}
.chat-avatar-bot {
    float: left;
    margin-right: 10px;
    background: linear-gradient(135deg, var(--accent-gold), #b8862e);
    border-radius: 50%;
    width: 36px; height: 36px;
    display: flex; align-items: center; justify-content: center;
    font-size: 1rem;
}
.chat-row { overflow: hidden; margin-bottom: 4px; }

/* ── KPI Cards ── */
.kpi-card {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 1.2rem;
    text-align: center;
    transition: all 0.2s ease;
}
.kpi-card:hover {
    border-color: var(--accent-gold);
    transform: translateY(-2px);
    box-shadow: var(--shadow);
}
.kpi-value {
    font-size: 1.9rem;
    font-weight: 700;
    color: var(--accent-gold);
    font-family: 'Playfair Display', serif;
}
.kpi-label {
    font-size: 0.8rem;
    color: var(--text-muted);
    text-transform: uppercase;
    letter-spacing: 0.08em;
    margin-top: 4px;
}
.kpi-delta {
    font-size: 0.85rem;
    color: var(--accent-teal);
    margin-top: 2px;
}

/* ── Info / alert boxes ── */
.info-box {
    background: rgba(45,212,191,0.08);
    border: 1px solid rgba(45,212,191,0.25);
    border-radius: 10px;
    padding: 12px 16px;
    margin: 10px 0;
    color: var(--text-primary);
    font-size: 0.9rem;
}
.warning-box {
    background: rgba(212,168,67,0.08);
    border: 1px solid rgba(212,168,67,0.25);
    border-radius: 10px;
    padding: 12px 16px;
    margin: 10px 0;
}

/* ── Provider badge ── */
.provider-badge {
    display: inline-block;
    background: rgba(212,168,67,0.15);
    border: 1px solid rgba(212,168,67,0.4);
    border-radius: 20px;
    padding: 3px 12px;
    font-size: 0.75rem;
    color: var(--accent-gold);
    font-weight: 600;
    letter-spacing: 0.05em;
}

/* ── Tabs ── */
.stTabs [data-baseweb="tab-list"] {
    background: var(--bg-secondary) !important;
    border-radius: 10px !important;
    gap: 4px !important;
}
.stTabs [data-baseweb="tab"] {
    background: transparent !important;
    color: var(--text-muted) !important;
    border-radius: 8px !important;
    font-family: 'DM Sans', sans-serif !important;
}
.stTabs [aria-selected="true"] {
    background: var(--bg-card) !important;
    color: var(--accent-gold) !important;
}

/* ── Dividers ── */
hr { border-color: var(--border) !important; margin: 1.5rem 0 !important; }

/* ── Dataframes ── */
[data-testid="stDataFrame"] {
    background: var(--bg-card) !important;
    border-radius: var(--radius) !important;
}

/* ── Scrollbar ── */
::-webkit-scrollbar { width: 6px; }
::-webkit-scrollbar-track { background: var(--bg-primary); }
::-webkit-scrollbar-thumb { background: var(--border); border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: var(--text-muted); }

/* ── Hide Streamlit branding ── */
#MainMenu, footer { visibility: hidden; }
</style>
"""


def apply_theme():
    """Inject the dark luxury CSS theme."""
    st.markdown(DARK_LUXURY_CSS, unsafe_allow_html=True)


def render_header(title: str, subtitle: str = "", icon: str = "✈️"):
    """Render the app header with logo and title."""
    st.markdown(f"""
    <div style="text-align:center; padding: 1.5rem 0 1rem;">
        <div style="font-size:3rem; margin-bottom:0.5rem;">{icon}</div>
        <h1 style="margin:0; font-size:2.2rem;">{title}</h1>
        <p style="color:#94a3b8; margin:0.3rem 0 0; font-size:1rem;">{subtitle}</p>
    </div>
    """, unsafe_allow_html=True)


def render_chat_message(role: str, content: str):
    """Render a chat bubble for user or assistant."""
    if role == "user":
        st.markdown(f"""
        <div class="chat-row">
            <div class="chat-avatar-user">👤</div>
            <div class="user-bubble">{content}</div>
        </div>
        """, unsafe_allow_html=True)
    else:
        # Use st.markdown for bot (supports full markdown tables, etc.)
        col1, col2 = st.columns([0.05, 0.95])
        with col1:
            st.markdown('<div style="background:linear-gradient(135deg,#d4a843,#b8862e);border-radius:50%;width:36px;height:36px;display:flex;align-items:center;justify-content:center;font-size:1rem;margin-top:4px;">🤖</div>', unsafe_allow_html=True)
        with col2:
            st.markdown(f'<div class="bot-bubble">', unsafe_allow_html=True)
            st.markdown(content)
            st.markdown('</div>', unsafe_allow_html=True)


def render_kpi_card(label: str, value: str, delta: str = "", color: str = "#d4a843"):
    """Render a single KPI card."""
    delta_html = f'<div class="kpi-delta">↑ {delta}</div>' if delta else ""
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-value" style="color:{color};">{value}</div>
        <div class="kpi-label">{label}</div>
        {delta_html}
    </div>
    """, unsafe_allow_html=True)


def render_info_box(text: str, type_: str = "info"):
    """Render a styled info or warning box."""
    css_class = "info-box" if type_ == "info" else "warning-box"
    icon = "ℹ️" if type_ == "info" else "⚠️"
    st.markdown(f'<div class="{css_class}">{icon} {text}</div>', unsafe_allow_html=True)


def render_provider_badge(provider: str):
    """Show which AI provider is active."""
    icons = {"OPENAI": "🟢", "GEMINI": "🔵", "DEMO": "🟡"}
    icon = icons.get(provider, "⚪")
    st.markdown(
        f'<span class="provider-badge">{icon} {provider} Mode</span>',
        unsafe_allow_html=True,
    )


def loading_placeholder(text: str = "TravelMind is thinking…"):
    """Return a Streamlit spinner context."""
    return st.spinner(text)
