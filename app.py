import os
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime

# Import modular helper utilities
from utils.data_loader import (
    get_available_datasets,
    load_dataset,
    save_uploaded_dataset,
    delete_dataset,
    filter_data_by_range
)
from utils.forecasting import run_forecast
from utils.news import fetch_stock_news

# -----------------------------------------------------------------------------
# 1. PAGE CONFIGURATION & CUSTOM CSS (VESPER-INSPIRED DARK THEME)
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="VesperStock | AI Market Forecasting",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS injection for dark mode cards, glowing accents, and modern typography
st.markdown("""
    <style>
    /* Global background and font styling */
    .stApp {
        background-color: #0b0e14;
        color: #e2e8f0;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }
    
    /* Hide Streamlit Deploy button, Header, MainMenu, and Footer */
    header {visibility: hidden;}
    .stAppDeployButton {display: none !important;}
    [data-testid="stAppDeployButton"] {display: none !important;}
    [data-testid="stToolbar"] {visibility: hidden !important;}
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* Modern Card container styling */
    .vesper-card {
        background: #151921;
        border: 1px solid #232936;
        border-radius: 12px;
        padding: 20px;
        margin-bottom: 20px;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.4);
    }
    
    .vesper-card-header {
        font-size: 1.2rem;
        font-weight: 600;
        color: #38bdf8;
        margin-bottom: 15px;
        display: flex;
        align-items: center;
        gap: 8px;
    }
    
    /* Custom metric badge styling */
    .metric-badge {
        background: #1e2430;
        border-left: 4px solid #38bdf8;
        padding: 12px 16px;
        border-radius: 6px;
        margin-bottom: 10px;
    }
    
    .metric-title {
        font-size: 0.8rem;
        color: #94a3b8;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    
    .metric-value {
        font-size: 1.5rem;
        font-weight: 700;
        color: #f8fafc;
    }

    /* Streamlit button styling override */
    .stButton>button {
        background: linear-gradient(135deg, #0284c7 0%, #0369a1 100%);
        color: #ffffff;
        border: none;
        border-radius: 8px;
        padding: 10px 24px;
        font-weight: 600;
        width: 100%;
        transition: all 0.3s ease;
    }
    
    .stButton>button:hover {
        background: linear-gradient(135deg, #38bdf8 0%, #0284c7 100%);
        box-shadow: 0 0 15px rgba(56, 189, 248, 0.4);
        color: #ffffff;
    }

    /* News card styling */
    .news-item {
        border-bottom: 1px solid #232936;
        padding: 10px 0;
    }
    
    .news-title {
        font-size: 0.95rem;
        font-weight: 600;
        color: #e2e8f0;
        text-decoration: none;
    }
    
    .news-title:hover {
        color: #38bdf8;
    }
    
    .news-meta {
        font-size: 0.75rem;
        color: #64748b;
        margin-top: 4px;
    }
    </style>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 2. SESSION STATE INITIALIZATION
# -----------------------------------------------------------------------------
if "model_history" not in st.session_state:
    st.session_state["model_history"] = {}

if "current_forecast" not in st.session_state:
    st.session_state["current_forecast"] = None

if "all_forecasts" not in st.session_state:
    # Stores all forecasts generated in current session: { "Prophet": {...}, "ARIMA": {...}, "LSTM": {...} }
    st.session_state["all_forecasts"] = {}

# -----------------------------------------------------------------------------
# 3. SIDEBAR CONTROLS
# -----------------------------------------------------------------------------
with st.sidebar:
    st.title("⚡ VesperStock AI")
    st.caption("Advanced Time-Series Market Forecasting")
    st.markdown("---")

    # Available Datasets
    st.subheader("📁 Dataset Manager")
    datasets = get_available_datasets()
    
    if datasets:
        selected_stock = st.selectbox(
            "Select Stock / Commodity Data",
            options=datasets,
            index=0,
            help="Choose a pre-loaded or uploaded CSV dataset."
        )
    else:
        selected_stock = None
        st.warning("No datasets found in datasets/ folder.")

    # Upload New Dataset
    uploaded_file = st.file_uploader(
        "Upload CSV Dataset",
        type=["csv"],
        help="CSV must contain 'Date' and 'Close' columns."
    )
    
    if uploaded_file is not None:
        if st.button("Save Uploaded Dataset"):
            saved_name = save_uploaded_dataset(uploaded_file)
            st.success(f"Saved {saved_name}!")
            st.rerun()

    # Delete Selected Dataset
    if selected_stock:
        with st.expander("🗑️ Delete Selected Dataset"):
            st.write(f"Are you sure you want to delete **{selected_stock}**?")
            if st.button("Confirm Delete", type="secondary"):
                delete_dataset(selected_stock)
                st.success(f"Deleted {selected_stock}!")
                st.rerun()

    st.markdown("---")
    st.info("💡 **Tip**: Train multiple models (Prophet, ARIMA, LSTM) to populate the Model Comparison matrix below.")

# -----------------------------------------------------------------------------
# 4. MAIN DASHBOARD CONTENT AREA
# -----------------------------------------------------------------------------

# Title Banner
st.title("📈 Market Intelligence & Forecasting Dashboard")
st.markdown("Real-time historical analysis and predictive AI modelling.")

if not selected_stock:
    st.info("👈 Please select or upload a dataset in the sidebar to get started.")
    st.stop()

# Load Selected Dataset
raw_df = load_dataset(selected_stock)

if raw_df.empty:
    st.error(f"Failed to load data for {selected_stock}. Please check CSV column format ('Date', 'Close').")
    st.stop()

# Layout: 2 Top Cards (Historical Chart + Controls/Forecast)
col_left, col_right = st.columns([2, 1])

# --- LEFT COLUMN: HISTORICAL CHART CARD ---
with col_left:
    st.markdown('<div class="vesper-card">', unsafe_allow_html=True)
    st.markdown(f'<div class="vesper-card-header">📊 Historical Price Action — {selected_stock}</div>', unsafe_allow_html=True)
    
    # Date Range Filter Selector
    range_option = st.radio(
        "Time Range:",
        options=["3 Months", "6 Months", "1 Year", "Max"],
        index=3,
        horizontal=True,
        key="time_range_selector"
    )
    
    # Filter DataFrame by user selection
    filtered_df = filter_data_by_range(raw_df, range_option)
    
    # Create Plotly Historical Price Line Chart
    fig_hist = go.Figure()
    fig_hist.add_trace(
        go.Scatter(
            x=filtered_df["Date"],
            y=filtered_df["Close"],
            mode="lines",
            name="Close Price",
            line=dict(color="#38bdf8", width=2)
        )
    )
    fig_hist.update_layout(
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=10, r=10, t=20, b=20),
        xaxis=dict(showgrid=True, gridcolor="#1e2430", title="Date"),
        yaxis=dict(showgrid=True, gridcolor="#1e2430", title="Price ($)"),
        height=380
    )
    st.plotly_chart(fig_hist, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

# --- RIGHT COLUMN: FORECAST CONTROLS & TRAINING CARD ---
with col_right:
    st.markdown('<div class="vesper-card">', unsafe_allow_html=True)
    st.markdown('<div class="vesper-card-header">🤖 AI Forecast Engine</div>', unsafe_allow_html=True)
    
    model_choice = st.selectbox(
        "Select Forecasting Model:",
        options=["Prophet", "ARIMA", "LSTM"],
        index=0,
        help="Choose between Meta Prophet, Statistical ARIMA, or Deep Learning LSTM."
    )
    
    forecast_days = 90  # Next 3 months (approx 90 days)
    st.write(f"Forecast Horizon: **{forecast_days} Days (3 Months)**")
    
    if st.button("🚀 Train & Forecast"):
        with st.spinner(f"Training {model_choice} model on {selected_stock}..."):
            progress_bar = st.progress(0)
            for percent_complete in range(1, 101, 25):
                progress_bar.progress(percent_complete)
            
            # Execute forecasting via routing layer
            forecast_df, metrics_dict = run_forecast(
                model_name=model_choice,
                df=raw_df,
                forecast_days=forecast_days
            )
            
            progress_bar.progress(100)
            
            forecast_payload = {
                "model": model_choice,
                "df": forecast_df,
                "metrics": metrics_dict,
                "stock": selected_stock
            }
            
            # Save into all_forecasts dictionary as well as current_forecast
            st.session_state["all_forecasts"][model_choice] = forecast_payload
            st.session_state["current_forecast"] = forecast_payload
            st.session_state["model_history"][model_choice] = metrics_dict
            st.success(f"Training Complete for {model_choice}!")
            
    # Display Latest Metrics summary if available
    if st.session_state["current_forecast"] is not None:
        curr_metrics = st.session_state["current_forecast"]["metrics"]
        m_col1, m_col2, m_col3 = st.columns(3)
        m_col1.metric("RMSE", f"{curr_metrics.get('RMSE', 0):.2f}")
        m_col2.metric("MAE", f"{curr_metrics.get('MAE', 0):.2f}")
        m_col3.metric("MAPE", f"{curr_metrics.get('MAPE', 0):.2f}%")
        
    st.markdown('</div>', unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 5. FORECAST RESULTS CHART CARD (MULTI-MODEL PERSISTENT VIEW)
# -----------------------------------------------------------------------------
if st.session_state["all_forecasts"]:
    st.markdown('<div class="vesper-card">', unsafe_allow_html=True)
    st.markdown(
        f'<div class="vesper-card-header">🔮 3-Month Price Projections ({selected_stock})</div>',
        unsafe_allow_html=True
    )
    
    # Model Selector Tabs / Radio
    available_models = list(st.session_state["all_forecasts"].keys())
    view_options = available_models.copy()
    if len(available_models) > 1:
        view_options.append("Combined Comparison")
        
    selected_view = st.radio(
        "View Model Projection:",
        options=view_options,
        index=0,
        horizontal=True,
        key="forecast_view_selector"
    )
    
    fig_fc = go.Figure()
    
    color_map = {
        "Prophet": "#38bdf8",   # Cyan
        "ARIMA": "#f97316",     # Orange
        "LSTM": "#10b981"       # Emerald Green
    }
    
    if selected_view == "Combined Comparison":
        # Plot historical price once
        first_df = list(st.session_state["all_forecasts"].values())[0]["df"]
        hist_mask = first_df["type"] == "Historical"
        fig_fc.add_trace(go.Scatter(
            x=first_df.loc[hist_mask, "Date"],
            y=first_df.loc[hist_mask, "Price"],
            mode="lines",
            name="Historical Price",
            line=dict(color="#94a3b8", width=2)
        ))
        
        # Overlay forecast lines for all trained models
        for m_name, m_data in st.session_state["all_forecasts"].items():
            m_df = m_data["df"]
            pred_mask = m_df["type"] == "Forecast"
            fig_fc.add_trace(go.Scatter(
                x=m_df.loc[pred_mask, "Date"],
                y=m_df.loc[pred_mask, "Price"],
                mode="lines",
                name=f"{m_name} Forecast",
                line=dict(color=color_map.get(m_name, "#a855f7"), width=3, dash="dash")
            ))
    else:
        # Plot single selected model forecast
        forecast_data = st.session_state["all_forecasts"][selected_view]
        fc_df = forecast_data["df"]
        
        hist_mask = fc_df["type"] == "Historical"
        fig_fc.add_trace(go.Scatter(
            x=fc_df.loc[hist_mask, "Date"],
            y=fc_df.loc[hist_mask, "Price"],
            mode="lines",
            name="Historical Price",
            line=dict(color="#94a3b8", width=2)
        ))
        
        pred_mask = fc_df["type"] == "Forecast"
        line_color = color_map.get(selected_view, "#10b981")
        
        fig_fc.add_trace(go.Scatter(
            x=fc_df.loc[pred_mask, "Date"],
            y=fc_df.loc[pred_mask, "Price"],
            mode="lines",
            name=f"{selected_view} Forecast",
            line=dict(color=line_color, width=3, dash="dash")
        ))
        
        if "Upper" in fc_df.columns and "Lower" in fc_df.columns:
            fig_fc.add_trace(go.Scatter(
                x=fc_df.loc[pred_mask, "Date"],
                y=fc_df.loc[pred_mask, "Upper"],
                mode="lines",
                name="Upper Bound",
                line=dict(color="rgba(56, 189, 248, 0.2)"),
                showlegend=False
            ))
            fig_fc.add_trace(go.Scatter(
                x=fc_df.loc[pred_mask, "Date"],
                y=fc_df.loc[pred_mask, "Lower"],
                mode="lines",
                name="Lower Bound",
                fill="tonexty",
                fillcolor="rgba(56, 189, 248, 0.1)",
                line=dict(color="rgba(56, 189, 248, 0.2)"),
                showlegend=False
            ))

    fig_fc.update_layout(
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=10, r=10, t=20, b=20),
        xaxis=dict(showgrid=True, gridcolor="#1e2430", title="Date"),
        yaxis=dict(showgrid=True, gridcolor="#1e2430", title="Price ($)"),
        height=400
    )
    st.plotly_chart(fig_fc, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 6. MODEL COMPARISON & NEWS SECTION (2 COLUMNS)
# -----------------------------------------------------------------------------
bottom_left, bottom_right = st.columns([1.5, 1])

# --- BOTTOM LEFT: MODEL COMPARISON CARD ---
with bottom_left:
    st.markdown('<div class="vesper-card">', unsafe_allow_html=True)
    st.markdown('<div class="vesper-card-header">📊 Model Accuracy Comparison</div>', unsafe_allow_html=True)
    
    if st.session_state["model_history"]:
        # Convert nested session state dict to DataFrame for display
        comp_data = []
        for model_name, m_dict in st.session_state["model_history"].items():
            comp_data.append({
                "Model": model_name,
                "RMSE": f"{m_dict.get('RMSE', 0):.2f}",
                "MAE": f"{m_dict.get('MAE', 0):.2f}",
                "MAPE (%)": f"{m_dict.get('MAPE', 0):.2f}%"
            })
        
        comp_df = pd.DataFrame(comp_data)
        st.dataframe(comp_df, use_container_width=True, hide_index=True)
    else:
        st.info("No models trained yet in this session. Click 'Train & Forecast' above to start comparing models!")
        
    st.markdown('</div>', unsafe_allow_html=True)

# --- BOTTOM RIGHT: NEWS CARD ---
with bottom_right:
    st.markdown('<div class="vesper-card">', unsafe_allow_html=True)
    st.markdown(f'<div class="vesper-card-header">📰 Market News & Sentiment — {selected_stock}</div>', unsafe_allow_html=True)
    
    news_items = fetch_stock_news(selected_stock)
    
    if news_items:
        for item in news_items[:4]:  # Show top 4 news items
            st.markdown(f"""
                <div class="news-item">
                    <a class="news-title" href="{item.get('url', '#')}" target="_blank">{item.get('title', 'News Headline')}</a>
                    <div class="news-meta">Source: {item.get('source', 'Financial News')} • {item.get('date', 'Recent')}</div>
                </div>
            """, unsafe_allow_html=True)
    else:
        st.write("No recent news articles found for this ticker.")
        
    st.markdown('</div>', unsafe_allow_html=True)
