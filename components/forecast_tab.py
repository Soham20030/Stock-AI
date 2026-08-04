import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from utils.data_loader import filter_data_by_range
from utils.forecasting import (
    run_forecast,
    generate_forecast_interpretability,
    generate_combined_interpretability
)
from utils.metrics import save_training_run_to_history
from state.mode_manager import is_developer_mode, is_user_mode
from components.helpers import render_summary_box


def render_historical_tab(raw_df, selected_stock):
    """
    Renders Tab 1: Historical Data chart and date range filtering options.
    """
    with st.container(border=True):
        st.markdown(f'<div class="intercom-title">Historical Price Action — {selected_stock}</div>', unsafe_allow_html=True)
        
        # Date Range Filter Selector
        range_option = st.radio(
            "Time Horizon:",
            options=["6 Months", "1 Year", "2 Years", "Max"],
            index=2,
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
                line=dict(color="#818cf8", width=2)
            )
        )
        fig_hist.update_layout(
            template="plotly_dark",
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            margin=dict(l=10, r=10, t=20, b=20),
            xaxis=dict(showgrid=True, gridcolor="#1a1d24", title="Date"),
            yaxis=dict(showgrid=True, gridcolor="#1a1d24", title="Price ($)"),
            height=400
        )
        st.plotly_chart(fig_hist, use_container_width=True)


