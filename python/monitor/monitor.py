import time
import requests
import threading
from flask import Flask, jsonify
from flask_cors import CORS
import sys
import os
import numpy as np

# Add parent directory to path to import config and utils
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from config import settings
from utils.logger import log_event

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

class Monitor:
    """
    Monitor service that polls servers for health metrics and detects fault trends.
    """
    def __init__(self):
        self.server_statuses = {sid: {"status": "unknown", "metrics": {}} for sid in settings.SERVER_PORTS}
        self.history = {sid: [] for sid in settings.SERVER_PORTS}
        self.max_history = 100
        self.faults = []

        self.app = Flask(__name__)
        CORS(self.app, origins=["https://ai-detection-liart.vercel.app", "http://localhost:3000"])
        self.setup_routes()

    def setup_routes(self):
        """Sets up HTTP API endpoints for the monitor."""
        @self.app.route('/health', methods=['GET'])
        def health():
            return jsonify({"status": "ok", "service": "monitor"}), 200

        @self.app.route('/monitor/status', methods=['GET'])
        def status():
            return jsonify(self.server_statuses)

        @self.app.route('/monitor/history/<server_id>', methods=['GET'])
        def server_history(server_id):
            return jsonify(self.history.get(server_id, []))

        @self.app.route('/monitor/faults', methods=['GET'])
        def get_faults():
            return jsonify(self.faults)

        @self.app.route('/monitor/ready', methods=['GET'])
        def ready():
            """Checks if all servers have enough snapshots for AI prediction."""
            counts = {sid: len(h) for sid, h in self.history.items()}
            min_met = all(count >= 5 for count in counts.values())
            return jsonify({
                "ready": min_met,
                "min_snapshots_met": min_met,
                "snapshot_counts": counts
            })

    def _detect_trends(self, server_id, metrics):
        """Analyzes metric history to detect performance degradation trends."""
        history = self.history[server_id]
        if len(history) < 5:
            return

        # Periodically trigger AI prediction via a side-effect poll
        try:
            requests.get(f"{settings.AI_SERVICE_URL}/predict/{server_id}", timeout=1)
        except Exception:
            pass

        if metrics.get('cpu', 0) > settings.HIGH_LOAD_THRESHOLD:
            self._report_fault(server_id, "high_cpu", f"CPU load {metrics['cpu']} exceeded threshold")

        if metrics.get('memory', 0) > settings.HIGH_LOAD_THRESHOLD:
            self._report_fault(server_id, "high_memory", f"Memory load {metrics['memory']} exceeded threshold")

        latencies = [h.get('latency_ms', 0) for h in history[-10:]]
        if len(latencies) >= 5:
            x = np.arange(len(latencies))
            slope, _ = np.polyfit(x, latencies, 1)
            if slope > 50:
                self._report_fault(server_id, "latency_trend", f"Latency trending upward (slope: {round(slope, 2)})")

        error_rates = [h.get('error_rate', 0) for h in history[-5:]]
        if any(er > 0.05 for er in error_rates):
            self._report_fault(server_id, "error_rate_high", "Error rate exceeded 5%")

    def _report_fault(self, server_id, fault_type, message):
        """Logs and records a detected fault."""
        fault_event = log_event("fault_detected", "monitor", message, server_id=server_id, metadata={"fault_type": fault_type})
        self.faults.append(fault_event)

    def _poll_servers(self):
        """Background loop to poll all servers for health metrics."""
        # Wait for dependencies
        wait_for_service(settings.SERVER1_URL, "Server 1")
        wait_for_service(settings.SERVER2_URL, "Server 2")
        wait_for_service(settings.SERVER3_URL, "Server 3")

        server_urls = {
            "server1": settings.SERVER1_URL,
            "server2": settings.SERVER2_URL,
            "server3": settings.SERVER3_URL
        }

        while True:
            for sid, url in server_urls.items():
                try:
                    response = requests.get(f"{url}/health", timeout=2)
                    if response.status_code == 200:
                        metrics = response.json()
                        self.server_statuses[sid] = {"status": metrics['status'], "metrics": metrics}
                        self.history[sid].append(metrics)
                        if len(self.history[sid]) > self.max_history:
                            self.history[sid].pop(0)
                        self._detect_trends(sid, metrics)
                    else:
                        self.server_statuses[sid]["status"] = "error"
                except Exception:
                    self.server_statuses[sid]["status"] = "down"
            time.sleep(settings.MONITOR_INTERVAL_SECONDS)

    def run(self):
        """Starts the monitor polling thread and uvicorn/flask app."""
        threading.Thread(target=self._poll_servers, daemon=True).start()
        self.app.run(host="0.0.0.0", port=settings.get_port(settings.MONITOR_PORT), debug=False)

if __name__ == "__main__":
    monitor = Monitor()
    monitor.run()
