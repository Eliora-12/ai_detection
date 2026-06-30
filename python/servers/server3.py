"""
Server instance 3: Network Degradation Profile.
"""
from python.servers.base_server import BaseServer
from python.config.settings import SERVER_PORTS

if __name__ == "__main__":
    server = BaseServer("server3", SERVER_PORTS["server3"], fault_type="network_degradation")
    server.run()
