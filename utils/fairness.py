import pandas as pd
import numpy as np
from fairlearn.metrics import MetricFrame, selection_rate, demographic_parity_difference
from sklearn.metrics import accuracy_score
import json

def load_benchmarks():
    try:
        with open("data/benchmarks.json", "r") as f:
            return json.load(f)
    except:
        return {}

def detect_advanced_bias(df, target_col, protected_col):
    results = {}
    benchmarks = load_benchmarks()
    
    # 1. Representation
    counts = df[protected_col].value_counts(normalize=True).to_dict()
    results['representation'] = {k: round(v * 100, 2) for k, v in counts.items()}
    
    # 2. Outcome
    if pd.api.types.is_numeric_dtype(df[target_col]):
        fav_outcome = df[target_col].max()
    else:
        fav_outcome = df[target_col].value_counts().idxmax()
        
    y_true = (df[target_col] == fav_outcome).astype(int)
    mf = MetricFrame(metrics=selection_rate, y_true=y_true, y_pred=y_true, sensitive_features=df[protected_col])
    rates = {str(k): round(v * 100, 2) for k, v in mf.by_group.to_dict().items()}
    results['selection_rates'] = rates
    
    disparity = demographic_parity_difference(y_true, y_true, sensitive_features=df[protected_col])
    results['fairness_score'] = max(0, 100 - (disparity * 100))
    
    # 3. Benchmark
    matched_benchmark = None
    for name, bench in benchmarks.items():
        if bench['protected_attribute'].lower() in protected_col.lower():
            matched_benchmark = bench
            break
            
    if matched_benchmark:
        b_disparity = round(matched_benchmark['standard_disparity'] * 100, 2)
        results['benchmark_comparison'] = {
            "name": name,
            "our_disparity": round(disparity * 100, 2),
            "benchmark_disparity": b_disparity,
            "benchmark_fairness_score": 100 - b_disparity # Higher is Better
        }
    else:
        results['benchmark_comparison'] = {
            "name": "General Industry Std", 
            "our_disparity": round(disparity * 100, 2), 
            "benchmark_disparity": 10.0,
            "benchmark_fairness_score": 90.0
        }

    # 4. Detailed Explanation (Plain English)
    if rates:
        max_group = max(rates, key=rates.get)
        min_group = min(rates, key=rates.get)
        max_val = rates[max_group]
        min_val = rates[min_group]
        gap = round(max_val - min_val, 1)
        prob_ratio = round((1 - (min_val / max(max_val, 0.1))) * 100, 1)
        
        results['detailed_explanation'] = {
            "attribute": protected_col,
            "percentage": gap,
            "comparison_text": f"Members of the {min_group} group are {prob_ratio}% less likely to receive favorable outcomes than {max_group} members (Gap: {gap}%).",
            "impact": "This systemic disparity presents moderate to high risk of regulatory non-compliance and talent attrition. Historical bias in local data may be propagating through current decision patterns.",
            "recommended_action": "We strongly recommend applying 'Reweighting' (Phase 3) to equalize the influence of different demographic segments before final production deployment."
        }

    return results
