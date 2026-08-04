import streamlit as st
from styles.custom_css import get_custom_css
from styles.theme import ACCENT_BLUE_LIGHT, ACCENT_GREEN, ACCENT_RED, ACCENT_AMBER


def inject_custom_css():
    """
    Injects the centralized Intercom + Linear + Stripe inspired dark mode CSS rules into Streamlit.
    """
    st.markdown(get_custom_css(), unsafe_allow_html=True)


def render_summary_box(label, value, subtext="", border_color=ACCENT_BLUE_LIGHT, val_class=""):
    """
    Renders an executive Vesper/Intercom summary card component.

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
