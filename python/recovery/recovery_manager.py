import time
import requests
import threading
import json
import os
import sys
import datetime
from flask import Flask, jsonify, request
from flask_cors import CORS

# Add parent directory to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from config import settings
from utils.logger import log_event

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
RECOVERY_LOG_FILE = os.path.join(BASE_DIR, "data", "recovery_log.json")

def wait_for_service(url: str, name: str, retries: int = 10, delay: int = 3):
    """Retry calling a dependency service until it responds or retries are exhausted."""
    for attempt in range(retries):
        try:
            r = requests.get(f"{url}/health", timeout=3)
            if r.status_code == 200:
                print(f"✓ {name} is ready")
                return True
        except Exception:
            pass
        print(f"  Waiting for {name}... (attempt {attempt + 1}/{retries})")
        time.sleep(delay)
    print(f"✗ {name} did not become ready — continuing anyway")
    return False

class RecoveryManager:
    """
    Autonomous recovery orchestrator that monitors AI predictions and triggers
    healing actions like server restarts.
    """
    def __init__(self):
        self.active_recoveries = set()
        self.recovery_history = []
        self.alert_counts = {}
        self.paused = False
        self._load_history()

    def _load_history(self):
        """Loads recovery history from flat JSON file."""
        os.makedirs(os.path.dirname(RECOVERY_LOG_FILE), exist_ok=True)
        if not os.path.exists(RECOVERY_LOG_FILE):
            with open(RECOVERY_LOG_FILE, "w") as f:
                f.write("[]")

        if os.path.exists(RECOVERY_LOG_FILE):
            try:
                with open(RECOVERY_LOG_FILE, 'r') as f:
                    self.recovery_history = json.load(f)
            except Exception:
                self.recovery_history = []

    def _save_history(self, entry):
        """Saves a new recovery event to the history log."""
        self.recovery_history.append(entry)
        os.makedirs(os.path.dirname(RECOVERY_LOG_FILE), exist_ok=True)
        with open(RECOVERY_LOG_FILE, 'w') as f:
            json.dump(self.recovery_history, f, indent=2)

    def _check_alert_fatigue(self, server_id):
        """Prevents infinite recovery loops by detecting rapid successive recovery attempts."""
        now = time.time()
        if server_id not in self.alert_counts:
            self.alert_counts[server_id] = []
        self.alert_counts[server_id] = [t for t in self.alert_counts[server_id] if now - t < 60]
        self.alert_counts[server_id].append(now)
        if len(self.alert_counts[server_id]) >= 3:
            return True
        return False

    def execute_recovery(self, server_id, action, confidence, fault_type, auto=True):
        """Triggers a recovery action (restart, reroute, etc.) for a specific server."""
        if server_id in self.active_recoveries:
            return {"status": "already_recovering"}
        if auto and self._check_alert_fatigue(server_id):
            return {"status": "paused"}

        self.active_recoveries.add(server_id)

        server_urls = {
            "server1": settings.SERVER1_URL,
            "server2": settings.SERVER2_URL,
            "server3": settings.SERVER3_URL
        }

        def run_action():
            try:
                time.sleep(1) # Simulate prep time
                requests.post(f"{server_urls[server_id]}/admin/restart")
                time.sleep(5) # Wait for restart
                self._save_history({
                    "timestamp": datetime.datetime.now().isoformat(),
                    "server_id": server_id,
                    "trigger": "ai_prediction" if auto else "manual",
                    "fault_type": fault_type,
                    "action_taken": action,
                    "action_confidence": confidence,
                    "outcome": "success",
                    "recovery_time_ms": 6000,
                    "auto_or_manual": "auto" if auto else "manual"
                })
            finally:
                if server_id in self.active_recoveries:
                    self.active_recoveries.remove(server_id)

        threading.Thread(target=run_action).start()
        return {"status": "triggered"}

    def poll_predictions(self):
        """Continuously polls the AI service for high-confidence fault predictions."""
        wait_for_service(settings.AI_SERVICE_URL, "AI Predictor")
        while True:
            try:
                response = requests.get(f"{settings.AI_SERVICE_URL}/predictions/history", timeout=2)
                if response.status_code == 200:
                    for pred in response.json():
                        if (pred['confidence'] >= settings.AI_CONFIDENCE_AUTO_RECOVER and
                            pred['recommended_action'] != "none" and
                            pred['server_id'] not in self.active_recoveries):
                            # Simple deduplication by not acting if we already have a success for this server recently
                            if not any(e['server_id'] == pred['server_id'] and
                                       (datetime.datetime.now() - datetime.datetime.fromisoformat(e['timestamp'])).total_seconds() < 30
                                       for e in self.recovery_history):
                                self.execute_recovery(pred['server_id'], pred['recommended_action'],
                                                       pred['confidence'], pred['fault_type'])
            except Exception:
                pass
            time.sleep(5)

    def run_api(self):
        """Starts the recovery manager HTTP API."""
        app = Flask(__name__)
        CORS(app, origins=["https://ai-detection-liart.vercel.app", "http://localhost:3000"])

        @app.route('/health', methods=['GET'])
        def health():
            return jsonify({"status": "ok", "service": "recovery-manager"}), 200

        @app.route('/recovery/log')
        def get_log(): return jsonify(self.recovery_history)

        @app.route('/recovery/trigger', methods=['POST'])
        def trigger():
            data = request.json
            return jsonify(self.execute_recovery(data['server_id'], data['action'], 1.0, "manual", auto=False))

        app.run(host="0.0.0.0", port=settings.get_port(settings.RECOVERY_PORT), debug=False)

if __name__ == "__main__":
    rm = RecoveryManager()
    threading.Thread(target=rm.poll_predictions, daemon=True).start()
    rm.run_api()
