import pandas as pd
import numpy as np
from datetime import timedelta
from utils.metrics import calculate_metrics

from performance.profiler import profile_step

# Try importing statsmodels ARIMA; provide fallback if library is not installed
try:
    from statsmodels.tsa.arima.model import ARIMA
    STATSMODELS_AVAILABLE = True
except ImportError:
    STATSMODELS_AVAILABLE = False


@profile_step("ARIMA Training")
def train_and_forecast_arima(df, forecast_days=90, order=(5, 1, 2)):
    """
    Trains an ARIMA (AutoRegressive Integrated Moving Average) statistical model
    on stock close prices, evaluates validation metrics, and forecasts N days into the future.

    Parameters:
        df (pd.DataFrame): Input DataFrame with 'Date' and 'Close' columns.
        forecast_days (int): Horizon days to forecast (default 90).
        order (tuple): ARIMA parameters (p, d, q). Default is (5, 1, 2).

    Returns:
        tuple: (forecast_df, metrics_dict)
            - forecast_df (pd.DataFrame): Standardized DataFrame with columns 
              ['Date', 'Price', 'Upper', 'Lower', 'type'].
            - metrics_dict (dict): Dictionary with RMSE, MAE, and MAPE scores.
    """
    if df.empty or len(df) < 30:
        return pd.DataFrame(), {"RMSE": 0, "MAE": 0, "MAPE": 0}

    arima_df = df[["Date", "Close"]].copy()
    arima_df["Date"] = pd.to_datetime(arima_df["Date"])
    prices = arima_df["Close"].values

    # Train / Test split (reserve last 60 points for validation metrics)
    test_size = min(60, int(len(prices) * 0.2))
    train_prices = prices[:-test_size]
    test_prices = prices[-test_size:]
    test_dates = arima_df["Date"].iloc[-test_size:]

    if STATSMODELS_AVAILABLE:
        try:
            # 1. Fit ARIMA on Training data for metrics evaluation
            model_val = ARIMA(train_prices, order=order)
            fitted_val = model_val.fit()
            
            # Predict validation horizon
            pred_val = fitted_val.forecast(steps=test_size)
            metrics = calculate_metrics(test_prices, pred_val)

            # 2. Fit ARIMA on Full historical dataset for future forecasting
            full_model = ARIMA(prices, order=order)
            full_fitted = full_model.fit()

            # Forecast future days and extract confidence intervals
            forecast_res = full_fitted.get_forecast(steps=forecast_days)
            forecast_mean = forecast_res.predicted_mean
            conf_int = forecast_res.conf_int(alpha=0.05)  # 95% confidence interval

            # Extract lower and upper bounds
            lower_bound = conf_int[:, 0] if conf_int.ndim == 2 else conf_int.iloc[:, 0].values
            upper_bound = conf_int[:, 1] if conf_int.ndim == 2 else conf_int.iloc[:, 1].values

            # Generate future timestamps
            last_date = arima_df["Date"].max()
            future_dates = [last_date + timedelta(days=i+1) for i in range(forecast_days)]

            forecast_output = pd.DataFrame({
                "Date": future_dates,
                "Price": forecast_mean,
                "Upper": upper_bound,
                "Lower": lower_bound,
                "type": "Forecast"
            })

        except Exception as e:
            print(f"ARIMA optimization warning: {e}. Executing fallback method.")
            metrics, forecast_output = _arima_fallback(arima_df, test_prices, forecast_days)
    else:
        metrics, forecast_output = _arima_fallback(arima_df, test_prices, forecast_days)

    # Format historical records component
    historical_output = pd.DataFrame({
        "Date": arima_df["Date"],
        "Price": arima_df["Close"],
        "Upper": arima_df["Close"],
        "Lower": arima_df["Close"],
        "type": "Historical"
    })

    final_df = pd.concat([historical_output, forecast_output], ignore_index=True)
    return final_df, metrics


def _arima_fallback(arima_df, test_prices, forecast_days):
    """
    Fallback forecasting implementation using Exponential Moving Average (EMA)
    and AR(1) autoregressive drift when statsmodels fails to converge or is missing.
    """
    prices = arima_df["Close"].values
    n_train = len(prices) - len(test_prices)
    
    # Calculate historical daily percentage returns and volatility
    train_prices = prices[:n_train]
    returns = np.diff(train_prices) / train_prices[:-1]
    mean_return = np.mean(returns) if len(returns) > 0 else 0.0005
    std_return = np.std(returns) if len(returns) > 0 else 0.015

    # Validation prediction using AR(1) constant growth assumption
    val_pred = train_prices[-1] * (1 + mean_return) ** np.arange(1, len(test_prices) + 1)
    metrics = calculate_metrics(test_prices, val_pred)

    # Forecast future days
    last_price = prices[-1]
    future_pred = last_price * (1 + mean_return) ** np.arange(1, forecast_days + 1)

    # Compute expanding standard error bounds
    std_errors = last_price * std_return * np.sqrt(np.arange(1, forecast_days + 1))
    upper = future_pred + (1.96 * std_errors)
    lower = np.maximum(future_pred - (1.96 * std_errors), 1.0)

    last_date = arima_df["Date"].max()
    future_dates = [last_date + timedelta(days=i+1) for i in range(forecast_days)]

    forecast_output = pd.DataFrame({
        "Date": future_dates,
        "Price": future_pred,
        "Upper": upper,
        "Lower": lower,
        "type": "Forecast"
    })

    return metrics, forecast_output
