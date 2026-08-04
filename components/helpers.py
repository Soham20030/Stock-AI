import streamlit as st


def inject_custom_css():
    """
    Injects authentic Intercom-inspired minimalist dark mode styling:
    Ultra-sleek off-black canvas (#090A0C), flat slate surfaces (#0F1115),
    Intercom signature indigo/blue accents (#6366F1), 9999px full-pill buttons,
    hairline micro-borders (#1A1D24), and spacious minimalist typography.
    """
    st.markdown("""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

        /* Global background & typography */
        .stApp {
            background-color: #090a0c !important;
            color: #f3f4f6 !important;
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif !important;
        }

        /* Hide Streamlit default clutter */
        header {visibility: hidden;}
        .stAppDeployButton {display: none !important;}
        [data-testid="stAppDeployButton"] {display: none !important;}
        [data-testid="stToolbar"] {visibility: hidden !important;}
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}

        /* Minimalist Intercom Surface Container */
        [data-testid="stVerticalBlockBorderWrapper"] {
            background: #0f1115 !important;
            border: 1px solid #1a1d24 !important;
            border-radius: 12px !important;
            padding: 22px !important;
            box-shadow: none !important;
            transition: border-color 0.2s ease;
        }

        [data-testid="stVerticalBlockBorderWrapper"]:hover {
            border-color: #242933 !important;
        }

        /* Intercom Signature Full-Pill Tab Bar */
        .stTabs [data-baseweb="tab-list"] {
            gap: 4px;
            background-color: #0f1115;
            padding: 5px;
            border-radius: 9999px;
            border: 1px solid #1a1d24;
            display: inline-flex;
        }
        
        .stTabs [data-baseweb="tab"] {
            height: 36px;
            border-radius: 9999px;
            color: #8f9bba;
            font-weight: 500;
            font-size: 0.84rem;
            padding: 0 16px;
            transition: all 0.2s ease;
            border: 1px solid transparent;
        }
        
        .stTabs [aria-selected="true"] {
            background-color: #1a1f2c !important;
            color: #ffffff !important;
            border-color: #2e364a !important;
            font-weight: 600;
        }

        /* Minimalist Headers */
        .intercom-title {
            color: #ffffff;
            font-size: 1.05rem;
            font-weight: 600;
            letter-spacing: -0.015em;
            margin-bottom: 12px;
        }

        .intercom-subtitle {
            font-size: 0.82rem;
            color: #8f9bba;
            margin-top: -6px;
            margin-bottom: 16px;
        }

        /* Flat Summary & Metric Cards */
        .summary-box {
            background: #14171f;
            border-radius: 10px;
            padding: 16px;
            border: 1px solid #1e222d;
            height: 100%;
        }

        .summary-label {
            font-size: 0.7rem;
            color: #8f9bba;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            font-weight: 600;
        }

        .summary-val {
            font-size: 1.2rem;
            font-weight: 700;
            color: #ffffff;
            margin-top: 4px;
            letter-spacing: -0.02em;
        }

        .summary-sub {
            font-size: 0.76rem;
            color: #64748b;
            margin-top: 4px;
            font-weight: 400;
        }

        /* Minimalist Market Signal Cards */
        .signal-box-pos {
            background: rgba(16, 185, 129, 0.06);
            border: 1px solid rgba(16, 185, 129, 0.2);
            border-radius: 8px;
            padding: 10px 14px;
            margin-bottom: 8px;
            color: #34d399;
            font-weight: 400;
            font-size: 0.86rem;
            line-height: 1.5;
        }

        .signal-box-neg {
            background: rgba(239, 68, 68, 0.06);
            border: 1px solid rgba(239, 68, 68, 0.2);
            border-radius: 8px;
            padding: 10px 14px;
            margin-bottom: 8px;
            color: #f87171;
            font-weight: 400;
            font-size: 0.86rem;
            line-height: 1.5;
        }

        /* Narrative Callout Box */
        .narrative-box {
            background: #14171f;
            border: 1px solid #1e222d;
            border-left: 3px solid #6366f1;
            border-radius: 10px;
            padding: 16px 18px;
            font-size: 0.92rem;
            line-height: 1.6;
            color: #e2e8f0;
            font-weight: 400;
        }

        /* Color Utility Classes */
        .val-positive { color: #34d399 !important; font-weight: 600; }
        .val-negative { color: #f87171 !important; font-weight: 600; }
        .val-neutral  { color: #fbbf24 !important; font-weight: 600; }

        /* Metric font overrides */
        [data-testid="stMetricValue"] {
            font-size: 1.25rem !important;
            font-weight: 700 !important;
            letter-spacing: -0.02em !important;
        }
        
        [data-testid="stMetricLabel"] {
            font-size: 0.75rem !important;
            color: #8f9bba !important;
            text-transform: uppercase !important;
            letter-spacing: 0.05em !important;
            font-weight: 600 !important;
        }

        /* Intercom Signature Full-Pill Buttons */
        .stButton>button {
            background: #6366f1 !important;
            color: #ffffff !important;
            border: none !important;
            border-radius: 9999px !important;
            padding: 8px 20px !important;
            font-weight: 500 !important;
            font-size: 0.85rem !important;
            transition: all 0.2s ease !important;
        }
        
        .stButton>button:hover {
            background: #4f46e5 !important;
            color: #ffffff !important;
            box-shadow: 0 4px 12px rgba(99, 102, 241, 0.25) !important;
        }

        /* Secondary Pill Buttons */
        [data-testid="stBaseButton-secondary"] {
            background: #14171f !important;
            color: #8f9bba !important;
            border: 1px solid #1e222d !important;
            border-radius: 9999px !important;
        }

        [data-testid="stBaseButton-secondary"]:hover {
            background: #1c212c !important;
            color: #ffffff !important;
            border-color: #2c3446 !important;
        }

        /* Flat News Card Container */
        .news-card-container {
            background: #14171f;
            border: 1px solid #1e222d;
            border-radius: 10px;
            padding: 16px;
            margin-bottom: 12px;
            transition: border-color 0.2s ease;
        }

        .news-card-container:hover {
            border-color: #2b3344;
        }

        .news-card-title {
            font-size: 0.98rem;
            font-weight: 600;
            color: #ffffff;
            margin-bottom: 8px;
            line-height: 1.4;
        }

        .news-card-title a {
            color: #818cf8;
            text-decoration: none;
        }

        .news-card-title a:hover {
            text-decoration: underline;
        }

        .news-card-summary {
            font-size: 0.86rem;
            color: #cbd5e1;
            margin-bottom: 12px;
            line-height: 1.55;
            background: #0f1115;
            padding: 10px 12px;
            border-radius: 8px;
            border: 1px solid #1a1d24;
        }

        .news-card-meta-row {
            display: flex;
            gap: 20px;
            font-size: 0.8rem;
            color: #8f9bba;
            align-items: center;
        }

        /* Intercom Chat Bubbles */
        [data-testid="stChatMessage"] {
            background-color: #14171f !important;
            border: 1px solid #1e222d !important;
            border-radius: 12px !important;
            padding: 12px 16px !important;
            margin-bottom: 10px !important;
        }

        /* Pill Badges */
        .badge-positive {
            background: rgba(16, 185, 129, 0.12);
            color: #34d399;
            padding: 2px 10px;
            border-radius: 9999px;
            font-weight: 500;
            font-size: 0.76rem;
        }

        .badge-negative {
            background: rgba(239, 68, 68, 0.12);
            color: #f87171;
            padding: 2px 10px;
            border-radius: 9999px;
            font-weight: 500;
            font-size: 0.76rem;
        }

        .badge-neutral {
            background: rgba(245, 158, 11, 0.12);
            color: #fbbf24;
            padding: 2px 10px;
            border-radius: 9999px;
            font-weight: 500;
            font-size: 0.76rem;
        }
        </style>
    """, unsafe_allow_html=True)


