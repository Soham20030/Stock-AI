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
    Compiles high-specificity CSS rules directly starting with <style>
    to guarantee Streamlit parses and applies all custom styles immediately to the DOM.
    """
    return f"""<style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

        /* Global Canvas Styling */
        .stApp {{
            background-color: {BG_APP} !important;
            color: {TEXT_PRIMARY} !important;
            font-family: {FONT_FAMILY} !important;
        }}

        p, span, label, div {{
            font-family: {FONT_FAMILY} !important;
        }}
        
        /* Hide Streamlit Native Footers and Header Toolbars */
        header {{visibility: hidden !important;}}
        .stAppDeployButton {{display: none !important;}}
        [data-testid="stAppDeployButton"] {{display: none !important;}}
        [data-testid="stToolbar"] {{visibility: hidden !important;}}
        #MainMenu {{visibility: hidden !important;}}
        footer {{visibility: hidden !important;}}
        
        /* Sidebar Styling (Linear / Notion Inspired) */
        section[data-testid="stSidebar"] {{
            background-color: #0f131a !important;
            border-right: 1px solid {BORDER_COLOR} !important;
        }}

        div[data-testid="stSidebarUserContent"] {{
            padding: 1.2rem 1rem 2rem 1rem !important;
        }}

        /* Modern Card Containers */
        div[data-testid="stVerticalBlockBorderWrapper"] {{
            background-color: {BG_CARD} !important;
            border: 1px solid {BORDER_COLOR} !important;
            border-radius: {RADIUS_LG} !important;
            padding: 20px !important;
            box-shadow: {SHADOW_CARD} !important;
            transition: border-color 0.2s ease, box-shadow 0.2s ease !important;
        }}

        div[data-testid="stVerticalBlockBorderWrapper"]:hover {{
            border-color: #2e384d !important;
            box-shadow: {SHADOW_HOVER} !important;
        }}

        /* STREAMLIT METRIC CARDS (INTERCOM ELEVATED CARDS) */
        div[data-testid="stMetric"] {{
            background: {BG_CARD} !important;
            border: 1px solid {BORDER_COLOR} !important;
            border-radius: {RADIUS_LG} !important;
            padding: 16px 20px !important;
            box-shadow: {SHADOW_CARD} !important;
            transition: transform 0.2s ease, border-color 0.2s ease !important;
        }}

        div[data-testid="stMetric"]:hover {{
            transform: translateY(-2px) !important;
            border-color: {ACCENT_BLUE} !important;
            box-shadow: {SHADOW_HOVER} !important;
        }}

        div[data-testid="stMetricLabel"] {{
            font-size: 0.75rem !important;
            text-transform: uppercase !important;
            letter-spacing: 0.05em !important;
            font-weight: 600 !important;
            color: {TEXT_SECONDARY} !important;
        }}

        div[data-testid="stMetricValue"] {{
            font-size: 1.35rem !important;
            font-weight: 700 !important;
            color: {TEXT_PRIMARY} !important;
            margin-top: 4px !important;
        }}

        div[data-testid="stMetricDelta"] {{
            font-size: 0.82rem !important;
            font-weight: 600 !important;
        }}

        /* Navigation Tabs Styling (Intercom Style) */
        div[data-baseweb="tab-list"] {{
            gap: 8px !important;
            background-color: {BG_CARD} !important;
            padding: 8px 12px !important;
            border-radius: {RADIUS_MD} !important;
            border: 1px solid {BORDER_COLOR} !important;
        }}
        
        button[data-baseweb="tab"] {{
            height: 42px !important;
            white-space: pre-wrap !important;
            border-radius: {RADIUS_SM} !important;
            color: {TEXT_SECONDARY} !important;
            font-weight: 600 !important;
            font-size: 0.88rem !important;
            padding: 0 16px !important;
            border: none !important;
            background-color: transparent !important;
            transition: all 0.2s ease !important;
        }}

        button[data-baseweb="tab"]:hover {{
            color: {TEXT_PRIMARY} !important;
            background-color: #1a202c80 !important;
        }}
        
        button[data-baseweb="tab"][aria-selected="true"] {{
            background-color: {BG_SUBCARD} !important;
            color: {ACCENT_BLUE_LIGHT} !important;
            border-bottom: 2px solid {ACCENT_BLUE_LIGHT} !important;
        }}

        /* Selectboxes & Controls */
        div[data-baseweb="select"] > div {{
            background-color: {BG_SUBCARD} !important;
            border: 1px solid {BORDER_COLOR} !important;
            border-radius: {RADIUS_MD} !important;
            color: {TEXT_PRIMARY} !important;
        }}
        
        /* Section Titles & Accent Headings */
        .vesper-title {{
            color: {ACCENT_BLUE_LIGHT};
            font-size: 1.05rem;
            font-weight: 600;
            margin-bottom: 14px;
            letter-spacing: -0.01em;
        }}

        /* Summary Info Grid Cards */
        .summary-box {{
            background: {BG_SUBCARD};
            border-radius: {RADIUS_MD};
            padding: 16px;
            border-left: 3px solid {ACCENT_BLUE_LIGHT};
            height: 100%;
            transition: transform 0.2s ease;
        }}

        .summary-box:hover {{
            transform: translateY(-2px);
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
            padding: 12px 16px;
            margin-bottom: 8px;
            color: #6ee7b7;
            font-weight: 600;
            font-size: 0.9rem;
        }}

        .signal-box-neg {{
            background: rgba(244, 63, 94, 0.08);
            border: 1px solid {ACCENT_RED};
            border-radius: {RADIUS_MD};
            padding: 12px 16px;
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
            padding: 18px;
            font-size: 1.02rem;
            line-height: 1.6;
            color: #f1f5f9;
        }}

        /* Utility Classes for Color Coding */
        .val-positive {{ color: {ACCENT_GREEN} !important; font-weight: 700; }}
        .val-negative {{ color: {ACCENT_RED} !important; font-weight: 700; }}
        .val-neutral  {{ color: {ACCENT_AMBER} !important; font-weight: 700; }}

        /* Standard Main Buttons (Intercom Pill Buttons) */
        div[data-testid="stMainBlockContainer"] .stButton>button,
        section[data-testid="stSidebar"] .stButton>button {{
            background: linear-gradient(135deg, {ACCENT_BLUE} 0%, #0369a1 100%) !important;
            color: #ffffff !important;
            border: none !important;
            border-radius: {RADIUS_MD} !important;
            padding: 10px 22px !important;
            font-weight: 600 !important;
            font-size: 0.9rem !important;
            width: 100% !important;
            transition: all 0.2s ease !important;
        }}

        div[data-testid="stMainBlockContainer"] .stButton>button:hover,
        section[data-testid="stSidebar"] .stButton>button:hover {{
            background: linear-gradient(135deg, {ACCENT_BLUE_LIGHT} 0%, {ACCENT_BLUE} 100%) !important;
            box-shadow: 0 0 14px rgba(56, 189, 248, 0.35) !important;
            color: #ffffff !important;
        }}

        /* Fix Streamlit File Uploader & Expander Button Icon Alignment */
        [data-testid="stFileUploader"] button {{
            background: {BG_SUBCARD} !important;
            border: 1px solid {BORDER_COLOR} !important;
            color: {TEXT_PRIMARY} !important;
            padding: 6px 14px !important;
            border-radius: {RADIUS_SM} !important;
            font-size: 0.85rem !important;
            box-shadow: none !important;
            width: auto !important;
        }}

        details[data-testid="stExpander"] summary {{
            color: {TEXT_PRIMARY} !important;
            font-size: 0.9rem !important;
            font-weight: 600 !important;
        }}

        details[data-testid="stExpander"] summary span {{
            color: {TEXT_PRIMARY} !important;
        }}

        /* Market News Card */
        .news-card-container {{
            background: {BG_CARD};
            border: 1px solid {BORDER_COLOR};
            border-radius: {RADIUS_LG};
            padding: 20px;
            margin-bottom: 16px;
            box-shadow: {SHADOW_CARD};
            transition: border-color 0.2s ease, transform 0.2s ease;
        }}

        .news-card-container:hover {{
            border-color: #2e384d;
            transform: translateY(-2px);
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
            line-height: 1.55;
            background: {BG_SUBCARD};
            padding: 14px 16px;
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
        div[data-testid="stChatMessage"] {{
            background-color: {BG_CARD} !important;
            border: 1px solid {BORDER_COLOR} !important;
            border-radius: {RADIUS_LG} !important;
            padding: 14px 18px !important;
            margin-bottom: 12px !important;
        }}

        div[data-testid="stChatInput"] {{
            background-color: {BG_SUBCARD} !important;
            border: 1px solid {BORDER_COLOR} !important;
            border-radius: {RADIUS_MD} !important;
        }}
        </style>
    """
