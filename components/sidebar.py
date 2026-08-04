import streamlit as st
from utils.data_loader import (
    get_available_datasets,
    save_uploaded_dataset,
    delete_dataset
)
from chatbot.memory import ChatbotMemory
from state.mode_manager import is_developer_mode
from components.access_control import get_allowed_navigation_options


from performance.profiler import profile_step


@profile_step("Sidebar Rendering")
def render_sidebar():
    """
    Renders the Intercom-inspired mode-aware sidebar.

    User Mode:
        - Mode-filtered vertical navigation
        - Asset selector dropdown

    Developer Mode:
        - Full vertical navigation
        - Asset selector dropdown
        - CSV Dataset Uploader
        - Dataset Eraser expander

    Returns:
        tuple: (selected_stock, active_tab)
    """
    memory_mgr = ChatbotMemory()

    with st.sidebar:
        st.markdown('<div style="font-size: 1.15rem; font-weight: 700; color: #ffffff; letter-spacing: -0.02em;">Stock AI Intelligence</div>', unsafe_allow_html=True)
        mode_label = "Developer Suite" if is_developer_mode() else "Quantitative Analytics"
        st.caption(mode_label)
        st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)

        # ---------------------------------------------------------------------
        # 1. MODE-FILTERED NAVIGATION MENU
        # ---------------------------------------------------------------------
        st.markdown("<div style='font-size: 0.72rem; font-weight: 700; color: #8f9bba; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 6px;'>Navigation</div>", unsafe_allow_html=True)
        
        allowed_options = get_allowed_navigation_options()
        
        active_tab = st.radio(
            "Dashboard Navigation",
            options=allowed_options,
            index=0,
            label_visibility="collapsed",
            key="sidebar_nav_menu"
        )

        st.markdown("<div style='height: 16px; border-bottom: 1px solid #1a1d24; margin-bottom: 16px;'></div>", unsafe_allow_html=True)

        # ---------------------------------------------------------------------
        # 2. DATASET SELECTOR
        # ---------------------------------------------------------------------
        st.markdown("<div style='font-size: 0.72rem; font-weight: 700; color: #8f9bba; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 6px;'>Asset Selection</div>", unsafe_allow_html=True)
        datasets = get_available_datasets()
        
        if datasets:
            selected_stock = st.selectbox(
                "Select Asset Dataset",
                options=datasets,
                index=0,
                help="Choose a pre-loaded or uploaded CSV dataset."
            )
        else:
            selected_stock = None
            st.warning("No datasets found in datasets/ directory.")

        # Detect REAL Stock Switch only (prevents clearing history on simple page refresh F5)
        if st.session_state.get("current_stock") is None:
            st.session_state["current_stock"] = selected_stock
        elif st.session_state["current_stock"] != selected_stock:
            st.session_state["current_stock"] = selected_stock
            st.session_state["all_forecasts"] = {}
            st.session_state["current_forecast"] = None
            st.session_state["model_history"] = {}
            st.cache_data.clear()      # Clear data cache on stock switch
            memory_mgr.clear_memory()  # Reset chat history only when switching tickers

        # ---------------------------------------------------------------------
        # 3. DEVELOPER MODE ONLY: DATASET MANAGEMENT (UPLOAD & DELETE)
        # ---------------------------------------------------------------------
        if is_developer_mode():
            st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)
            st.markdown("<div style='font-size: 0.72rem; font-weight: 700; color: #8f9bba; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 6px;'>Dataset Management</div>", unsafe_allow_html=True)
            
            uploaded_file = st.file_uploader(
                "Upload CSV Data",
                type=["csv"],
                help="CSV must contain 'Date' and 'Close' columns."
            )
            
            if uploaded_file is not None:
                if st.button("Save Dataset"):
                    saved_name = save_uploaded_dataset(uploaded_file)
                    st.success(f"Saved {saved_name}!")
                    st.rerun()

            if selected_stock:
                with st.expander("Remove Dataset"):
                    st.write(f"Remove **{selected_stock}** from workspace?")
                    if st.button("Confirm Delete", type="secondary"):
                        delete_dataset(selected_stock)
                        st.success(f"Deleted {selected_stock}!")
                        st.rerun()

    return selected_stock, active_tab
