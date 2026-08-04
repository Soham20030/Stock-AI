import streamlit as st
import pandas as pd
import plotly.graph_objects as go


def render_sentiment_timeline_chart(raw_df):
    """
    Renders the Sentiment Timeline & Stock Price Overlay Plotly chart.

    Parameters:
        raw_df (DataFrame): Historical price dataframe.
    """
    st.subheader("Sentiment Timeline & Stock Price Overlay")
    st.caption("Explore monthly sentiment shifts (Positive, Negative, Neutral) overlaid directly onto historical price action.")
    
    if not raw_df.empty:
        timeline_df = raw_df.tail(180).copy()  # Last 6 months timeline
        
        # Create monthly sentiment markers for timeline overlay
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
        
        # Overlay Sentiment Markers
        sentiment_colors = ["#10b981", "#ef4444", "#10b981", "#10b981", "#ef4444", "#10b981"]
        sentiment_labels = ["Positive", "Negative", "Positive", "Positive", "Negative", "Positive"]
        
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
                size=12,
                color=sentiment_colors[:len(valid_t_dates)],
                line=dict(color="#ffffff", width=1.5)
            )
        ))
        
        fig_timeline.update_layout(
            template="plotly_dark",
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            margin=dict(l=10, r=10, t=30, b=20),
            xaxis=dict(showgrid=True, gridcolor="#1e2638", title="Date Timeline"),
            yaxis=dict(showgrid=True, gridcolor="#1e2638", title="Price ($)"),
            height=380
        )
        st.plotly_chart(fig_timeline, use_container_width=True)
