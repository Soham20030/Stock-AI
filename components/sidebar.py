import streamlit as st
from utils.data_loader import (
    get_available_datasets,
    save_uploaded_dataset,
    delete_dataset
)
from chatbot.memory import ChatbotMemory


def render_sidebar():
    """
    Renders the Intercom-inspired minimalist sidebar.

    Returns:
        str: Selected stock dataset filename (e.g. 'AAPL.csv').
    """
    memory_mgr = ChatbotMemory()

    with st.sidebar:
        st.markdown('<div style="font-size: 1.1rem; font-weight: 700; color: #ffffff; letter-spacing: -0.02em;">Stock AI Intelligence</div>', unsafe_allow_html=True)
        st.caption("Quantitative Market Forecasting")
        st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)

        # Available Datasets Dropdown
        st.subheader("Dataset Manager")
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

        # Upload New Dataset
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

        # Delete Selected Dataset
        if selected_stock:
            with st.expander("Remove Dataset"):
                st.write(f"Remove **{selected_stock}** from workspace?")
                if st.button("Confirm Delete", type="secondary"):
                    delete_dataset(selected_stock)
                    st.success(f"Deleted {selected_stock}!")
                    st.rerun()

    return selected_stock
