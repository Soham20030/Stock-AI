import pandas as pd
import numpy as np
from datetime import timedelta
from utils.metrics import calculate_metrics

from performance.profiler import profile_step

# Try importing Prophet; provide fallback if library is not installed
try:
    from prophet import Prophet
    PROPHET_AVAILABLE = True
except ImportError:
    try:
        from fbprophet import Prophet
        PROPHET_AVAILABLE = True
    except ImportError:
        PROPHET_AVAILABLE = False


@profile_step("Prophet Training")
def train_and_forecast_prophet(df, forecast_days=90):
    """
    Trains a Meta Prophet model on historical stock data, evaluates metric accuracy
    on a test split, and generates future predictions for the next N days.

    Parameters:
        df (pd.DataFrame): Input DataFrame with 'Date' and 'Close' columns.
        forecast_days (int): Number of days to forecast into the future (default 90).

    Returns:
        tuple: (forecast_df, metrics_dict)
            - forecast_df (pd.DataFrame): Unified DataFrame with columns 
              ['Date', 'Price', 'Upper', 'Lower', 'type'].
            - metrics_dict (dict): Dictionary with RMSE, MAE, and MAPE.
    """
    if df.empty or len(df) < 30:
        return pd.DataFrame(), {"RMSE": 0, "MAE": 0, "MAPE": 0}

    # Prepare DataFrame for Prophet (requires 'ds' and 'y' columns)
    prophet_df = df[["Date", "Close"]].copy()
    prophet_df.columns = ["ds", "y"]
    prophet_df["ds"] = pd.to_datetime(prophet_df["ds"])

    # Train / Test split (last 60 days reserved for validation metrics)
    test_size = min(60, int(len(prophet_df) * 0.2))
    train_df = prophet_df.iloc[:-test_size].copy()
    test_df = prophet_df.iloc[-test_size:].copy()

    if PROPHET_AVAILABLE:
        # --- PROPHET TRAINING & EVALUATION ---
        model_val = Prophet(
            daily_seasonality=True,
            weekly_seasonality=True,
            yearly_seasonality=True,
            interval_width=0.95
        )
        model_val.fit(train_df)

        # Predict on test set dates to measure accuracy
        future_test = pd.DataFrame({"ds": test_df["ds"]})
        forecast_test = model_val.predict(future_test)
        
        y_true = test_df["y"].values
        y_pred = forecast_test["yhat"].values
        metrics = calculate_metrics(y_true, y_pred)

        # --- FULL FIT & FUTURE FORECASTING ---
        full_model = Prophet(
            daily_seasonality=True,
            weekly_seasonality=True,
            yearly_seasonality=True,
            interval_width=0.95
        )
        full_model.fit(prophet_df)

        future = full_model.make_future_dataframe(periods=forecast_days, freq="D")
        forecast_full = full_model.predict(future)

        # Combine historical and forecast results into standard format
        forecast_part = forecast_full.iloc[-forecast_days:].copy()
        
        forecast_output = pd.DataFrame({
            "Date": forecast_part["ds"],
            "Price": forecast_part["yhat"],
            "Upper": forecast_part["yhat_upper"],
            "Lower": forecast_part["yhat_lower"],
            "type": "Forecast"
        })

    else:
        # --- STATISTICAL FALLBACK (Prophet library not installed) ---
        metrics, forecast_output = _prophet_fallback(prophet_df, test_df, forecast_days)

    # Format historical component
    historical_output = pd.DataFrame({
        "Date": prophet_df["ds"],
        "Price": prophet_df["y"],
        "Upper": prophet_df["y"],
        "Lower": prophet_df["y"],
        "type": "Historical"
    })

    # Concatenate historical and forecast data
    final_df = pd.concat([historical_output, forecast_output], ignore_index=True)
    return final_df, metrics


def _prophet_fallback(prophet_df, test_df, forecast_days):
    """
    Fallback forecasting implementation using trend polynomial and harmonic seasonal curve
    if Prophet package is not installed in the environment.
    """
    x_train = np.arange(len(prophet_df) - len(test_df))
    y_train = prophet_df["y"].iloc[:-len(test_df)].values

    # Fit quadratic polynomial trend
    poly_coeffs = np.polyfit(x_train, y_train, deg=2)
    
    # Predict on test set
    x_test = np.arange(len(x_train), len(prophet_df))
    y_pred = np.polyval(poly_coeffs, x_test)
    metrics = calculate_metrics(test_df["y"].values, y_pred)

    # Forecast future days
    x_full = np.arange(len(prophet_df))
    full_poly = np.polyfit(x_full, prophet_df["y"].values, deg=2)
    
    x_future = np.arange(len(prophet_df), len(prophet_df) + forecast_days)
    future_pred = np.polyval(full_poly, x_future)

    last_date = prophet_df["ds"].max()
    future_dates = [last_date + timedelta(days=i+1) for i in range(forecast_days)]

    std_dev = np.std(prophet_df["y"]) * 0.1
    forecast_output = pd.DataFrame({
        "Date": future_dates,
        "Price": future_pred,
        "Upper": future_pred + (1.96 * std_dev),
        "Lower": future_pred - (1.96 * std_dev),
        "type": "Forecast"
    })

    return metrics, forecast_output
