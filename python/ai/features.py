import pandas as pd
import numpy as np

def extract_features(metric_history):
    if not metric_history or len(metric_history) < 5:
        return None

    df = pd.DataFrame(metric_history)
    cols = ['cpu', 'memory', 'error_rate', 'latency_ms']
    for col in cols:
        if col not in df.columns:
            df[col] = 0

    features = {}
    for col in cols:
        features[f'{col}_avg_5'] = float(df[col].tail(5).mean())
        if len(df) >= 2:
            features[f'{col}_delta'] = float(df[col].iloc[-1] - df[col].iloc[-2])
        else:
            features[f'{col}_delta'] = 0.0
        features[f'{col}_var_5'] = float(df[col].tail(5).var())

    features['cpu_latest'] = float(df['cpu'].iloc[-1])
    features['memory_latest'] = float(df['memory'].iloc[-1])
    features['latency_latest'] = float(df['latency_ms'].iloc[-1])
    features['error_rate_latest'] = float(df['error_rate'].iloc[-1])

    return features

def features_to_vector(features):
    if features is None:
        return None
    return np.array([features[k] for k in sorted(features.keys())]).reshape(1, -1)
