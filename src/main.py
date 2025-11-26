"""
 MAIN CODE
Runs the End-to-End Financial Pipeline.
1. Generate Data (Simulate Ops)
2. Ingest & Clean
3. Reconcile (Ops)
4. Analyze FX Risk (Finance)
5. Detect Anomalies (ML)
"""
import sys
from pathlib import Path

# Add 'src' to python path to import modules
sys.path.append(str(Path(__file__).parent / "src"))

import config
from data_generator import generate_market_rates, generate_provider_A, generate_provider_B_with_errors
from ingestion import load_data
from reconciliation import perform_reconciliation
from fx_analytics import apply_market_rates, generate_fx_report, calculate_var
from anomaly_models import detect_anomalies

def run_pipeline():
    print("="*50)
    print("🚀 STARTING PAYMENTS OPS & RISK PIPELINE")
    print("="*50)

    # --- STEP 1: DATA GENERATION ---
    print("\n[STEP 1] Generating Synthetic Data...")
    generate_market_rates()
    df_a = generate_provider_A()
    generate_provider_B_with_errors(df_a)

    # --- STEP 2: INGESTION ---
    print("\n[STEP 2] Ingesting & Cleaning Data...")
    df_a_clean, df_b_clean, df_rates = load_data()

    # --- STEP 3: RECONCILIATION ---
    print("\n[STEP 3] Running Reconciliation Engine...")
    df_recon = perform_reconciliation(df_a_clean, df_b_clean)
    # Save intermediate result
    df_recon.to_csv(config.PROCESSED_DATA_DIR / "reconciliation_output.csv", index=False)

    # --- STEP 4: FINANCIAL ANALYTICS ---
    print("\n[STEP 4] Calculating FX P&L and Risk (VaR)...")
    df_enriched = apply_market_rates(df_recon, df_rates)
    generate_fx_report(df_enriched)
    calculate_var(df_enriched) # Prints VaR

    # --- STEP 5: ML ANOMALY DETECTION ---
    print("\n[STEP 5] Detecting Anomalies with AI...")
    df_final = detect_anomalies(df_enriched)
    
    # Final Export
    final_path = config.PROCESSED_DATA_DIR / "final_global_report.csv"
    df_final.to_csv(final_path, index=False)
    
    print("\n" + "="*50)
    print(f" PIPELINE FINISHED SUCCESSFULY")
    print(f" Final Report available at: {final_path}")
    print("="*50)

if __name__ == "__main__":
    run_pipeline()