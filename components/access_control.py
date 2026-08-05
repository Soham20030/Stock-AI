import streamlit as st
from state.mode_manager import (
    get_mode,
    is_user_mode,
    is_developer_authenticated,
    authenticate_developer,
    reset_to_user_mode,
    is_dark_theme,
    toggle_theme,
    MODE_USER,
    MODE_DEVELOPER
)


def render_mode_switcher():
    """
    Renders an executive settings-style panel card for User/Developer view mode selection
    and password authentication, matching modern SaaS designs (Stripe, Linear, Notion, Intercom).
    """
    current_authenticated = is_developer_authenticated()
    current_mode = get_mode()

    with st.container(border=True):
        n_left, n_right = st.columns([4, 1])

        with n_left:
            st.markdown("""
                <div style="padding: 2px 0;">
                    <div style="display: flex; align-items: center; gap: 10px;">
                        <span style="font-size: 1.15rem; font-weight: 700; letter-spacing: -0.02em;">Market Intelligence & Forecasting</span>
                        <span style="background: rgba(99, 102, 241, 0.12); color: #6366f1; font-size: 0.72rem; font-weight: 700; padding: 2px 8px; border-radius: 9999px;">Enterprise AI</span>
                    </div>
                    <div style="font-size: 0.8rem; opacity: 0.7; margin-top: 2px;">Time-series predictive modeling, evaluation benchmarks, and RAG contextual analysis</div>
                </div>
            """, unsafe_allow_html=True)

        with n_right:
            st.markdown("""
                <style>
                div[data-testid="stColumn"]:nth-of-type(2) div.stButton {
                    display: flex !important;
                    justify-content: flex-end !important;
                }
                div[data-testid="stColumn"]:nth-of-type(2) div.stButton > button {
                    margin-left: auto !important;
                }
                </style>
            """, unsafe_allow_html=True)
            theme_icon = "☀️ Light" if is_dark_theme() else "🌙 Dark"
            if st.button(theme_icon, type="secondary", key="btn_navbar_theme"):
                toggle_theme()
                st.rerun()

        st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)

        # Settings Card Title: View
        st.markdown("""
            <div style="font-size: 0.75rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.06em; opacity: 0.65; margin-bottom: 6px;">
                View
            </div>
        """, unsafe_allow_html=True)

        default_index = 1 if (current_mode == MODE_DEVELOPER and current_authenticated) else 0

        selected_mode = st.radio(
            "View",
            options=["User", "Developer"],
            index=default_index,
            label_visibility="collapsed",
            key="view_mode_selector"
        )

        # Mode switching logic
        if selected_mode == "User":
            if current_mode == MODE_DEVELOPER or current_authenticated:
                reset_to_user_mode()
                st.rerun()

        elif selected_mode == "Developer":
            if not current_authenticated:
                render_developer_auth_modal()

    st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)


@st.dialog("Unlock Developer Mode")
def render_developer_auth_modal():
    """
    Renders a modern modal dialog pop-up for developer password authentication.
    """
    st.write("Please enter the developer password to access developer suite and features.")
    dev_password = st.text_input(
        "Developer password",
        type="password",
        placeholder="Enter developer password",
        key="input_developer_password_modal"
    )
    st.markdown("<div style='height: 6px;'></div>", unsafe_allow_html=True)

    col_unlock, col_cancel = st.columns([1, 1])
    with col_unlock:
        if st.button("Unlock", type="primary", use_container_width=True, key="btn_unlock_modal"):
            if authenticate_developer(dev_password):
                st.success("Developer mode enabled")
                st.rerun()
            else:
                st.error("Incorrect password")
    with col_cancel:
        if st.button("Cancel", type="secondary", use_container_width=True, key="btn_cancel_modal"):
            reset_to_user_mode()
            st.rerun()


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
