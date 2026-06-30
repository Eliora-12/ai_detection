import pytest
import os
import json
from python.recovery.recovery_manager import RecoveryManager, RECOVERY_LOG_FILE

@pytest.fixture
def rm():
    if os.path.exists(RECOVERY_LOG_FILE):
        os.remove(RECOVERY_LOG_FILE)
    return RecoveryManager()

def test_alert_fatigue(rm):
    server_id = "server1"
    assert rm._check_alert_fatigue(server_id) == False
    assert rm._check_alert_fatigue(server_id) == False
    assert rm._check_alert_fatigue(server_id) == True

def test_recovery_log_entry(rm):
    entry = {"server_id": "server1", "outcome": "success"}
    rm._save_history(entry)
    assert os.path.exists(RECOVERY_LOG_FILE)
