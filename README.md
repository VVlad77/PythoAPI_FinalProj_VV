# Currency Rates CLI Application

A Python console application powered by NBU API data, able to show current rates for USD and EUR, as well as historical 30-day statistics, providig a mean, standard deviation, minimum, and maximum values, along with rolling averages.

## Project Description

Simple CLI application on Python, able to provide metrics on USD or EUR currency rates relative to UAH (current rates, last 30 days avg., rolling avg., volatility/std, change rate, range), by fetching data via the NBU API, and processing it using Pandas and NumPy. Supports USD and EUR currencies currently, with historical data up to the last 30 days.

Features:
- Interactive CLI menu interface
- Summary view with current rates and 30-day averages for both EUR and USD
- Detailed breakdown with full statistics for the last 30 days for selected currency (USD or EUR)
   - Includes statistical metrics: mean, std, min, max, via NumPy  
   - 7-day rolling averages
- Data saveable to CSV: each query (summary view, or detailed per-currecy breakdown) can be saved as a CSV file

## Technology Stack Used

- **Python 3**: Core backend language
- **Pandas**: for Data manipulation and DataFrame operations
- **NumPy**: for Statistical calculations (mean, std, min, max)
- **Requests**: for HTTP requests to NBU API
- **Tabulate**: for prettier Table formatting of CLI output

## API Used

**National Bank of Ukraine (NBU) Exchange Rate API**

- **Base URL**: `https://bank.gov.ua/NBUStatService/v1/statdirectory/exchange`
- **Documentation**: [NBU API Documentation](https://bank.gov.ua/en/open-data/api-dev)
- **Endpoint Format**: `?date=YYYYMMDD&json`

The API provides daily exchange rates for various currencies relative to UAH. This application is specificlly focused on USD/EUR.

## RUN : How to Run Locally

### Prerequisites

- Python 3 or higher
- pip (Python package manager)

### Installation Steps

1. Clone the repository: (or download the repo manually, unpack, and 'cd' the full path to unzipped folder)
```bash
git clone https://github.com/VVlad77/PythoAPI_FinalProj_VV.git
cd PythoAPI_FinalProj_VV
```

RECOMMENDED
- Set up a .venv, by running the following in your terminal after the previous step:
```bash
python3 -m venv .venv
source .venv/bin/activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the application:
```bash
python3 main.py
```

## RUN : How to Run via Docker

### Prerequisites

- Docker installed on your system

1. 

2. 

3. 

4. 

5. 
docker run -it --rm hellcat888/currency_rates_cli

mkdir -p data
docker run -it --rm \
  -v "$(pwd)/data:/app/data" \
  hellcat888/currency_rates_cli

### How to Use

This application works via an interactive CLI-input-based menu. 
Navigation is done by inputting respective number or letter(s) as prompted:

Main menu:
   1. **Summary**: View current rates and 30-day averages for USD and EUR
   2. **Full Breakdown**: Get detailed statistics and full 30-day data for USD or EUR
   3. **Save Data**: Manually save previously fetched data to CSV
   4. **Exit**: Quit the application

After each query (Option 1 or 2), the user is prompted to:
   c. (continue): Return to main menu
   s. (save): Save the query results to a CSV file and continue
   q. (quit): Exit the application

## Example CLI Commands

STUB FIX

## Code Structure

```
PythoAPI_FinalProj_VV/
├── main.py              # Entry point
├── code/
│   ├── __init__.py
│   ├── api.py          # NBU API interaction, HTTP requests for data fetching
│   ├── cli.py          # CLI menu interface and user input/output interactions, app flow
│   ├── core.py         # Data processing with Pandas and NumPy (DataFrame operations, metrics, data formatting)
│   ├── display.py      # Separated logic for the full 30-day breakdown display, for cleaner CLI file
│   └── constants.py    # Centralised application config constants (currencies, rolling avg. window size, dates window)
├── data/               # CSV file output directory
├── requirements.txt    # required Python dependencies
├── Dockerfile          # Docker configuration
└── README.md          # This file
```

## Code Standards

All of the project code aims to follow the best practices:
- PEP-8 formatting guidelines
- Docstrings for functions
- Comments elaborating logic

## License

This project is for educational purposes.

