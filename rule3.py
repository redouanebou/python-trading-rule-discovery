import pandas as pd
import numpy as np
from sklearn.tree import DecisionTreeClassifier
import json
from numba import njit
from tqdm import tqdm
import random

FEATURES_FILE_PATH = "features_HTF.csv" 
OUTPUT_BUY_RULES_PATH = "buy30.json"
OUTPUT_SELL_RULES_PATH = "sell30.json"

TRAIN_END_DATE = '2021-12-31' 
VALIDATION_START_DATE = '2022-01-01'
VALIDATION_END_DATE = '2023-12-31'

ITERATIONS = 5000 
MIN_VALIDATION_TRADES = 100 
MIN_VALIDATION_WIN_RATE = 0.90 
ATR_PERIOD = 14
ATR_MULTIPLIER_SL = 1.0
RR_TP = 2.0
LOOKAHEAD_CANDLES = 12

@njit
def validate_rule_performance(indices, open_prices, high_prices, low_prices, atr_values, trade_type):
    """
    An honest validator. For each signal, it simulates a realistic trade
    with an ATR-based SL and TP to see what the real outcome was on UNSEEN data.
    (This function is sound and remains unchanged)
    """
    total_trades = len(indices)
    wins = 0

    for i in range(total_trades):
        signal_idx = indices[i]
        entry_idx = signal_idx + 1
        
        if entry_idx + LOOKAHEAD_CANDLES >= len(open_prices):
            continue

        sl_distance = atr_values[signal_idx] * ATR_MULTIPLIER_SL
        if sl_distance <= 0:
            continue

        entry_price = open_prices[entry_idx]
        
        if trade_type == 'Buy':
            sl_price = entry_price - sl_distance
            tp_price = entry_price + (sl_distance * RR_TP)
            hit_tp = False
            for k in range(entry_idx, entry_idx + LOOKAHEAD_CANDLES):
                if low_prices[k] <= sl_price:
                    break 
                if high_prices[k] >= tp_price:
                    hit_tp = True
                    break
            if hit_tp:
                wins += 1
        
        elif trade_type == 'Sell':
            sl_price = entry_price + sl_distance
            tp_price = entry_price - (sl_distance * RR_TP)
            hit_tp = False
            for k in range(entry_idx, entry_idx + LOOKAHEAD_CANDLES):
                if high_prices[k] >= sl_price:
                    break
                if low_prices[k] <= tp_price:
                    hit_tp = True
                    break
            if hit_tp:
                wins += 1
            
    win_rate = wins / total_trades if total_trades > 0 else 0.0
    return total_trades, win_rate

def extract_rules(tree, feature_names, class_names, tree_classes):
    """
    Extracts human-readable rules from a trained decision tree.
    (This function is sound and remains unchanged)
    """
    tree_ = tree.tree_
    feature_name = [feature_names[i] if i != -2 else "undefined!" for i in tree_.feature]
    rules = []

    def recurse(node, rule):
        if tree_.feature[node] != -2:
            name = feature_name[node]
            threshold = tree_.threshold[node]
            recurse(tree_.children_left[node], rule + [(name, "<=", threshold)])
            recurse(tree_.children_right[node], rule + [(name, ">", threshold)])
        else:
            class_index = np.argmax(tree_.value[node])
            original_label = tree_classes[class_index]
            predicted_class = class_names[original_label]
            if predicted_class != 'No_Trade':
                rules.append((predicted_class, rule))
    recurse(0, [])
    return rules

if __name__ == "__main__":
    print("🚀 Starting Phase 2 (HONEST): Rule Discovery for HTF Features...")

    print(f"Loading HONEST feature set from '{FEATURES_FILE_PATH}'...")
    df = pd.read_csv(FEATURES_FILE_PATH, parse_dates=['datetime'], index_col='datetime')
    print("Data loaded.")

    for col in df.select_dtypes(include=['object']).columns:
        df[col] = df[col].astype('category')
        
    X = pd.get_dummies(df.drop(columns=['open', 'high', 'low', 'close', 'label', 'atr']), drop_first=True)
    y = df['label']
    
    train_X = X.loc[:TRAIN_END_DATE]
    train_y = y.loc[:TRAIN_END_DATE]
    val_df = df.loc[VALIDATION_START_DATE:VALIDATION_END_DATE]
    
    val_open_np = val_df['open'].to_numpy()
    val_high_np = val_df['high'].to_numpy()
    val_low_np = val_df['low'].to_numpy()
    val_atr_np = val_df['atr'].to_numpy()

    print(f"Training set size: {len(train_X)} (up to {TRAIN_END_DATE})")
    print(f"Validation set size: {len(val_df)} ({VALIDATION_START_DATE} to {VALIDATION_END_DATE})")

    print(f"\n🔥 Starting {ITERATIONS} brute-force iterations to find robust rules...")
    found_buy_rules = []
    found_sell_rules = []
    class_names = {0: 'No_Trade', 1: 'Buy', -1: 'Sell'}

    for i in tqdm(range(ITERATIONS), desc="Discovering Rules"):
        num_features = random.randint(15, 35)
        feature_subset = random.sample(list(train_X.columns), num_features)
        
        dt = DecisionTreeClassifier(max_depth=6, min_samples_leaf=200, class_weight='balanced')
        dt.fit(train_X[feature_subset], train_y)
        
        rules = extract_rules(dt, feature_subset, class_names, dt.classes_)
        
        for trade_type, conditions in rules:
            try:
                query = " & ".join([f"`{feat}` {op} {val}" for feat, op, val in conditions])
                trade_indices_loc = val_df.query(query).index
                trade_indices_pos = val_df.index.get_indexer_for(trade_indices_loc)

                if len(trade_indices_pos) < MIN_VALIDATION_TRADES:
                    continue

                trade_count, win_rate = validate_rule_performance(
                    trade_indices_pos, val_open_np, val_high_np, val_low_np, val_atr_np, trade_type
                )
                
                if win_rate >= MIN_VALIDATION_WIN_RATE:
                    rule_data = {
                        "conditions": [{"feature": c[0], "operator": c[1], "value": float(c[2])} for c in conditions],
                        "validation_trades": trade_count,
                        "validation_winrate": win_rate,
                    }
                    if trade_type == 'Buy':
                        found_buy_rules.append(rule_data)
                    elif trade_type == 'Sell':
                        found_sell_rules.append(rule_data)
            except Exception as e:
                continue

    print(f"\nDiscovery complete. Found {len(found_buy_rules)} Buy rules and {len(found_sell_rules)} Sell rules that passed validation.")

    found_buy_rules.sort(key=lambda x: x['validation_winrate'], reverse=True)
    found_sell_rules.sort(key=lambda x: x['validation_winrate'], reverse=True)

    for i, rule in enumerate(found_buy_rules):
        rule['rule_id'] = f"HTF_GBPUSD_BUY_{i+1:03d}"
    for i, rule in enumerate(found_sell_rules):
        rule['rule_id'] = f"HTF_GBPUSD_SELL_{i+1:03d}"

    with open(OUTPUT_BUY_RULES_PATH, "w") as f:
        json.dump(found_buy_rules, f, indent=4)
    print(f"\n✅ Saved {len(found_buy_rules)} validated Buy rules to '{OUTPUT_BUY_RULES_PATH}'")

    with open(OUTPUT_SELL_RULES_PATH, "w") as f:
        json.dump(found_sell_rules, f, indent=4)
    print(f"✅ Saved {len(found_sell_rules)} validated Sell rules to '{OUTPUT_SELL_RULES_PATH}'")