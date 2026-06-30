import time, requests, pytest

def test_full_system_recovery():
    """
    End-to-end verification:
    1. Wait for system readiness (handled by conftest/monitor/ready)
    2. Baseline traffic check
    3. Fault injection on Server 2
    4. Monitor detection verification
    5. Autonomous recovery verification
    6. Post-recovery health verification
    """
    # 1. Baseline
    for i in range(5):
        res = requests.post("http://localhost:5000/request", json={"test": "baseline"})
        assert res.status_code == 200

    # 2. Inject Fault
    print("\nInjecting CPU Spike on Server 2...")
    res = requests.post("http://localhost:5002/admin/inject-fault", json={"fault_type": "cpu_spike", "severity": "high"})
    assert res.status_code == 200

    # 3. Wait for Detection (Monitor)
    detected = False
    for _ in range(20):
        res = requests.get("http://localhost:5020/monitor/faults")
        if any(f['server_id'] == 'server2' for f in res.json()):
            detected = True
            break
        time.sleep(2)
    assert detected, "Monitor failed to detect fault on Server 2 within 40s"

    # 4. Wait for Recovery (Success in log)
    recovered = False
    for _ in range(30):
        res = requests.get("http://localhost:5030/recovery/log")
        if any(e['server_id'] == 'server2' and e['outcome'] == 'success' for e in res.json()):
            recovered = True
            break
        time.sleep(2)
    assert recovered, "Recovery Manager failed to heal Server 2 within 60s"

    # 5. Final Health Check
    res = requests.get("http://localhost:5002/health")
    assert res.json()['status'] == 'ok'
