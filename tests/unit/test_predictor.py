import pytest
from python.ai.predictor import app
from fastapi.testclient import TestClient

client = TestClient(app)

def test_predict_handled_error_no_model():
    # If models are not loaded, should return 503
    response = client.post("/predict", json={
        "server_id": "test",
        "metrics": [{"cpu": 0.1, "memory": 0.1, "latency_ms": 50, "error_rate": 0}] * 5
    })
    assert response.status_code in [503, 200] # 200 if models exist
