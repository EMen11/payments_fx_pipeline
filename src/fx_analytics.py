import pandas as pd
import numpy as np
import config

# --------------------------------------------------------------------------
# 1. PREPARATION & ENRICHMENT (Mark-to-Market)
# --------------------------------------------------------------------------
def apply_market_rates(df_transactions, df_rates):
    """
    Joins transactions with market rates to calculate EUR equivalents.
    
    Logic:
    1. Create a common key (e.g., 'EURUSD') to join tables.
    2. Merge transactions with rates based on Date + Currency Pair.
    3. Convert amounts to EUR (Base Currency).
    """
    print("--- 3.1 FX Analysis: Applying Market Rates ---")
    
    # 1. Prepare Join Keys
    # We assume Base Currency is EUR. So key is "EUR" + "USD" = "EURUSD".
    df_transactions["join_key"] = "EUR" + df_transactions["currency_A"]
    
    # Ensure dates are datetime objects for merging
    df_transactions["date_A"] = pd.to_datetime(df_transactions["date_A"])
    df_rates["date"] = pd.to_datetime(df_rates["date"])
    
    # 2. Merge (Left Join)
    df_enriched = pd.merge(
        df_transactions,
        df_rates,
        left_on=["date_A", "join_key"],
        right_on=["date", "currency_pair"],
        how="left"
    )
    
    # 3. Calculate EUR Equivalent (Mark-to-Market)
    # Rate is usually quoted as 1 EUR = X USD (e.g., 1.10).
    # So: Amount EUR = Amount USD / Rate.
    df_enriched["amount_eur"] = df_enriched["amount_A"] / df_enriched["market_rate"]
    
    # 4. Calculate Financial Impact of Discrepancies
    # We convert the loss (amount_diff) into EUR.
    df_enriched["pnl_impact_eur"] = df_enriched["amount_diff"] / df_enriched["market_rate"]
    
    # Handling cases where currency is EUR (Rate = 1)
    mask_eur = df_transactions["currency_A"] == "EUR"
    df_enriched.loc[mask_eur, "amount_eur"] = df_enriched.loc[mask_eur, "amount_A"]
    df_enriched.loc[mask_eur, "pnl_impact_eur"] = df_enriched.loc[mask_eur, "amount_diff"]

    return df_enriched

# --------------------------------------------------------------------------
# 2. ANALYTICS & REPORTING
# --------------------------------------------------------------------------
def generate_fx_report(df):
    """
    Computes aggregated metrics for the Finance team.
    """
    print("\n💰 FINANCIAL IMPACT REPORT 💰")
    
    # Total Volume processed in EUR
    total_volume_eur = df["amount_eur"].sum()
    print(f"Total Volume Processed: {total_volume_eur:,.2f} €")
    
    # Total Discrepancy Value (The "Hidden Cost")
    total_loss_eur = df["pnl_impact_eur"].sum()
    print(f"Total Discrepancy Impact: {total_loss_eur:,.2f} €")
    print("-" * 30)
    
    return total_loss_eur

# --------------------------------------------------------------------------
# 3. MONTE CARLO SIMULATION (RISK ENGINE)
# --------------------------------------------------------------------------
def calculate_var(df_enriched, confidence_level=0.95, simulations=1000, days=30):
    """
    Simulates future FX moves using Geometric Brownian Motion to calculate Value at Risk (VaR).
    
    Logic:
    1. Calculate current Net Open Position (NOP) per currency.
    2. Simulate 1000 paths for FX rates over 30 days.
    3. Re-evaluate the portfolio value in each scenario.
    4. The 5th percentile of the P&L distribution is the VaR (95%).
    """
    print("\n STARTING MONTE CARLO SIMULATION (Risk Engine) ")
    
    # 1. Get Net Open Position (Exposure) in EUR
    # We group by currency pair (e.g., EURUSD) to see how much we hold.
    exposure = df_enriched.groupby("currency_A")["amount_eur"].sum()
    exposure = exposure.drop("EUR", errors="ignore") # Remove EUR, no FX risk
    
    print("Current Net Exposure by Currency (in EUR):")
    print(exposure.apply(lambda x: f"{x:,.2f} €"))
    
    total_potential_loss = 0
    
    # Simulation Parameters
    # We assume a daily volatility of 0.5% (typical for major pairs)
    daily_vol = 0.005 
    dt = 1 # 1 day step
    
    print(f"\nSimulating {simulations} scenarios over {days} days...")
    
    results = {}
    
    for currency, position_eur in exposure.items():
        # Geometric Brownian Motion Formula:
        # We simulate 1000 scenarios of returns over 30 days
        random_shocks = np.random.normal(0, 1, (simulations, days))
        
        # Calculate price path evolution (Log returns)
        log_returns = np.cumsum(( -0.5 * daily_vol**2 ) * dt + (daily_vol * np.sqrt(dt)) * random_shocks, axis=1)
        
        # Convert to price factor (e.g., 0.98 means -2% drop)
        price_paths = np.exp(log_returns)
        
        # Get the final return at day 30 for each scenario
        final_returns = price_paths[:, -1]
        
        # Calculate P&L: If we hold 1M and returns are 0.95, we lost 50k.
        simulated_pnl = position_eur * (final_returns - 1)
        
        # Calculate VaR (5th percentile = worst 5% cases)
        var_95 = np.percentile(simulated_pnl, (1 - confidence_level) * 100)
        
        print(f" -> Risk for {currency}: VaR 95% = {var_95:,.2f} €")
        total_potential_loss += var_95
        results[currency] = var_95
        
    print("-" * 30)
    print(f"📉 TOTAL PORTFOLIO VaR (95%): {total_potential_loss:,.2f} €")
    print(f"(Meaning: There is a 5% chance we lose more than {abs(total_potential_loss):,.2f} € next month due to FX volatility)")
    
    return total_potential_loss

# --------------------------------------------------------------------------
# 4. MAIN EXECUTION
# --------------------------------------------------------------------------
if __name__ == "__main__":
    # 1. Load Data
    print("Loading reconciliation data...")
    try:
        df_recon = pd.read_csv(config.PROCESSED_DATA_DIR / "reconciliation_output.csv")
        df_rates = pd.read_csv(config.FILE_MARKET_RATES)
    except FileNotFoundError:
        print(" Error: Files not found. Run Phase 2 first.")
        exit()

    # 2. Run FX Analytics (Mark-to-Market)
    df_fx = apply_market_rates(df_recon, df_rates)
    
    # 3. Generate Report
    loss = generate_fx_report(df_fx)
    
    # 4. Save Enriched Data
    output_path = config.PROCESSED_DATA_DIR / "transactions_enriched.csv"
    df_fx.to_csv(output_path, index=False)
    print(f" Enriched data saved to {output_path}")

    # 5. Run Monte Carlo Simulation
    calculate_var(df_fx)