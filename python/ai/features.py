import pandas as pd
import numpy as np

def extract_features(metric_history):
    """
    Converts raw metric history (list of health snapshots) into a feature vector.
    Calculates rolling averages, deltas, and variance for key metrics.
    """
    if not metric_history or len(metric_history) < 5:
        return None

    df = pd.DataFrame(metric_history)

    # Target columns
    cols = ['cpu', 'memory', 'error_rate', 'latency_ms']
    # Ensure columns exist, if not fill with 0
    for col in cols:
        if col not in df.columns:
            df[col] = 0

    features = {}

    for col in cols:
        # Rolling averages
        features[f'{col}_avg_5'] = float(df[col].tail(5).mean())
        # Rate of change (delta)
        if len(df) >= 2:
            features[f'{col}_delta'] = float(df[col].iloc[-1] - df[col].iloc[-2])
        else:
            features[f'{col}_delta'] = 0.0
        # Variance
        features[f'{col}_var_5'] = float(df[col].tail(5).var())

    # Latest values
    features['cpu_latest'] = float(df['cpu'].iloc[-1])
    features['memory_latest'] = float(df['memory'].iloc[-1])
    features['latency_latest'] = float(df['latency_ms'].iloc[-1])
    features['error_rate_latest'] = float(df['error_rate'].iloc[-1])

    return features

def features_to_vector(features):
    """
    Converts a feature dictionary into a sorted numpy vector for prediction.
    """
    if features is None:
        return None
    # Sort keys to ensure consistent vector order
    return np.array([features[k] for k in sorted(features.keys())]).reshape(1, -1)
