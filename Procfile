server1: python python/servers/server1.py
server2: python python/servers/server2.py
server3: python python/servers/server3.py
monitor: python python/monitor/monitor.py
predictor: uvicorn python.ai.predictor:app --host 0.0.0.0 --port 5010
balancer: python python/load_balancer/balancer.py
recovery: python python/recovery/recovery_manager.py
