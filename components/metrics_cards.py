import streamlit as st
from components.helpers import render_summary_box


def render_top_metrics_row(summary, active_view=None, all_forecasts=None):
    """
    Renders the top 4 metric cards (Current Price, 3M Target, 24h Change, 30D Volume),
    dynamically synced to the active forecasting model selected by the user.

    Parameters:
        summary (dict): Stock summary fundamentals.
        active_view (str, optional): Active model name ('Prophet', 'ARIMA', 'LSTM', 'Combined Comparison').
        all_forecasts (dict, optional): Map of trained model payloads.
    """
    m_col1, m_col2, m_col3, m_col4 = st.columns(4)

    with m_col1:
        st.metric(
            label="Current Price",
            value=f"${summary['current_price']:.2f}",
            delta=f"{summary['price_change']:+.2f} ({summary['pct_change']:+.2f}%)"
        )

    with m_col2:
        # Dynamically find the target prediction price for the active model view
        target_pred_price = None
        pred_delta_val = 0.0
        pred_delta_pct = 0.0
        active_label = active_view

        if all_forecasts and len(all_forecasts) > 0:
            if not active_label or active_label == "Combined Comparison":
                active_label = list(all_forecasts.keys())[-1]

            if active_label in all_forecasts:
                fc_payload = all_forecasts[active_label]
                fc_df = fc_payload.get("df")
                if fc_df is not None and not fc_df.empty:
                    pred_mask = fc_df["type"] == "Forecast"
                    if pred_mask.any():
                        target_pred_price = float(fc_df.loc[pred_mask, "Price"].iloc[-1])
                        pred_delta_val = target_pred_price - summary['current_price']
                        pred_delta_pct = (pred_delta_val / summary['current_price']) * 100

        if target_pred_price is not None:
            st.metric(
                label=f"3M Predicted ({active_label})",
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


def render_stock_fundamentals(summary):
    """
    Renders the Stock Fundamentals & Profile 5-column container card.

    Parameters:
        summary (dict): Stock profile dictionary containing current_price, market_cap, high_52w, low_52w.
    """
    with st.container(border=True):
        st.markdown(f'<div class="vesper-title">🏛️ Stock Fundamentals & Profile — {summary["company_name"]}</div>', unsafe_allow_html=True)
        
        s1, s2, s3, s4, s5 = st.columns(5)
        
        with s1:
            render_summary_box("Company Asset", summary["company_name"])
            
        with s2:
            change_class = "val-positive" if summary['price_change'] >= 0 else "val-negative"
            render_summary_box("Current Price", f"${summary['current_price']:.2f}", val_class=change_class)

        with s3:
            render_summary_box("Market Capitalization", summary['market_cap'])

        with s4:
            render_summary_box("52-Week High", f"${summary['high_52w']:.2f}", val_class="val-positive")

        with s5:
            render_summary_box("52-Week Low", f"${summary['low_52w']:.2f}", val_class="val-negative")

    st.markdown("<br>", unsafe_allow_html=True)
