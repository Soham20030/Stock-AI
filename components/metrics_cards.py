import streamlit as st
from components.helpers import render_summary_box


def render_top_metrics_row(summary, active_view=None, all_forecasts=None):
    """
    Renders the top 4 metric cards (Current Price, 3M Target, 24h Change, 30D Volume),
    dynamically synced to the active forecasting model selected by the user.
    """
    m_col1, m_col2, m_col3, m_col4 = st.columns(4, gap="small")

    with m_col1:
        st.metric(
            label="Current Price",
            value=f"${summary['current_price']:.2f}",
            delta=f"{summary['price_change']:+.2f} ({summary['pct_change']:+.2f}%)"
        )

    with m_col2:
        c_3m_val = summary.get('change_3m_val', 0.0)
        c_3m_pct = summary.get('change_3m_pct', 0.0)
        st.metric(
            label="3M Price Change",
            value=f"${c_3m_val:+.2f}",
            delta=f"{c_3m_pct:+.2f}%"
        )

    with m_col3:
        c_6m_val = summary.get('change_6m_val', 0.0)
        c_6m_pct = summary.get('change_6m_pct', 0.0)
        st.metric(
            label="6M Price Change",
            value=f"${c_6m_val:+.2f}",
            delta=f"{c_6m_pct:+.2f}%"
        )

    with m_col4:
        st.metric(
            label="30D Avg Volume",
            value=summary['avg_volume'],
            delta="Normal Liquidity",
            delta_color="off"
        )

    st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)


def render_stock_fundamentals(summary):
    """
    Renders the Stock Fundamentals & Profile 5-column container card with tight column gap fitting.
    """
    with st.container(border=True):
        st.markdown(f'<div class="intercom-title">Stock Profile — {summary["company_name"]}</div>', unsafe_allow_html=True)
        
        s1, s2, s3, s4, s5 = st.columns(5, gap="small")
        
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

    st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)