def render_summary_box(label, value, subtext="", border_color="", val_class=""):
    """
    Renders an Intercom-styled minimalist summary card.
    """
    subtext_html = f'<div class="summary-sub">{subtext}</div>' if subtext else ""
    border_style = f' style="border-left: 3px solid {border_color};"' if border_color else ''
    st.markdown(f"""
        <div class="summary-box"{border_style}>
            <div class="summary-label">{label}</div>
            <div class="summary-val {val_class}">{value}</div>
            {subtext_html}
        </div>
    """, unsafe_allow_html=True)


def render_signal_box(text, signal_type="positive"):
    """
    Renders a clean, minimalist market signal callout.
    """
    box_class = "signal-box-pos" if signal_type == "positive" else "signal-box-neg"
    prefix = "Bullish Signal — " if signal_type == "positive" else "Bearish Signal — "
    st.markdown(f'<div class="{box_class}"><strong>{prefix}</strong>{text}</div>', unsafe_allow_html=True)


def render_news_card(title, summary, source, date, url, sentiment_badge=""):
    """
    Renders a minimalist news article card.
    """
    st.markdown(f"""
        <div class="news-card-container">
            <div class="news-card-title"><a href="{url}" target="_blank">{title}</a></div>
            <div class="news-card-summary">
                {summary}
            </div>
            <div class="news-card-meta-row">
                <div>Sentiment: {sentiment_badge}</div>
                <div>Source: <span style="color: #e2e8f0;">{source}</span></div>
                <div>Date: <span style="color: #e2e8f0;">{date}</span></div>
            </div>
        </div>
    """, unsafe_allow_html=True)
