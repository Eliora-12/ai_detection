import os
import json
import datetime
import pytest
from python.utils.logger import log_event, LOG_FILE

def test_log_event_structure():
    if os.path.exists(LOG_FILE):
        os.remove(LOG_FILE)

    event_type = "fault_detected"
    source = "monitor"
    message = "Test message"
    server_id = "server1"
    metadata = {"cpu": 0.9}

    log_entry = log_event(event_type, source, message, server_id, metadata)

    assert log_entry["event_type"] == event_type
    assert log_entry["source"] == source
    assert log_entry["message"] == message
    assert log_entry["server_id"] == server_id
    assert log_entry["metadata"] == metadata
    assert "timestamp" in log_entry

    try:
        datetime.datetime.fromisoformat(log_entry["timestamp"])
    except ValueError:
        pytest.fail("Timestamp is not valid ISO 8601")

def test_log_file_persistence():
    if os.path.exists(LOG_FILE):
        os.remove(LOG_FILE)
    log_event("info", "test", "message 1")
    log_event("info", "test", "message 2")
    assert os.path.exists(LOG_FILE)
    with open(LOG_FILE, 'r') as f:
        logs = json.load(f)
        assert len(logs) == 2

def test_log_corrupt_file_handling():
    os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
    with open(LOG_FILE, 'w') as f:
        f.write("corrupt json")
    log_event("info", "test", "message after corruption")
    with open(LOG_FILE, 'r') as f:
        logs = json.load(f)
        assert len(logs) == 1
