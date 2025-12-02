import time
from typing import Optional, Tuple

import pandas as pd

from code.api import fetch_last_n_days
from code.constants import SUPPORTED_CURRENCIES, DAYS_TO_FETCH, DEFAULT_CSV_FILENAME
from code.core import (
    records_to_dataframe,
    add_rolling_average,
    format_summary_table,
)
from code.display import display_breakdown

"""CORE LOGIC FOR CLI MENU INTERFACE"""

def show_menu() -> None:
    """Display the main menu."""
    print("\n==============================")
    print(" Currency Rates (Based on NBU API data) ")
    print("==============================")
    print("1) Summary: Current rates + 30-day averages (USD & EUR)")
    print("2) Full breakdown: Detailed stats for USD or EUR")
    print("3) Save current data to CSV")
    print("4) Exit")


def _get_filename(default: str) -> str:
    """Get filename from user input."""
    filename = input(f"\nEnter filename (default: {default}): ").strip()
    if not filename:
        filename = default
    if not filename.endswith(".csv"):
        filename += ".csv"
    return filename


def save_data_to_csv(data_df: pd.DataFrame, default_filename: str) -> bool:
    """
    Save DataFrame to CSV file.
    
    :param data_df: DataFrame to save.
    :param default_filename: Default filename if user doesn't provide one.
    :return: True if saved successfully, False otherwise.
    """
    import os
    
    filename = _get_filename(default_filename)
    
    try:
        os.makedirs("data", exist_ok=True)
        filepath = os.path.join("data", filename)
        
        if "rolling_avg" not in data_df.columns:
            data_df_to_save = add_rolling_average(data_df)
        else:
            data_df_to_save = data_df.copy()
        
        data_df_to_save.to_csv(filepath, index=False)
        
        print(f"\n[INFO] Data saved to {filepath}")
        print(f"[INFO] Saved {len(data_df_to_save)} rows")
        return True
    
    except Exception as e:
        print(f"\n[ERROR] Failed to save CSV: {e}")
        return False


def ask_continue_or_save(data_df: Optional[pd.DataFrame] = None, default_filename: str = DEFAULT_CSV_FILENAME) -> bool:
    """
    Ask user if they want to continue, save (and continue), or quit.
    
    :param data_df: Optional DataFrame to save if user chooses 's'.
    :param default_filename: Default filename for saving.
    :return: True if user wants to continue (or save and continue), False if quit.
    """
    while True:
        if data_df is not None:
            response = input("\nContinue, Save, or Quit? (c/s/q): ").strip().lower()
        else:
            response = input("\nContinue or Quit? (c/q): ").strip().lower()
        
        if response in ["c", "continue"]:
            return True
        elif response in ["s", "save"]:
            if data_df is not None:
                save_data_to_csv(data_df, default_filename)
                return True  # Continue after saving
            else:
                print("\n[WARN] No data available to save.")
                continue
        elif response in ["q", "quit"]:
            return False
        else:
            if data_df is not None:
                print("[ERROR] Please enter 'c' to continue, 's' to save, or 'q' to quit.")
            else:
                print("[ERROR] Please enter 'c' to continue or 'q' to quit.")


def _fetch_data() -> Optional[pd.DataFrame]:
    """Fetch and return data, or None if failed."""
    print(f"\n> Fetching last {DAYS_TO_FETCH} days of currency data (USD and EUR only)...")
    start_time = time.time()
    
    try:
        records = fetch_last_n_days(DAYS_TO_FETCH)
        df = records_to_dataframe(records)
        elapsed_time = time.time() - start_time
        print(f"[INFO] Query completed in {elapsed_time:.2f} seconds")
        return df
    except Exception as e:
        elapsed_time = time.time() - start_time
        print(f"\n[ERROR] Failed to fetch data after {elapsed_time:.2f} seconds: {e}")
        return None


def _handle_option_1() -> Optional[pd.DataFrame]:
    """Handle Option 1: Summary view - concise for both currencies."""
    df = _fetch_data()
    if df is None:
        return None
    
    if df.empty:
        print("\n[WARN] No data fetched.")
        return None
    
    print(format_summary_table(df))
    return add_rolling_average(df)


def _handle_option_2(df: Optional[pd.DataFrame]) -> Tuple[Optional[pd.DataFrame], Optional[str]]:
    """Handle Option 2: Full breakdown - detailed for one currency. Returns (dataframe, currency)."""
    df = _fetch_data()
    if df is None or df.empty:
        return None, None
    
    while True:
        currency = input("\nSelect currency for detailed breakdown (USD/EUR): ").strip().upper()
        
        if currency not in SUPPORTED_CURRENCIES:
            print(f"\n[ERROR] Invalid currency. Only USD and EUR are supported. Please try again.")
            continue
        
        currency_df_rolling = display_breakdown(df, currency)
        if currency_df_rolling.empty:
            return None, None
        return currency_df_rolling, currency


def _handle_option_3(df: Optional[pd.DataFrame]) -> None:
    """Handle Option 3: Save data."""
    if df is None or df.empty:
        print("\n[WARN] No data loaded. Please fetch data first (option 1 or 2).")
        return
    
    filename = _get_filename(DEFAULT_CSV_FILENAME)
    import os
    
    try:
        os.makedirs("data", exist_ok=True)
        filepath = os.path.join("data", filename)
        
        df_to_save = add_rolling_average(df)
        df_to_save.to_csv(filepath, index=False)
        
        print(f"\n[INFO] Data saved to {filepath}")
        print(f"[INFO] Saved {len(df_to_save)} rows")
    except Exception as e:
        print(f"\n[ERROR] Failed to save CSV: {e}")


def run_cli() -> None:
    """
    CLI interface menu.
    Menu is shown initially and then only after user chooses to continue.
    """
    df: Optional[pd.DataFrame] = None
    
    show_menu()
    
    while True:
        choice = input("Choose an option [1-4]: ").strip()

        if choice == "1":
            result_df = _handle_option_1()
            if result_df is not None:
                df = result_df
                if not ask_continue_or_save(result_df, "summary_usd_eur_30days.csv"):
                    break
            else:
                if not ask_continue_or_save():
                    break
            show_menu()

        elif choice == "2":
            result_df, currency = _handle_option_2(df)
            if result_df is not None and currency is not None:
                df = result_df
                if not ask_continue_or_save(result_df, f"breakdown_{currency.lower()}_30days.csv"):
                    break
            else:
                if not ask_continue_or_save():
                    break
            show_menu()

        elif choice == "3":
            _handle_option_3(df)
            if not ask_continue_or_save():
                break
            show_menu()

        elif choice == "4":
            print("\nExiting.")
            break
        else:
            print("\n[ERROR] Invalid choice. Choose 1, 2, 3, or 4.")