import streamlit as st
from state.mode_manager import is_light_theme


def inject_custom_css():
    """
    Injects authentic Intercom-inspired minimalist styling with full Dark / Light mode theme support.
    Enforces 100% contrast readability for all text, sidebars, charts, borders, and inputs.
    """
    light_mode = is_light_theme()

    if light_mode:
        # ---------------------------------------------------------------------
        # INTERCOM LIGHT MODE THEME PALETTE (High Contrast Black Borders)
        # ---------------------------------------------------------------------
        bg_app = "#f1f5f9"
        text_main = "#0f172a"
        text_muted = "#334155"
        surface_bg = "#ffffff"
        border_color = "#000000"
        hover_border = "#000000"
        sidebar_bg = "#ffffff"
        card_bg = "#f8fafc"
        card_border = "#000000"
        btn_sec_bg = "#e2e8f0"
        btn_sec_text = "#0f172a"
        btn_sec_border = "#000000"
        shadow_box = "0 2px 8px rgba(0, 0, 0, 0.05)"
        chat_user_bg = "#e2e8f0"
        chat_user_text = "#0f172a"
        chat_bot_bg = "#ffffff"
        chat_bot_text = "#0f172a"
        input_bg = "#ffffff"
        input_border = "#000000"
        badge_off_bg = "#e2e8f0"
        badge_off_text = "#0f172a"
    else:
        # ---------------------------------------------------------------------
        # INTERCOM DARK MODE THEME PALETTE
        # ---------------------------------------------------------------------
        bg_app = "#090a0c"
        text_main = "#f3f4f6"
        text_muted = "#8f9bba"
        surface_bg = "#0f1115"
        border_color = "#1a1d24"
        hover_border = "#242933"
        sidebar_bg = "#0c0e12"
        card_bg = "#14171f"
        card_border = "#1e222d"
        btn_sec_bg = "#14171f"
        btn_sec_text = "#8f9bba"
        btn_sec_border = "#1e222d"
        shadow_box = "none"
        chat_user_bg = "#1a202c"
        chat_user_text = "#f8fafc"
        chat_bot_bg = "#121620"
        chat_bot_text = "#e2e8f0"
        input_bg = "#121620"
        input_border = "#1e2433"
        badge_off_bg = "#1e2433"
        badge_off_text = "#94a3b8"

    st.markdown(f"""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

        /* Global background & typography */
        .stApp {{
            background-color: {bg_app} !important;
            color: {text_main} !important;
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif !important;
        }}

        /* Hide Deploy button and Footer, keep Header & Sidebar toggle arrow 100% visible */
        .stAppDeployButton {{display: none !important;}}
        [data-testid="stAppDeployButton"] {{display: none !important;}}
        #MainMenu {{visibility: hidden;}}
        footer {{visibility: hidden;}}

        /* Ensure Streamlit Header container is positioned cleanly */
        header[data-testid="stHeader"] {{
            background-color: transparent !important;
            height: 0px !important;
            z-index: 99999 !important;
        }}

        /* Zero out top margin/padding to attach navbar directly to the top edge */
        .block-container {{
            padding-top: 1rem !important;
            padding-bottom: 2rem !important;
        }}

        /* Sidebar Expand & Collapse toggle buttons */
        [data-testid="stSidebarCollapsedControl"],
        [data-testid="stSidebarExpandButton"],
        [data-testid="stSidebarCollapseButton"],
        button[aria-label="Expand sidebar"],
        button[aria-label="Collapse sidebar"] {{
            display: flex !important;
            visibility: visible !important;
            opacity: 1 !important;
            color: {text_main} !important;
            background-color: {card_bg} !important;
            border: 1.5px solid {border_color} !important;
            border-radius: 8px !important;
            padding: 4px 8px !important;
            margin: 8px !important;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1) !important;
        }}

        [data-testid="stSidebarCollapsedControl"]:hover,
        button[aria-label="Expand sidebar"]:hover {{
            background-color: {btn_sec_bg} !important;
            border-color: #6366f1 !important;
            color: #6366f1 !important;
        }}

        /* Minimalist Surface Containers & Section Borders Across ENTIRE Dashboard */
        div[data-testid="stVerticalBlockBorderWrapper"],
        [data-testid="stVerticalBlockBorderWrapper"],
        .element-container [data-testid="stVerticalBlockBorderWrapper"],
        div[data-testid="stVerticalBlock"] > div[style*="border"],
        div[data-testid="stVerticalBlockBorderWrapper"] > div {{
            background: {surface_bg} !important;
            border: 1.5px solid {border_color} !important;
            border-radius: 12px !important;
            padding: 18px 20px !important;
            box-shadow: {shadow_box} !important;
            transition: border-color 0.2s ease;
        }}

        div[data-testid="stVerticalBlockBorderWrapper"]:hover,
        [data-testid="stVerticalBlockBorderWrapper"]:hover {{
            border-color: {hover_border} !important;
        }}

        /* Sidebar Container & Typography */
        [data-testid="stSidebar"] {{
            background-color: {sidebar_bg} !important;
            border-right: 1px solid {border_color} !important;
        }}

        [data-testid="stSidebar"] *, 
        [data-testid="stSidebar"] label,
        [data-testid="stSidebar"] span,
        [data-testid="stSidebar"] p,
        [data-testid="stSidebar"] div {{
            color: {text_main} !important;
        }}

        [data-testid="stSidebar"] caption {{
            color: {text_muted} !important;
        }}

        /* Radio Options text across the app */
        div[data-testid="stRadio"] label,
        div[data-testid="stRadio"] label span,
        div[data-testid="stRadio"] label p {{
            color: {text_main} !important;
        }}

        /* HIDE DEFAULT RADIO CIRCLE DOTS IN SIDEBAR MENU */
        div[aria-label="Dashboard Navigation"] div[role="radiogroup"] label > div:first-child {{
            display: none !important;
        }}

        /* STYLE SIDEBAR VERTICAL MENU ITEMS AS SLEEK RECTANGULAR SAAS BUTTONS */
        div[aria-label="Dashboard Navigation"] div[role="radiogroup"] label {{
            background: transparent !important;
            border-radius: 8px !important;
            padding: 9px 14px !important;
            margin-bottom: 3px !important;
            transition: all 0.2s ease !important;
            cursor: pointer !important;
            border: 1px solid transparent !important;
            color: {text_muted} !important;
            font-size: 0.86rem !important;
            font-weight: 500 !important;
            display: block !important;
        }}

        div[aria-label="Dashboard Navigation"] div[role="radiogroup"] label:hover {{
            background-color: {card_bg} !important;
            color: {text_main} !important;
            border-color: {border_color} !important;
        }}

        /* ACTIVE SELECTED SIDEBAR MENU ITEM */
        div[aria-label="Dashboard Navigation"] div[role="radiogroup"] label[data-checked="true"] {{
            background-color: #6366f1 !important;
            color: #ffffff !important;
            font-weight: 600 !important;
            box-shadow: 0 4px 12px rgba(99, 102, 241, 0.2) !important;
        }}

        div[aria-label="Dashboard Navigation"] div[role="radiogroup"] label[data-checked="true"] * {{
            color: #ffffff !important;
        }}

        /* Typography & Section Titles */
        .intercom-title {{
            font-size: 1.05rem;
            font-weight: 700;
            color: {text_main} !important;
            letter-spacing: -0.01em;
            margin-bottom: 12px;
        }}

        /* Summary Cards */
        .summary-box {{
            background: {card_bg};
            border: 1px solid {card_border};
            border-radius: 10px;
            padding: 14px 16px;
            box-shadow: {shadow_box};
            transition: transform 0.15s ease, border-color 0.15s ease;
        }}

        .summary-box:hover {{
            border-color: {hover_border};
        }}

        .summary-label {{
            font-size: 0.72rem;
            font-weight: 600;
            color: {text_muted} !important;
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }}

        .summary-val {{
            font-size: 0.95rem;
            font-weight: 700;
            color: {text_main} !important;
            margin-top: 4px;
            letter-spacing: -0.01em;
            white-space: nowrap;
            overflow: visible;
        }}

        .summary-sub {{
            font-size: 0.74rem;
            color: {text_muted} !important;
            margin-top: 2px;
            font-weight: 400;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
        }}

        /* Minimalist Market Signal Cards */
        .signal-box-pos {{
            background: rgba(16, 185, 129, 0.1);
            border: 1px solid rgba(16, 185, 129, 0.3);
            border-radius: 8px;
            padding: 10px 14px;
            margin-bottom: 8px;
            color: #047857;
            font-weight: 600;
            font-size: 0.86rem;
            line-height: 1.5;
        }}

        .signal-box-neg {{
            background: rgba(239, 68, 68, 0.1);
            border: 1px solid rgba(239, 68, 68, 0.3);
            border-radius: 8px;
            padding: 10px 14px;
            margin-bottom: 8px;
            color: #b91c1c;
            font-weight: 600;
            font-size: 0.86rem;
            line-height: 1.5;
        }}

        /* Narrative Callout Box */
        .narrative-box {{
            background: {card_bg};
            border: 1px solid {card_border};
            border-left: 3px solid #6366f1;
            border-radius: 10px;
            padding: 16px 18px;
            font-size: 0.92rem;
            line-height: 1.6;
            color: {text_main} !important;
            font-weight: 400;
        }}

        /* Color Utility Classes */
        .val-positive {{ color: #059669 !important; font-weight: 600; }}
        .val-negative {{ color: #dc2626 !important; font-weight: 600; }}
        .val-neutral  {{ color: #d97706 !important; font-weight: 600; }}

        /* Metric font overrides */
        [data-testid="stMetricValue"] {{
            font-size: 1.25rem !important;
            font-weight: 700 !important;
            color: {text_main} !important;
            letter-spacing: -0.02em !important;
        }}
        
        [data-testid="stMetricLabel"] {{
            font-size: 0.75rem !important;
            color: {text_muted} !important;
            text-transform: uppercase !important;
            letter-spacing: 0.05em !important;
            font-weight: 600 !important;
        }}

        [data-testid="stMetricDelta"] {{
            color: {badge_off_text} !important;
        }}

        [data-testid="stMetricDelta"] > div {{
            background-color: {badge_off_bg} !important;
            color: {badge_off_text} !important;
            padding: 2px 8px !important;
            border-radius: 9999px !important;
            font-weight: 600 !important;
        }}

        /* Intercom Signature Full-Pill Buttons */
        .stButton>button {{
            background: #6366f1 !important;
            color: #ffffff !important;
            border: none !important;
            border-radius: 9999px !important;
            padding: 8px 20px !important;
            font-weight: 500 !important;
            font-size: 0.85rem !important;
            transition: all 0.2s ease !important;
        }}
        
        .stButton>button:hover {{
            background: #4f46e5 !important;
            color: #ffffff !important;
            box-shadow: 0 4px 12px rgba(99, 102, 241, 0.25) !important;
        }}

        /* Secondary Pill Buttons */
        [data-testid="stBaseButton-secondary"] {{
            background: {btn_sec_bg} !important;
            color: {btn_sec_text} !important;
            border: 1px solid {btn_sec_border} !important;
            border-radius: 9999px !important;
        }}

        [data-testid="stBaseButton-secondary"]:hover {{
            background: {card_bg} !important;
            color: {text_main} !important;
            border-color: #6366f1 !important;
        }}

        /* Flat News Card Container */
        .news-card-container {{
            background: {card_bg};
            border: 1px solid {card_border};
            border-radius: 10px;
            padding: 16px;
            margin-bottom: 12px;
            box-shadow: {shadow_box};
            transition: border-color 0.2s ease;
        }}

        .news-card-container:hover {{
            border-color: {hover_border};
        }}

        .news-card-title {{
            font-size: 0.98rem;
            font-weight: 600;
            color: {text_main};
            margin-bottom: 8px;
            line-height: 1.4;
        }}

        .news-card-title a {{
            color: #6366f1 !important;
            text-decoration: none;
        }}

        .news-card-title a:hover {{
            text-decoration: underline;
        }}

        .news-card-summary {{
            font-size: 0.86rem;
            color: {text_main} !important;
            margin-bottom: 12px;
            line-height: 1.55;
            background: {surface_bg};
            padding: 10px 12px;
            border-radius: 8px;
            border: 1px solid {card_border};
        }}

        .news-card-meta-row {{
            display: flex;
            gap: 20px;
            font-size: 0.8rem;
            color: {text_muted} !important;
            align-items: center;
        }}

        /* Intercom Custom Chat Interface & Typed Text Visibility */
        .chat-user-bubble {{
            background: {chat_user_bg};
            border: 1px solid {card_border};
            border-radius: 14px 14px 2px 14px;
            padding: 12px 16px;
            margin-left: auto;
            max-width: 80%;
            color: {chat_user_text} !important;
            font-size: 0.9rem;
            line-height: 1.5;
            margin-bottom: 12px;
        }}

        .chat-assistant-bubble {{
            background: {chat_bot_bg};
            border: 1px solid {card_border};
            border-left: 3px solid #6366f1;
            border-radius: 2px 14px 14px 14px;
            padding: 14px 18px;
            max-width: 88%;
            color: {chat_bot_text} !important;
            font-size: 0.9rem;
            line-height: 1.6;
            margin-bottom: 16px;
        }}

        /* Streamlit Chat Input Box & Text Field Override */
        [data-testid="stChatInput"] {{
            border-radius: 9999px !important;
            border: 1px solid {input_border} !important;
            background: {input_bg} !important;
            box-shadow: {shadow_box} !important;
        }}

        [data-testid="stChatInput"] input,
        [data-testid="stChatInput"] textarea {{
            color: {text_main} !important;
            background-color: transparent !important;
        }}

        /* Selectboxes, Dropdown Inputs and Option Menus */
        div[data-testid="stSelectbox"] label,
        div[data-testid="stSelectbox"] p,
        div[data-testid="stSelectbox"] span {{
            color: {text_main} !important;
            font-weight: 600 !important;
        }}

        div[data-testid="stSelectbox"] > div,
        div[data-testid="stSelectbox"] > div > div,
        div[data-testid="stSelectbox"] div[role="combobox"],
        div[data-testid="stSelectbox"] div[role="button"],
        div[data-baseweb="select"],
        div[data-baseweb="select"] > div,
        div[data-baseweb="select"] > div > div,
        div[data-baseweb="select"] div[role="combobox"],
        div[data-baseweb="select"] div[role="button"] {{
            background-color: {card_bg} !important;
            background: {card_bg} !important;
            border: 1.5px solid {border_color} !important;
            border-radius: 8px !important;
        }}

        div[data-baseweb="select"] *,
        div[data-baseweb="select"] span,
        div[data-baseweb="select"] p,
        div[data-baseweb="select"] div,
        div[data-baseweb="select"] svg {{
            color: {text_main} !important;
            fill: {text_main} !important;
            font-weight: 600 !important;
        }}

        /* Dropdown Popup Menu List Items */
        ul[data-baseweb="menu"],
        div[data-baseweb="popover"] ul {{
            background-color: {surface_bg} !important;
            border: 1.5px solid {border_color} !important;
            border-radius: 8px !important;
        }}

        li[data-baseweb="option"],
        div[data-baseweb="popover"] li {{
            background-color: {surface_bg} !important;
            color: {text_main} !important;
            font-weight: 500 !important;
        }}

        li[data-baseweb="option"]:hover,
        div[data-baseweb="popover"] li:hover {{
            background-color: {btn_sec_bg} !important;
            color: #6366f1 !important;
        }}

        /* Pill Badges */
        .badge-positive {{
            background: rgba(16, 185, 129, 0.15);
            color: #059669;
            padding: 2px 10px;
            border-radius: 9999px;
            font-weight: 600;
            font-size: 0.76rem;
        }}

        .badge-negative {{
            background: rgba(239, 68, 68, 0.15);
            color: #dc2626;
            padding: 2px 10px;
            border-radius: 9999px;
            font-weight: 600;
            font-size: 0.76rem;
        }}

        .badge-neutral {{
            background: rgba(245, 158, 11, 0.15);
            color: #d97706;
            padding: 2px 10px;
            border-radius: 9999px;
            font-weight: 600;
            font-size: 0.76rem;
        }}
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
                <div>Source: <span>{source}</span></div>
                <div>Date: <span>{date}</span></div>
            </div>
        </div>
    """, unsafe_allow_html=True)
