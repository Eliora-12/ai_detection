from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import joblib
import os
import sys
import numpy as np
import requests

# Add parent directory to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from ai.features import extract_features
from config.settings import AI_SERVICE_PORT, MONITOR_PORT
from utils.logger import log_event

app = FastAPI()

MODEL_DIR = os.path.join(os.path.dirname(__file__), 'model')
ANOMALY_MODEL_PATH = os.path.join(MODEL_DIR, 'anomaly_model.pkl')
CLASSIFIER_MODEL_PATH = os.path.join(MODEL_DIR, 'fault_classifier.pkl')

try:
    iso_forest = joblib.load(ANOMALY_MODEL_PATH)
    classifier = joblib.load(CLASSIFIER_MODEL_PATH)
except:
    iso_forest = None
    classifier = None

prediction_history = []

class PredictRequest(BaseModel):
    server_id: str
    metrics: list

@app.post("/predict")
def predict_manual(request: PredictRequest):
    server_id = request.server_id
    metrics = request.metrics
    if not iso_forest or not classifier:
        raise HTTPException(status_code=503, detail="Models not trained")
    feat = extract_features(metrics)
    if not feat: return {"error": "Not enough data"}
    vector = np.array([feat[k] for k in sorted(feat.keys())]).reshape(1, -1)
    is_anomaly = iso_forest.predict(vector)[0] == -1
    fault_type = classifier.predict(vector)[0]
    probabilities = classifier.predict_proba(vector)[0]
    class_idx = list(classifier.classes_).index(fault_type)
    confidence = float(probabilities[class_idx])
    recommended_action = "none"
    if fault_type == "memory_leak" or fault_type == "cpu_spike": recommended_action = "restart"
    elif fault_type == "network_degradation": recommended_action = "reroute"
    explanation = f"Detected {fault_type} pattern with {round(confidence*100, 1)}% confidence."
    clean_feat = {k: (float(v) if isinstance(v, (np.float64, np.int64)) else v) for k, v in feat.items()}
    result = {
        "server_id": server_id, "is_anomaly": bool(is_anomaly),
        "fault_probability": float(confidence) if fault_type != "healthy" else 1 - float(confidence),
        "fault_type": str(fault_type), "recommended_action": recommended_action,
        "confidence": float(confidence), "feature_importances": clean_feat, "explanation": explanation
    }
    prediction_history.append(result)
    log_event("fault_predicted", "ai", explanation, server_id=server_id, metadata=result)
    return result

@app.get("/predict/{server_id}")
def predict_server(server_id: str):
    try:
        response = requests.get(f"http://localhost:{MONITOR_PORT}/monitor/history/{server_id}")
        if response.status_code == 200:
            return predict_manual(PredictRequest(server_id=server_id, metrics=response.json()))
    except: pass
    raise HTTPException(status_code=404)

@app.get("/predictions/history")
def get_history(): return prediction_history

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=AI_SERVICE_PORT)