def render_forecast_tab(raw_df, selected_stock, summary):
    """
    Renders Tab 2: Forecast Engine controls and Plotly projection charts.

    User Mode:
        - Displays 3-Month Projection Chart & AI Interpretability Commentary
        - Hides model training panel & technical error metrics (RMSE/MAE/MAPE)

    Developer Mode:
        - Displays Model Selection, Progress Bar, Train Button, RMSE/MAE/MAPE cards
        - Displays 3-Month Projection Chart & AI Interpretability Commentary
    """
    # -------------------------------------------------------------------------
    # DEVELOPER MODE ONLY: MODEL TRAINING CONTROLS & ERROR METRICS PANEL
    # -------------------------------------------------------------------------
    if is_developer_mode():
        col_ctrl, col_chart = st.columns([1, 2.5])
        
        with col_ctrl:
            with st.container(border=True):
                st.markdown('<div class="intercom-title">Model Controls</div>', unsafe_allow_html=True)
                
                model_choice = st.selectbox(
                    "Forecasting Model:",
                    options=["Prophet", "ARIMA", "LSTM"],
                    index=0,
                    help="Choose between Meta Prophet, Statistical ARIMA, or Deep Learning LSTM."
                )
                
                forecast_days = 90  # Next 3 months (approx 90 days)
                st.caption(f"Forecast Horizon: **{forecast_days} Days (3 Months)**")
                st.markdown("<div style='height: 8px;'></div>", unsafe_allow_html=True)
                
                if st.button("Train & Forecast"):
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
                        
                        st.cache_data.clear()  # Refresh RAG cache for new forecast
                        
                        st.success(f"Training Complete for {model_choice}!")
                        st.rerun()
                        
                active_model_metrics = None
                active_model_name = model_choice
                if model_choice in st.session_state["all_forecasts"]:
                    active_model_metrics = st.session_state["all_forecasts"][model_choice]["metrics"]
                elif st.session_state["current_forecast"] is not None:
                    active_model_metrics = st.session_state["current_forecast"]["metrics"]
                    active_model_name = st.session_state["current_forecast"]["model"]

                if active_model_metrics is not None:
                    st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)
                    st.markdown(f"**{active_model_name} Technical Metrics:**")
                    
                    m_c1, m_c2, m_c3 = st.columns(3)
                    with m_c1: render_summary_box("RMSE", f"${active_model_metrics.get('RMSE', 0):.2f}")
                    with m_c2: render_summary_box("MAE", f"${active_model_metrics.get('MAE', 0):.2f}")
                    with m_c3: render_summary_box("MAPE", f"{active_model_metrics.get('MAPE', 0):.2f}%")

        chart_container = col_chart
    else:
        # User Mode: Full width projection chart container
        chart_container = st.container()

    # -------------------------------------------------------------------------
    # PROJECTION CHART (BOTH MODES)
    # -------------------------------------------------------------------------
    with chart_container:
        with st.container(border=True):
            st.markdown(
                f'<div class="intercom-title">3-Month Price Projections ({selected_stock})</div>',
                unsafe_allow_html=True
            )
            
            selected_view = None
            if st.session_state["all_forecasts"]:
                available_models = list(st.session_state["all_forecasts"].keys())
                view_options = available_models.copy()
                if len(available_models) > 1 and is_developer_mode():
                    view_options.append("Combined Comparison")
                    
                selected_view = st.radio(
                    "View Model Projection:",
                    options=view_options,
                    index=0,
                    horizontal=True,
                    key="forecast_view_selector"
                )
                
                fig_fc = go.Figure()
                color_map = {"Prophet": "#818cf8", "ARIMA": "#f97316", "LSTM": "#10b981"}
                
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
                            line=dict(color=color_map.get(m_name, "#a855f7"), width=2.5, dash="dash")
                        ))
                else:
                    target_model = selected_view if selected_view else list(st.session_state["all_forecasts"].keys())[0]
                    forecast_data = st.session_state["all_forecasts"][target_model]
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
                    line_color = color_map.get(target_model, "#10b981")
                    
                    fig_fc.add_trace(go.Scatter(
                        x=fc_df.loc[pred_mask, "Date"],
                        y=fc_df.loc[pred_mask, "Price"],
                        mode="lines",
                        name=f"{target_model} Forecast",
                        line=dict(color=line_color, width=2.5, dash="dash")
                    ))
                    
                    if "Upper" in fc_df.columns and "Lower" in fc_df.columns:
                        fig_fc.add_trace(go.Scatter(
                            x=fc_df.loc[pred_mask, "Date"],
                            y=fc_df.loc[pred_mask, "Upper"],
                            mode="lines",
                            name="Upper Bound",
                            line=dict(color="rgba(129, 140, 248, 0.15)"),
                            showlegend=False
                        ))
                        fig_fc.add_trace(go.Scatter(
                            x=fc_df.loc[pred_mask, "Date"],
                            y=fc_df.loc[pred_mask, "Lower"],
                            mode="lines",
                            name="Lower Bound",
                            fill="tonexty",
                            fillcolor="rgba(129, 140, 248, 0.08)",
                            line=dict(color="rgba(129, 140, 248, 0.15)"),
                            showlegend=False
                        ))

                fig_fc.update_layout(
                    template="plotly_dark",
                    paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor="rgba(0,0,0,0)",
                    margin=dict(l=10, r=10, t=20, b=20),
                    xaxis=dict(showgrid=True, gridcolor="#1a1d24", title="Date"),
                    yaxis=dict(showgrid=True, gridcolor="#1a1d24", title="Price ($)"),
                    height=380
                )
                st.plotly_chart(fig_fc, use_container_width=True)
            else:
                if is_developer_mode():
                    st.info("Select a model and click 'Train & Forecast' to generate predictions.")
                else:
                    st.info("No forecast payload loaded yet. Switch to Developer Mode to train a forecasting model.")

    # -------------------------------------------------------------------------
    # FORECAST INTERPRETABILITY & COMMENTARY CARD (BOTH MODES)
    # -------------------------------------------------------------------------
    if st.session_state["all_forecasts"]:
        st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)
        with st.container(border=True):
            st.markdown('<div class="intercom-title">Forecast Insights & Commentary</div>', unsafe_allow_html=True)
            
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
                    bullish_c = interp.get("bullish_cnt", 0)
                    total_m = interp.get("total_models", 0)
                    change_cls = "val-positive" if sentiment_val.startswith("BULLISH") else ("val-negative" if sentiment_val.startswith("BEARISH") else "val-neutral")
                    
                    render_summary_box(
                        label="Multi-Model Consensus",
                        value=sentiment_val,
                        subtext=f"{bullish_c} of {total_m} models predict Bullish trend",
                        border_color=badge_col,
                        val_class=change_cls
                    )
                    
                with ic2:
                    avg_t = interp.get("avg_target", summary['current_price'])
                    avg_d = interp.get("avg_delta_pct", 0.0)
                    change_cls = "val-positive" if avg_d >= 0 else "val-negative"
                    render_summary_box(
                        label="Ensemble Avg Target",
                        value=f"${avg_t:.2f}",
                        subtext=f"{avg_d:+.2f}% average expected return",
                        val_class=change_cls
                    )

                with ic3:
                    b_model = interp.get("best_model", "LSTM")
                    b_mape = interp.get("best_mape", 0.0)
                    render_summary_box(
                        label="Top Model Consensus",
                        value=b_model,
                        subtext=f"Highest accuracy model",
                        val_class="val-positive"
                    )

                with ic4:
                    min_t = interp.get("min_target", summary['current_price'])
                    max_t = interp.get("max_target", summary['current_price'])
                    render_summary_box(
                        label="Target Range Spread",
                        value=f"${min_t:.2f} — ${max_t:.2f}",
                        subtext="Min to Max target range"
                    )

            else:
                target_model_name = selected_view if (selected_view and selected_view in st.session_state["all_forecasts"]) else list(st.session_state["all_forecasts"].keys())[0]
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
                    trend_d = interp.get("trend_desc", "predicts trend")
                    change_cls = "val-positive" if sentiment_val == "BULLISH" else ("val-negative" if sentiment_val == "BEARISH" else "val-neutral")
                    
                    render_summary_box(
                        label="Directional Sentiment",
                        value=sentiment_val,
                        subtext=f"Predicted {trend_d}",
                        border_color=badge_col,
                        val_class=change_cls
                    )
                    
                with ic2:
                    t_price = interp.get("target_price", summary['current_price'])
                    d_pct = interp.get("delta_pct", 0.0)
                    t_date = interp.get("target_date", "N/A")
                    change_cls = "val-positive" if d_pct >= 0 else "val-negative"
                    
                    render_summary_box(
                        label="90-Day Target Projection",
                        value=f"${t_price:.2f}",
                        subtext=f"{d_pct:+.2f}% return by {t_date}",
                        val_class=change_cls
                    )

                with ic3:
                    l_bound = interp.get("lower_bound", summary['current_price'])
                    u_bound = interp.get("upper_bound", summary['current_price'])
                    
                    render_summary_box(
                        label="95% Confidence Channel",
                        value=f"${l_bound:.2f} — ${u_bound:.2f}",
                        subtext="Support to Resistance trading band"
                    )

                with ic4:
                    c_spread = interp.get("channel_spread", 0.0)
                    r_text = interp.get("risk_text", "market volatility")
                    
                    render_summary_box(
                        label="Volatility Band Spread",
                        value=f"${c_spread:.2f}",
                        subtext=f"Reflecting {r_text}"
                    )
