import pandas as pd
import numpy as np
import config

# --------------------------------------------------------------------------
# 1. PREPARATION & ENRICHMENT
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
    # In transactions, we have 'currency' (e.g., USD).
    # In rates, we have 'currency_pair' (e.g., EURUSD).
    # We assume Base Currency is EUR. So key is "EUR" + "USD" = "EURUSD".
    df_transactions["join_key"] = "EUR" + df_transactions["currency_A"]
    
    # Ensure dates are datetime objects for merging
    df_transactions["date_A"] = pd.to_datetime(df_transactions["date_A"])
    df_rates["date"] = pd.to_datetime(df_rates["date"])
    
    # 2. Merge (Left Join)
    # We want to keep all transactions, even if a rate is missing (though it shouldn't happen).
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
    # Phase 2 gave us 'amount_diff' (e.g., missing 50 USD).
    # We convert this loss into EUR.
    df_enriched["pnl_impact_eur"] = df_enriched["amount_diff"] / df_enriched["market_rate"]
    
    # Handling cases where currency is EUR (Rate = 1) or missing rate
    # If currency is EUR, market_rate might be NaN because we didn't generate EUREUR rates.
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
    print("\n FINANCIAL IMPACT REPORT ")
    
    # Total Volume processed in EUR
    total_volume_eur = df["amount_eur"].sum()
    print(f"Total Volume Processed: {total_volume_eur:,.2f} €")
    
    # Total Discrepancy Value (The "Hidden Cost")
    # This sums up all the 'amount_diff' converted to EUR.
    # If amount_diff is positive (A > B), it means we lost money (Bank received less).
    total_loss_eur = df["pnl_impact_eur"].sum()
    
    print(f"Total Discrepancy Impact: {total_loss_eur:,.2f} €")
    print("-" * 30)
    
    return total_loss_eur

# --------------------------------------------------------------------------
# 3. MAIN EXECUTION
# --------------------------------------------------------------------------
if __name__ == "__main__":
    # 1. Load Data
    # We load the output from Phase 2 (Reconciliation) and Phase 1 (Rates)
    print("Loading reconciliation data...")
    try:
        df_recon = pd.read_csv(config.PROCESSED_DATA_DIR / "reconciliation_output.csv")
        df_rates = pd.read_csv(config.FILE_MARKET_RATES)
    except FileNotFoundError:
        print(" Error: Files not found. Run Phase 2 first.")
        exit()

    # 2. Run FX Analytics
    df_fx = apply_market_rates(df_recon, df_rates)
    
    # 3. Generate Report
    loss = generate_fx_report(df_fx)
    
    # 4. Save for Phase 3.2 (Monte Carlo)
    output_path = config.PROCESSED_DATA_DIR / "transactions_enriched.csv"
    df_fx.to_csv(output_path, index=False)
    print(f" Enriched data saved to {output_path}")
    
    # Preview
    print("\nPreview of Financial Impact:")
    cols = ["transaction_id", "amount_A", "currency_A", "market_rate", "amount_eur", "pnl_impact_eur"]
    print(df_fx[cols].head(3))