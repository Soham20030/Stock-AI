import streamlit as st
from state.mode_manager import (
    get_mode,
    set_mode,
    is_user_mode,
    is_developer_mode,
    MODE_USER,
    MODE_DEVELOPER
)


def render_mode_switcher():
    """
    Renders an executive Intercom-styled navigation bar at the top of the app,
    featuring title branding on the left and segmented mode switcher pills on the right.
    """
    with st.container():
        n_left, n_right = st.columns([2.5, 1])
        
        with n_left:
            st.markdown("""
                <div style="padding-top: 4px;">
                    <div style="font-size: 1.25rem; font-weight: 700; color: #ffffff; letter-spacing: -0.02em;">Market Intelligence & Forecasting</div>
                    <div style="font-size: 0.8rem; color: #8f9bba;">Time-series predictive modeling, evaluation benchmarks, and RAG contextual analysis</div>
                </div>
            """, unsafe_allow_html=True)

        with n_right:
            st.markdown("<div style='font-size: 0.72rem; font-weight: 700; color: #8f9bba; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 4px; text-align: right;'>Application Mode</div>", unsafe_allow_html=True)
            u_col, d_col = st.columns(2)
            
            with u_col:
                u_type = "primary" if is_user_mode() else "secondary"
                if st.button("User", type=u_type, key="btn_navbar_user"):
                    if not is_user_mode():
                        set_mode(MODE_USER)
                        st.rerun()

            with d_col:
                d_type = "primary" if is_developer_mode() else "secondary"
                if st.button("Developer", type=d_type, key="btn_navbar_dev"):
                    if not is_developer_mode():
                        set_mode(MODE_DEVELOPER)
                        st.rerun()

        st.markdown("<div style='height: 14px; border-bottom: 1px solid #1a1d24; margin-bottom: 20px;'></div>", unsafe_allow_html=True)


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
