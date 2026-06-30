import os
import sys
import json
import time
import requests
import pytest

def test_full_system_recovery():
    # 1. Start is handled by conftest.py

    # 2. Baseline traffic
    for _ in range(10):
        requests.post("http://localhost:5000/request", json={"test": "data"})
        time.sleep(0.1)

    # 3. Force fault on server2
    requests.post("http://localhost:5002/admin/inject-fault", json={
        "fault_type": "cpu_spike",
        "severity": "high"
    })

    # 4. Wait for fault detection
    detected = False
    for _ in range(20):
        res = requests.get("http://localhost:5020/monitor/faults")
        if res.status_code == 200:
            faults = res.json()
            if any(f['server_id'] == 'server2' for f in faults):
                detected = True
                break
        time.sleep(2)
    assert detected, "Fault was not detected by monitor"

    # 5. Wait for recovery success
    recovered = False
    for _ in range(30):
        res = requests.get("http://localhost:5030/recovery/log")
        if res.status_code == 200:
            log = res.json()
            if any(e['server_id'] == 'server2' and e['outcome'] == 'success' for e in log):
                recovered = True
                break
        time.sleep(2)
    assert recovered, "Recovery was not successful"

    # 6. Verify health
    res = requests.get("http://localhost:5002/health")
    assert res.status_code == 200
    assert res.json()['status'] == "ok"
