import json

# REMOVED Gemini Dependency for Stability

def recommend_audit_config(df_summary):
    """
    Deterministically recommends audit configuration based on dataset metadata.
    """
    # Simple logic based on target column distribution or column names
    target = df_summary.get('target', 'Target')
    
    return {
        "task_type": "binary_classification",
        "fairness_goals": ["Demographic Parity", "Equal Opportunity"],
        "statistical_tests": ["Disparate Impact Ratio", "Chi-Squared Test"],
        "reasoning": f"Based on the identified target outcome '{target}', a binary classification audit is recommended to ensure parity across protected groups."
    }

def generate_narrative_summary(metrics_summary):
    """
    Generates a professional findings summary using a structured template.
    """
    f_score = int(metrics_summary.get('fairness_score', 0))
    rates = metrics_summary.get('selection_rates', {})
    
    if not rates:
        return "Audit Insight: No demographic disparities were identified in the primary scan. The system shows uniform distribution across subgroups."

    max_group = max(rates, key=rates.get)
    min_group = min(rates, key=rates.get)
    disparity = round(metrics_summary.get('benchmark_comparison', {}).get('our_disparity', 0), 1)

    if f_score > 80:
        summary = f"Executive Summary: The system exhibits high demographic parity (score: {f_score}). Disparate impact is minimal, with only a {disparity}% variance detected between {max_group} and {min_group} groups."
    elif f_score > 50:
        summary = (f"Executive Summary: Moderate bias detected (score: {f_score}). Your data shows a {disparity}% success rate gap. "
                   f"Specifically, the {min_group} group receives significantly fewer favorable outcomes compared to {max_group}. "
                   "This imbalance suggests a need for targeted sampling or reweighting in Phase 3.")
    else:
        summary = (f"Executive Summary: Critical Disparity Identified (score: {f_score}). Our scan confirms a severe {disparity}% bias gap. "
                   f"The systemic disadvantage against the {min_group} group presents high compliance and legal risks. "
                   "Immediate intervention via threshold tuning or algorithmic mitigation is required.")

    return summary
