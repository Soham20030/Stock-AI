import pandas as pd
import numpy as np
from datetime import timedelta
from sklearn.preprocessing import MinMaxScaler
from sklearn.neural_network import MLPRegressor
from utils.metrics import calculate_metrics

from performance.profiler import profile_step

# Try importing TensorFlow / Keras; set flag for fallback if missing
try:
    import tensorflow as tf
    from tensorflow.keras.models import Sequential
    from tensorflow.keras.layers import LSTM, Dense, Dropout
    # Suppress verbose TensorFlow logging
    import os
    os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
    TF_AVAILABLE = True
except ImportError:
    TF_AVAILABLE = False


@profile_step("LSTM Training")
def train_and_forecast_lstm(df, forecast_days=90, window_size=30):
    """
    Trains an LSTM (Long Short-Term Memory) neural network on stock close prices,
    evaluates validation accuracy on a test set, and generates a 90-day future forecast.

    Parameters:
        df (pd.DataFrame): Input DataFrame with 'Date' and 'Close' columns.
        forecast_days (int): Number of future days to forecast (default 90).
        window_size (int): Number of lookback days used as input sequence (default 30).

    Returns:
        tuple: (forecast_df, metrics_dict)
            - forecast_df (pd.DataFrame): Standardized output DataFrame.
            - metrics_dict (dict): Dictionary with RMSE, MAE, and MAPE metrics.
    """
    if df.empty or len(df) < (window_size + 30):
        return pd.DataFrame(), {"RMSE": 0, "MAE": 0, "MAPE": 0}

    lstm_df = df[["Date", "Close"]].copy()
    lstm_df["Date"] = pd.to_datetime(lstm_df["Date"])
    prices = lstm_df["Close"].values.reshape(-1, 1)

    # 1. Normalize data between 0 and 1
    scaler = MinMaxScaler(feature_range=(0, 1))
    scaled_prices = scaler.fit_transform(prices)

    # 2. Train / Test split (reserve last 60 data points for testing)
    test_size = min(60, int(len(prices) * 0.2))
    train_scaled = scaled_prices[:-test_size]
    test_scaled = scaled_prices[-(test_size + window_size):]
    test_actuals = prices[-test_size:].flatten()

    # 3. Create 3D Sliding Window sequences for Training
    X_train, y_train = _create_sequences(train_scaled, window_size)

    if len(X_train) == 0:
        return pd.DataFrame(), {"RMSE": 0, "MAE": 0, "MAPE": 0}

    if TF_AVAILABLE:
        try:
            # --- TENSORFLOW / KERAS LSTM TRAINING ---
            X_train_3d = X_train.reshape((X_train.shape[0], X_train.shape[1], 1))

            model = Sequential([
                LSTM(units=50, return_sequences=True, input_shape=(window_size, 1)),
                Dropout(0.2),
                LSTM(units=50, return_sequences=False),
                Dropout(0.2),
                Dense(units=25),
                Dense(units=1)
            ])

            model.compile(optimizer='adam', loss='mean_squared_error')
            # Train model fast with 12 epochs
            model.fit(X_train_3d, y_train, epochs=12, batch_size=32, verbose=0)

            # Evaluate on Test Set
            X_test, _ = _create_sequences(test_scaled, window_size)
            if len(X_test) > 0:
                X_test_3d = X_test.reshape((X_test.shape[0], X_test.shape[1], 1))
                scaled_preds = model.predict(X_test_3d, verbose=0)
                y_pred_val = scaler.inverse_transform(scaled_preds).flatten()
                metrics = calculate_metrics(test_actuals[:len(y_pred_val)], y_pred_val)
            else:
                metrics = {"RMSE": 0, "MAE": 0, "MAPE": 0}

            # Multi-Step Autoregressive Future Forecasting
            full_X, full_y = _create_sequences(scaled_prices, window_size)
            full_X_3d = full_X.reshape((full_X.shape[0], full_X.shape[1], 1))

            full_model = Sequential([
                LSTM(units=50, return_sequences=True, input_shape=(window_size, 1)),
                Dropout(0.2),
                LSTM(units=50, return_sequences=False),
                Dropout(0.2),
                Dense(units=25),
                Dense(units=1)
            ])
            full_model.compile(optimizer='adam', loss='mean_squared_error')
            full_model.fit(full_X_3d, full_y, epochs=12, batch_size=32, verbose=0)

            # Generate 90-day future sequence iteratively
            last_window = scaled_prices[-window_size:].reshape(1, window_size, 1)
            future_scaled_preds = []

            for _ in range(forecast_days):
                next_pred = full_model.predict(last_window, verbose=0)[0, 0]
                future_scaled_preds.append(next_pred)
                # Slide window forward by 1 step
                next_window = np.append(last_window[0, 1:, 0], next_pred)
                last_window = next_window.reshape(1, window_size, 1)

            future_preds = scaler.inverse_transform(
                np.array(future_scaled_preds).reshape(-1, 1)
            ).flatten()

        except Exception as e:
            print(f"TensorFlow LSTM training warning: {e}. Executing MLP Neural Net fallback.")
            metrics, future_preds = _mlp_fallback(scaler, scaled_prices, window_size, forecast_days, test_actuals, test_scaled)

    else:
        # Fallback to Scikit-Learn Neural Net / Regressor if TensorFlow not installed
        metrics, future_preds = _mlp_fallback(scaler, scaled_prices, window_size, forecast_days, test_actuals, test_scaled)

    # Compute bounds and structure output DataFrame
    last_date = lstm_df["Date"].max()
    future_dates = [last_date + timedelta(days=i+1) for i in range(forecast_days)]

    std_dev = np.std(prices) * 0.08
    forecast_output = pd.DataFrame({
        "Date": future_dates,
        "Price": future_preds,
        "Upper": future_preds + (1.96 * std_dev),
        "Lower": np.maximum(future_preds - (1.96 * std_dev), 1.0),
        "type": "Forecast"
    })

    historical_output = pd.DataFrame({
        "Date": lstm_df["Date"],
        "Price": lstm_df["Close"],
        "Upper": lstm_df["Close"],
        "Lower": lstm_df["Close"],
        "type": "Historical"
    })

    final_df = pd.concat([historical_output, forecast_output], ignore_index=True)
    return final_df, metrics


