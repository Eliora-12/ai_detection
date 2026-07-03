import time
import requests
import threading
import random
from flask import Flask, jsonify, request
from flask_cors import CORS
import sys
import os

# Add parent directory to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from config import settings
from utils.logger import log_event

class LoadBalancer:
    """
    Load Balancer that routes traffic between servers using various strategies.
    Supports AI-guided routing for predictive traffic draining.
    """
    def __init__(self):
        self.strategy = settings.BALANCER_STRATEGY
        self.servers = list(settings.SERVER_PORTS.keys())
        self.rr_index = 0
        self.server_stats = {sid: {"requests": 0, "fault_prob": 0.0, "status": "ok"} for sid in self.servers}

        self.app = Flask(__name__)
        CORS(self.app, origins=["https://ai-detection-liart.vercel.app", "http://localhost:3000"])
        self.setup_routes()

    def setup_routes(self):
        """Sets up HTTP API endpoints for the load balancer."""
        @self.app.route('/health', methods=['GET'])
        def health():
            return jsonify({"status": "ok", "service": "load-balancer"}), 200

        @self.app.route('/request', methods=['POST'])
        def handle_request():
            """Proxies an incoming request to a selected backend server."""
            target = self._select_server()
            if not target:
                return jsonify({"error": "No healthy servers available"}), 503
            self.server_stats[target]["requests"] += 1
            return jsonify({"status": "success", "server": target})

        @self.app.route('/balancer/stats', methods=['GET'])
        def stats():
            """Returns current load balancer statistics and strategy."""
            return jsonify({"strategy": self.strategy, "server_stats": self.server_stats})

        @self.app.route('/balancer/drain/<server_id>', methods=['POST'])
        def drain(server_id):
            """Drains traffic from a specific server."""
            if server_id in self.server_stats:
                self.server_stats[server_id]["status"] = "draining"
                return jsonify({"message": f"Server {server_id} draining"})
            return jsonify({"error": "Unknown server"}), 404

        @self.app.route('/balancer/restore/<server_id>', methods=['POST'])
        def restore(server_id):
            """Restores a server back into the routing rotation."""
            if server_id in self.server_stats:
                self.server_stats[server_id]["status"] = "ok"
                return jsonify({"message": f"Server {server_id} restored"})
            return jsonify({"error": "Unknown server"}), 404

    def _select_server(self):
        """Selects a backend server based on the active strategy."""
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
        """Starts the load balancer HTTP API."""
        self.app.run(host="0.0.0.0", port=settings.get_port(settings.LOAD_BALANCER_PORT), debug=False)

if __name__ == "__main__":
    lb = LoadBalancer()
    lb.run()
