import os, pandas as pd, numpy as np, joblib
from python.ai.features import extract_features

def generate_dummy_data():
    """Generates synthetic training data for Isolation Forest and Random Forest."""
    data = []
    # Healthy: Low stable load, zero errors
    for _ in range(100):
        data.append([{"cpu": 0.05 + 0.05*np.random.rand(), "memory": 0.1, "latency_ms": 50, "error_rate": 0, "label": "healthy"}] * 10)
    # Memory leak: memory climbs, error rate starts to rise
    for _ in range(60):
        data.append([{"cpu": 0.1, "memory": 0.1 + 0.09 * i, "latency_ms": 50 + 20 * i, "error_rate": 0.02 * i, "label": "memory_leak"} for i in range(10)])
    # CPU spike: cpu jumps to max, latency spikes, high errors
    for _ in range(60):
        data.append([{"cpu": 0.1 if i < 7 else 0.98, "memory": 0.1, "latency_ms": 50 if i < 7 else 900, "error_rate": 0 if i < 7 else 0.6, "label": "cpu_spike"} for i in range(10)])
    return data

def train_models():
    """Trains anomaly detection and fault classification models."""
    os.makedirs("python/ai/model", exist_ok=True)
    raw_data = generate_dummy_data()
    feature_sets, labels = [], []
    for history in raw_data:
        feat = extract_features(history)
        if feat:
            feature_sets.append([feat[k] for k in sorted(feat.keys())])
            labels.append(history[-1]['label'])
    from sklearn.ensemble import IsolationForest, RandomForestClassifier
    iso_forest = IsolationForest(contamination=0.2, random_state=42).fit(feature_sets)
    joblib.dump(iso_forest, "python/ai/model/anomaly_model.pkl")
    classifier = RandomForestClassifier(n_estimators=100, random_state=42).fit(feature_sets, labels)
    joblib.dump(classifier, "python/ai/model/fault_classifier.pkl")
    print(f"Models trained. Classes: {classifier.classes_}")

if __name__ == "__main__":
    train_models()
