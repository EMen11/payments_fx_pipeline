import os
from pathlib import Path

# --------------------------------------------------------------------------
# 1. DIRECTORY PATHS
# --------------------------------------------------------------------------
# Dynamically determine the root of the project to ensure portability
# src/config.py -> src/ -> PROJECT_ROOT
PROJECT_ROOT = Path(__file__).parent.parent

DATA_DIR = PROJECT_ROOT / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
PROCESSED_DATA_DIR = DATA_DIR / "processed"

# Ensure essential directories exist before running anything
os.makedirs(RAW_DATA_DIR, exist_ok=True)
os.makedirs(PROCESSED_DATA_DIR, exist_ok=True)

# --------------------------------------------------------------------------
# 2. DATA GENERATION SETTINGS
# --------------------------------------------------------------------------
START_DATE = "2024-01-01"
END_DATE = "2024-01-31"
NUM_TRANSACTIONS = 5000  # Number of simulated transactions

# --------------------------------------------------------------------------
# 3. BUSINESS LOGIC & CONSTANTS
# --------------------------------------------------------------------------
PROVIDERS = ["Provider_A", "Provider_B"]
CURRENCIES = ["EUR", "USD", "GBP", "CHF"]

# Tolerance threshold for amounts matching (to handle floating point errors)
# If difference < 0.01, we consider it a match.
AMOUNT_TOLERANCE = 0.01 

# --------------------------------------------------------------------------
# 4. OUTPUT FILE PATHS
# --------------------------------------------------------------------------
FILE_PROVIDER_A = RAW_DATA_DIR / "transactions_provider_A.csv"
FILE_PROVIDER_B = RAW_DATA_DIR / "transactions_provider_B.csv"
FILE_MARKET_RATES = RAW_DATA_DIR / "fx_rates_market.csv"

# Random seed for reproducibility
RANDOM_SEED = 42