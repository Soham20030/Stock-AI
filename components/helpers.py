import streamlit as st


def inject_custom_css():
    """
    Injects the complete Vesper dark mode theme CSS styles for containers,
    tabs, metric badges, signals, and news cards into the Streamlit app.
    """
    st.markdown("""
        <style>
        /* Global background and font styling */
        .stApp {
            background-color: #0b0e14;
            color: #e2e8f0;
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
        }
        
        /* Hide Streamlit Deploy button, Header, MainMenu, and Footer */
        header {visibility: hidden;}
        .stAppDeployButton {display: none !important;}
        [data-testid="stAppDeployButton"] {display: none !important;}
        [data-testid="stToolbar"] {visibility: hidden !important;}
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        
        /* Modern Container Card styling */
        [data-testid="stVerticalBlockBorderWrapper"] {
            background-color: #151921 !important;
            border: 1px solid #232936 !important;
            border-radius: 12px !important;
            padding: 15px !important;
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.4) !important;
        }

        /* Tab navigation styling */
        .stTabs [data-baseweb="tab-list"] {
            gap: 8px;
            background-color: #151921;
            padding: 8px 12px;
            border-radius: 10px;
            border: 1px solid #232936;
        }
        
        .stTabs [data-baseweb="tab"] {
            height: 45px;
            white-space: pre-wrap;
            border-radius: 8px;
            color: #94a3b8;
            font-weight: 600;
            padding: 0 14px;
        }
        
        .stTabs [aria-selected="true"] {
            background-color: #1e293b !important;
            color: #38bdf8 !important;
            border-bottom: 2px solid #38bdf8 !important;
        }
        
        /* Title accent class */
        .vesper-title {
            color: #38bdf8;
            font-size: 1.2rem;
            font-weight: 600;
            margin-bottom: 12px;
        }

        /* Summary info grid items */
        .summary-box {
            background: #1e2430;
            border-radius: 8px;
            padding: 14px;
            border-left: 3px solid #38bdf8;
            height: 100%;
        }
        .summary-label {
            font-size: 0.75rem;
            color: #94a3b8;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            font-weight: 600;
        }
        .summary-val {
            font-size: 1.2rem;
            font-weight: 700;
            color: #f8fafc;
            margin-top: 4px;
        }
        .summary-sub {
            font-size: 0.8rem;
            color: #64748b;
            margin-top: 4px;
        }

        /* Signal Cards */
        .signal-box-pos {
            background: #064e3b20;
            border: 1px solid #10b981;
            border-radius: 8px;
            padding: 10px 14px;
            margin-bottom: 8px;
            color: #6ee7b7;
            font-weight: 600;
            font-size: 0.9rem;
        }

        .signal-box-neg {
            background: #7f1d1d20;
            border: 1px solid #ef4444;
            border-radius: 8px;
            padding: 10px 14px;
            margin-bottom: 8px;
            color: #fca5a5;
            font-weight: 600;
            font-size: 0.9rem;
        }

        /* Narrative Box */
        .narrative-box {
            background: #1e2430;
            border-left: 4px solid #38bdf8;
            border-radius: 8px;
            padding: 16px;
            font-size: 1.05rem;
            line-height: 1.6;
            color: #f1f5f9;
            font-style: italic;
        }

        /* Color coding utility classes */
        .val-positive { color: #10b981 !important; font-weight: 700; }
        .val-negative { color: #ef4444 !important; font-weight: 700; }
        .val-neutral  { color: #f59e0b !important; font-weight: 700; }

        /* Metric font sizing override for compact containers */
        [data-testid="stMetricValue"] {
            font-size: 1.25rem !important;
            white-space: nowrap !important;
            overflow: visible !important;
        }
        
        [data-testid="stMetricLabel"] {
            font-size: 0.8rem !important;
            color: #94a3b8 !important;
        }

        /* Streamlit button styling override */
        .stButton>button {
            background: linear-gradient(135deg, #0284c7 0%, #0369a1 100%);
            color: #ffffff;
            border: none;
            border-radius: 8px;
            padding: 10px 24px;
            font-weight: 600;
            width: 100%;
            transition: all 0.3s ease;
        }
        
        .stButton>button:hover {
            background: linear-gradient(135deg, #38bdf8 0%, #0284c7 100%);
            box-shadow: 0 0 15px rgba(56, 189, 248, 0.4);
            color: #ffffff;
        }

        /* News Card Enhancements */
        .news-card-container {
            background: #151921;
            border: 1px solid #232936;
            border-radius: 10px;
            padding: 16px;
            margin-bottom: 16px;
            box-shadow: 0 4px 15px rgba(0, 0, 0, 0.3);
        }

        .news-card-title {
            font-size: 1.1rem;
            font-weight: 700;
            color: #f8fafc;
            margin-bottom: 8px;
        }

        .news-card-title a {
            color: #38bdf8;
            text-decoration: none;
        }

        .news-card-title a:hover {
            text-decoration: underline;
        }

        .news-card-summary {
            font-size: 0.9rem;
            color: #cbd5e1;
            margin-bottom: 12px;
            line-height: 1.5;
            background: #1e2430;
            padding: 12px 14px;
            border-radius: 6px;
            border-left: 3px solid #0284c7;
        }

        .news-card-meta-row {
            display: flex;
            gap: 24px;
            font-size: 0.85rem;
            color: #94a3b8;
            align-items: center;
        }
        </style>
    """, unsafe_allow_html=True)


def render_summary_box(label, value, subtext="", border_color="#38bdf8", val_class=""):
    """
    Renders a styled Vesper summary card component.

    Parameters:
        label (str): Metric title label.
        value (str): Main metric value string.
        subtext (str): Subtitle or detail description.
        border_color (str): CSS left border color accent.
        val_class (str): Optional value CSS class ('val-positive', 'val-negative', 'val-neutral').
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
    Renders a color-coded market signal card (Bullish/Bearish).

    Parameters:
        text (str): Signal message string.
        signal_type (str): 'positive' (green) or 'negative' (red).
    """
    box_class = "signal-box-pos" if signal_type == "positive" else "signal-box-neg"
    st.markdown(f'<div class="{box_class}">{text}</div>', unsafe_allow_html=True)


def render_news_card(title, summary, source, date, url, sentiment_badge=""):
    """
    Renders an enhanced financial news card with title, summary, source, and sentiment.
    """
    st.markdown(f"""
        <div class="news-card-container">
            <div class="news-card-title">📄 <a href="{url}" target="_blank">{title}</a></div>
            <div class="news-card-summary">
                <strong>Summary:</strong><br>{summary}
            </div>
            <div class="news-card-meta-row">
                <div><strong>Sentiment:</strong> {sentiment_badge}</div>
                <div><strong>Source:</strong> <span style="color: #e2e8f0;">{source}</span></div>
                <div><strong>Date:</strong> <span style="color: #e2e8f0;">{date}</span></div>
            </div>
        </div>
    """, unsafe_allow_html=True)
