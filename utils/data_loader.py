import os
import glob
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# Path to the datasets directory relative to project root
DATASETS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "datasets")


def ensure_datasets_dir_exists():
    """
    Ensures that the datasets/ directory exists.
    If it is empty, creates default synthetic sample datasets (AAPL, TSLA, BTC).
    """
    if not os.path.exists(DATASETS_DIR):
        os.makedirs(DATASETS_DIR)

    # Check if directory has any CSV files
    csv_files = glob.glob(os.path.join(DATASETS_DIR, "*.csv"))
    if not csv_files:
        _generate_sample_datasets()


def _generate_sample_datasets():
    """
    Private helper function to generate realistic synthetic stock market datasets
    for initial testing when no datasets are present.
    """
    end_date = datetime.today()
    start_date = end_date - timedelta(days=730)  # 2 years of daily data
    date_range = pd.date_range(start=start_date, end=end_date, freq="D")

    sample_stocks = {
        "AAPL.csv": {"base": 150.0, "volatility": 1.5, "trend": 0.08},
        "TSLA.csv": {"base": 220.0, "volatility": 3.2, "trend": 0.12},
        "BTC.csv": {"base": 45000.0, "volatility": 500.0, "trend": 15.0}
    }

    for filename, config in sample_stocks.items():
        np.random.seed(42 + len(filename))
        n_days = len(date_range)
        
        # Simulate price series using Random Walk with trend
        returns = np.random.normal(config["trend"], config["volatility"], n_days)
        prices = np.cumsum(returns) + config["base"]
        prices = np.maximum(prices, 10.0)  # Ensure positive stock prices

        close_p = np.round(prices, 2)
        open_p = np.round(prices + np.random.normal(0, config["volatility"] * 0.4, n_days), 2)
        open_p = np.maximum(open_p, 1.0)
        
        max_oc = np.maximum(open_p, close_p)
        min_oc = np.minimum(open_p, close_p)
        
        high_p = np.round(max_oc + np.abs(np.random.normal(0.2, config["volatility"] * 0.3, n_days)), 2)
        low_p = np.round(min_oc - np.abs(np.random.normal(0.2, config["volatility"] * 0.3, n_days)), 2)
        low_p = np.maximum(low_p, 0.5)

        df = pd.DataFrame({
            "Date": date_range.strftime("%Y-%m-%d"),
            "Open": open_p,
            "High": high_p,
            "Low": low_p,
            "Close": close_p,
            "Volume": np.random.randint(1000000, 50000000, size=n_days)
        })

        file_path = os.path.join(DATASETS_DIR, filename)
        df.to_csv(file_path, index=False)


def get_available_datasets():
    """
    Scans datasets/ directory and returns a list of available CSV filenames.
    Returns:
        list of str: List of dataset filenames (e.g. ['AAPL.csv', 'TSLA.csv']).
    """
    ensure_datasets_dir_exists()
    csv_files = glob.glob(os.path.join(DATASETS_DIR, "*.csv"))
    return [os.path.basename(f) for f in sorted(csv_files)]


def load_dataset(filename):
    """
    Reads a CSV dataset from the datasets/ folder, standardizes column names,
    parses date strings to datetime objects, drops empty rows, and sorts chronologically.

    Parameters:
        filename (str): Name of CSV file (e.g., 'AAPL.csv').

    Returns:
        pd.DataFrame: Processed DataFrame containing 'Date' and 'Close' columns.
    """
    ensure_datasets_dir_exists()
    file_path = os.path.join(DATASETS_DIR, filename)

    if not os.path.exists(file_path):
        return pd.DataFrame()

    try:
        df = pd.read_csv(file_path)

        # Standardize column headers (lowercase strip whitespace)
        col_map = {col: col.strip().capitalize() for col in df.columns}
        df.rename(columns=col_map, inplace=True)

        # Verify required columns exist
        if "Date" not in df.columns or "Close" not in df.columns:
            # Case insensitive check fallback
            date_col = next((c for c in df.columns if c.lower() == "date"), None)
            close_col = next((c for c in df.columns if c.lower() in ["close", "adj close", "price"]), None)

            if date_col and close_col:
                df.rename(columns={date_col: "Date", close_col: "Close"}, inplace=True)
            else:
                return pd.DataFrame()

        # Parse Date column to pandas datetime
        df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
        df["Close"] = pd.to_numeric(df["Close"], errors="coerce")

        # Drop invalid missing values
        df.dropna(subset=["Date", "Close"], inplace=True)

        # Sort by Date ascending
        df.sort_values(by="Date", ascending=True, inplace=True)
        df.reset_index(drop=True, inplace=True)

        return df

    except Exception as e:
        print(f"Error loading dataset {filename}: {e}")
        return pd.DataFrame()


