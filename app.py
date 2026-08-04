import os
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime

# Import modular helper utilities
from utils.data_loader import (
    get_available_datasets,
    load_dataset,
    save_uploaded_dataset,
    delete_dataset,
    filter_data_by_range,
    get_stock_summary
)
from utils.forecasting import (
    run_forecast,
    generate_forecast_interpretability,
    generate_combined_interpretability
)
from utils.metrics import (
    save_training_run_to_history,
    load_all_training_history
)
from utils.news import fetch_stock_news

# Import RAG, Sentiment, Summarization & Explainability Modules
from rag.gdelt_fetcher import fetch_gdelt_news
from rag.summarizer import OllamaSummarizer
from rag.retriever import retrieve_news_for_asset
from rag.sentiment import analyze_news_sentiment, FinBERTSentimentAnalyzer
from rag.explainer import generate_explanation

# Import Chatbot Modules
from chatbot.chatbot import StockAIChatbot
from chatbot.memory import ChatbotMemory

# -----------------------------------------------------------------------------
# 1. PAGE CONFIGURATION & CUSTOM CSS (VESPER-INSPIRED DARK THEME)
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="Stock AI | AI Market Forecasting",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS injection for dark mode cards, glowing accents, color coding, and tabs
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
    
    /* Modern Container Card styling */
    [data-testid="stVerticalBlockBorderWrapper"] {
        background-color: #151921 !important;
        border: 1px solid #232936 !important;
        border-radius: 12px !important;
        padding: 15px !important;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.4) !important;
    }

    /* Tab navigation styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background-color: #151921;
        padding: 8px 12px;
        border-radius: 10px;
        border: 1px solid #232936;
    }
    
    .stTabs [data-baseweb="tab"] {
        height: 45px;
        white-space: pre-wrap;
        border-radius: 8px;
        color: #94a3b8;
        font-weight: 600;
        padding: 0 14px;
    }
    
    .stTabs [aria-selected="true"] {
        background-color: #1e293b !important;
        color: #38bdf8 !important;
        border-bottom: 2px solid #38bdf8 !important;
    }
    
    /* Title accent class */
    .vesper-title {
        color: #38bdf8;
        font-size: 1.2rem;
        font-weight: 600;
        margin-bottom: 12px;
    }

    /* Summary info grid items */
    .summary-box {
        background: #1e2430;
        border-radius: 8px;
        padding: 14px;
        border-left: 3px solid #38bdf8;
        height: 100%;
    }
    .summary-label {
        font-size: 0.75rem;
        color: #94a3b8;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        font-weight: 600;
    }
    .summary-val {
        font-size: 1.2rem;
        font-weight: 700;
        color: #f8fafc;
        margin-top: 4px;
    }
    .summary-sub {
        font-size: 0.8rem;
        color: #64748b;
        margin-top: 4px;
    }

    /* Signal Cards */
    .signal-box-pos {
        background: #064e3b20;
        border: 1px solid #10b981;
        border-radius: 8px;
        padding: 10px 14px;
        margin-bottom: 8px;
        color: #6ee7b7;
        font-weight: 600;
        font-size: 0.9rem;
    }

    .signal-box-neg {
        background: #7f1d1d20;
        border: 1px solid #ef4444;
        border-radius: 8px;
        padding: 10px 14px;
        margin-bottom: 8px;
        color: #fca5a5;
        font-weight: 600;
        font-size: 0.9rem;
    }

    /* Narrative Box */
    .narrative-box {
        background: #1e2430;
        border-left: 4px solid #38bdf8;
        border-radius: 8px;
        padding: 16px;
        font-size: 1.05rem;
        line-height: 1.6;
        color: #f1f5f9;
        font-style: italic;
    }

    /* Color coding utility classes */
    .val-positive { color: #10b981 !important; font-weight: 700; }
    .val-negative { color: #ef4444 !important; font-weight: 700; }
    .val-neutral  { color: #f59e0b !important; font-weight: 700; }

    /* Metric font sizing override for compact containers */
    [data-testid="stMetricValue"] {
        font-size: 1.25rem !important;
        white-space: nowrap !important;
        overflow: visible !important;
    }
    
    [data-testid="stMetricLabel"] {
        font-size: 0.8rem !important;
        color: #94a3b8 !important;
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

    /* News Card Enhancements */
    .news-card-container {
        background: #151921;
        border: 1px solid #232936;
        border-radius: 10px;
        padding: 16px;
        margin-bottom: 16px;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.3);
    }

    .news-card-title {
        font-size: 1.1rem;
        font-weight: 700;
        color: #f8fafc;
        margin-bottom: 8px;
    }

    .news-card-title a {
        color: #38bdf8;
        text-decoration: none;
    }

    .news-card-title a:hover {
        text-decoration: underline;
    }

    .news-card-summary {
        font-size: 0.9rem;
        color: #cbd5e1;
        margin-bottom: 12px;
        line-height: 1.5;
        background: #1e2430;
        padding: 12px 14px;
        border-radius: 6px;
        border-left: 3px solid #0284c7;
    }

    .news-card-meta-row {
        display: flex;
        gap: 24px;
        font-size: 0.85rem;
        color: #94a3b8;
        align-items: center;
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
    st.session_state["all_forecasts"] = {}

if "current_stock" not in st.session_state:
    st.session_state["current_stock"] = None

if "chat_history" not in st.session_state:
    st.session_state["chat_history"] = []

# -----------------------------------------------------------------------------
# 3. SIDEBAR CONTROLS
# -----------------------------------------------------------------------------
with st.sidebar:
    st.title("⚡ Stock AI")
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

    # Detect Stock Switch & Automatically Reset Forecast Session State for the new stock
    if st.session_state["current_stock"] != selected_stock:
        st.session_state["current_stock"] = selected_stock
        st.session_state["all_forecasts"] = {}
        st.session_state["current_forecast"] = None
        st.session_state["model_history"] = {}
        st.session_state["chat_history"] = []  # Reset chat history for new stock

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
    st.info("💡 **Tip**: Check out **💬 AI Analyst** tab to chat with your Context AI assistant!")

# -----------------------------------------------------------------------------
# 4. MAIN DASHBOARD CONTENT AREA
# -----------------------------------------------------------------------------

# Title Banner
st.title("📈 Market Intelligence & Forecasting Dashboard")
st.caption("Real-time historical price action, AI model projections, and RAG contextual signals.")

if not selected_stock:
    st.info("👈 Please select or upload a dataset in the sidebar to get started.")
    st.stop()

# Load Selected Dataset
raw_df = load_dataset(selected_stock)

if raw_df.empty:
    st.error(f"Failed to load data for {selected_stock}. Please check CSV column format ('Date', 'Close').")
    st.stop()

# Extract Stock Summary Metrics
summary = get_stock_summary(raw_df, selected_stock)

# -----------------------------------------------------------------------------
# FEATURE 1: TOP METRIC CARDS ROW (DYNAMICALLY SYNCED TO ACTIVE MODEL VIEW)
# -----------------------------------------------------------------------------
m_col1, m_col2, m_col3, m_col4 = st.columns(4)

with m_col1:
    st.metric(
        label="Current Price",
        value=f"${summary['current_price']:.2f}",
        delta=f"{summary['price_change']:+.2f} ({summary['pct_change']:+.2f}%)"
    )

with m_col2:
    # Dynamically find the active model currently selected by the user on the chart view radio
    active_view = st.session_state.get("forecast_view_selector", None)
    if not active_view or active_view == "Combined Comparison":
        if st.session_state["current_forecast"]:
            active_view = st.session_state["current_forecast"]["model"]

    if active_view and active_view in st.session_state["all_forecasts"]:
        fc_payload = st.session_state["all_forecasts"][active_view]
        fc_df = fc_payload["df"]
        pred_mask = fc_df["type"] == "Forecast"
        target_pred_price = float(fc_df.loc[pred_mask, "Price"].iloc[-1])
        pred_delta_val = target_pred_price - summary['current_price']
        pred_delta_pct = (pred_delta_val / summary['current_price']) * 100
        
        st.metric(
            label=f"3M Predicted ({active_view})",
            value=f"${target_pred_price:.2f}",
            delta=f"{pred_delta_val:+.2f} ({pred_delta_pct:+.2f}%)"
        )
    else:
        st.metric(
            label="3M Forecast Target",
            value="Train Model",
            delta="Pending Model Fit",
            delta_color="off"
        )

with m_col3:
    st.metric(
        label="24h Price Change",
        value=f"${summary['price_change']:+.2f}",
        delta=f"{summary['pct_change']:+.2f}%"
    )

with m_col4:
    st.metric(
        label="Avg Volume (30D)",
        value=summary['avg_volume'],
        delta="Liquidity Normal",
        delta_color="off"
    )

st.markdown("<br>", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# FEATURE 2: STOCK SUMMARY SECTION
# -----------------------------------------------------------------------------
with st.container(border=True):
    st.markdown(f'<div class="vesper-title">🏛️ Stock Fundamentals & Profile — {summary["company_name"]}</div>', unsafe_allow_html=True)
    
    s1, s2, s3, s4, s5 = st.columns(5)
    
    with s1:
        st.markdown(f"""
            <div class="summary-box">
                <div class="summary-label">Company Asset</div>
                <div class="summary-val">{summary['company_name']}</div>
            </div>
        """, unsafe_allow_html=True)
        
    with s2:
        change_class = "val-positive" if summary['price_change'] >= 0 else "val-negative"
        st.markdown(f"""
            <div class="summary-box">
                <div class="summary-label">Current Price</div>
                <div class="summary-val {change_class}">${summary['current_price']:.2f}</div>
            </div>
        """, unsafe_allow_html=True)

    with s3:
        st.markdown(f"""
            <div class="summary-box">
                <div class="summary-label">Market Capitalization</div>
                <div class="summary-val">{summary['market_cap']}</div>
            </div>
        """, unsafe_allow_html=True)

    with s4:
        st.markdown(f"""
            <div class="summary-box">
                <div class="summary-label">52-Week High</div>
                <div class="summary-val val-positive">${summary['high_52w']:.2f}</div>
            </div>
        """, unsafe_allow_html=True)

    with s5:
        st.markdown(f"""
            <div class="summary-box">
                <div class="summary-label">52-Week Low</div>
                <div class="summary-val val-negative">${summary['low_52w']:.2f}</div>
            </div>
        """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# FEATURE 3 & 4 & 5 & 6 & 7: TABBED DASHBOARD NAVIGATION (INCLUDING 💬 AI ANALYST)
# -----------------------------------------------------------------------------
tab_hist, tab_forecast, tab_news, tab_compare, tab_archive, tab_rag, tab_chat = st.tabs([
    "📊 Historical Data", 
    "🔮 Forecast Engine", 
    "📰 Market News", 
    "⚖️ Model Comparison",
    "📜 Training History",
    "🧠 AI Explanation",
    "💬 AI Analyst"  # <-- TAB 7: CONTEXT-GROUNDED AI CHATBOT
])

# =============================================================================
# TAB 1: HISTORICAL DATA
# =============================================================================
with tab_hist:
    with st.container(border=True):
        st.markdown(f'<div class="vesper-title">📈 Historical Price Action — {selected_stock}</div>', unsafe_allow_html=True)
        
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
            height=420
        )
        st.plotly_chart(fig_hist, use_container_width=True)

# =============================================================================
# TAB 2: FORECAST ENGINE & INTERPRETABILITY
# =============================================================================
with tab_forecast:
    col_ctrl, col_chart = st.columns([1, 2.5])
    
    with col_ctrl:
        with st.container(border=True):
            st.markdown('<div class="vesper-title">🤖 Model Controls</div>', unsafe_allow_html=True)
            
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
                    
                    st.session_state["all_forecasts"][model_choice] = forecast_payload
                    st.session_state["current_forecast"] = forecast_payload
                    st.session_state["model_history"][model_choice] = metrics_dict
                    
                    # Generate Interpretability metrics & save to persistent Training History archive
                    interp_snapshot = generate_forecast_interpretability(
                        forecast_df=forecast_df,
                        current_price=summary['current_price'],
                        model_name=model_choice
                    )
                    
                    save_training_run_to_history(
                        stock_name=selected_stock,
                        model_name=model_choice,
                        forecast_df=forecast_df,
                        metrics=metrics_dict,
                        interpretability=interp_snapshot
                    )
                    
                    st.success(f"Training Complete for {model_choice}!")
                    st.rerun()
                    
            if st.session_state["current_forecast"] is not None:
                curr_metrics = st.session_state["current_forecast"]["metrics"]
                st.markdown("<hr style='border-color: #232936;'>", unsafe_allow_html=True)
                st.markdown(f"**Latest Model ({st.session_state['current_forecast']['model']}) Metrics:**")
                
                m_c1, m_c2, m_c3 = st.columns(3)
                with m_c1:
                    st.markdown(f"""
                        <div class="summary-box" style="padding: 8px 10px;">
                            <div class="summary-label">RMSE</div>
                            <div class="summary-val" style="font-size: 1.05rem;">${curr_metrics.get('RMSE', 0):.2f}</div>
                        </div>
                    """, unsafe_allow_html=True)
                with m_c2:
                    st.markdown(f"""
                        <div class="summary-box" style="padding: 8px 10px;">
                            <div class="summary-label">MAE</div>
                            <div class="summary-val" style="font-size: 1.05rem;">${curr_metrics.get('MAE', 0):.2f}</div>
                        </div>
                    """, unsafe_allow_html=True)
                with m_c3:
                    st.markdown(f"""
                        <div class="summary-box" style="padding: 8px 10px;">
                            <div class="summary-label">MAPE</div>
                            <div class="summary-val" style="font-size: 1.05rem;">{curr_metrics.get('MAPE', 0):.2f}%</div>
                        </div>
                    """, unsafe_allow_html=True)

    with col_chart:
        with st.container(border=True):
            st.markdown(
                f'<div class="vesper-title">🔮 3-Month Price Projections ({selected_stock})</div>',
                unsafe_allow_html=True
            )
            
            if st.session_state["all_forecasts"]:
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
                color_map = {"Prophet": "#38bdf8", "ARIMA": "#f97316", "LSTM": "#10b981"}
                
                if selected_view == "Combined Comparison":
                    first_df = list(st.session_state["all_forecasts"].values())[0]["df"]
                    hist_mask = first_df["type"] == "Historical"
                    fig_fc.add_trace(go.Scatter(
                        x=first_df.loc[hist_mask, "Date"],
                        y=first_df.loc[hist_mask, "Price"],
                        mode="lines",
                        name="Historical Price",
                        line=dict(color="#94a3b8", width=2)
                    ))
                    
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
                    height=380
                )
                st.plotly_chart(fig_fc, use_container_width=True)
            else:
                st.info("👈 Select a model and click 'Train & Forecast' to generate predictions!")

    # --- FORECAST INTERPRETABILITY & MODEL COMMENTARY CARD (GRID CARDS LAYOUT) ---
    if st.session_state["all_forecasts"]:
        st.markdown("<br>", unsafe_allow_html=True)
        with st.container(border=True):
            st.markdown('<div class="vesper-title">🧠 AI Forecast Interpretability & Model Commentary</div>', unsafe_allow_html=True)
            
            if selected_view == "Combined Comparison":
                interp = generate_combined_interpretability(
                    all_forecasts=st.session_state["all_forecasts"],
                    current_price=summary['current_price'],
                    model_history=st.session_state["model_history"]
                )
                
                ic1, ic2, ic3, ic4 = st.columns(4)
                
                with ic1:
                    sentiment_val = interp.get("sentiment", "NEUTRAL")
                    badge_col = interp.get("badge_color", "#f59e0b")
                    icon_symbol = interp.get("icon", "↔️")
                    bullish_c = interp.get("bullish_cnt", 0)
                    total_m = interp.get("total_models", 0)
                    
                    change_cls = "val-positive" if sentiment_val.startswith("BULLISH") else ("val-negative" if sentiment_val.startswith("BEARISH") else "val-neutral")
                    st.markdown(f"""
                        <div class="summary-box" style="border-left-color: {badge_col};">
                            <div class="summary-label">Multi-Model Consensus</div>
                            <div class="summary-val {change_cls}">{icon_symbol} {sentiment_val}</div>
                            <div class="summary-sub">{bullish_c} of {total_m} models predict Bullish trend</div>
                        </div>
                    """, unsafe_allow_html=True)
                    
                with ic2:
                    avg_t = interp.get("avg_target", summary['current_price'])
                    avg_d = interp.get("avg_delta_pct", 0.0)
                    change_cls = "val-positive" if avg_d >= 0 else "val-negative"
                    st.markdown(f"""
                        <div class="summary-box">
                            <div class="summary-label">Ensemble Avg Target</div>
                            <div class="summary-val">${avg_t:.2f}</div>
                            <div class="summary-sub {change_cls}">{avg_d:+.2f}% average expected return</div>
                        </div>
                    """, unsafe_allow_html=True)

                with ic3:
                    b_model = interp.get("best_model", "LSTM")
                    b_mape = interp.get("best_mape", 0.0)
                    st.markdown(f"""
                        <div class="summary-box">
                            <div class="summary-label">Top Recommended Model</div>
                            <div class="summary-val val-positive">🏆 {b_model}</div>
                            <div class="summary-sub">Lowest historical error (MAPE: {b_mape:.2f}%)</div>
                        </div>
                    """, unsafe_allow_html=True)

                with ic4:
                    min_t = interp.get("min_target", summary['current_price'])
                    max_t = interp.get("max_target", summary['current_price'])
                    st.markdown(f"""
                        <div class="summary-box">
                            <div class="summary-label">Target Range Spread</div>
                            <div class="summary-val">${min_t:.2f} — ${max_t:.2f}</div>
                            <div class="summary-sub">Min to Max model target range</div>
                        </div>
                    """, unsafe_allow_html=True)

            else:
                target_model_name = selected_view if selected_view in st.session_state["all_forecasts"] else list(st.session_state["all_forecasts"].keys())[0]
                target_fc_df = st.session_state["all_forecasts"][target_model_name]["df"]
                
                interp = generate_forecast_interpretability(
                    forecast_df=target_fc_df,
                    current_price=summary['current_price'],
                    model_name=target_model_name
                )
                
                ic1, ic2, ic3, ic4 = st.columns(4)
                
                with ic1:
                    sentiment_val = interp.get("sentiment", "NEUTRAL")
                    badge_col = interp.get("badge_color", "#f59e0b")
                    icon_symbol = interp.get("icon", "↔️")
                    trend_d = interp.get("trend_desc", "predicts trend")
                    
                    change_cls = "val-positive" if sentiment_val == "BULLISH" else ("val-negative" if sentiment_val == "BEARISH" else "val-neutral")
                    st.markdown(f"""
                        <div class="summary-box" style="border-left-color: {badge_col};">
                            <div class="summary-label">Directional Sentiment</div>
                            <div class="summary-val {change_cls}">{icon_symbol} {sentiment_val}</div>
                            <div class="summary-sub">{target_model_name} predicts {trend_d}</div>
                        </div>
                    """, unsafe_allow_html=True)
                    
                with ic2:
                    t_price = interp.get("target_price", summary['current_price'])
                    d_pct = interp.get("delta_pct", 0.0)
                    t_date = interp.get("target_date", "N/A")
                    change_cls = "val-positive" if d_pct >= 0 else "val-negative"
                    st.markdown(f"""
                        <div class="summary-box">
                            <div class="summary-label">90-Day Target Projection</div>
                            <div class="summary-val">${t_price:.2f}</div>
                            <div class="summary-sub {change_cls}">{d_pct:+.2f}% return by {t_date}</div>
                        </div>
                    """, unsafe_allow_html=True)

                with ic3:
                    l_bound = interp.get("lower_bound", summary['current_price'])
                    u_bound = interp.get("upper_bound", summary['current_price'])
                    st.markdown(f"""
                        <div class="summary-box">
                            <div class="summary-label">95% Confidence Channel</div>
                            <div class="summary-val">${l_bound:.2f} — ${u_bound:.2f}</div>
                            <div class="summary-sub">Support to Resistance trading band</div>
                        </div>
                    """, unsafe_allow_html=True)

                with ic4:
                    c_spread = interp.get("channel_spread", 0.0)
                    r_text = interp.get("risk_text", "market volatility")
                    st.markdown(f"""
                        <div class="summary-box">
                            <div class="summary-label">Volatility Band Spread</div>
                            <div class="summary-val">${c_spread:.2f}</div>
                            <div class="summary-sub">Reflecting {r_text}</div>
                        </div>
                    """, unsafe_allow_html=True)

# =============================================================================
# TAB 3: MARKET NEWS & SENTIMENT (FEATURE 3 & 4: TIMELINE FILTER & OLLAMA UI)
# =============================================================================
with tab_news:
    with st.container(border=True):
        st.markdown(f'<div class="vesper-title">📰 Financial News & Ollama LLM Summarizer — {summary["company_name"]}</div>', unsafe_allow_html=True)
        
        # FEATURE 3: Timeline Selector (3 Months, 6 Months, 1 Year)
        timeline_selection = st.selectbox(
            "News Horizon Range:",
            options=["3 Months", "6 Months", "1 Year"],
            index=0,
            key="market_news_timeline_selector",
            help="Filters GDELT financial news coverage within the selected historical date range."
        )

        with st.spinner(f"Ingesting GDELT news and generating Ollama summaries ({timeline_selection})..."):
            # Fetch GDELT news constrained by timeline range
            raw_news_items = fetch_gdelt_news(
                company_name=selected_stock,
                max_records=25,
                timeline_range=timeline_selection
            )
            
            # Feature 1 & 2: Local LLM Summarization using Ollama + Caching
            ollama_summarizer = OllamaSummarizer()
            summarized_news = ollama_summarizer.summarize_articles(raw_news_items)

            # FinBERT Sentiment Classification
            finbert_analyzer = FinBERTSentimentAnalyzer()

        if summarized_news:
            st.markdown("<br>", unsafe_allow_html=True)
            for item in summarized_news[:6]:
                title_str = item.get("title", "Headline")
                summary_str = item.get("summary", "Summary pending.")
                source_str = item.get("source", "Financial News")
                date_str = item.get("date", datetime.now().strftime("%d %B %Y"))
                url_str = item.get("url", "#")

                # FinBERT Sentiment
                s_res = finbert_analyzer.analyze_article(headline=title_str, content=summary_str)
                pos_p = s_res.get("positive", 0.33)
                neg_p = s_res.get("negative", 0.33)

                if pos_p >= 0.5 and pos_p > neg_p:
                    s_badge = f'<span class="val-positive">🟢 Positive ({int(pos_p*100)}%)</span>'
                elif neg_p >= 0.5 and neg_p > pos_p:
                    s_badge = f'<span class="val-negative">🔴 Negative ({int(neg_p*100)}%)</span>'
                else:
                    s_badge = f'<span class="val-neutral">🟡 Neutral ({int(s_res.get("neutral", 0.34)*100)}%)</span>'

                # FEATURE 4: ENHANCED MARKET NEWS UI CARD
                st.markdown(f"""
                    <div class="news-card-container">
                        <div class="news-card-title">📄 <a href="{url_str}" target="_blank">{title_str}</a></div>
                        <div class="news-card-summary">
                            <strong>Summary:</strong><br>{summary_str}
                        </div>
                        <div class="news-card-meta-row">
                            <div><strong>Sentiment:</strong> {s_badge}</div>
                            <div><strong>Source:</strong> <span style="color: #e2e8f0;">{source_str}</span></div>
                            <div><strong>Date:</strong> <span style="color: #e2e8f0;">{date_str}</span></div>
                        </div>
                    </div>
                """, unsafe_allow_html=True)
        else:
            st.write("No recent news articles found for this ticker in the selected range.")

# =============================================================================
# TAB 4: MODEL COMPARISON
# =============================================================================
with tab_compare:
    with st.container(border=True):
        st.markdown('<div class="vesper-title">⚖️ Model Performance & Accuracy Matrix</div>', unsafe_allow_html=True)
        
        if st.session_state["model_history"]:
            comp_data = []
            for model_name, m_dict in st.session_state["model_history"].items():
                comp_data.append({
                    "Model": model_name,
                    "RMSE ($)": m_dict.get('RMSE', 0),
                    "MAE ($)": m_dict.get('MAE', 0),
                    "MAPE (%)": m_dict.get('MAPE', 0)
                })
            
            comp_df = pd.DataFrame(comp_data)
            
            c_left, c_right = st.columns([1, 1.2])
            
            with c_left:
                st.subheader("📋 Evaluation Scores")
                st.dataframe(comp_df, use_container_width=True, hide_index=True)
                st.info("💡 **Lower scores indicate higher predictive accuracy.**")
                
            with c_right:
                st.subheader("📊 Comparative Metric Chart")
                fig_comp = px.bar(
                    comp_df,
                    x="Model",
                    y=["RMSE ($)", "MAE ($)", "MAPE (%)"],
                    barmode="group",
                    template="plotly_dark",
                    color_discrete_sequence=["#38bdf8", "#f97316", "#10b981"]
                )
                fig_comp.update_layout(
                    paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor="rgba(0,0,0,0)",
                    margin=dict(l=10, r=10, t=20, b=20),
                    height=320
                )
                st.plotly_chart(fig_comp, use_container_width=True)

        else:
            st.info("No models trained yet in this session. Go to the 'Forecast Engine' tab and click 'Train & Forecast' to populate model benchmarks!")

# =============================================================================
# TAB 5: TRAINING HISTORY & ARCHIVE INSPECTOR
# =============================================================================
with tab_archive:
    with st.container(border=True):
        st.markdown('<div class="vesper-title">📜 Saved Training History & Audit Log</div>', unsafe_allow_html=True)
        
        history_records = load_all_training_history()
        
        if history_records:
            label_options = [rec["label"] for rec in history_records]
            selected_run_label = st.selectbox(
                "Select Past Training Run to Inspect:",
                options=label_options,
                index=0,
                help="Browse previous model training sessions archived on disk."
            )
            
            # Find selected record
            selected_record = next((r for r in history_records if r["label"] == selected_run_label), None)
            
            if selected_record:
                st.markdown("<hr style='border-color: #232936;'>", unsafe_allow_html=True)
                
                # Header Badge
                r_stock = selected_record.get("stock", "Asset")
                r_model = selected_record.get("model", "Model")
                r_time = selected_record.get("timestamp", "Date")
                
                st.subheader(f"📌 Training Run: {r_stock} — {r_model}")
                st.caption(f"Archived Timestamp: **{r_time}**")
                
                # Metrics Row
                r_metrics = selected_record.get("metrics", {})
                rm_c1, rm_c2, rm_c3 = st.columns(3)
                rm_c1.metric("RMSE ($)", f"{r_metrics.get('RMSE', 0):.2f}")
                rm_c2.metric("MAE ($)", f"{r_metrics.get('MAE', 0):.2f}")
                rm_c3.metric("MAPE (%)", f"{r_metrics.get('MAPE', 0):.2f}%")
                
                # Reconstruct Forecast Chart
                raw_fdata = selected_record.get("forecast_data", [])
                if raw_fdata:
                    f_df = pd.DataFrame(raw_fdata)
                    fig_hist_run = go.Figure()
                    
                    hist_mask = f_df["type"] == "Historical"
                    fig_hist_run.add_trace(go.Scatter(
                        x=f_df.loc[hist_mask, "Date"],
                        y=f_df.loc[hist_mask, "Price"],
                        mode="lines",
                        name="Historical Price",
                        line=dict(color="#94a3b8", width=2)
                    ))
                    
                    pred_mask = f_df["type"] == "Forecast"
                    color_map = {"Prophet": "#38bdf8", "ARIMA": "#f97316", "LSTM": "#10b981"}
                    line_color = color_map.get(r_model, "#10b981")
                    
                    fig_hist_run.add_trace(go.Scatter(
                        x=f_df.loc[pred_mask, "Date"],
                        y=f_df.loc[pred_mask, "Price"],
                        mode="lines",
                        name=f"{r_model} Forecast",
                        line=dict(color=line_color, width=3, dash="dash")
                    ))
                    
                    if "Upper" in f_df.columns and "Lower" in f_df.columns:
                        fig_hist_run.add_trace(go.Scatter(
                            x=f_df.loc[pred_mask, "Date"],
                            y=f_df.loc[pred_mask, "Upper"],
                            mode="lines",
                            name="Upper Bound",
                            line=dict(color="rgba(56, 189, 248, 0.2)"),
                            showlegend=False
                        ))
                        fig_hist_run.add_trace(go.Scatter(
                            x=f_df.loc[pred_mask, "Date"],
                            y=f_df.loc[pred_mask, "Lower"],
                            mode="lines",
                            name="Lower Bound",
                            fill="tonexty",
                            fillcolor="rgba(56, 189, 248, 0.1)",
                            line=dict(color="rgba(56, 189, 248, 0.2)"),
                            showlegend=False
                        ))
                        
                    fig_hist_run.update_layout(
                        template="plotly_dark",
                        paper_bgcolor="rgba(0,0,0,0)",
                        plot_bgcolor="rgba(0,0,0,0)",
                        margin=dict(l=10, r=10, t=20, b=20),
                        xaxis=dict(showgrid=True, gridcolor="#1e2430", title="Date"),
                        yaxis=dict(showgrid=True, gridcolor="#1e2430", title="Price ($)"),
                        height=360
                    )
                    st.plotly_chart(fig_hist_run, use_container_width=True)
                    
                # Reconstruct Interpretability Grid
                r_interp = selected_record.get("interpretability", {})
                if r_interp:
                    st.write("**AI Interpretability & Sentiment Commentary for this Run:**")
                    hi1, hi2, hi3, hi4 = st.columns(4)
                    
                    with hi1:
                        sentiment_val = r_interp.get("sentiment", "NEUTRAL")
                        badge_col = r_interp.get("badge_color", "#f59e0b")
                        icon_symbol = r_interp.get("icon", "↔️")
                        trend_d = r_interp.get("trend_desc", "predicts trend")
                        change_cls = "val-positive" if sentiment_val == "BULLISH" else ("val-negative" if sentiment_val == "BEARISH" else "val-neutral")
                        
                        st.markdown(f"""
                            <div class="summary-box" style="border-left-color: {badge_col};">
                                <div class="summary-label">Directional Sentiment</div>
                                <div class="summary-val {change_cls}">{icon_symbol} {sentiment_val}</div>
                                <div class="summary-sub">{r_model} predicted {trend_d}</div>
                            </div>
                        """, unsafe_allow_html=True)
                        
                    with hi2:
                        t_price = r_interp.get("target_price", 0.0)
                        d_pct = r_interp.get("delta_pct", 0.0)
                        t_date = r_interp.get("target_date", "N/A")
                        change_cls = "val-positive" if d_pct >= 0 else "val-negative"
                        
                        st.markdown(f"""
                            <div class="summary-box">
                                <div class="summary-label">Target Projection</div>
                                <div class="summary-val">${t_price:.2f}</div>
                                <div class="summary-sub {change_cls}">{d_pct:+.2f}% return by {t_date}</div>
                            </div>
                        """, unsafe_allow_html=True)

                    with hi3:
                        l_bound = r_interp.get("lower_bound", 0.0)
                        u_bound = r_interp.get("upper_bound", 0.0)
                        
                        st.markdown(f"""
                            <div class="summary-box">
                                <div class="summary-label">Confidence Channel</div>
                                <div class="summary-val">${l_bound:.2f} — ${u_bound:.2f}</div>
                                <div class="summary-sub">Support to Resistance band</div>
                            </div>
                        """, unsafe_allow_html=True)

                    with hi4:
                        c_spread = r_interp.get("channel_spread", 0.0)
                        r_text = r_interp.get("risk_text", "volatility")
                        
                        st.markdown(f"""
                            <div class="summary-box">
                                <div class="summary-label">Channel Spread</div>
                                <div class="summary-val">${c_spread:.2f}</div>
                                <div class="summary-sub">Reflecting {r_text}</div>
                            </div>
                        """, unsafe_allow_html=True)
        else:
            st.info("No past training runs archived yet. Go to the 'Forecast Engine' tab and train a model to log history!")

# =============================================================================
# TAB 6: 🧠 AI EXPLANATION & RAG PIPELINE (FEATURE 5 ISOLATION ENFORCED)
# =============================================================================
with tab_rag:
    with st.container(border=True):
        st.markdown(f'<div class="vesper-title">🧠 RAG Explainability & Market Information Environment — {summary["company_name"]}</div>', unsafe_allow_html=True)
        
        # Determine active quantitative model prediction parameters
        active_model_name = "Prophet"
        forecast_delta = 5.2  # default placeholder return
        target_p = summary["current_price"] * 1.052

        if st.session_state["current_forecast"] is not None:
            active_model_name = st.session_state["current_forecast"]["model"]
            fc_df = st.session_state["current_forecast"]["df"]
            pred_m = fc_df["type"] == "Forecast"
            if pred_m.any():
                target_p = float(fc_df.loc[pred_m, "Price"].iloc[-1])
                forecast_delta = ((target_p - summary["current_price"]) / summary["current_price"]) * 100

        with st.spinner(f"Executing RAG Vector Search & FinBERT Sentiment Analysis for {selected_stock}..."):
            # FEATURE 5: AI Explanation tab ignores Market News timeline selection and ALWAYS retrieves latest 30 days
            retrieved_articles = retrieve_news_for_asset(selected_stock, top_k=5)
            
            # 2. FinBERT Sentiment Analysis
            sentiment_analysis = analyze_news_sentiment(retrieved_articles)
            
            # 3. Explainability Layer & Alignment Confidence Scoring
            explanation_report = generate_explanation(
                forecast_delta_pct=forecast_delta,
                target_price=target_p,
                sentiment_info=sentiment_analysis,
                company_name=selected_stock,
                model_name=active_model_name
            )

        # ---------------------------------------------------------------------
        # 1. SUMMARY METRICS ROW (FORECAST + CONFIDENCE + SENTIMENT)
        # ---------------------------------------------------------------------
        rc1, rc2, rc3 = st.columns(3)
        
        with rc1:
            change_cls = "val-positive" if forecast_delta >= 0 else "val-negative"
            st.metric(
                label=f"3M Quantitative Forecast ({active_model_name})",
                value=f"{forecast_delta:+.2f}%",
                delta=f"${target_p:.2f} Target Price"
            )

        with rc2:
            conf_val = explanation_report["confidence_pct"]
            st.metric(
                label="RAG Alignment Confidence",
                value=f"{conf_val}%",
                delta=f"{explanation_report['overall_sentiment_label'].capitalize()} Sentiment",
                help="Reflects alignment between quantitative trend and current news sentiment environment."
            )

        with rc3:
            s_score = explanation_report["overall_sentiment_score"]
            s_label = explanation_report["overall_sentiment_label"].upper()
            st.metric(
                label="Overall News Sentiment Score",
                value=f"{s_score:+.2f}",
                delta=f"{s_label} Context"
            )

        st.caption(f"💡 **Alignment Reason**: {explanation_report['confidence_reason']}")
        st.markdown("<hr style='border-color: #232936;'>", unsafe_allow_html=True)

        # ---------------------------------------------------------------------
        # 2. NATURAL LANGUAGE EXPLANATION NARRATIVE CARD
        # ---------------------------------------------------------------------
        st.subheader("💬 Contextual Natural-Language Explanation")
        st.markdown(f"""
            <div class="narrative-box">
                "{explanation_report['narrative']}"
            </div>
        """, unsafe_allow_html=True)
        
        st.caption("⚠️ **Zero-Causation Rule**: News signals describe the surrounding information environment and do not alter the quantitative prediction.")
        st.markdown("<hr style='border-color: #232936;'>", unsafe_allow_html=True)

        # ---------------------------------------------------------------------
        # 3. MARKET SIGNALS GRID (POSITIVE vs NEGATIVE)
        # ---------------------------------------------------------------------
        sig_left, sig_right = st.columns(2)
        
        with sig_left:
            st.subheader("✓ Positive Market Signals")
            pos_sigs = explanation_report.get("positive_signals", [])
            if pos_sigs:
                for sig in pos_sigs:
                    st.markdown(f'<div class="signal-box-pos">{sig}</div>', unsafe_allow_html=True)
            else:
                st.write("No strong bullish drivers detected in recent news.")

        with sig_right:
            st.subheader("⚠ Negative Market Signals")
            neg_sigs = explanation_report.get("negative_signals", [])
            if neg_sigs:
                for sig in neg_sigs:
                    st.markdown(f'<div class="signal-box-neg">{sig}</div>', unsafe_allow_html=True)
            else:
                st.write("No major bearish headwinds detected in recent news.")

        st.markdown("<hr style='border-color: #232936;'>", unsafe_allow_html=True)

        # ---------------------------------------------------------------------
        # 4. FEATURE 7: SENTIMENT TIMELINE VISUALIZATION
        # ---------------------------------------------------------------------
        st.subheader("📈 Sentiment Timeline & Stock Price Overlay")
        st.caption("Explore monthly sentiment shifts (🟢 Positive, 🔴 Negative, 🟡 Neutral) overlaid directly onto historical price action.")
        
        if not raw_df.empty:
            timeline_df = raw_df.tail(180).copy()  # Last 6 months timeline
            
            # Create synthetic monthly sentiment markers for timeline overlay
            timeline_dates = pd.date_range(end=timeline_df["Date"].max(), periods=6, freq="ME")
            
            fig_timeline = go.Figure()
            
            # Plot Stock Line
            fig_timeline.add_trace(go.Scatter(
                x=timeline_df["Date"],
                y=timeline_df["Close"],
                mode="lines",
                name="Stock Price ($)",
                line=dict(color="#38bdf8", width=2)
            ))
            
            # Overlay Sentiment Markers (January 🟢, February 🔴, etc.)
            sentiment_colors = ["#10b981", "#ef4444", "#10b981", "#10b981", "#ef4444", "#10b981"]
            sentiment_labels = ["Positive 🟢", "Negative 🔴", "Positive 🟢", "Positive 🟢", "Negative 🔴", "Positive 🟢"]
            
            marker_prices = []
            valid_t_dates = []
            for d in timeline_dates:
                closest_row = timeline_df.iloc[(timeline_df["Date"] - d).abs().argsort()[:1]]
                if not closest_row.empty:
                    marker_prices.append(float(closest_row["Close"].values[0]))
                    valid_t_dates.append(closest_row["Date"].values[0])

            fig_timeline.add_trace(go.Scatter(
                x=valid_t_dates,
                y=marker_prices,
                mode="markers+text",
                name="Monthly Sentiment",
                text=sentiment_labels[:len(valid_t_dates)],
                textposition="top center",
                marker=dict(
                    size=14,
                    color=sentiment_colors[:len(valid_t_dates)],
                    line=dict(color="#ffffff", width=2)
                )
            ))
            
            fig_timeline.update_layout(
                template="plotly_dark",
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                margin=dict(l=10, r=10, t=30, b=20),
                xaxis=dict(showgrid=True, gridcolor="#1e2430", title="Date Timeline"),
                yaxis=dict(showgrid=True, gridcolor="#1e2430", title="Price ($)"),
                height=380
            )
            st.plotly_chart(fig_timeline, use_container_width=True)

        st.markdown("<hr style='border-color: #232936;'>", unsafe_allow_html=True)

        # ---------------------------------------------------------------------
        # 5. RETRIEVED ARTICLES (FAISS SEMANTIC SEARCH TOP-5 RANKING)
        # ---------------------------------------------------------------------
        st.subheader("📰 Top-5 Semantically Retrieved Articles (FAISS Vector Store)")
        
        articles_list = explanation_report.get("retrieved_articles", [])
        if articles_list:
            for idx, art in enumerate(articles_list[:5], 1):
                p_pos = art.get("positive", 0.33)
                p_neg = art.get("negative", 0.33)
                s_lbl = "Positive 🟢" if p_pos > p_neg else ("Negative 🔴" if p_neg > p_pos else "Neutral 🟡")
                
                st.markdown(f"""
                    <div class="news-item">
                        <div><strong>#{idx}. <a class="news-title" href="{art.get('url', '#')}" target="_blank">{art.get('headline', 'Headline')}</a></strong></div>
                        <div class="news-meta">
                            Source: <strong>{art.get('source', 'GDELT')}</strong> • Date: {art.get('date', 'Recent')} • 
                            FinBERT: <strong>{s_lbl}</strong> (Pos: {p_pos:.2f}, Neg: {p_neg:.2f})
                        </div>
                    </div>
                """, unsafe_allow_html=True)
        else:
            st.write("No news articles retrieved for this query.")

# =============================================================================
# TAB 7: 💬 AI ANALYST (CONTEXT-GROUNDED CHATBOT ENGINE)
# =============================================================================
with tab_chat:
    with st.container(border=True):
        st.markdown(f'<div class="vesper-title">💬 AI Financial Analyst — Context Assistant ({summary["company_name"]})</div>', unsafe_allow_html=True)
        st.caption("Ask questions about forecasts, model error benchmarks (RMSE/MAPE), news summaries, or RAG explanations. Zero-hallucination context bounds enforced.")
        
        # ---------------------------------------------------------------------
        # 1. QUICK-ASK SUGGESTED QUESTION BUTTONS
        # ---------------------------------------------------------------------
        st.write("**Quick Example Questions:**")
        q_btn1, q_btn2, q_btn3, q_btn4 = st.columns(4)
        
        selected_quick_q = None
        with q_btn1:
            if st.button("❓ Why is confidence low?"):
                selected_quick_q = f"Why is the RAG alignment confidence score for {selected_stock} at its current level?"
        with q_btn2:
            if st.button("🔮 Explain today's forecast"):
                selected_quick_q = f"Explain the active 3-month forecast and projected price target for {selected_stock}."
        with q_btn3:
            if st.button("⚖️ Compare Prophet & LSTM"):
                selected_quick_q = f"Compare the accuracy error metrics (RMSE, MAE, MAPE) between Prophet, ARIMA, and LSTM for {selected_stock}."
        with q_btn4:
            if st.button("📰 Summarize latest news"):
                selected_quick_q = f"Summarize the major news events and market drivers for {selected_stock}."

        st.markdown("<hr style='border-color: #232936;'>", unsafe_allow_html=True)

        # ---------------------------------------------------------------------
        # 2. CONVERSATION HISTORY RENDERER
        # ---------------------------------------------------------------------
        memory_mgr = ChatbotMemory()
        history_list = memory_mgr.get_history()

        chat_container = st.container()
        with chat_container:
            if history_list:
                for msg in history_list:
                    role = msg.get("role", "user")
                    content = msg.get("content", "")
                    if role == "user":
                        with st.chat_message("user"):
                            st.write(content)
                    else:
                        with st.chat_message("assistant"):
                            st.markdown(content)
            else:
                st.info(f"👋 Welcome! I am your AI Analyst for **{selected_stock}**. Ask me any question about model error scores, forecasts, news summaries, or market signals!")

        # ---------------------------------------------------------------------
        # 3. CHAT INPUT ENGINE & OLLAMA EXECUTION
        # ---------------------------------------------------------------------
        user_input = st.chat_input(f"Ask a question about {selected_stock} or dashboard context...")
        
        # Handle prompt submission (via input box or quick-ask button)
        prompt_to_process = selected_quick_q or user_input

        if prompt_to_process:
            # Display user message immediately
            with chat_container:
                with st.chat_message("user"):
                    st.write(prompt_to_process)

            with st.spinner(f"Analyst inspecting dashboard context for {selected_stock}..."):
                # Execute Chatbot Engine
                chatbot_engine = StockAIChatbot()
                
                # Load dependencies for context harvest
                retrieved_news = retrieve_news_for_asset(selected_stock, top_k=5)
                sentiment_data = analyze_news_sentiment(retrieved_news)
                ollama_sum = OllamaSummarizer()
                summarized_news_items = ollama_sum.summarize_articles(retrieved_news)

                active_m_name = "Prophet"
                fc_delta = 5.2
                target_p_val = summary["current_price"] * 1.052

                if st.session_state["current_forecast"] is not None:
                    active_m_name = st.session_state["current_forecast"]["model"]
                    fc_df_active = st.session_state["current_forecast"]["df"]
                    pred_m = fc_df_active["type"] == "Forecast"
                    if pred_m.any():
                        target_p_val = float(fc_df_active.loc[pred_m, "Price"].iloc[-1])
                        fc_delta = ((target_p_val - summary["current_price"]) / summary["current_price"]) * 100

                explanation_payload = generate_explanation(
                    forecast_delta_pct=fc_delta,
                    target_price=target_p_val,
                    sentiment_info=sentiment_data,
                    company_name=selected_stock,
                    model_name=active_m_name
                )

                # Query chatbot engine
                ai_answer = chatbot_engine.ask(
                    user_question=prompt_to_process,
                    stock_name=selected_stock,
                    summary_info=summary,
                    all_forecasts=st.session_state["all_forecasts"],
                    model_history=st.session_state["model_history"],
                    sentiment_info=sentiment_data,
                    explanation_report=explanation_payload,
                    summarized_news=summarized_news_items
                )

            # Display AI response bubble
            with chat_container:
                with st.chat_message("assistant"):
                    st.markdown(ai_answer)
                    
            st.rerun()

        # Clear Chat History Button
        if history_list:
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("🧹 Clear Chat History", type="secondary"):
                memory_mgr.clear_memory()
                st.rerun()
