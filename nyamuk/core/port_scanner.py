"""Port Scanner - Find free ports for MQTT brokers."""

import socket
from typing import List, Optional


class PortScanner:
    """Scan and find free ports."""

    # Default MQTT port range
    MQTT_PORT_START = 1883
    MQTT_PORT_END = 1900

    # Well-known ports to avoid
    RESERVED_PORTS = {
        22, 80, 443, 3306, 5432, 6379, 8080, 8443, 8888, 9090, 27017
    }

    def __init__(self, port_range: tuple = (MQTT_PORT_START, MQTT_PORT_END)):
        self.port_range = port_range

    def is_port_free(self, port: int) -> bool:
        """Check if a specific port is free."""
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(1)
                result = s.connect_ex(('localhost', port))
                return result != 0  # Connection refused = port is free
        except Exception:
            return False

    def is_port_reserved(self, port: int) -> bool:
        """Check if port is in reserved list."""
        return port in self.RESERVED_PORTS

    def find_free_port(self) -> Optional[int]:
        """Find first free port in range."""
        for port in range(self.port_range[0], self.port_range[1] + 1):
            if not self.is_port_reserved(port) and self.is_port_free(port):
                return port
        return None

    def find_all_free_ports(self) -> List[int]:
        """Find all free ports in range."""
        free_ports = []
        for port in range(self.port_range[0], self.port_range[1] + 1):
            if not self.is_port_reserved(port) and self.is_port_free(port):
                free_ports.append(port)
        return free_ports

    def suggest_port(self) -> int:
        """Suggest a port, preferring 1883 if free."""
        # Try default MQTT port first
        if self.is_port_free(self.MQTT_PORT_START):
            return self.MQTT_PORT_START

        # Find next free port
        free_port = self.find_free_port()
        if free_port:
            return free_port

        # Fallback to 1883 (will fail if occupied)
        return self.MQTT_PORT_START

    def get_port_info(self, port: int) -> dict:
        """Get information about a port."""
        return {
            "port": port,
            "is_free": self.is_port_free(port),
            "is_reserved": self.is_port_reserved(port),
            "is_mqtt_default": port == self.MQTT_PORT_START,
        }
