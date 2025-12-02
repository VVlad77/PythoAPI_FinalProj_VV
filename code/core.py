from typing import List, Dict, Any, Optional

import numpy as np
import pandas as pd
from tabulate import tabulate

from code.constants import SUPPORTED_CURRENCIES, ROLLING_WINDOW

"""CORE LOGIC FOR NBU DATA MANIPULATION"""

def records_to_dataframe(records: List[Dict[str, Any]]) -> pd.DataFrame:
    """
    Convert raw NBU records list into DataFrame.

    We want:
      - iso_date: normalized date (string or datetime)
      - cc: currency code, e.g. 'USD'
      - rate: exchange rate in UAH per unit of currency
    
    Only USD and EUR currencies are kept.
    """
    if not records:
        return pd.DataFrame(columns=["iso_date", "cc", "rate"])

    df = pd.DataFrame(records)

    # Keep only relevant columns if they exist
    cols = [c for c in ["iso_date", "cc", "rate"] if c in df.columns]
    df = df[cols]

    # Filter to only supported currencies
    df = df[df["cc"].isin(SUPPORTED_CURRENCIES)].copy()

    df["iso_date"] = pd.to_datetime(df["iso_date"])
    df["rate"] = pd.to_numeric(df["rate"], errors="coerce")
    df = df.dropna(subset=["rate"])

    return df


def filter_currency(df: pd.DataFrame, currency_code: str) -> pd.DataFrame:
    """
    Filter the DataFrame by currency code (USD or EUR only).

    :param df: DataFrame with column 'cc'.
    :param currency_code: Currency code to filter (USD or EUR), case-insensitive.
    :return: Filtered DataFrame sorted by date.
    """
    currency_code = currency_code.upper()
    if currency_code not in SUPPORTED_CURRENCIES:
        return pd.DataFrame(columns=["iso_date", "cc", "rate"])
    
    filtered = df[df["cc"] == currency_code].copy()
    return filtered.sort_values("iso_date")


def compute_stats(df: pd.DataFrame) -> Optional[Dict[str, float]]:
    """
    Compute mean, std, min, max for the 'rate' column using numpy.

    :param df: DataFrame filtered to a single currency.
    :return: Dict with statistics, or None if df is empty.
    """
    if df.empty:
        return None

    rates = df["rate"].to_numpy()

    return {
        "mean": float(np.mean(rates)),
        "std": float(np.std(rates)),  # population std using numpy.std()
        "min": float(np.min(rates)),
        "max": float(np.max(rates)),
    }


def format_stats_table(stats: Dict[str, float], currency_code: str) -> str:
    """
    Format statistics as a table for CLI output.

    :param stats: Dictionary with mean, std, min, max.
    :param currency_code: Currency code for display.
    :return: Formatted table string.
    """
    stats_df = pd.DataFrame([{
        "Currency": currency_code,
        "Mean": f"{stats['mean']:.4f}",
        "Std": f"{stats['std']:.4f}",
        "Min": f"{stats['min']:.4f}",
        "Max": f"{stats['max']:.4f}"
    }])
    
    return tabulate(stats_df, headers="keys", tablefmt="pretty", showindex=False)


def add_rolling_average(df: pd.DataFrame, window: int = ROLLING_WINDOW) -> pd.DataFrame:
    """
    Add rolling average column to DataFrame.

    :param df: DataFrame with 'rate' column, sorted by date.
    :param window: Rolling window size (default 7 days).
    :return: DataFrame with added 'rolling_avg' column.
    """
    df = df.copy()
    df = df.sort_values("iso_date")
    df["rolling_avg"] = df["rate"].rolling(window=window, min_periods=1).mean()
    return df


def format_table(df: pd.DataFrame, max_rows: int = 20) -> str:
    """
    Format a DataFrame as a pretty table for CLI output.
    Formats iso_date to show only date (no time) and rolling_avg to 4 decimals.

    :param df: DataFrame to display.
    :param max_rows: Max rows to show.
    :return: String with table.
    """
    if df.empty:
        return "No data to display."

    df_sorted = df.sort_values("iso_date").copy()

    # Format iso_date to show only date (no time component)
    if "iso_date" in df_sorted.columns:
        df_sorted["iso_date"] = df_sorted["iso_date"].dt.date
    
    # Format rolling_avg to 4 decimal places
    if "rolling_avg" in df_sorted.columns:
        df_sorted["rolling_avg"] = df_sorted["rolling_avg"].round(4)

    if len(df_sorted) > max_rows:
        df_to_show = df_sorted.head(max_rows)
    else:
        df_to_show = df_sorted

    return tabulate(df_to_show, headers="keys", tablefmt="pretty", showindex=False)


def _get_currency_data(df: pd.DataFrame, currency_code: str) -> pd.DataFrame:
    """
    Internal helper to get filtered currency data.
    
    :param df: DataFrame with currency data.
    :param currency_code: Currency code.
    :return: Filtered DataFrame.
    """
    return filter_currency(df, currency_code)


def get_current_rate(df: pd.DataFrame, currency_code: str) -> Optional[float]:
    """
    Get the most recent (current) exchange rate for a currency.

    :param df: DataFrame with currency data.
    :param currency_code: Currency code (USD or EUR).
    :return: Current rate or None if not found.
    """
    currency_df = _get_currency_data(df, currency_code)
    if currency_df.empty:
        return None
    
    currency_df_sorted = currency_df.sort_values("iso_date", ascending=False)
    return float(currency_df_sorted.iloc[0]["rate"])


def get_avg_rate(df: pd.DataFrame, currency_code: str) -> Optional[float]:
    """
    Get the 30-day average exchange rate for a currency using numpy.

    :param df: DataFrame with currency data.
    :param currency_code: Currency code (USD or EUR).
    :return: Average rate or None if not found.
    """
    currency_df = _get_currency_data(df, currency_code)
    if currency_df.empty:
        return None
    
    rates = currency_df["rate"].to_numpy()
    return float(np.mean(rates))


def format_summary_table(df: pd.DataFrame) -> str:
    """
    Format a summary table showing current rates and 30-day averages for USD and EUR.

    :param df: DataFrame with currency data.
    :return: Formatted summary table string.
    """
    # Get current rates and averages
    usd_current = get_current_rate(df, "USD")
    usd_avg = get_avg_rate(df, "USD")
    eur_current = get_current_rate(df, "EUR")
    eur_avg = get_avg_rate(df, "EUR")
    
    # Get current date for display
    if not df.empty:
        current_date = df["iso_date"].max().date()
    else:
        current_date = "N/A"
    
    summary_data = []
    
    if usd_current is not None and usd_avg is not None:
        summary_data.append({
            "Currency": "USD",
            "Current Rate": f"{usd_current:.4f}",
            "30-Day Avg": f"{usd_avg:.4f}",
            "Difference": f"{usd_current - usd_avg:+.4f}"
        })
    
    if eur_current is not None and eur_avg is not None:
        summary_data.append({
            "Currency": "EUR",
            "Current Rate": f"{eur_current:.4f}",
            "30-Day Avg": f"{eur_avg:.4f}",
            "Difference": f"{eur_current - eur_avg:+.4f}"
        })
    
    if not summary_data:
        return "No data available for summary."
    
    summary_df = pd.DataFrame(summary_data)
    table = tabulate(summary_df, headers="keys", tablefmt="pretty", showindex=False)
    
    return f"\nCurrency Summary (Last 30 Days)\nDate: {current_date}\n\n{table}"