import time
import requests
import threading
import random
from flask import Flask, jsonify, request
import sys
import os

# Add parent directory to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from config.settings import SERVER_PORTS, LOAD_BALANCER_PORT, BALANCER_STRATEGY, AI_SERVICE_PORT, MONITOR_PORT
from utils.logger import log_event

class LoadBalancer:
    def __init__(self):
        self.strategy = BALANCER_STRATEGY
        self.servers = list(SERVER_PORTS.keys())
        self.rr_index = 0
        self.server_stats = {sid: {"requests": 0, "fault_prob": 0.0, "status": "ok"} for sid in self.servers}

        self.app = Flask(__name__)
        self.setup_routes()

    def setup_routes(self):
        @self.app.route('/request', methods=['POST'])
        def handle_request():
            target = self._select_server()
            if not target:
                return jsonify({"error": "No healthy servers available"}), 503
            self.server_stats[target]["requests"] += 1
            return jsonify({"status": "success", "server": target})

        @self.app.route('/balancer/stats', methods=['GET'])
        def stats():
            return jsonify({"strategy": self.strategy, "server_stats": self.server_stats})

        @self.app.route('/balancer/drain/<server_id>', methods=['POST'])
        def drain(server_id):
            if server_id in self.server_stats:
                self.server_stats[server_id]["status"] = "draining"
                return jsonify({"message": f"Server {server_id} draining"})
            return jsonify({"error": "Unknown server"}), 404

        @self.app.route('/balancer/restore/<server_id>', methods=['POST'])
        def restore(server_id):
            if server_id in self.server_stats:
                self.server_stats[server_id]["status"] = "ok"
                return jsonify({"message": f"Server {server_id} restored"})
            return jsonify({"error": "Unknown server"}), 404

    def _select_server(self):
        healthy_servers = [s for s in self.servers if self.server_stats[s]["status"] == "ok"]
        if not healthy_servers:
            return None

        if self.strategy == "round_robin":
            server = healthy_servers[self.rr_index % len(healthy_servers)]
            self.rr_index += 1
            return server

        elif self.strategy == "least_load":
            return min(healthy_servers, key=lambda s: self.server_stats[s]["requests"])

        elif self.strategy == "ai_guided":
            weights = []
            for s in healthy_servers:
                prob = self.server_stats[s].get("fault_prob", 0.0)
                weights.append((1.0 - prob) ** 2 + 0.01)
            return random.choices(healthy_servers, weights=weights, k=1)[0]

        return healthy_servers[0]

    def run(self):
        self.app.run(port=LOAD_BALANCER_PORT, debug=False)

if __name__ == "__main__":
    lb = LoadBalancer()
    lb.run()
