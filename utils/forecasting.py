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
    Analyzes a 90-day forecast DataFrame and returns structured metrics for UI display.

    Parameters:
        forecast_df (pd.DataFrame): Standardized forecast DataFrame.
        current_price (float): Current closing price of the stock.
        model_name (str): Name of the model used (e.g. 'LSTM').

    Returns:
        dict: Structured numerical metrics, sentiment classification, and bounds.
    """
    default_res = {
        "sentiment": "NEUTRAL",
        "badge_color": "#f59e0b",
        "icon": "↔️",
        "delta_pct": 0.0,
        "target_price": current_price,
        "target_date": "N/A",
        "upper_bound": current_price,
        "lower_bound": current_price,
        "channel_spread": 0.0,
        "risk_text": "N/A",
        "trend_desc": "neutral trend",
        "model_name": model_name
    }

    if forecast_df.empty or "type" not in forecast_df.columns:
        return default_res

    pred_df = forecast_df[forecast_df["type"] == "Forecast"].copy()
    if pred_df.empty:
        return default_res

    target_price = float(pred_df["Price"].iloc[-1])
    target_date = str(pred_df["Date"].iloc[-1])[:10]
    
    delta_val = target_price - current_price
    delta_pct = (delta_val / current_price * 100) if current_price != 0 else 0.0

    upper_bound = float(pred_df["Upper"].iloc[-1]) if "Upper" in pred_df.columns else target_price
    lower_bound = float(pred_df["Lower"].iloc[-1]) if "Lower" in pred_df.columns else target_price
    channel_spread = upper_bound - lower_bound

    if delta_pct >= 2.0:
        sentiment = "BULLISH"
        badge_color = "#10b981"
        icon = "🚀"
        trend_desc = "upward momentum"
    elif delta_pct <= -2.0:
        sentiment = "BEARISH"
        badge_color = "#ef4444"
        icon = "🔻"
        trend_desc = "downward pressure"
    else:
        sentiment = "SIDEWAYS / NEUTRAL"
        badge_color = "#f59e0b"
        icon = "↔️"
        trend_desc = "consolidating sideways"

    risk_text = "low risk stability" if channel_spread < current_price * 0.15 else "moderate to high volatility"

    return {
        "sentiment": sentiment,
        "badge_color": badge_color,
        "icon": icon,
        "delta_pct": delta_pct,
        "delta_val": delta_val,
        "target_price": target_price,
        "target_date": target_date,
        "upper_bound": upper_bound,
        "lower_bound": lower_bound,
        "channel_spread": channel_spread,
        "risk_text": risk_text,
        "trend_desc": trend_desc,
        "model_name": model_name
    }


def generate_combined_interpretability(all_forecasts, current_price, model_history):
    """
    Generates multi-model consensus interpretability metrics for Combined Comparison mode.

    Parameters:
        all_forecasts (dict): Dictionary of all trained model forecasts.
        current_price (float): Current price of the stock.
        model_history (dict): Dictionary of model metrics (RMSE, MAE, MAPE).

    Returns:
        dict: Multi-model consensus metrics for UI grid display.
    """
    if not all_forecasts:
        return {
            "sentiment": "NEUTRAL",
            "badge_color": "#f59e0b",
            "icon": "↔️",
            "avg_target": current_price,
            "best_model": "N/A",
            "best_mape": 0.0,
            "min_target": current_price,
            "max_target": current_price,
            "bullish_cnt": 0,
            "total_models": 0
        }

    targets = []
    sentiments = []

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

    avg_target = float(sum(targets) / len(targets)) if targets else current_price
    avg_delta_pct = ((avg_target - current_price) / current_price) * 100

    bullish_cnt = sentiments.count("BULLISH")
    bearish_cnt = sentiments.count("BEARISH")
    total_models = len(sentiments)

    if bullish_cnt > total_models / 2:
        consensus_sentiment = "BULLISH CONSENSUS"
        badge_color = "#10b981"
        icon = "🚀"
    elif bearish_cnt > total_models / 2:
        consensus_sentiment = "BEARISH CONSENSUS"
        badge_color = "#ef4444"
        icon = "🔻"
    else:
        consensus_sentiment = "MIXED / NEUTRAL CONSENSUS"
        badge_color = "#f59e0b"
        icon = "↔️"

    best_model_name = "LSTM"
    best_mape = 0.0
    if model_history:
        sorted_models = sorted(model_history.items(), key=lambda x: x[1].get("MAPE", float("inf")))
        best_model_name = sorted_models[0][0]
        best_mape = sorted_models[0][1].get("MAPE", 0.0)

    min_target = min(targets) if targets else current_price
    max_target = max(targets) if targets else current_price

    return {
        "sentiment": consensus_sentiment,
        "badge_color": badge_color,
        "icon": icon,
        "avg_target": avg_target,
        "avg_delta_pct": avg_delta_pct,
        "best_model": best_model_name,
        "best_mape": best_mape,
        "min_target": min_target,
        "max_target": max_target,
        "bullish_cnt": bullish_cnt,
        "total_models": total_models
    }
