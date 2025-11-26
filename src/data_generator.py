import pandas as pd
import numpy as np
from faker import Faker
import random
from datetime import timedelta, date

# Import config variables to ensure consistency across the project
import config

# --------------------------------------------------------------------------
# 0. SETUP & INITIALIZATION
# --------------------------------------------------------------------------
# Initialize Faker to generate realistic dummy data (Transaction IDs, Countries)
fake = Faker()

# Set random seeds for reproducibility.
# This ensures that every time we run the script, we get the EXACT same "random" data.
# Crucial for debugging and sharing the project.
Faker.seed(config.RANDOM_SEED)
np.random.seed(config.RANDOM_SEED)
random.seed(config.RANDOM_SEED)

# --------------------------------------------------------------------------
# 1. MARKET DATA GENERATION (FX RATES)
# --------------------------------------------------------------------------
def generate_market_rates():
    """
    Generates daily FX rates for the defined period (EURUSD, EURGBP, etc.).
    Uses a 'Random Walk' model (Geometric Brownian Motion) to simulate realistic market volatility.
    """
    print("--- 1. Generating Market Rates (FX Market) ---")
    
    # Create a daily timeline from start_date to end_date
    dates = pd.date_range(start=config.START_DATE, end=config.END_DATE)
    
    # Base rates (Approximate starting point for Jan 2024)
    base_rates = {
        "EURUSD": 1.08,
        "EURGBP": 0.85,
        "EURCHF": 0.95
    }
    
    market_data = []
    
    for pair, start_rate in base_rates.items():
        # Simulate daily returns using a normal distribution (Gaussian)
        # loc=0 (no drift), scale=0.002 (daily volatility ~0.2%)
        returns = np.random.normal(loc=0, scale=0.002, size=len(dates))
        
        # Calculate the price path: Price_t = Price_0 * exp(sum(returns))
        price_path = start_rate * np.exp(np.cumsum(returns))
        
        # Store data row by row
        for d, rate in zip(dates, price_path):
            market_data.append({
                "date": d.date(),
                "currency_pair": pair,
                "market_rate": round(rate, 4)
            })
            
    # Convert to DataFrame and Save
    df_market = pd.DataFrame(market_data)
    df_market.to_csv(config.FILE_MARKET_RATES, index=False)
    print(f" Market rates saved to: {config.FILE_MARKET_RATES}")
    return df_market

# --------------------------------------------------------------------------
# 2. INTERNAL SYSTEM DATA (PROVIDER A - THE TRUTH)
# --------------------------------------------------------------------------
def generate_provider_A():
    """
    Generates the internal 'clean' dataset (Provider A).
    This represents the 'Source of Truth' from our Treasury Management System.
    """
    print("--- 2. Generating Provider A (Internal System) ---")
    
    data = []
    dates = pd.date_range(start=config.START_DATE, end=config.END_DATE)
    
    for _ in range(config.NUM_TRANSACTIONS):
        # 2.1 Random Selection of basic attributes
        txn_date = random.choice(dates).date()
        currency = random.choice(config.CURRENCIES)
        
        # Skip EUR because we want to focus on Cross-Border FX transactions
        if currency == "EUR": continue 
        
        # 2.2 Generate Financial Details
        amount = round(random.uniform(100, 10000), 2) # Amount between 100 and 10k
        txn_id = fake.uuid4()                         # Unique ID (e.g., 3e4r-5t6y...)
        
        # 2.3 Append to list
        data.append({
            "transaction_id": txn_id,
            "date": txn_date,
            "currency": currency,
            "amount": amount,
            "status": "COMPLETED",
            "source": "Internal_System"
        })
        
    # Convert to DataFrame and Save
    df_a = pd.DataFrame(data)
    df_a.to_csv(config.FILE_PROVIDER_A, index=False)
    print(f" Provider A data saved ({len(df_a)} rows) to: {config.FILE_PROVIDER_A}")
    return df_a

# --------------------------------------------------------------------------
# 3. BANK STATEMENT GENERATION (PROVIDER B - THE DIRTY DATA)
# --------------------------------------------------------------------------
def generate_provider_B_with_errors(df_a):
    """
    Generates the external bank dataset (Provider B).
    Clones Provider A but injects realistic operational errors to simulate real-world mismatches.
    """
    print("--- 3. Generating Provider B (Bank Statement with Errors) ---")
    
    # 3.1 Clone the clean data
    df_b = df_a.copy()
    df_b["source"] = "Bank_Provider_B"
    
    # 3.2 INJECT ERROR: Missing Transactions (Cash missing or Timing issue)
    # Scenario: The bank hasn't processed these payments yet, or data was lost.
    # Logic: Randomly select 2% of indices and drop them.
    drop_indices = np.random.choice(df_b.index, size=int(len(df_b) * 0.02), replace=False)
    df_b = df_b.drop(drop_indices)
    
    # 3.3 INJECT ERROR: Amount Mismatch (Hidden Fees / FX Slippage)
    # Scenario: We sent 1000, Bank says 990 (Fees deducted).
    # Logic: Select 1% of transactions and reduce amount by 0.5% to 2%.
    mismatch_indices = np.random.choice(df_b.index, size=int(len(df_b) * 0.01), replace=False)
    for idx in mismatch_indices:
        original_amount = df_b.loc[idx, "amount"]
        fee_factor = random.uniform(0.98, 0.995) # 0.5% to 2% fee
        df_b.loc[idx, "amount"] = round(original_amount * fee_factor, 2)
        
    # 3.4 INJECT ERROR: Status Mismatch
    # Scenario: System says 'Completed', Bank says 'Pending'.
    # Logic: Select 3% of transactions and change status.
    status_indices = np.random.choice(df_b.index, size=int(len(df_b) * 0.03), replace=False)
    df_b.loc[status_indices, "status"] = "PENDING"
    
    # Save
    df_b.to_csv(config.FILE_PROVIDER_B, index=False)
    print(f" Provider B data saved ({len(df_b)} rows) with injected errors.")
    return df_b

# --------------------------------------------------------------------------
# 4. MAIN EXECUTION
# --------------------------------------------------------------------------
if __name__ == "__main__":
    generate_market_rates()
    df_a = generate_provider_A()
    generate_provider_B_with_errors(df_a)
    print("\n Phase 1 Complete: Data Generation Successful!")