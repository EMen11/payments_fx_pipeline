import pandas as pd
import numpy as np
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
import config

# --------------------------------------------------------------------------
# 1. PREPARE DATA FOR ML
# --------------------------------------------------------------------------
def prepare_features(df):
    """
    Selects and transforms columns to be understandable by a Machine Learning model.
    ML models only understand numbers, so we must encode text (One-Hot Encoding).
    """
    print("--- 4.1 ML Prep: Feature Engineering ---")
    
    # We work on a copy to avoid messing up the original data
    df_ml = df.copy()
    
    # Fill NaNs (Missing values crash ML models)
    df_ml["amount_diff"] = df_ml["amount_diff"].fillna(0)
    df_ml["amount_eur"] = df_ml["amount_eur"].fillna(0)
    
    # Feature 1: The Discrepancy Ratio (How big is the error relative to the amount?)
    # If error is 10€ on 100€ transaction -> 10% (Huge!)
    # If error is 10€ on 1M€ transaction -> 0.001% (Noise)
    # We add 0.01 to avoid division by zero.
    df_ml["discrepancy_ratio"] = df_ml["amount_diff"] / (df_ml["amount_eur"] + 0.01)
    
    # Feature 2: Encoding Currency (Text -> Numbers)
    # We use One-Hot Encoding: currency_USD becomes a column [0, 1]
    df_encoded = pd.get_dummies(df_ml, columns=["currency_A"], prefix="curr")
    
    # Select features for the model
    # We want the model to look at: Amount, The Error (diff), and the Currency.
    features = ["amount_eur", "amount_diff", "discrepancy_ratio"]
    
    # Add the dynamic currency columns (curr_USD, curr_GBP...)
    currency_cols = [c for c in df_encoded.columns if c.startswith("curr_")]
    features += currency_cols
    
    # Final dataset for training
    X = df_encoded[features]
    
    # Standardize data (Put all features on same scale)
    # Important because 'amount' (10,000) is huge compared to 'discrepancy_ratio' (0.01)
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    
    return X_scaled, df_ml

# --------------------------------------------------------------------------
# 2. TRAIN MODEL (UNSUPERVISED)
# --------------------------------------------------------------------------
def detect_anomalies(df_enriched):
    """
    Trains an Isolation Forest model to detect suspicious transactions.
    """
    print("\n🤖 STARTING AI ANOMALY DETECTION (Isolation Forest) 🤖")
    
    # 1. Prepare Data
    X, df_labeled = prepare_features(df_enriched)
    
    # 2. Train Model
    # contamination=0.05 means we estimate about 5% of data is anomalous.
    model = IsolationForest(n_estimators=100, contamination=0.05, random_state=config.RANDOM_SEED)
    model.fit(X)
    
    # 3. Predict
    # -1 means Anomaly, 1 means Normal
    df_labeled["anomaly_prediction"] = model.predict(X)
    
    # 4. Get Anomaly Score (Lower is more abnormal)
    df_labeled["anomaly_score"] = model.decision_function(X)
    
    # 5. Clean Output (Map -1 to "ANOMALY")
    df_labeled["is_anomaly_ml"] = df_labeled["anomaly_prediction"].apply(lambda x: "YES" if x == -1 else "NO")
    
    # Count results
    anomaly_count = df_labeled[df_labeled["is_anomaly_ml"] == "YES"].shape[0]
    print(f"-> Model Analysis Complete.")
    print(f"-> Detected {anomaly_count} anomalies out of {df_labeled.shape[0]} transactions.")
    
    return df_labeled

# --------------------------------------------------------------------------
# 3. MAIN EXECUTION
# --------------------------------------------------------------------------
if __name__ == "__main__":
    # 1. Load Data (From Phase 3)
    print("Loading enriched data...")
    try:
        df_fx = pd.read_csv(config.PROCESSED_DATA_DIR / "transactions_enriched.csv")
    except FileNotFoundError:
        print(" Error: File not found. Run Phase 3 first.")
        exit()

    # 2. Run ML
    df_final = detect_anomalies(df_fx)
    
    # 3. Save Final Dataset (This is the one for Power BI!)
    output_path = config.PROCESSED_DATA_DIR / "final_transactions_with_anomalies.csv"
    df_final.to_csv(output_path, index=False)
    print(f" Final dataset saved to {output_path}")
    
    # 4. Show Top Anomalies
    print("\n TOP 3 SUSPICIOUS TRANSACTIONS DETECTED BY AI:")
    cols = ["transaction_id", "amount_eur", "amount_diff", "recon_status", "anomaly_score"]
    # Sort by score (lowest score = most anomalous)
    print(df_final[df_final["is_anomaly_ml"] == "YES"].sort_values("anomaly_score").head(3)[cols])