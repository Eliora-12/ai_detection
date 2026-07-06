import subprocess
import time
import sys
import os
import signal

# Add python dir to path
sys.path.append(os.path.join(os.getcwd(), 'python'))

processes = []

def start_service(name, path, port, args=None):
    """Starts a python service as a subprocess and waits for its port to be active."""
    print(f"Starting {name:20} on port {port}... ", end="", flush=True)
    env = os.environ.copy()
    env["PYTHONPATH"] = os.path.join(os.getcwd())
    cmd = [sys.executable, path]
    if args:
        cmd.extend(args)
    proc = subprocess.Popen(cmd, env=env, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    processes.append(proc)

    # Wait for port to be active
    ready = False
    for _ in range(10):
        try:
            import socket
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                if s.connect_ex(('localhost', port)) == 0:
                    ready = True
                    break
        except Exception:
            pass
        time.sleep(1)

    if ready:
        print("READY")
    else:
        print("TIMEOUT (Check logs)")
    return proc

def cleanup(signum, frame):
    """Terminates all started processes."""
    print("\nShutting down all services...")
    for proc in processes:
        proc.terminate()
    sys.exit(0)

signal.signal(signal.SIGINT, cleanup)
signal.signal(signal.SIGTERM, cleanup)

if __name__ == "__main__":
    print("AI Detection System Orchestrator")
    print("-------------------------------")

    # Ensure models are trained
    if not os.path.exists("python/ai/model/fault_classifier.pkl"):
        print("Training models...")
        # Since we modified the name inside train.py and it calls train_and_save_models() in main, this is still fine.
        subprocess.run([sys.executable, "python/ai/train.py"], env={"PYTHONPATH": os.getcwd()})

    from python.config.settings import SERVER_PORTS, MONITOR_PORT, AI_SERVICE_PORT, LOAD_BALANCER_PORT, RECOVERY_PORT

    start_service("Server 1", "python/servers/server1.py", SERVER_PORTS["server1"])
    start_service("Server 2", "python/servers/server2.py", SERVER_PORTS["server2"])
    start_service("Server 3", "python/servers/server3.py", SERVER_PORTS["server3"])
    start_service("Monitor", "python/monitor/monitor.py", MONITOR_PORT)
    start_service("AI Predictor", "python/ai/predictor.py", AI_SERVICE_PORT)
    start_service("Load Balancer", "python/load_balancer/balancer.py", LOAD_BALANCER_PORT)
    start_service("Recovery Manager", "python/recovery/recovery_manager.py", RECOVERY_PORT)

    print("-------------------------------")
    print("All services started. Press Ctrl+C to stop.")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        cleanup(None, None)
