import streamlit as st


def inject_custom_css():
    """
    Injects Intercom-inspired executive dark mode CSS:
    Refined slate cards, electric cyan/sapphire accents, crisp typography,
    subtle micro-borders, and elegant visual hierarchy.
    """
    st.markdown("""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

        /* Global background & typography */
        .stApp {
            background-color: #0b0d12 !important;
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

        /* Modern Intercom-Style Card Container */
        [data-testid="stVerticalBlockBorderWrapper"] {
            background: #121620 !important;
            border: 1px solid #1e2433 !important;
            border-radius: 14px !important;
            padding: 20px !important;
            box-shadow: 0 10px 30px -10px rgba(0, 0, 0, 0.5) !important;
            transition: border-color 0.2s ease-in-out;
        }

        [data-testid="stVerticalBlockBorderWrapper"]:hover {
            border-color: #2b3448 !important;
        }

        /* Minimalist Intercom Tab Bar */
        .stTabs [data-baseweb="tab-list"] {
            gap: 6px;
            background-color: #121620;
            padding: 6px;
            border-radius: 12px;
            border: 1px solid #1e2433;
        }
        
        .stTabs [data-baseweb="tab"] {
            height: 40px;
            border-radius: 8px;
            color: #9ca3af;
            font-weight: 500;
            font-size: 0.88rem;
            padding: 0 16px;
            transition: all 0.2s ease;
        }
        
        .stTabs [aria-selected="true"] {
            background-color: #1a202c !important;
            color: #38bdf8 !important;
            border-bottom: 2px solid #38bdf8 !important;
            font-weight: 600;
        }

        /* Typography Headers */
        .intercom-title {
            color: #f8fafc;
            font-size: 1.15rem;
            font-weight: 600;
            letter-spacing: -0.01em;
            margin-bottom: 14px;
            display: flex;
            align-items: center;
            gap: 8px;
        }

        .intercom-subtitle {
            font-size: 0.85rem;
            color: #9ca3af;
            margin-top: -8px;
            margin-bottom: 16px;
        }

        /* Metric & Summary Cards */
        .summary-box {
            background: #181e2b;
            border-radius: 10px;
            padding: 16px;
            border: 1px solid #232b3e;
            border-left: 4px solid #38bdf8;
            height: 100%;
            transition: transform 0.2s ease;
        }

        .summary-label {
            font-size: 0.72rem;
            color: #94a3b8;
            text-transform: uppercase;
            letter-spacing: 0.06em;
            font-weight: 600;
        }

        .summary-val {
            font-size: 1.25rem;
            font-weight: 700;
            color: #f8fafc;
            margin-top: 6px;
            letter-spacing: -0.02em;
        }

        .summary-sub {
            font-size: 0.78rem;
            color: #64748b;
            margin-top: 4px;
            font-weight: 400;
        }

        /* Market Signal Cards */
        .signal-box-pos {
            background: rgba(16, 185, 129, 0.08);
            border: 1px solid rgba(16, 185, 129, 0.25);
            border-radius: 10px;
            padding: 12px 16px;
            margin-bottom: 10px;
            color: #34d399;
            font-weight: 500;
            font-size: 0.88rem;
            line-height: 1.5;
        }

        .signal-box-neg {
            background: rgba(239, 68, 68, 0.08);
            border: 1px solid rgba(239, 68, 68, 0.25);
            border-radius: 10px;
            padding: 12px 16px;
            margin-bottom: 10px;
            color: #f87171;
            font-weight: 500;
            font-size: 0.88rem;
            line-height: 1.5;
        }

        /* Narrative Box */
        .narrative-box {
            background: #181e2b;
            border-left: 4px solid #0284c7;
            border-radius: 10px;
            padding: 18px 20px;
            font-size: 0.95rem;
            line-height: 1.65;
            color: #e2e8f0;
            font-weight: 400;
        }

        /* Color Utility Classes */
        .val-positive { color: #34d399 !important; font-weight: 600; }
        .val-negative { color: #f87171 !important; font-weight: 600; }
        .val-neutral  { color: #fbbf24 !important; font-weight: 600; }

        /* Metric font overrides */
        [data-testid="stMetricValue"] {
            font-size: 1.3rem !important;
            font-weight: 700 !important;
            letter-spacing: -0.02em !important;
        }
        
        [data-testid="stMetricLabel"] {
            font-size: 0.78rem !important;
            color: #94a3b8 !important;
            text-transform: uppercase !important;
            letter-spacing: 0.05em !important;
            font-weight: 600 !important;
        }

        /* Intercom Pill Buttons */
        .stButton>button {
            background: #0284c7 !important;
            color: #ffffff !important;
            border: 1px solid #0369a1 !important;
            border-radius: 8px !important;
            padding: 8px 18px !important;
            font-weight: 500 !important;
            font-size: 0.88rem !important;
            transition: all 0.2s ease !important;
            box-shadow: 0 2px 5px rgba(0,0,0,0.2) !important;
        }
        
        .stButton>button:hover {
            background: #0369a1 !important;
            border-color: #38bdf8 !important;
            box-shadow: 0 4px 12px rgba(2, 132, 199, 0.3) !important;
            color: #ffffff !important;
        }

        /* Secondary Pill Buttons */
        [data-testid="stBaseButton-secondary"] {
            background: #1e293b !important;
            color: #94a3b8 !important;
            border: 1px solid #334155 !important;
        }

        [data-testid="stBaseButton-secondary"]:hover {
            background: #334155 !important;
            color: #f8fafc !important;
        }

        /* News Card Container */
        .news-card-container {
            background: #141824;
            border: 1px solid #1e2638;
            border-radius: 12px;
            padding: 18px;
            margin-bottom: 14px;
            transition: all 0.2s ease;
        }

        .news-card-container:hover {
            border-color: #2b364e;
            background: #181e2d;
        }

        .news-card-title {
            font-size: 1.02rem;
            font-weight: 600;
            color: #f8fafc;
            margin-bottom: 10px;
            line-height: 1.4;
        }

        .news-card-title a {
            color: #38bdf8;
            text-decoration: none;
        }

        .news-card-title a:hover {
            text-decoration: underline;
        }

        .news-card-summary {
            font-size: 0.88rem;
            color: #cbd5e1;
            margin-bottom: 14px;
            line-height: 1.6;
            background: #1a202c;
            padding: 12px 14px;
            border-radius: 8px;
            border-left: 3px solid #0284c7;
        }

        .news-card-meta-row {
            display: flex;
            gap: 24px;
            font-size: 0.82rem;
            color: #94a3b8;
            align-items: center;
        }

        /* Chat Bubbles (Intercom Style) */
        [data-testid="stChatMessage"] {
            background-color: #141824 !important;
            border: 1px solid #1e2638 !important;
            border-radius: 12px !important;
            padding: 12px 16px !important;
            margin-bottom: 12px !important;
        }

        /* Badges */
        .badge-positive {
            background: rgba(16, 185, 129, 0.15);
            color: #34d399;
            padding: 3px 8px;
            border-radius: 6px;
            font-weight: 600;
            font-size: 0.78rem;
        }

        .badge-negative {
            background: rgba(239, 68, 68, 0.15);
            color: #f87171;
            padding: 3px 8px;
            border-radius: 6px;
            font-weight: 600;
            font-size: 0.78rem;
        }

        .badge-neutral {
            background: rgba(245, 158, 11, 0.15);
            color: #fbbf24;
            padding: 3px 8px;
            border-radius: 6px;
            font-weight: 600;
            font-size: 0.78rem;
        }
        </style>
    """, unsafe_allow_html=True)


