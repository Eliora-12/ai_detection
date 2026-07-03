import time
import random
import threading
from flask import Flask, jsonify, request
import sys
import os
import datetime

# Add parent directory to path to import config and utils
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from config import settings
from utils.logger import log_event

class BaseServer:
    def __init__(self, server_id, port, fault_type="none"):
        self.server_id = server_id
        self.port = port
        self.fault_type = fault_type
        self.status = "ok"
        self.cpu_load = 0.1
        self.memory_load = 0.1
        self.request_count = 0
        self.error_count = 0
        self.uptime_start = time.time()
        self.metric_history = []
        self.max_history = 50

        self.app = Flask(__name__)
        self.setup_routes()

        # Start background metrics simulation
        threading.Thread(target=self._simulate_metrics, daemon=True).start()

    def setup_routes(self):
        @self.app.route('/health', methods=['GET'])
        def health():
            return jsonify({
                "server_id": self.server_id,
                "status": self.status,
                "cpu": round(self.cpu_load, 2),
                "memory": round(self.memory_load, 2),
                "latency_ms": self._get_simulated_latency(),
                "error_rate": round(self.error_count / max(1, self.request_count), 2),
                "request_count": self.request_count,
                "uptime_seconds": int(time.time() - self.uptime_start)
            })

        @self.app.route('/process', methods=['POST'])
        def process():
            self.request_count += 1
            if self.status == "down":
                return jsonify({"error": "Server Down"}), 503

            # Simulate processing time
            time.sleep(self._get_simulated_latency() / 1000)
            return jsonify({"status": "success", "server": self.server_id})

        @self.app.route('/admin/restart', methods=['POST'])
        def restart():
            self.status = "restarting"
            def do_restart():
                time.sleep(3)
                self.cpu_load = 0.1
                self.memory_load = 0.1
                self.error_count = 0
                self.request_count = 0
                self.uptime_start = time.time()
                self.status = "ok"
            threading.Thread(target=do_restart).start()
            return jsonify({"message": "Restarting..."})

        @self.app.route('/admin/drain', methods=['POST'])
        def drain():
            self.status = "draining"
            return jsonify({"message": "Draining..."})

        @self.app.route('/metrics/history', methods=['GET'])
        def metrics_history():
            return jsonify(self.metric_history)

        @self.app.route('/admin/inject-fault', methods=['POST'])
        def inject_fault():
            data = request.json
            self.fault_type = data.get('fault_type', 'none')
            severity = data.get('severity', 'low')
            if severity == 'high':
                self.cpu_load = 0.95
                self.error_count += 50
            log_event("alert", self.server_id, f"Fault injected: {self.fault_type}", metadata=data)
            return jsonify({"message": f"Fault {self.fault_type} injected"})

    def _get_simulated_latency(self):
        base_latency = 50
        if self.cpu_load > settings.HIGH_LOAD_THRESHOLD:
            base_latency += (self.cpu_load - settings.HIGH_LOAD_THRESHOLD) * 1000
        return int(base_latency + random.uniform(0, 20))

    def _simulate_metrics(self):
        while True:
            if self.status == "ok":
                self.cpu_load = max(0.05, min(0.95, self.cpu_load + random.uniform(-0.02, 0.03)))
                self.memory_load = max(0.05, min(0.95, self.memory_load + random.uniform(-0.01, 0.02)))

            snapshot = {
                "timestamp": datetime.datetime.now().isoformat(),
                "cpu": round(self.cpu_load, 2),
                "memory": round(self.memory_load, 2),
                "error_rate": round(self.error_count / max(1, self.request_count), 2),
                "status": self.status,
                "latency_ms": self._get_simulated_latency()
            }
            self.metric_history.append(snapshot)
            if len(self.metric_history) > self.max_history:
                self.metric_history.pop(0)
            time.sleep(2)

    def run(self):
        self.app.run(host="0.0.0.0", port=settings.get_port(self.port), debug=False, threaded=True)
