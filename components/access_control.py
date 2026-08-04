import streamlit as st
from state.mode_manager import (
    get_mode,
    set_mode,
    is_user_mode,
    is_developer_mode,
    is_dark_theme,
    toggle_theme,
    MODE_USER,
    MODE_DEVELOPER
)


def render_mode_switcher():
    """
    Renders an executive Intercom-styled navigation bar at the top of the app,
    featuring title branding on the left, mode switcher pills, and a Dark/Light theme toggle button.
    """
    with st.container(border=True):
        n_left, n_right = st.columns([2.2, 1.8])
        
        with n_left:
            st.markdown("""
                <div style="padding: 2px 0;">
                    <div style="display: flex; align-items: center; gap: 10px;">
                        <span style="font-size: 1.2rem; font-weight: 700; letter-spacing: -0.02em;">Market Intelligence & Forecasting</span>
                        <span style="background: rgba(99, 102, 241, 0.15); color: #6366f1; font-size: 0.72rem; font-weight: 700; padding: 2px 8px; border-radius: 9999px;">Enterprise AI</span>
                    </div>
                    <div style="font-size: 0.8rem; opacity: 0.7; margin-top: 2px;">Time-series predictive modeling, evaluation benchmarks, and RAG contextual analysis</div>
                </div>
            """, unsafe_allow_html=True)

        with n_right:
            u_col, d_col, t_col = st.columns([1, 1, 1])
            
            with u_col:
                u_type = "primary" if is_user_mode() else "secondary"
                if st.button("User Mode", type=u_type, key="btn_navbar_user"):
                    if not is_user_mode():
                        set_mode(MODE_USER)
                        st.rerun()

            with d_col:
                d_type = "primary" if is_developer_mode() else "secondary"
                if st.button("Developer", type=d_type, key="btn_navbar_dev"):
                    if not is_developer_mode():
                        set_mode(MODE_DEVELOPER)
                        st.rerun()

            with t_col:
                theme_icon = "☀️ Light" if is_dark_theme() else "🌙 Dark"
                if st.button(theme_icon, type="secondary", key="btn_navbar_theme"):
                    toggle_theme()
                    st.rerun()

    st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)


def get_allowed_navigation_options():
    """
    Returns the list of navigation options allowed for the active mode.

    User Mode:
        - Historical Data
        - Forecast Engine
        - Market News
        - Training History
        - AI Explanation
        - AI Analyst

    Developer Mode:
        - Historical Data
        - Forecast Engine
        - Market News
        - Model Comparison
        - Training History
        - AI Explanation
        - AI Analyst

    Returns:
        list: Allowed tab title strings.
    """
    all_options = [
        "Historical Data",
        "Forecast Engine",
        "Market News",
        "Model Comparison",
        "Training History",
        "AI Explanation",
        "AI Analyst"
    ]

    if is_user_mode():
        # Hide technical model comparison matrix tab in User Mode
        return [opt for opt in all_options if opt != "Model Comparison"]

    return all_options
