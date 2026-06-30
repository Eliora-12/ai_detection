"""
Server instance 2: Memory Leak Profile.
"""
from python.servers.base_server import BaseServer
from python.config.settings import SERVER_PORTS

if __name__ == "__main__":
    server = BaseServer("server2", SERVER_PORTS["server2"], fault_type="memory_leak")
    server.run()
