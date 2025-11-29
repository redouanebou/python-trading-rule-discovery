# 🔍 Python Rule Discovery Engine (RDE)

### Transparent, Causal, Decision-Tree–Based Alpha Mining

---

## 📖 Overview

This repository contains a **clean, honest, and reproducible** implementation of a rule-discovery engine built around shallow Decision Trees, strict causal validation, and fast Numba-accelerated backtesting.

No hype. No imaginary modules. No marketing fluff.

This project does **one thing** , and does it well:

> **Systematically mine interpretable trading rules and validate them on truly unseen data using a fast, realistic simulation engine.**

If you want a solid foundation for building causal quant systems, this is it.

---

## 🧠 What This Project *Actually Does*

### ✔️ 1. Feature-subset randomization ("feature bagging")

Each iteration selects a random subset of features (15–35) to enforce diversity and avoid overfitting.

### ✔️ 2. Shallow Decision Tree training

A small tree forces human-interpretable logic like:

```
IF rsi_14 <= 30 AND adx_14 > 25 THEN BUY
```

### ✔️ 3. Logic extraction

Tree splits are recursively converted into readable rule structures.

### ✔️ 4. Strict out-of-sample validation

A JIT-compiled Numba backtester evaluates rules only on untouched validation data.

Validation includes:

* ATR-based stop loss
* 1.5R take profit
* max-horizon outcome logic
* minimum trade count
* win-rate threshold

### ✔️ 5. Automatically saving only robust rules

Validated BUY/SELL rules are stored in JSON.

---

## 📂 Project Structure

```bash
python-trading-rule-discovery/
├── rule2.py                # Main rule mining engine
├── rule3.py                # Higher-timeframe variant
├── features_GBP.csv        # Input dataset (not included)
├── buyking.json            # Robust out-of-sample BUY rules
├── sellking.json           # Robust out-of-sample SELL rules
├── requirements.txt        # Dependencies
└── README.md               # Documentation
```

---

## 📦 Installation

### 1. Clone the repository

```bash
git clone https://github.com/redouanebou/python-trading-rule-discovery
cd python-trading-rule-discovery
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

---

## 📊 Data Requirements

Your input CSV (`features_GBP.csv`) must include:

* timestamp column
* open, high, low, close
* computed technical features (RSI, ADX, EMAs, volatility measures, etc.)
* **NO look-ahead leakage**
* **all features shifted by +1 candle** if derived from OHLC

A minimal schema example:

```text
timestamp, open, high, low, close, rsi_14, adx_14, ema_50, ema_200, atr_14, ...
```

---

## 🚀 Usage

### Run the discovery engine

```bash
python rule2.py
```

You will see a TQDM progress bar as rules are generated and validated.

### Inspect generated rules

Example (from `buyking.json`):

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

## 🔒 Causality & Validation Integrity

This engine enforces:

* **T-1 causal consistency**
* **no future data access**
* realistic trade simulation
* rejection of weak or overfit rules

A rule is accepted only if:

* it fires **>100 trades** in validation
* win rate is **>75%**

---

## 🧪 Roadmap (Realistic + Deliverable)

* Add automated feature-drift analysis
* Add multi-symbol batch processing
* Add cross-regime validation (rolling windows)
* Add Monte-Carlo stress tests
* Add export to PineScript

---

## ⚠️ Disclaimer

This project is for quantitative research purposes.
It does not constitute financial advice or guarantee profitability.
Use in live trading entirely at your own risk.

---

Maintained by **Redouane Boundra**.
