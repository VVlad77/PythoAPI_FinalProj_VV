import datetime as dt
from typing import List, Dict, Any

import requests

from code.constants import SUPPORTED_CURRENCIES

"""CORE LOGIC FOR NBU API INTERACTION"""

NBU_BASE_URL = "https://bank.gov.ua/NBUStatService/v1/statdirectory/exchange"


def fetch_rates_for_date(date: dt.date) -> List[Dict[str, Any]]:
    """
    Fetch NBU exchange rates for a specific date.
    Only USD and EUR currencies are returned.

    :param date: datetime.date object.
    :return: List of rate dictionaries from the NBU API (USD and EUR only).
    """
    date_str = date.strftime("%Y%m%d")
    url = f"{NBU_BASE_URL}?date={date_str}&json"

    response = requests.get(url, timeout=10)
    response.raise_for_status()

    data = response.json()

    # Filter to only supported currencies
    data = [record for record in data if record.get("cc") in SUPPORTED_CURRENCIES]

    # normalized ISO date field for consistency
    for record in data:
        record["iso_date"] = date.isoformat()

    return data


def fetch_last_n_days(n: int = 30) -> List[Dict[str, Any]]:
    """
    Fetch NBU exchange rates for the last n days (including today).

    :param n: Number of days to go back from today.
    :return: Combined list of rate records for all days.
    """
    today = dt.date.today()
    all_records: List[Dict[str, Any]] = []

    for i in range(n):
        day = today - dt.timedelta(days=i)
        daily_rates = fetch_rates_for_date(day)
        all_records.extend(daily_rates)

    return all_records