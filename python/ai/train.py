import json
import os
import pandas as pd
import numpy as np
from sklearn.ensemble import IsolationForest, RandomForestClassifier
import joblib
import sys

# Add parent directory to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from ai.features import extract_features

MODEL_DIR = os.path.join(os.path.dirname(__file__), 'model')
ANOMALY_MODEL_PATH = os.path.join(MODEL_DIR, 'anomaly_model.pkl')
CLASSIFIER_MODEL_PATH = os.path.join(MODEL_DIR, 'fault_classifier.pkl')

def generate_dummy_data():
    data = []
    # Healthy
    for _ in range(50):
        history = [{"cpu": 0.1 + 0.05 * np.random.rand(), "memory": 0.2, "latency_ms": 50, "error_rate": 0, "label": "healthy"} for _ in range(10)]
        data.append(history)
    # Memory leak
    for _ in range(20):
        history = [{"cpu": 0.1, "memory": 0.2 + 0.05 * i, "latency_ms": 50, "error_rate": 0, "label": "memory_leak"} for i in range(10)]
        data.append(history)
    # CPU spike
    for _ in range(20):
        history = [{"cpu": 0.1 if i < 8 else 0.9, "memory": 0.2, "latency_ms": 50 if i < 8 else 500, "error_rate": 0, "label": "cpu_spike"} for i in range(10)]
        data.append(history)
    return data

def train_models():
    os.makedirs(MODEL_DIR, exist_ok=True)
    raw_data = generate_dummy_data()
    feature_sets, labels = [], []
    for history in raw_data:
        feat = extract_features(history)
        if feat:
            feature_sets.append([feat[k] for k in sorted(feat.keys())])
            labels.append(history[-1]['label'])
    X, y = np.array(feature_sets), np.array(labels)
    iso_forest = IsolationForest(contamination=0.2, random_state=42).fit(X)
    joblib.dump(iso_forest, ANOMALY_MODEL_PATH)
    classifier = RandomForestClassifier(n_estimators=100, random_state=42).fit(X, y)
    joblib.dump(classifier, CLASSIFIER_MODEL_PATH)

if __name__ == "__main__":
    train_models()
