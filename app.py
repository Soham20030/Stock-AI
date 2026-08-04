import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from utils.data_loader import load_dataset, get_stock_summary
from utils.metrics import load_all_training_history

# Import UI Component Modules
from components.helpers import inject_custom_css, render_summary_box
from components.sidebar import render_sidebar
from components.metrics_cards import render_top_metrics_row, render_stock_fundamentals
from components.forecast_tab import render_historical_tab, render_forecast_tab
from components.news_tab import render_news_tab
from components.model_comparison_tab import render_model_comparison_tab
from components.explanation_tab import render_explanation_tab
from components.chatbot_tab import render_chatbot_tab

# -----------------------------------------------------------------------------
# 1. PAGE CONFIGURATION & CUSTOM CSS
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="Stock AI | AI Market Forecasting",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)
inject_custom_css()

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

# -----------------------------------------------------------------------------
# 3. SIDEBAR CONTROLS DELEGATION
# -----------------------------------------------------------------------------
selected_stock = render_sidebar()

# -----------------------------------------------------------------------------
# 4. MAIN DASHBOARD CONTENT AREA & DATA LOADING
# -----------------------------------------------------------------------------
st.title("📈 Market Intelligence & Forecasting Dashboard")
st.caption("Real-time historical price action, AI model projections, and RAG contextual signals.")

if not selected_stock:
    st.info("👈 Please select or upload a dataset in the sidebar to get started.")
    st.stop()

# Load Active Dataset
raw_df = load_dataset(selected_stock)

if raw_df.empty:
    st.error(f"Failed to load data for {selected_stock}. Please check CSV column format ('Date', 'Close').")
    st.stop()

# Extract Stock Summary Metrics
summary = get_stock_summary(raw_df, selected_stock)

# -----------------------------------------------------------------------------
# 5. TOP METRICS ROW & STOCK FUNDAMENTALS PROFILE
# -----------------------------------------------------------------------------
active_view = st.session_state.get("forecast_view_selector", None)
render_top_metrics_row(summary, active_view=active_view, all_forecasts=st.session_state["all_forecasts"])
render_stock_fundamentals(summary)

# -----------------------------------------------------------------------------
# 6. TABBED DASHBOARD NAVIGATION DELEGATION
# -----------------------------------------------------------------------------
tab_hist, tab_forecast, tab_news, tab_compare, tab_archive, tab_rag, tab_chat = st.tabs([
    "📊 Historical Data", 
    "🔮 Forecast Engine", 
    "📰 Market News", 
    "⚖️ Model Comparison",
    "📜 Training History",
    "🧠 AI Explanation",
    "💬 AI Analyst"
])

# Tab 1: Historical Data
with tab_hist:
    render_historical_tab(raw_df, selected_stock)

# Tab 2: Forecast Engine
with tab_forecast:
    render_forecast_tab(raw_df, selected_stock, summary)

# Tab 3: Market News
with tab_news:
    render_news_tab(selected_stock, summary["company_name"])

# Tab 4: Model Comparison
with tab_compare:
    render_model_comparison_tab(st.session_state["model_history"])

# Tab 5: Training History Inspector
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
            selected_record = next((r for r in history_records if r["label"] == selected_run_label), None)
            
            if selected_record:
                st.markdown("<hr style='border-color: #232936;'>", unsafe_allow_html=True)
                r_stock = selected_record.get("stock", "Asset")
                r_model = selected_record.get("model", "Model")
                r_time = selected_record.get("timestamp", "Date")
                
                st.subheader(f"📌 Training Run: {r_stock} — {r_model}")
                st.caption(f"Archived Timestamp: **{r_time}**")
                
                r_metrics = selected_record.get("metrics", {})
                rm_c1, rm_c2, rm_c3 = st.columns(3)
                with rm_c1: render_summary_box("RMSE", f"${r_metrics.get('RMSE', 0):.2f}")
                with rm_c2: render_summary_box("MAE", f"${r_metrics.get('MAE', 0):.2f}")
                with rm_c3: render_summary_box("MAPE", f"{r_metrics.get('MAPE', 0):.2f}%")
                
                raw_fdata = selected_record.get("forecast_data", [])
                if raw_fdata:
                    f_df = pd.DataFrame(raw_fdata)
                    fig_hist_run = go.Figure()
                    hist_mask = f_df["type"] == "Historical"
                    fig_hist_run.add_trace(go.Scatter(x=f_df.loc[hist_mask, "Date"], y=f_df.loc[hist_mask, "Price"], mode="lines", name="Historical Price", line=dict(color="#94a3b8", width=2)))
                    pred_mask = f_df["type"] == "Forecast"
                    color_map = {"Prophet": "#38bdf8", "ARIMA": "#f97316", "LSTM": "#10b981"}
                    fig_hist_run.add_trace(go.Scatter(x=f_df.loc[pred_mask, "Date"], y=f_df.loc[pred_mask, "Price"], mode="lines", name=f"{r_model} Forecast", line=dict(color=color_map.get(r_model, "#10b981"), width=3, dash="dash")))
                    fig_hist_run.update_layout(template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", margin=dict(l=10, r=10, t=20, b=20), xaxis=dict(showgrid=True, gridcolor="#1e2430", title="Date"), yaxis=dict(showgrid=True, gridcolor="#1e2430", title="Price ($)"), height=360)
                    st.plotly_chart(fig_hist_run, use_container_width=True)
        else:
            st.info("No past training runs archived yet. Go to the 'Forecast Engine' tab and train a model to log history!")

# Tab 6: AI Explanation
with tab_rag:
    render_explanation_tab(selected_stock, summary, raw_df)

# Tab 7: AI Analyst Chatbot
with tab_chat:
    render_chatbot_tab(selected_stock, summary)
