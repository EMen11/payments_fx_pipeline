import pandas as pd
import config

# --------------------------------------------------------------------------
# 1. CLEANING FUNCTIONS
# --------------------------------------------------------------------------
def clean_dataframe(df: pd.DataFrame, source_name: str) -> pd.DataFrame:
    """
    Standardizes the format of the transaction datasets.
    Ensures dates are datetime objects and amounts are rounded floats.
    """
    print(f"   -> Cleaning data for: {source_name}...")
    
    # 1. Standardize Dates
    # Converts string "2024-01-12" to a real Datetime object.
    # 'coerce' means: if a date is unreadable, turn it into NaT (Not a Time) instead of crashing.
    if "date" in df.columns:
        df["date"] = pd.to_datetime(df["date"], errors="coerce")

    # 2. Standardize Amounts (The "Float" Problem)
    # In finance, strict rounding is key to avoid 100.000000001 mismatches.
    if "amount" in df.columns:
        df["amount"] = df["amount"].astype(float).round(2)

    # 3. String Cleanup
    # Removes accidental spaces (e.g., " USD " -> "USD")
    cols_to_strip = ["currency", "status", "transaction_id"]
    for col in cols_to_strip:
        if col in df.columns:
            df[col] = df[col].astype(str).str.strip()

    return df

# --------------------------------------------------------------------------
# 2. INGESTION FUNCTION
# --------------------------------------------------------------------------
def load_data():
    """
    Loads raw CSV files from the data/raw directory.
    Applies cleaning and returns dictionary of DataFrames.
    """
    print("--- 1. Ingestion & Cleaning Started ---")

    # Check if files exist (via config paths)
    if not config.FILE_PROVIDER_A.exists():
        raise FileNotFoundError(f"CRITICAL: {config.FILE_PROVIDER_A} not found. Run Phase 1 first.")

    # Load Raw CSVs
    print(f"Loading {config.FILE_PROVIDER_A}...")
    df_a = pd.read_csv(config.FILE_PROVIDER_A)
    
    print(f"Loading {config.FILE_PROVIDER_B}...")
    df_b = pd.read_csv(config.FILE_PROVIDER_B)
    
    print(f"Loading {config.FILE_MARKET_RATES}...")
    df_rates = pd.read_csv(config.FILE_MARKET_RATES)

    # Apply Cleaning Logic
    df_a_clean = clean_dataframe(df_a, "Provider A")
    df_b_clean = clean_dataframe(df_b, "Provider B")
    
    # Specific cleaning for Market Rates (ensure date is datetime)
    df_rates["date"] = pd.to_datetime(df_rates["date"])

    print("--- Ingestion Complete: Data is clean and typed. ---")
    
    # Return the clean datasets to be used by other scripts
    return df_a_clean, df_b_clean, df_rates

# --------------------------------------------------------------------------
# 3. MAIN EXECUTION (FOR TESTING)
# --------------------------------------------------------------------------
if __name__ == "__main__":
    # This block allows us to test the script individually
    df_a, df_b, df_rates = load_data()
    
    print("\nData Quality Check:")
    print(f"Provider A: {df_a.shape[0]} rows (Dates: {df_a['date'].dtype})")
    print(f"Provider B: {df_b.shape[0]} rows (Dates: {df_b['date'].dtype})")
    print(f"Market Rates: {df_rates.shape[0]} rows")
    
    # Preview
    print("\nHead of Provider A:")
    print(df_a.head(3))