def render_summary_box(label, value, subtext="", border_color="#38bdf8", val_class=""):
    """
    Renders an Intercom-styled summary card component.
    """
    subtext_html = f'<div class="summary-sub">{subtext}</div>' if subtext else ""
    st.markdown(f"""
        <div class="summary-box" style="border-left-color: {border_color};">
            <div class="summary-label">{label}</div>
            <div class="summary-val {val_class}">{value}</div>
            {subtext_html}
        </div>
    """, unsafe_allow_html=True)


def render_signal_box(text, signal_type="positive"):
    """
    Renders a clean market signal card without tacky emojis.
    """
    box_class = "signal-box-pos" if signal_type == "positive" else "signal-box-neg"
    prefix = "Bullish Indicator — " if signal_type == "positive" else "Bearish Indicator — "
    st.markdown(f'<div class="{box_class}"><strong>{prefix}</strong>{text}</div>', unsafe_allow_html=True)


def render_news_card(title, summary, source, date, url, sentiment_badge=""):
    """
    Renders an executive financial news card with clean metadata.
    """
    st.markdown(f"""
        <div class="news-card-container">
            <div class="news-card-title"><a href="{url}" target="_blank">{title}</a></div>
            <div class="news-card-summary">
                <strong>Executive Summary:</strong><br>{summary}
            </div>
            <div class="news-card-meta-row">
                <div><strong>Sentiment:</strong> {sentiment_badge}</div>
                <div><strong>Source:</strong> <span style="color: #e2e8f0;">{source}</span></div>
                <div><strong>Date:</strong> <span style="color: #e2e8f0;">{date}</span></div>
            </div>
        </div>
    """, unsafe_allow_html=True)