def save_uploaded_dataset(uploaded_file):
    """
    Saves a user-uploaded CSV file from Streamlit's file_uploader into the datasets/ folder.

    Parameters:
        uploaded_file (UploadedFile): Streamlit uploaded file object.

    Returns:
        str: Cleaned filename saved on disk.
    """
    ensure_datasets_dir_exists()
    
    # Clean filename
    raw_name = uploaded_file.name
    clean_name = raw_name.replace(" ", "_")
    if not clean_name.endswith(".csv"):
        clean_name += ".csv"

    destination_path = os.path.join(DATASETS_DIR, clean_name)

    with open(destination_path, "wb") as f:
        f.write(uploaded_file.getbuffer())

    return clean_name


def delete_dataset(filename):
    """
    Deletes a specified dataset CSV file from the datasets/ folder.

    Parameters:
        filename (str): Filename to delete (e.g. 'AAPL.csv').

    Returns:
        bool: True if deleted successfully, False otherwise.
    """
    file_path = os.path.join(DATASETS_DIR, filename)
    if os.path.exists(file_path):
        os.remove(file_path)
        return True
    return False


def filter_data_by_range(df, range_option):
    """
    Filters a stock DataFrame based on a selected time range option
    relative to the max date present in the dataset.

    Parameters:
        df (pd.DataFrame): Input DataFrame containing 'Date' column.
        range_option (str): '3 Months', '6 Months', '1 Year', or 'Max'.

    Returns:
        pd.DataFrame: Subset DataFrame matching the requested date range.
    """
    if df.empty or "Date" not in df.columns:
        return df

    max_date = df["Date"].max()

    if range_option == "6 Months":
        cutoff_date = max_date - timedelta(days=180)
    elif range_option == "1 Year":
        cutoff_date = max_date - timedelta(days=365)
    elif range_option == "2 Years":
        cutoff_date = max_date - timedelta(days=730)
    else:  # 'Max' or default
        return df

    filtered_df = df[df["Date"] >= cutoff_date].copy()
    return filtered_df


def get_stock_summary(df, filename):
    """
    Extracts summary statistics (Company Name, Current Price, 24h Change, 
    52-Week High/Low, Avg Volume, Market Cap) from a stock DataFrame.

    Parameters:
        df (pd.DataFrame): Input DataFrame containing stock data.
        filename (str): Name of the dataset file (e.g. 'AAPL.csv').

    Returns:
        dict: Financial summary dictionary for UI display.
    """
    if df.empty or "Close" not in df.columns:
        return {
            "company_name": "Unknown Entity",
            "current_price": 0.0,
            "price_change": 0.0,
            "pct_change": 0.0,
            "high_52w": 0.0,
            "low_52w": 0.0,
            "avg_volume": "N/A",
            "market_cap": "N/A"
        }

    # Map filename to human-readable Company Name
    clean_ticker = filename.replace(".csv", "").strip().upper()
    company_names = {
        "AAPL": "Apple Inc. (AAPL)",
        "TSLA": "Tesla, Inc. (TSLA)",
        "BTC": "Bitcoin USD (BTC-USD)"
    }
    company_name = company_names.get(clean_ticker, f"{clean_ticker} Stock")

    # Current Price and Previous Close Price
    current_price = float(df["Close"].iloc[-1])
    prev_price = float(df["Close"].iloc[-2]) if len(df) >= 2 else current_price

    price_change = current_price - prev_price
    pct_change = (price_change / prev_price * 100) if prev_price != 0 else 0.0

    # 52-Week (365 days) High and Low
    max_date = df["Date"].max()
    year_cutoff = max_date - timedelta(days=365)
    last_year_df = df[df["Date"] >= year_cutoff]

    if not last_year_df.empty:
        high_col = "High" if "High" in last_year_df.columns else "Close"
        low_col = "Low" if "Low" in last_year_df.columns else "Close"
        high_52w = float(last_year_df[high_col].max())
        low_52w = float(last_year_df[low_col].min())
    else:
        high_52w = current_price
        low_52w = current_price

    # Average Volume calculation
    if "Volume" in df.columns:
        recent_vol = df["Volume"].tail(30).mean()
        if recent_vol >= 1_000_000:
            avg_volume = f"{recent_vol / 1_000_000:.2f}M"
        elif recent_vol >= 1_000:
            avg_volume = f"{recent_vol / 1_000:.2f}K"
        else:
            avg_volume = f"{int(recent_vol)}"
    else:
        avg_volume = "N/A"

    # Market Cap calculation / placeholder
    market_caps = {
        "AAPL": "$2.82 Trillion",
        "TSLA": "$780 Billion",
        "BTC": "$1.25 Trillion"
    }
    if clean_ticker in market_caps:
        market_cap = market_caps[clean_ticker]
    else:
        # Dynamic estimation fallback based on asset price
        est_cap = current_price * 15_000_000_000  # Estimated shares out
        if est_cap >= 1_000_000_000_000:
            market_cap = f"${est_cap / 1_000_000_000_000:.2f} Trillion"
        else:
            market_cap = f"${est_cap / 1_000_000_000:.2f} Billion"

    return {
        "company_name": company_name,
        "current_price": round(current_price, 2),
        "price_change": round(price_change, 2),
        "pct_change": round(pct_change, 2),
        "high_52w": round(high_52w, 2),
        "low_52w": round(low_52w, 2),
        "avg_volume": avg_volume,
        "market_cap": market_cap
    }
