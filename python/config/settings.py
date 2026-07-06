"""
Central configuration settings for the AI Detection system.
Defines ports, thresholds, and intervals for all microservices.
"""
import os

# Inter-service URLs — set these as environment variables in Railway
MONITOR_URL = os.getenv("MONITOR_URL", "http://localhost:5020")
AI_SERVICE_URL = os.getenv("AI_SERVICE_URL", "http://localhost:5010")
LOAD_BALANCER_URL = os.getenv("LOAD_BALANCER_URL", "http://localhost:5000")
RECOVERY_URL = os.getenv("RECOVERY_URL", "http://localhost:5030")
SERVER1_URL = os.getenv("SERVER1_URL", "http://localhost:5001")
SERVER2_URL = os.getenv("SERVER2_URL", "http://localhost:5002")
SERVER3_URL = os.getenv("SERVER3_URL", "http://localhost:5003")

# Port — Railway injects $PORT automatically; fall back to service default
def get_port(default: int) -> int:
    return int(os.getenv("PORT", default))

SERVER_PORTS = {"server1": 5001, "server2": 5002, "server3": 5003}
MONITOR_INTERVAL_SECONDS = 5
FAULT_PROBABILITY_RANGE = (0.0, 0.15)   # per-request random fault chance
HIGH_LOAD_THRESHOLD = 0.80
AI_CONFIDENCE_AUTO_RECOVER = 0.70       # above this → auto-recover
AI_CONFIDENCE_ALERT_ONLY = 0.60         # between this and above → alert only
BALANCER_STRATEGY = "ai_guided"         # round_robin | least_load | ai_guided
LOAD_BALANCER_PORT = 5000
AI_SERVICE_PORT = 5010
MONITOR_PORT = 5020
RECOVERY_PORT = 5030
