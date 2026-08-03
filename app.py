import os
import streamlit as st
import pandas as pd
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
    generate_forecast_interpretability
)
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
        gap: 12px;
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
        padding: 0 20px;
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

    /* Interpretability Sentiment Badge */
    .sentiment-badge {
        display: inline-block;
        padding: 6px 14px;
        border-radius: 20px;
        font-weight: 700;
        font-size: 0.9rem;
        letter-spacing: 0.05em;
        margin-bottom: 12px;
    }

    /* Summary info grid items */
    .summary-box {
        background: #1e2430;
        border-radius: 8px;
        padding: 12px;
        border-left: 3px solid #38bdf8;
    }
    .summary-label {
        font-size: 0.75rem;
        color: #94a3b8;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    .summary-val {
        font-size: 1.1rem;
        font-weight: 700;
        color: #f8fafc;
        margin-top: 2px;
    }

    /* Color coding utility classes */
    .val-positive { color: #10b981 !important; }
    .val-negative { color: #ef4444 !important; }
    .val-neutral  { color: #f59e0b !important; }

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
        padding: 12px 0;
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
    st.info("💡 **Tip**: Train Prophet, ARIMA, and LSTM to unlock full Model Comparison insights!")

# -----------------------------------------------------------------------------
# 4. MAIN DASHBOARD CONTENT AREA
# -----------------------------------------------------------------------------

# Title Banner
st.title("📈 Market Intelligence & Forecasting Dashboard")
st.caption("Real-time historical price action, AI model projections, and stock fundamentals.")

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
# FEATURE 3 & 4: TABBED NAVIGATION DASHBOARD & COLOR CODING
# -----------------------------------------------------------------------------
tab_hist, tab_forecast, tab_news, tab_compare = st.tabs([
    "📊 Historical Data", 
    "🔮 Forecast Engine", 
    "📰 Market News", 
    "⚖️ Model Comparison"
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
                    st.success(f"Training Complete for {model_choice}!")
                    st.rerun()
                    
            if st.session_state["current_forecast"] is not None:
                curr_metrics = st.session_state["current_forecast"]["metrics"]
                st.markdown("<hr style='border-color: #232936;'>", unsafe_allow_html=True)
                st.write(f"**Latest Model ({st.session_state['current_forecast']['model']}) Metrics:**")
                m_c1, m_c2, m_c3 = st.columns(3)
                m_c1.metric("RMSE", f"{curr_metrics.get('RMSE', 0):.2f}")
                m_c2.metric("MAE", f"{curr_metrics.get('MAE', 0):.2f}")
                m_c3.metric("MAPE", f"{curr_metrics.get('MAPE', 0):.2f}%")

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

    # --- FORECAST INTERPRETABILITY & MODEL COMMENTARY CARD ---
    if st.session_state["all_forecasts"]:
        st.markdown("<br>", unsafe_allow_html=True)
        with st.container(border=True):
            st.markdown('<div class="vesper-title">🧠 AI Forecast Interpretability & Model Commentary</div>', unsafe_allow_html=True)
            
            # Determine target model for interpretability
            target_model_name = selected_view if (selected_view != "Combined Comparison" and selected_view in st.session_state["all_forecasts"]) else list(st.session_state["all_forecasts"].keys())[0]
            target_fc_df = st.session_state["all_forecasts"][target_model_name]["df"]
            
            interp = generate_forecast_interpretability(
                forecast_df=target_fc_df,
                current_price=summary['current_price'],
                model_name=target_model_name
            )
            
            # Render Color-Coded Sentiment Badge
            st.markdown(f"""
                <div class="sentiment-badge" style="background-color: {interp['badge_color']}20; color: {interp['badge_color']}; border: 1px solid {interp['badge_color']};">
                    {interp['icon']} {interp['sentiment']} FORECAST ({target_model_name} Model)
                </div>
            """, unsafe_allow_html=True)
            
            # Render Insights Bullet Points
            for point in interp["insights"]:
                st.markdown(f"- {point}")

# =============================================================================
# TAB 3: MARKET NEWS & SENTIMENT
# =============================================================================
with tab_news:
    with st.container(border=True):
        st.markdown(f'<div class="vesper-title">📰 Financial News & Sentiment Feed — {summary["company_name"]}</div>', unsafe_allow_html=True)
        
        news_items = fetch_stock_news(selected_stock)
        
        if news_items:
            n_cols = st.columns(2)
            for idx, item in enumerate(news_items[:6]):
                col_idx = idx % 2
                with n_cols[col_idx]:
                    st.markdown(f"""
                        <div class="news-item">
                            <a class="news-title" href="{item.get('url', '#')}" target="_blank">🔗 {item.get('title', 'Headline')}</a>
                            <div class="news-meta">Source: <strong>{item.get('source', 'News')}</strong> • {item.get('date', 'Recent')}</div>
                        </div>
                    """, unsafe_allow_html=True)
        else:
            st.write("No recent news articles found for this ticker.")

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
