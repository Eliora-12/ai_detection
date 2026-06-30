from python.servers.base_server import BaseServer
from python.config.settings import SERVER_PORTS

if __name__ == "__main__":
    server = BaseServer("server1", SERVER_PORTS["server1"], fault_type="cpu_spike")
    server.run()
