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
        change_class = "val-positive"
    elif delta_pct <= -2.0:
        sentiment = "BEARISH"
        badge_color = "#ef4444"  # Red
        icon = "🔻"
        trend_desc = "downward pressure"
        change_class = "val-negative"
    else:
        sentiment = "SIDEWAYS / NEUTRAL"
        badge_color = "#f59e0b"  # Amber Yellow
        icon = "↔️"
        trend_desc = "consolidating sideways"
        change_class = "val-neutral"

    risk_text = "low risk stability" if channel_spread < current_price * 0.15 else "moderate to high market volatility"

    # Construct Clean HTML Interpretability Insight Points (using <b> tags instead of ** asterisks)
    insights = [
        f"<b>Directional Sentiment:</b> The <b>{model_name}</b> model forecasts <b>{sentiment}</b> {trend_desc} over the next 90 days.",
        f"<b>Target Projection:</b> Projected price is <b>${target_price:.2f}</b> by <b>{target_date}</b> (an expected return of <span class='{change_class}'><b>{delta_pct:+.2f}%</b></span> from current <b>${current_price:.2f}</b>).",
        f"<b>95% Confidence Channel:</b> Future prices are expected to trade between a lower support of <b>${lower_bound:.2f}</b> and upper resistance of <b>${upper_bound:.2f}</b>.",
        f"<b>Volatility Band Spread:</b> Channel width is <b>${channel_spread:.2f}</b>, reflecting <b>{risk_text}</b>."
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


def generate_combined_interpretability(all_forecasts, current_price, model_history):
    """
    Generates multi-model consensus interpretability, ensemble average target prices,
    and best model recommendation when 'Combined Comparison' mode is selected.

    Parameters:
        all_forecasts (dict): Dictionary of all trained model forecasts.
        current_price (float): Current price of the stock.
        model_history (dict): Dictionary of model metrics (RMSE, MAE, MAPE).

    Returns:
        dict: Consensus sentiment, best model recommendation, and insight bullet points.
    """
    if not all_forecasts:
        return {
            "sentiment": "NEUTRAL",
            "badge_color": "#f59e0b",
            "icon": "↔️",
            "insights": ["No models trained yet."]
        }

    targets = []
    sentiments = []
    model_summaries = []

    for m_name, m_data in all_forecasts.items():
        m_df = m_data["df"]
        pred_mask = m_df["type"] == "Forecast"
        if pred_mask.any():
            t_price = float(m_df.loc[pred_mask, "Price"].iloc[-1])
            targets.append(t_price)
            
            d_pct = ((t_price - current_price) / current_price) * 100
            if d_pct >= 2.0:
                sentiments.append("BULLISH")
            elif d_pct <= -2.0:
                sentiments.append("BEARISH")
            else:
                sentiments.append("NEUTRAL")
                
            model_summaries.append(f"{m_name}: ${t_price:.2f} ({d_pct:+.2f}%)")

    # Calculate Ensemble Average Target
    avg_target = float(sum(targets) / len(targets)) if targets else current_price
    avg_delta_pct = ((avg_target - current_price) / current_price) * 100

    # Count Sentiment Majority
    bullish_cnt = sentiments.count("BULLISH")
    bearish_cnt = sentiments.count("BEARISH")
    total_models = len(sentiments)

    if bullish_cnt > total_models / 2:
        consensus_sentiment = "BULLISH CONSENSUS"
        badge_color = "#10b981"
        icon = "🚀"
        change_class = "val-positive"
    elif bearish_cnt > total_models / 2:
        consensus_sentiment = "BEARISH CONSENSUS"
        badge_color = "#ef4444"
        icon = "🔻"
        change_class = "val-negative"
    else:
        consensus_sentiment = "MIXED / NEUTRAL CONSENSUS"
        badge_color = "#f59e0b"
        icon = "↔️"
        change_class = "val-neutral"

    # Find Best Model (lowest MAPE)
    best_model_name = None
    best_mape = float("inf")
    for m_name, m_metrics in model_history.items():
        mape_val = m_metrics.get("MAPE", float("inf"))
        if mape_val < best_mape:
            best_mape = mape_val
            best_model_name = m_name

    min_target = min(targets) if targets else current_price
    max_target = max(targets) if targets else current_price

    insights = [
        f"<b>Multi-Model Agreement:</b> <b>{bullish_cnt} of {total_models} models</b> predict an upward <b>Bullish trajectory</b>, establishing market consensus.",
        f"<b>Ensemble Average Target:</b> Combined average 90-day target is <b>${avg_target:.2f}</b> (an expected return of <span class='{change_class}'><b>{avg_delta_pct:+.2f}%</b></span>).",
        f"<b>Best Model Recommendation:</b> The <b>{best_model_name if best_model_name else 'LSTM'}</b> model is recommended as primary forecast due to lowest error (<b>MAPE: {best_mape:.2f}%</b>).",
        f"<b>Projection Range Spread:</b> Predictions across models range from a conservative <b>${min_target:.2f}</b> to an optimistic <b>${max_target:.2f}</b>."
    ]

    return {
        "sentiment": consensus_sentiment,
        "badge_color": badge_color,
        "icon": icon,
        "avg_target": avg_target,
        "best_model": best_model_name,
        "insights": insights
    }
