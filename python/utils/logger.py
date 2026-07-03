import json
import datetime
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
LOG_FILE = os.path.join(BASE_DIR, "data", "logs.json")

def log_event(event_type, source, message, server_id=None, metadata=None):
    """
    Logs an event in structured JSON format.
    """
    log_entry = {
        "timestamp": datetime.datetime.now().isoformat(),
        "event_type": event_type,
        "source": source,
        "server_id": server_id,
        "message": message,
        "metadata": metadata or {}
    }

    os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
    if not os.path.exists(LOG_FILE):
        with open(LOG_FILE, "w") as f:
            f.write("[]")

    logs = []
    if os.path.exists(LOG_FILE):
        try:
            with open(LOG_FILE, 'r') as f:
                logs = json.load(f)
        except (json.JSONDecodeError, IOError):
            logs = []

    logs.append(log_entry)

    if len(logs) > 1000:
        logs = logs[-1000:]

    with open(LOG_FILE, 'w') as f:
        json.dump(logs, f, indent=2)

    return log_entry
