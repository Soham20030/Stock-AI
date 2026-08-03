import pandas as pd
from models.prophet_model import train_and_forecast_prophet
from models.arima_model import train_and_forecast_arima
from models.lstm_model import train_and_forecast_lstm
from utils.metrics import save_metrics_to_json


def run_forecast(model_name, df, forecast_days=90):
    """
    Central dispatcher function (Facade Pattern) that routes forecasting tasks 
    to the appropriate model strategy based on user selection.

    Parameters:
        model_name (str): Selected model name ('Prophet', 'ARIMA', or 'LSTM').
        df (pd.DataFrame): Processed historical DataFrame containing 'Date' and 'Close'.
        forecast_days (int): Horizon days to project into the future (default 90 days).

    Returns:
        tuple: (forecast_df, metrics_dict)
            - forecast_df (pd.DataFrame): Unified output DataFrame with columns 
              ['Date', 'Price', 'Upper', 'Lower', 'type'].
            - metrics_dict (dict): Dictionary with keys 'RMSE', 'MAE', and 'MAPE'.
    """
    if df.empty or "Close" not in df.columns:
        return pd.DataFrame(), {"RMSE": 0, "MAE": 0, "MAPE": 0}

    # Normalize model selection string
    selected = model_name.strip().upper()

    if selected == "PROPHET":
        forecast_df, metrics = train_and_forecast_prophet(df, forecast_days=forecast_days)
    elif selected == "ARIMA":
        forecast_df, metrics = train_and_forecast_arima(df, forecast_days=forecast_days)
    elif selected == "LSTM":
        forecast_df, metrics = train_and_forecast_lstm(df, forecast_days=forecast_days)
    else:
        # Fallback to Prophet if unknown selection string is passed
        forecast_df, metrics = train_and_forecast_prophet(df, forecast_days=forecast_days)

    # Automatically persist metrics to results/ folder if stock identifier present
    stock_identifier = "Dataset"
    save_metrics_to_json(
        model_name=model_name,
        stock_name=stock_identifier,
        metrics=metrics
    )

    return forecast_df, metrics


def generate_forecast_interpretability(forecast_df, current_price, model_name="Model"):
    """
    Analyzes a 90-day forecast DataFrame and generates human-readable interpretability
    insights, market sentiment classification (Bullish, Bearish, Neutral), and confidence bounds.

    Parameters:
        forecast_df (pd.DataFrame): Standardized forecast DataFrame.
        current_price (float): Current closing price of the stock.
        model_name (str): Name of the model used (e.g. 'LSTM').

    Returns:
        dict: Interpretability metrics, sentiment category, color badge, and bullet points.
    """
    if forecast_df.empty or "type" not in forecast_df.columns:
        return {
            "sentiment": "NEUTRAL",
            "badge_color": "#f59e0b",
            "icon": "↔️",
            "delta_pct": 0.0,
            "target_price": current_price,
            "insights": ["No forecast data available."]
        }

    # Extract future forecast rows
    pred_df = forecast_df[forecast_df["type"] == "Forecast"].copy()
    if pred_df.empty:
        return {
            "sentiment": "NEUTRAL",
            "badge_color": "#f59e0b",
            "icon": "↔️",
            "delta_pct": 0.0,
            "target_price": current_price,
            "insights": ["No forecast data available."]
        }

    target_price = float(pred_df["Price"].iloc[-1])
    target_date = str(pred_df["Date"].iloc[-1])[:10]
    
    # Calculate projected gain/loss
    delta_val = target_price - current_price
    delta_pct = (delta_val / current_price * 100) if current_price != 0 else 0.0

    # Extract Upper and Lower confidence bounds
    upper_bound = float(pred_df["Upper"].iloc[-1]) if "Upper" in pred_df.columns else target_price
    lower_bound = float(pred_df["Lower"].iloc[-1]) if "Lower" in pred_df.columns else target_price
    channel_spread = upper_bound - lower_bound

    # Classify Sentiment (Bullish >= +2%, Bearish <= -2%, Sideways within +-2%)
    if delta_pct >= 2.0:
        sentiment = "BULLISH"
        badge_color = "#10b981"  # Emerald Green
        icon = "🚀"
        trend_desc = "upward momentum"
    elif delta_pct <= -2.0:
        sentiment = "BEARISH"
        badge_color = "#ef4444"  # Red
        icon = "🔻"
        trend_desc = "downward pressure"
    else:
        sentiment = "SIDEWAYS / NEUTRAL"
        badge_color = "#f59e0b"  # Amber Yellow
        icon = "↔️"
        trend_desc = "consolidating sideways"

    # Construct Interpretability Insight Points
    insights = [
        f"**Directional Sentiment**: The **{model_name}** model forecasts **{sentiment}** {trend_desc} over the next 90 days.",
        f"**Target Projection**: Projected price is **${target_price:.2f}** by **{target_date}** (an expected return of **{delta_pct:+.2f}%** from current ${current_price:.2f}).",
        f"**95% Confidence Channel**: Future prices are expected to trade between a lower support of **${lower_bound:.2f}** and upper resistance of **${upper_bound:.2f}**.",
        f"**Volatility Band Spread**: Channel width is **${channel_spread:.2f}**, reflecting {'low risk stability' if channel_spread < current_price * 0.15 else 'moderate to high market volatility'}."
    ]

    return {
        "sentiment": sentiment,
        "badge_color": badge_color,
        "icon": icon,
        "delta_pct": delta_pct,
        "target_price": target_price,
        "target_date": target_date,
        "upper_bound": upper_bound,
        "lower_bound": lower_bound,
        "insights": insights
    }
