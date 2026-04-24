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
    """
    Detects bias in the dataset using Fairlearn metrics.
    """
    try:
        # Validation
        if df is None or df.empty:
            raise ValueError("Dataset is empty.")
        if target_col not in df.columns or protected_col not in df.columns:
            raise ValueError(f"Required columns '{target_col}' or '{protected_col}' not found.")

        results = {}
        benchmarks = load_benchmarks()
        
        # Drop NaNs for the analysis
        temp_df = df[[target_col, protected_col]].dropna()
        if temp_df.empty:
            raise ValueError("No data left after dropping missing values.")

        # 1. Representation
        counts = temp_df[protected_col].value_counts(normalize=True).to_dict()
        results['representation'] = {str(k): round(v * 100, 2) for k, v in counts.items()}
        
        # 2. Outcome Processing
        # Determine favorable outcome
        if pd.api.types.is_numeric_dtype(temp_df[target_col]):
            # If numeric, assume higher is better or 1 is better
            fav_outcome = temp_df[target_col].max()
        else:
            # If categorical, try to find 'positive' keywords or use mode
            fav_keywords = ['yes', 'approved', 'hired', 'pass', '1', 'success', 'good', 'accepted']
            unique_vals = temp_df[target_col].unique()
            fav_outcome = next((v for v in unique_vals if str(v).lower() in fav_keywords), unique_vals[0])
            
        y_true = (temp_df[target_col] == fav_outcome).astype(int)
        
        # MetricFrame for selection rates
        # In Fairlearn 0.10.0, use 'metrics' dictionary
        mf = MetricFrame(
            metrics={'selection_rate': selection_rate}, 
            y_true=y_true, 
            y_pred=y_true, # We are auditing the dataset labels
            sensitive_features=temp_df[protected_col]
        )
        
        # mf.by_group is a Series if only one metric is passed
        by_group_series = mf.by_group
        if isinstance(by_group_series, pd.DataFrame):
            by_group_series = by_group_series['selection_rate']
            
        rates = {str(k): round(float(v) * 100, 2) for k, v in by_group_series.to_dict().items()}
        results['selection_rates'] = rates
        
        # Fairness Score based on Demographic Parity Difference
        disparity = demographic_parity_difference(
            y_true, 
            y_true, 
            sensitive_features=temp_df[protected_col]
        )
        results['fairness_score'] = max(0, 100 - (float(disparity) * 100))
        
        # 3. Benchmark Comparison
        matched_benchmark = None
        for name, bench in benchmarks.items():
            if bench.get('protected_attribute', '').lower() in protected_col.lower():
                matched_benchmark = bench
                matched_benchmark['name'] = name
                break
                
        if matched_benchmark:
            b_disparity = round(matched_benchmark['standard_disparity'] * 100, 2)
            results['benchmark_comparison'] = {
                "name": matched_benchmark['name'],
                "our_disparity": round(float(disparity) * 100, 2),
                "benchmark_disparity": b_disparity,
                "benchmark_fairness_score": 100 - b_disparity
            }
        else:
            results['benchmark_comparison'] = {
                "name": "General Industry Std", 
                "our_disparity": round(float(disparity) * 100, 2), 
                "benchmark_disparity": 10.0,
                "benchmark_fairness_score": 90.0
            }

        # 4. Detailed Explanation
        if rates:
            max_group = max(rates, key=rates.get)
            min_group = min(rates, key=rates.get)
            max_val = rates[max_group]
            min_val = rates[min_group]
            gap = round(max_val - min_val, 1)
            
            # Avoid division by zero
            denom = max(max_val, 0.1)
            prob_ratio = round((1 - (min_val / denom)) * 100, 1)
            
            results['detailed_explanation'] = {
                "attribute": protected_col,
                "percentage": gap,
                "comparison_text": f"Members of the {min_group} group are {prob_ratio}% less likely to receive favorable outcomes than {max_group} members (Gap: {gap}%).",
                "impact": "This systemic disparity presents moderate to high risk of regulatory non-compliance. Historical bias in local data may be propagating through current decision patterns.",
                "recommended_action": "We recommend applying 'Reweighting' to equalize the influence of different demographic segments."
            }

        return results
    except Exception as e:
        # Return a structure that allows the app to show the error
        return {"error": str(e), "fairness_score": 0, "selection_rates": {}, "narrative": f"Error during analysis: {str(e)}"}
