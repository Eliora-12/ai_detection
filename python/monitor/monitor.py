import time
import requests
import threading
from flask import Flask, jsonify
import sys
import os
import numpy as np

# Add parent directory to path to import config and utils
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from config.settings import SERVER_PORTS, MONITOR_INTERVAL_SECONDS, MONITOR_PORT, HIGH_LOAD_THRESHOLD
from utils.logger import log_event

class Monitor:
    def __init__(self):
        self.server_statuses = {sid: {"status": "unknown", "metrics": {}} for sid in SERVER_PORTS}
        self.history = {sid: [] for sid in SERVER_PORTS}
        self.max_history = 100
        self.faults = []

        self.app = Flask(__name__)
        self.setup_routes()

    def setup_routes(self):
        @self.app.route('/monitor/status', methods=['GET'])
        def status():
            return jsonify(self.server_statuses)

        @self.app.route('/monitor/history/<server_id>', methods=['GET'])
        def server_history(server_id):
            return jsonify(self.history.get(server_id, []))

        @self.app.route('/monitor/faults', methods=['GET'])
        def get_faults():
            return jsonify(self.faults)

    def _detect_trends(self, server_id, metrics):
        history = self.history[server_id]
        if len(history) < 5:
            return

        if metrics.get('cpu', 0) > HIGH_LOAD_THRESHOLD:
            self._report_fault(server_id, "high_cpu", f"CPU load {metrics['cpu']} exceeded threshold")

        if metrics.get('memory', 0) > HIGH_LOAD_THRESHOLD:
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
        fault_event = log_event("fault_detected", "monitor", message, server_id=server_id, metadata={"fault_type": fault_type})
        self.faults.append(fault_event)

    def _poll_servers(self):
        while True:
            for sid, port in SERVER_PORTS.items():
                try:
                    response = requests.get(f"http://localhost:{port}/health", timeout=2)
                    if response.status_code == 200:
                        metrics = response.json()
                        self.server_statuses[sid] = {"status": metrics['status'], "metrics": metrics}
                        self.history[sid].append(metrics)
                        if len(self.history[sid]) > self.max_history:
                            self.history[sid].pop(0)
                        self._detect_trends(sid, metrics)
                    else:
                        self.server_statuses[sid]["status"] = "error"
                except:
                    self.server_statuses[sid]["status"] = "down"
            time.sleep(MONITOR_INTERVAL_SECONDS)

    def run(self):
        threading.Thread(target=self._poll_servers, daemon=True).start()
        self.app.run(port=MONITOR_PORT, debug=False)

if __name__ == "__main__":
    monitor = Monitor()
    monitor.run()
