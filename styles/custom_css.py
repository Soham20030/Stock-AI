from styles.theme import (
    BG_APP,
    BG_CARD,
    BG_SUBCARD,
    BORDER_COLOR,
    ACCENT_BLUE,
    ACCENT_BLUE_LIGHT,
    ACCENT_GREEN,
    ACCENT_RED,
    ACCENT_AMBER,
    TEXT_PRIMARY,
    TEXT_SECONDARY,
    TEXT_MUTED,
    FONT_FAMILY,
    RADIUS_SM,
    RADIUS_MD,
    RADIUS_LG,
    SHADOW_CARD,
    SHADOW_HOVER
)


def get_custom_css():
    """
    Compiles and returns the clean Intercom + Linear + Stripe inspired CSS stylesheet.

    Returns:
        str: Sanitized CSS rules string.
    """
    return f"""
        <style>
        /* Global Canvas Styling */
        .stApp {{
            background-color: {BG_APP};
            color: {TEXT_PRIMARY};
            font-family: {FONT_FAMILY};
        }}
        
        /* Hide Streamlit Native Footers and Header Toolbars */
        header {{visibility: hidden;}}
        .stAppDeployButton {{display: none !important;}}
        [data-testid="stAppDeployButton"] {{display: none !important;}}
        [data-testid="stToolbar"] {{visibility: hidden !important;}}
        #MainMenu {{visibility: hidden;}}
        footer {{visibility: hidden;}}
        
        /* Sidebar Styling (Linear / Notion Inspired) */
        [data-testid="stSidebar"] {{
            background-color: #0f131a !important;
            border-right: 1px solid {BORDER_COLOR} !important;
        }}

        /* Modern Card Containers */
        [data-testid="stVerticalBlockBorderWrapper"] {{
            background-color: {BG_CARD} !important;
            border: 1px solid {BORDER_COLOR} !important;
            border-radius: {RADIUS_LG} !important;
            padding: 16px 20px !important;
            box-shadow: {SHADOW_CARD} !important;
            transition: border-color 0.2s ease, box-shadow 0.2s ease;
        }}

        [data-testid="stVerticalBlockBorderWrapper"]:hover {{
            border-color: #2e384d !important;
            box-shadow: {SHADOW_HOVER} !important;
        }}

        /* Navigation Tabs Styling (Intercom Style) */
        .stTabs [data-baseweb="tab-list"] {{
            gap: 6px;
            background-color: {BG_CARD};
            padding: 6px 10px;
            border-radius: {RADIUS_MD};
            border: 1px solid {BORDER_COLOR};
        }}
        
        .stTabs [data-baseweb="tab"] {{
            height: 42px;
            white-space: pre-wrap;
            border-radius: {RADIUS_SM};
            color: {TEXT_SECONDARY};
            font-weight: 600;
            font-size: 0.88rem;
            padding: 0 14px;
            transition: all 0.2s ease;
        }}

        .stTabs [data-baseweb="tab"]:hover {{
            color: {TEXT_PRIMARY};
            background-color: #1a202c50;
        }}
        
        .stTabs [aria-selected="true"] {{
            background-color: {BG_SUBCARD} !important;
            color: {ACCENT_BLUE_LIGHT} !important;
            border-bottom: 2px solid {ACCENT_BLUE_LIGHT} !important;
        }}
        
        /* Section Titles & Accent Headings */
        .vesper-title {{
            color: {ACCENT_BLUE_LIGHT};
            font-size: 1.05rem;
            font-weight: 600;
            margin-bottom: 12px;
            letter-spacing: -0.01em;
        }}

        /* Summary Info Grid Cards */
        .summary-box {{
            background: {BG_SUBCARD};
            border-radius: {RADIUS_MD};
            padding: 14px;
            border-left: 3px solid {ACCENT_BLUE_LIGHT};
            height: 100%;
            transition: transform 0.2s ease;
        }}

        .summary-box:hover {{
            transform: translateY(-1px);
        }}

        .summary-label {{
            font-size: 0.75rem;
            color: {TEXT_SECONDARY};
            text-transform: uppercase;
            letter-spacing: 0.05em;
            font-weight: 600;
        }}

        .summary-val {{
            font-size: 1.25rem;
            font-weight: 700;
            color: {TEXT_PRIMARY};
            margin-top: 4px;
        }}

        .summary-sub {{
            font-size: 0.8rem;
            color: {TEXT_MUTED};
            margin-top: 4px;
        }}

        /* Market Signal Cards */
        .signal-box-pos {{
            background: rgba(16, 185, 129, 0.08);
            border: 1px solid {ACCENT_GREEN};
            border-radius: {RADIUS_MD};
            padding: 10px 14px;
            margin-bottom: 8px;
            color: #6ee7b7;
            font-weight: 600;
            font-size: 0.9rem;
        }}

        .signal-box-neg {{
            background: rgba(244, 63, 94, 0.08);
            border: 1px solid {ACCENT_RED};
            border-radius: {RADIUS_MD};
            padding: 10px 14px;
            margin-bottom: 8px;
            color: #fca5a5;
            font-weight: 600;
            font-size: 0.9rem;
        }}

        /* RAG Narrative Explanation Box */
        .narrative-box {{
            background: {BG_SUBCARD};
            border-left: 4px solid {ACCENT_BLUE_LIGHT};
            border-radius: {RADIUS_MD};
            padding: 16px;
            font-size: 1.02rem;
            line-height: 1.6;
            color: #f1f5f9;
        }}

        /* Utility Classes for Color Coding */
        .val-positive {{ color: {ACCENT_GREEN} !important; font-weight: 700; }}
        .val-negative {{ color: {ACCENT_RED} !important; font-weight: 700; }}
        .val-neutral  {{ color: {ACCENT_AMBER} !important; font-weight: 700; }}

        /* Metric Sizing Overrides */
        [data-testid="stMetricValue"] {{
            font-size: 1.25rem !important;
            white-space: nowrap !important;
            overflow: visible !important;
            color: {TEXT_PRIMARY} !important;
        }}
        
        [data-testid="stMetricLabel"] {{
            font-size: 0.8rem !important;
            color: {TEXT_SECONDARY} !important;
        }}

        /* Action Buttons (Intercom Pill Buttons) */
        .stButton>button {{
            background: linear-gradient(135deg, {ACCENT_BLUE} 0%, #0369a1 100%);
            color: #ffffff;
            border: none;
            border-radius: {RADIUS_MD};
            padding: 9px 20px;
            font-weight: 600;
            font-size: 0.9rem;
            width: 100%;
            transition: all 0.2s ease;
        }}
        
        .stButton>button:hover {{
            background: linear-gradient(135deg, {ACCENT_BLUE_LIGHT} 0%, {ACCENT_BLUE} 100%);
            box-shadow: 0 0 12px rgba(56, 189, 248, 0.3);
            color: #ffffff;
        }}

        /* Market News Card */
        .news-card-container {{
            background: {BG_CARD};
            border: 1px solid {BORDER_COLOR};
            border-radius: {RADIUS_LG};
            padding: 18px;
            margin-bottom: 16px;
            box-shadow: {SHADOW_CARD};
            transition: border-color 0.2s ease;
        }}

        .news-card-container:hover {{
            border-color: #2e384d;
        }}

        .news-card-title {{
            font-size: 1.05rem;
            font-weight: 700;
            color: {TEXT_PRIMARY};
            margin-bottom: 8px;
        }}

        .news-card-title a {{
            color: {ACCENT_BLUE_LIGHT};
            text-decoration: none;
        }}

        .news-card-title a:hover {{
            text-decoration: underline;
        }}

        .news-card-summary {{
            font-size: 0.9rem;
            color: #cbd5e1;
            margin-bottom: 12px;
            line-height: 1.5;
            background: {BG_SUBCARD};
            padding: 12px 14px;
            border-radius: {RADIUS_SM};
            border-left: 3px solid {ACCENT_BLUE};
        }}

        .news-card-meta-row {{
            display: flex;
            gap: 24px;
            font-size: 0.85rem;
            color: {TEXT_SECONDARY};
            align-items: center;
        }}

        /* Chatbot Intercom Bubble Styling */
        .stChatMessage {{
            background-color: {BG_CARD} !important;
            border: 1px solid {BORDER_COLOR} !important;
            border-radius: {RADIUS_LG} !important;
            padding: 12px 16px !important;
            margin-bottom: 12px !important;
        }}

        [data-testid="stChatInput"] {{
            background-color: {BG_SUBCARD} !important;
            border: 1px solid {BORDER_COLOR} !important;
            border-radius: {RADIUS_MD} !important;
        }}
        </style>
    """
