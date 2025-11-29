<div align="center">

# 🐍 "HONEST" Python Rule Discovery Engine

### Brute-Force Alpha Extraction & Validation

![Python](https://img.shields.io/badge/Python-3.9%2B-3776AB?style=for-the-badge\&logo=python\&logoColor=white)
![Decision Trees](https://img.shields.io/badge/SKLearn-Decision_Trees-F7931E?style=for-the-badge\&logo=scikit-learn\&logoColor=white)
![Numba](https://img.shields.io/badge/Numba-JIT_Optimized-00A3E0?style=for-the-badge)

<p align="center">
  <em>A transparent "White-Box" research engine designed to discover human-readable trading rules using brute-force decision trees and honest out-of-sample validation.</em>
</p>

</div>

---

## 📖 The Philosophy: "White Box" over "Black Box"

While Deep Learning offers power, it lacks interpretability. In high-stakes trading, not knowing *why* a model takes a trade is a risk.

This engine solves that by brute-forcing thousands of **Decision Trees** on random feature subsets to extract explicit, robust logic (e.g., `IF RSI < 30 AND H4_EMA > 200 THEN BUY`). It prioritizes **"Honest Validation"**—rejecting any rule that doesn't survive on unseen data with realistic friction.

---

## ⚙️ Core Workflow

```mermaid
graph TD
    subgraph Ingestion
    A[Training Data (2005-2020)] -->|Random Feature Subsets| B(Train Shallow Decision Trees)
    B -->|Extract Logic| C[Candidate Rules Pool]
    C -->|Simulate Trade| D{Honest Validator (2020-2023)}
    D -->|Win Rate > 75%| E[Saved to JSON]
    D -->|Win Rate < 75%| F[Discarded]
```

### 1. Brute-Force Mining (`rule2.py`)

* **Iterations:** 5,000+ cycles.
* **Feature Bagging:** Random subset of 15–35 features per cycle.
* **Logic Extraction:** Parses the Decision Tree structure into human‑readable SQL‑like rules.

### 2. The "Honest" Validator

The immune system of the engine. Every rule is tested on untouched validation data.

**Validation Logic:**

* JIT‑compiled backtester using **Numba**.
* **ATR‑based Stop Loss** and **1.5R Take Profit**.
* Time‑window outcome evaluation.
* A rule is saved only if:

  * It generates **>100 trades**, and
  * Achieves **>75% win rate**.

---

## 🚀 Performance Optimization

| Component     | Tech            | Impact                                   |
| ------------- | --------------- | ---------------------------------------- |
| Backtester    | Numba (`@njit`) | Validates 100,000+ signals in seconds    |
| Tree Training | Scikit‑Learn    | Uses class balancing for rare events     |
| Data I/O      | Pandas          | Handles large H4/M5 datasets efficiently |

---

## 📂 Project Structure

```bash
python-trading-rule-discovery/
├── rule2.py                # Main Discovery Engine (Brute Force + Validation)
├── rule3.py                # HTF Variant
├── features_GBP.csv        # Input Dataset (GitIgnored)
├── buyking.json            # Validated Buy Rules
├── sellking.json           # Validated Sell Rules
└── README.md               # Documentation
```

---

## 💻 Usage

### 1. Prepare Data

Ensure you have a cleaned CSV file (`features_GBP.csv`) containing your full feature set.

### 2. Run Discovery

```bash
python rule2.py
```

The script will show a TQDM progress bar as it mines and validates rules.

### 3. Inspect Output

Example from `buyking.json`:

```json
{
    "rule_id": "HONEST_GBPUSD_BUY_001",
    "conditions": [
        {"feature": "rsi_14", "operator": "<=", "value": 30.5},
        {"feature": "adx_14", "operator": ">", "value": 25.0}
    ],
    "validation_winrate": 0.78,
    "validation_trades": 142
}
```

---

## ⚠️ Disclaimer

<div align="center"><strong>Research Code</strong></div>

This engine is intended for quantitative research and educational use.

* Overfitting remains a risk—"Honest Validation" reduces but does not eliminate it.
* Market regimes change; a rule found in one may fail in another.
* Real trading includes spread & slippage not fully modeled here.

---

Engineered by **Redouane Boundra**.
