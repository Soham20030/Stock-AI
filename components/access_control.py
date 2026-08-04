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
    Renders an Intercom-style segmented mode control switcher bar ([ User ] | [ Developer ]).
    Allows instant mode switching and re-renders the dashboard layout.
    """
    current_mode = get_mode()
    
    col_title, col_toggle = st.columns([3, 1.2])
    
    with col_toggle:
        m_u_col, m_d_col = st.columns(2)
        
        with m_u_col:
            u_type = "primary" if is_user_mode() else "secondary"
            if st.button("User", type=u_type, key="btn_mode_user"):
                if not is_user_mode():
                    set_mode(MODE_USER)
                    st.rerun()

        with m_d_col:
            d_type = "primary" if is_developer_mode() else "secondary"
            if st.button("Developer", type=d_type, key="btn_mode_dev"):
                if not is_developer_mode():
                    set_mode(MODE_DEVELOPER)
                    st.rerun()

    st.markdown("<div style='height: 4px;'></div>", unsafe_allow_html=True)


def get_allowed_navigation_options():
    """
    Returns the list of navigation options allowed for the active mode.

    User Mode:
        - Historical Data
        - Forecast Engine
        - Market News
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
        # Hide technical ML engineer tabs in User Mode
        return [opt for opt in all_options if opt not in ["Model Comparison", "Training History"]]

    return all_options
