"""Display functions for CLI output."""

from typing import Dict

import pandas as pd

from code.core import (
    filter_currency,
    compute_stats,
    format_stats_table,
    add_rolling_average,
    format_table,
)


def display_breakdown(df: pd.DataFrame, currency: str) -> pd.DataFrame:
    """
    Display full breakdown for a currency.
    
    :param df: DataFrame with currency data.
    :param currency: Currency code (USD or EUR).
    :return: DataFrame with rolling averages (for saving).
    """
    currency_df = filter_currency(df, currency)
    
    if currency_df.empty:
        print(f"\n[WARN] No data found for {currency}.")
        return pd.DataFrame()
    
    stats = compute_stats(currency_df)
    if not stats:
        print(f"\n[WARN] Could not compute statistics for {currency}.")
        return pd.DataFrame()
    
    print(f"\n{'='*60}")
    print(f"FULL BREAKDOWN: {currency}")
    print(f"{'='*60}")
    
    min_date = currency_df["iso_date"].min().date()
    max_date = currency_df["iso_date"].max().date()
    print(f"\nDate Range: {min_date} → {max_date}")
    print(f"Total Data Points: {len(currency_df)}")
    
    print(f"\nStatistical Summary:")
    print(format_stats_table(stats, currency))
    
    currency_df_rolling = add_rolling_average(currency_df)
    print(f"\nFull 30-Day Data with 7-Day Rolling Average:")
    print(format_table(currency_df_rolling[["iso_date", "rate", "rolling_avg"]], max_rows=100))
    
    _display_insights(currency_df_rolling, stats)
    
    return currency_df_rolling


def _display_insights(currency_df_rolling: pd.DataFrame, stats: Dict[str, float]) -> None:
    """Display additional insights."""
    current_rate = currency_df_rolling.iloc[-1]["rate"]
    avg_rate = stats["mean"]
    change_pct = ((current_rate - avg_rate) / avg_rate) * 100
    
    print(f"\nInsights:")
    print(f"   Current Rate: {current_rate:.4f} UAH")
    print(f"   30-Day Average: {avg_rate:.4f} UAH")
    print(f"   Change from Average: {change_pct:+.2f}%")
    print(f"   Volatility (Std Dev): {stats['std']:.4f} UAH")
    print(f"   Range: {stats['min']:.4f} - {stats['max']:.4f} UAH")