def _create_sequences(data, window_size):
    """
    Converts 1D price array into 2D sequence matrix [X, y].
    """
    X, y = [], []
    for i in range(len(data) - window_size):
        X.append(data[i : i + window_size, 0])
        y.append(data[i + window_size, 0])
    return np.array(X), np.array(y)


def _mlp_fallback(scaler, scaled_prices, window_size, forecast_days, test_actuals, test_scaled):
    """
    Fallback implementation using Scikit-Learn's Multi-Layer Perceptron (MLPRegressor)
    neural network if TensorFlow is unavailable.
    """
    X_train, y_train = _create_sequences(scaled_prices[:-len(test_actuals)], window_size)
    
    mlp = MLPRegressor(hidden_layer_sizes=(50, 25), max_iter=200, random_state=42)
    if len(X_train) > 0:
        mlp.fit(X_train, y_train)

    X_test, _ = _create_sequences(test_scaled, window_size)
    if len(X_test) > 0:
        val_preds_scaled = mlp.predict(X_test)
        val_preds = scaler.inverse_transform(val_preds_scaled.reshape(-1, 1)).flatten()
        metrics = calculate_metrics(test_actuals[:len(val_preds)], val_preds)
    else:
        metrics = {"RMSE": 0, "MAE": 0, "MAPE": 0}

    # Autoregressive future forecasting
    full_X, full_y = _create_sequences(scaled_prices, window_size)
    mlp_full = MLPRegressor(hidden_layer_sizes=(50, 25), max_iter=200, random_state=42)
    mlp_full.fit(full_X, full_y)

    last_window = scaled_prices[-window_size:].reshape(1, -1)
    future_scaled_preds = []

    for _ in range(forecast_days):
        next_pred = mlp_full.predict(last_window)[0]
        future_scaled_preds.append(next_pred)
        last_window = np.append(last_window[0, 1:], next_pred).reshape(1, -1)

    future_preds = scaler.inverse_transform(
        np.array(future_scaled_preds).reshape(-1, 1)
    ).flatten()

    return metrics, future_preds
