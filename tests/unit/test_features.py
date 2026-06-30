import pytest
from python.ai.features import extract_features, features_to_vector

def test_extract_features_vector_length():
    mock_history = [{"cpu": 0.1, "memory": 0.2, "latency_ms": 50, "error_rate": 0} for _ in range(5)]
    features = extract_features(mock_history)
    assert features is not None
    assert len(features) == 16
    vector = features_to_vector(features)
    assert vector.shape == (1, 16)

def test_rolling_averages():
    mock_history = [{"cpu": i/10, "memory": 0.2, "latency_ms": 50, "error_rate": 0} for i in range(1, 11)]
    features = extract_features(mock_history)
    assert round(features["cpu_avg_5"], 2) == 0.80

def test_rate_of_change():
    mock_history = [{"cpu": i/10, "memory": 0.2, "latency_ms": 50, "error_rate": 0} for i in range(1, 6)]
    features = extract_features(mock_history)
    assert round(features["cpu_delta"], 2) == 0.1

def test_missing_metrics_handling():
    mock_history = [{"cpu": 0.1} for _ in range(5)]
    features = extract_features(mock_history)
    assert features["memory_latest"] == 0
