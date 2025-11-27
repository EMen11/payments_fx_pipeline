#  End-to-End Payments Reconciliation & FX Risk Engine

![Python](https://img.shields.io/badge/Python-3.9%2B-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Pandas](https://img.shields.io/badge/Pandas-Data_Analysis-150458?style=for-the-badge&logo=pandas&logoColor=white)
![Power BI](https://img.shields.io/badge/Power_BI-Dashboard-F2C811?style=for-the-badge&logo=powerbi&logoColor=black)
![Scikit-Learn](https://img.shields.io/badge/Sklearn-Anomaly_Detection-F7931E?style=for-the-badge&logo=scikitlearn&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)

##  Executive Summary

This project is a comprehensive **Financial Operations (FinOps) Pipeline** designed to bridge the gap between Treasury systems and Banking data.

It automates the **Reconciliation** of high-volume cross-border payments to identify liquidity leaks, calculates hidden **FX Risk** and spreads, and simulates future market exposure using **Monte Carlo** methods. By integrating **Machine Learning** for audit purposes, this engine moves beyond static rules to detect complex financial anomalies and operational errors.

---

##  Dashboard Gallery

The technical output feeds a **Power BI Executive Dashboard**, enabling CFOs and Treasury Managers to monitor operational health and financial risk.

### 1. Operations View: Reconciliation Health
*A control tower for Ops teams. It visualizes match rates and isolates discrepancies (Missing Cash, Status Mismatches) for immediate investigation.*
![Ops View](dashboards/dashboard_01_ops_reconciliation.jpg)

### 2. Finance View: P&L & FX Risk
*A financial view for the CFO. It analyzes realized losses (Hidden Costs) by currency and projects future exposure using the Monte Carlo Value at Risk (VaR) model.*
![Finance View](dashboards/dashboard_02_fx_risk_pnl.jpg)

### 3. AI Audit View: Anomaly Detection
*Advanced scatter plot visualizing the Isolation Forest algorithm results. The model automatically isolates anomalies (Red/Orange points) from standard transactions, prioritizing audit efforts based on an anomaly score.*
![AI View](dashboards/dashboard_03_ml_anomalies.jpg)

---
## Architecture & Pipeline

The project follows a modular **ETL (Extract, Transform, Load)** architecture, designed to ensure data integrity from ingestion to reporting.

```mermaid
graph LR
    A[Raw Data Gen] -->|Chaos Injection| B(Ingestion & Cleaning)
    B --> C{Reconciliation Engine}
    C -->|Matched Data| D[FX Analytics & P&L]
    D --> E[Risk Engine - Monte Carlo]
    D --> F[ML Anomaly Detection]
    F --> G[Final Power BI Report]
   ``` 

### 1. Data Ingestion & Cleaning
* **Source:** Synthetic CSV files generated with specific "Chaos" parameters (Missing data, Formatting errors).
* **Process:** The `ingestion.py` module standardizes date formats, handles floating-point precision (decimal rounding), and cleans string inconsistencies.

### 2. Reconciliation Engine (The "Core")
Unlike simple matching scripts, this engine uses a **Full Outer Join** logic.
* **Why:** To capture 100% of the data universe, ensuring that no transaction—whether internal-only or bank-only—falls through the cracks.
* **Output:** A classified dataset (`MATCH`, `MISSING`, `MISMATCH`) ready for financial analysis.

### 3. Financial Enrichment & AI Audit
Once data is reconciled, it flows into two parallel streams:
* **The Quantitative Stream:** Converts all flows to EUR (Mark-to-Market) and calculates the **Net Open Position** for the Risk Engine.
* **The Intelligence Stream:** Feeds enriched transaction features (Amount, Currency, Discrepancy) into the **Isolation Forest** model to detect outliers.

---

##   Financial & Statistical Methodologies

This project goes beyond simple data processing; it implements industry-standard financial models and statistical algorithms to ensure the results are robust enough for decision-making.

### A. Reconciliation Logic: The "Full Outer Join" Principle
Standard reconciliation scripts often use `Inner Joins` (matching only perfect pairs) or `Left Joins` (trusting one source blindly). This approach creates **Blind Spots**.

* **My Approach:** I implemented a **Full Outer Join** logic.
* **The Financial Reason:** In Treasury, a missing record (a payment sent but not received, or an unauthorized bank debit) is a higher risk than a mismatched amount.
* **Outcome:** This guarantees **Completeness Assurance**, ensuring that 100% of transactions from both the Ledger (ERP) and the Bank Statement are accounted for, visualizing "Breaks" on both sides.


### B. Risk Engine: Monte Carlo & Geometric Brownian Motion
To forecast future FX exposure, the pipeline moves away from linear extrapolation and uses **Stochastic Calculus**.

* **The Model:** I utilized **Geometric Brownian Motion (GBM)** to simulate currency path evolution.
* **The Formula:**
  $$dS_t = \mu S_t dt + \sigma S_t dW_t$$

  * *Where **μ** is the drift (trend), **σ** is the volatility (risk), and **dWt** is the Wiener process (random shock).*

* **The Application:** By running 1,000+ simulations per currency pair, the engine calculates the **Value at Risk (VaR 95%)**, providing the CFO with a "Worst Case Scenario" probability rather than a simple average.
* 
### C. AI Audit: Unsupervised Anomaly Detection
Traditional rule-based audits (e.g., "if amount > 10k") generate too many false positives and fail to catch complex fraud schemes.

* **The Algorithm:** **Isolation Forest** (Scikit-Learn).
* **Why Unsupervised?** We do not have "labeled" fraud data. This algorithm isolates anomalies by randomly selecting a feature and randomly selecting a split value.
* **The Logic:** Anomalies are "few and different." They are isolated in fewer steps (shorter path lengths in the tree) than normal observations. This allows the system to flag "Unknown Unknowns"—irregularities that human auditors didn't know they needed to look for.

##  Tech Stack & Installation

This project is built with a modular structure to separate data generation, processing, and analysis, adhering to clean code principles.

### 💻 Stack Overview
| Category | Tool/Library | Usage |
| :--- | :--- | :--- |
| **Language** | **Python 3.9+** | Core logic and orchestration. |
| **ETL & Analysis** | **Pandas / NumPy** | Vectorized data manipulation and financial calculations. |
| **ML Core** | **Scikit-Learn** | `IsolationForest` implementation for anomaly detection. |
| **Reporting** | **Power BI** | Interactive dashboards (DAX measures & Data Modeling). |

###  Installation & Execution
To run this pipeline locally, follow these steps. The system is designed to be self-contained: it will **generate its own synthetic data** automatically upon execution.

**1. Clone the repository**
```bash
git clone [https://github.com/YOUR_USERNAME/payments_fx_pipeline.git](https://github.com/YOUR_USERNAME/payments_fx_pipeline.git)
cd payments_fx_pipeline
```
**2. Set up the environment**
It is recommended to use a virtual environment to manage dependencies to avoid conflicts.

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

**3. Run the Pipeline**
Execute the main orchestration script. This triggers the full ETL flow: Data Generation → Cleaning → Reconciliation → ML Analysis → Export.

```bash
python python main.py
```

*Output: Check the `/data/processed/` folder for `final_report_with_anomalies.csv`, which serves as the source for the Power BI dashboard.*

---

##  Author

**Elie Menassa**
* **Focus:** Bridging the gap between Financial Operations and Data Science through automation.

*Open to feedback and collaboration on FinOps automation and Risk Management topics.*
