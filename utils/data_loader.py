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

    if range_option == "3 Months":
        cutoff_date = max_date - timedelta(days=90)
    elif range_option == "6 Months":
        cutoff_date = max_date - timedelta(days=180)
    elif range_option == "1 Year":
        cutoff_date = max_date - timedelta(days=365)
    else:  # 'Max' or default
        return df

    filtered_df = df[df["Date"] >= cutoff_date].copy()
    return filtered_df
