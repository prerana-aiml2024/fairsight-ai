import pandas as pd
import numpy as np

def detect_columns(df):
    """
    Automatically detects potential target and protected columns.
    Returns (target_col, protected_cols_list)
    """
    if df is None or df.empty:
        return None, []

    cols = df.columns.tolist()
    
    # Heuristic for target column
    target_keywords = ['target', 'outcome', 'label', 'status', 'decision', 'hired', 'loan', 'accepted', 'approved', 'prediction']
    potential_targets = [c for c in cols if any(kw in c.lower() for kw in target_keywords)]
    
    # If no keywords, take the last column if it's likely a label (few unique values or numeric)
    if not potential_targets:
        target = cols[-1]
    else:
        target = potential_targets[0]
    
    # Heuristic for protected columns
    protected_keywords = ['gender', 'sex', 'age', 'race', 'ethnicity', 'religion', 'education', 'region', 'nationality', 'marital', 'disability']
    protected = [c for c in cols if any(kw in c.lower() for kw in protected_keywords)]
    
    # Exclude target from protected
    protected = [p for p in protected if p != target]
    
    return target, protected

def calculate_fairness_metrics(df, target_col, protected_col):
    """
    Calculates basic fairness metrics for a given target and protected column.
    """
    temp_df = df.dropna(subset=[target_col, protected_col]).copy()
    
    # Binary conversion for target if needed
    if not pd.api.types.is_numeric_dtype(temp_df[target_col]):
        # Guess favorable outcome: usually 'yes', 'approved', 1, or the most frequent if it's binary
        unique_vals = temp_df[target_col].unique()
        fav_keywords = ['yes', 'approved', 'hired', 'pass', '1', 'success', 'good']
        fav_outcome = None
        for v in unique_vals:
            if str(v).lower() in fav_keywords:
                fav_outcome = v
                break
        if fav_outcome is None:
            fav_outcome = unique_vals[0] # Default to first one
            
        y = (temp_df[target_col] == fav_outcome).astype(int)
    else:
        # If numeric, assume 1 is good, 0 is bad if binary-like, or use mean as threshold
        if temp_df[target_col].nunique() == 2:
            fav_outcome = temp_df[target_col].max()
            y = (temp_df[target_col] == fav_outcome).astype(int)
        else:
            mid = temp_df[target_col].median()
            fav_outcome = f"> {mid}"
            y = (temp_df[target_col] > mid).astype(int)

    A = temp_df[protected_col]
    
    # Rates per group
    rates = y.groupby(A).mean()
    
    max_rate = rates.max()
    min_rate = rates.min()
    disparity = max_rate - min_rate
    
    fairness_score = max(0, 100 - (disparity * 100))
    
    return {
        'score': fairness_score,
        'rates': rates.to_dict(),
        'disparity': disparity,
        'min_group': rates.idxmin(),
        'max_group': rates.idxmax(),
        'fav_outcome': fav_outcome
    }
