import pandas as pd
import numpy as np
import config
from ingestion import load_data

# --------------------------------------------------------------------------
# 1. RECONCILIATION LOGIC
# --------------------------------------------------------------------------
def perform_reconciliation(df_a, df_b):
    """
    Merges the two datasets using a Full Outer Join and classifies each transaction.
    
    Logic Steps:
    1. Merge on transaction_id.
    2. Identify missing transactions (left_only vs right_only).
    3. For matched transactions, compare amounts and status.
    """
    print("--- 2. Starting Reconciliation Process ---")

    # 1. FULL OUTER JOIN
    # We join on 'transaction_id'. 
    # Suffixes '_A' and '_B' are added to columns that exist in both (like amount, status).
    # indicator=True adds a column '_merge' telling us if it's left_only, right_only, or both.
    df_merged = pd.merge(
        df_a, 
        df_b, 
        on="transaction_id", 
        how="outer", 
        suffixes=("_A", "_B"),
        indicator=True
    )

    # 2. CLASSIFICATION FUNCTION
    # We define the logic to tag each row with a specific status.
    def classify_row(row):
        # Case 1: Missing in Bank (Provider B)
        if row["_merge"] == "left_only":
            return "MISSING_IN_B"
        
        # Case 2: Missing in Internal System (Provider A)
        elif row["_merge"] == "right_only":
            return "MISSING_IN_A"
        
        # Case 3: Present in both, but amounts mismatch
        # We use the tolerance from config to avoid floating point errors (0.01)
        # abs() gets the absolute difference.
        elif abs(row["amount_A"] - row["amount_B"]) > config.AMOUNT_TOLERANCE:
            return "AMOUNT_MISMATCH"
        
        # Case 4: Present in both, amounts match, but status mismatch
        # e.g., COMPLETED vs PENDING
        elif row["status_A"] != row["status_B"]:
            return "STATUS_MISMATCH"
        
        # Case 5: Perfect Match
        else:
            return "MATCH"

    # Apply the classification row by row
    print("   -> Classifying discrepancies...")
    df_merged["recon_status"] = df_merged.apply(classify_row, axis=1)

    # 3. CALCULATE DISCREPANCIES (For analysis)
    # If there is a mismatch, how big is it? (Amount A - Amount B)
    # We fill NaN with 0 to allow calculation.
    df_merged["amount_diff"] = df_merged["amount_A"].fillna(0) - df_merged["amount_B"].fillna(0)

    # Clean up: organize columns nicely for the output
    # We prioritize the ID and the status.
    cols_order = [
        "transaction_id", "recon_status", "amount_diff", 
        "amount_A", "amount_B", 
        "currency_A", "currency_B",
        "date_A", "date_B", 
        "status_A", "status_B"
    ]
    
    # Select only existing columns (in case some are missing) and available
    final_cols = [c for c in cols_order if c in df_merged.columns]
    
    return df_merged[final_cols]

# --------------------------------------------------------------------------
# 2. MAIN EXECUTION
# --------------------------------------------------------------------------
if __name__ == "__main__":
    # 1. Load Clean Data (using the script from Step 2.1)
    df_a, df_b, _ = load_data()
    
    # 2. Run Reconciliation
    df_results = perform_reconciliation(df_a, df_b)
    
    # 3. Save Results
    output_path = config.PROCESSED_DATA_DIR / "reconciliation_output.csv"
    df_results.to_csv(output_path, index=False)
    
    print(f" Reconciliation Complete. Results saved to {output_path}")
    
    # 4. SHOW KPI SUMMARY (The "Analyst View")
    print("\n RECONCILIATION SUMMARY 📊")
    print(df_results["recon_status"].value_counts())
    
    # Show a few examples of mismatches
    print("\n Example of Amount Mismatches:")
    mismatches = df_results[df_results["recon_status"] == "AMOUNT_MISMATCH"]
    if not mismatches.empty:
        print(mismatches[["transaction_id", "amount_A", "amount_B", "amount_diff"]].head(3))