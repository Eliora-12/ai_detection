import os
import sys
import subprocess
import time
import pytest

@pytest.fixture(scope="session", autouse=True)
def manage_services():
    # Train models first if not present
    if not os.path.exists("python/ai/model/fault_classifier.pkl"):
        subprocess.run([sys.executable, "python/ai/train.py"], env={"PYTHONPATH": os.getcwd()})

    processes = []
    services = [
        "python/servers/server1.py",
        "python/servers/server2.py",
        "python/servers/server3.py",
        "python/monitor/monitor.py",
        "python/ai/predictor.py",
        "python/load_balancer/balancer.py",
        "python/recovery/recovery_manager.py"
    ]

    for service in services:
        p = subprocess.Popen([sys.executable, service], env={"PYTHONPATH": os.getcwd()})
        processes.append(p)

    time.sleep(10) # Startup grace period

    yield

    for p in processes:
        p.terminate()
        p.wait()
