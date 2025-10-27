# 🐍 "HONEST" Python Rule Discovery Engine

This project is a brute-force trading rule discovery engine. The goal isn't to build one complex "black box" model, but to discover *dozens* of simple, robust, human-readable rules (e.g., "IF RSI < 30 AND H4_EMA > 200 THEN...").

The entire philosophy is built around **"Honest" Validation** to avoid overfitting.

---

## How It Works

### 1. The Brute-Force Iteration
The script runs for thousands of iterations (`ITERATIONS = 5000`). In each iteration, it:
* Picks a **random subset of features** (15-35 features).
* Trains a simple, shallow **Decision Tree** (`max_depth=6`) on the **Training Data** (e.g., 2010-2021).

### 2. The Rule Extraction
It then extracts all the human-readable rules from the trained tree. For example:
`IF 'm5_rsi' <= 30 AND 'h1_price_vs_ema' > 0.001 THEN predict 'Buy'`

### 3. The "HONEST" Validation
This is the most important part. Each extracted rule is immediately tested on **Unseen Validation Data** (e.g., 2022-2023).

* It finds every candle in the validation set that matches the rule's conditions.
* It runs a high-speed, **Numba-accelerated backtester** (`@njit validate_rule_performance`) on those specific signals.
* This backtester simulates a *realistic* trade (ATR-based Stop Loss, 1.5 R:R Take Profit) to see what the *actual* outcome was.

### 4. The Result
If a rule passes the strict criteria (e.g., `MIN_VALIDATION_TRADES > 100` and `MIN_VALIDATION_WIN_RATE > 0.80`), it is considered "robust" and saved to a final `.json` file.

These validated JSON rules can then be loaded by a live bot (`master.py`) to trade with high confidence.
