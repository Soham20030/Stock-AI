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
