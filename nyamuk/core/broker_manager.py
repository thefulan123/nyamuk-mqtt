"""Broker Manager - Create, start, stop, delete MQTT brokers."""

import json
import shutil
import subprocess
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional, Tuple

from nyamuk.core.config_generator import ConfigGenerator
from nyamuk.core.port_scanner import PortScanner


@dataclass
class BrokerConfig:
    """Broker configuration data."""

    name: str
    port: int
    password: str
    allow_anonymous: bool = False
    persistence: bool = True
    persistence_location: str = "/mosquitto/data/"
    log_dest: str = "file /mosquitto/log/mosquitto.log"
    max_connections: int = -1
    max_inflight_messages: int = 20
    max_queued_messages: int = 1000
    message_size_limit: int = 0
    created_at: str = ""
    status: str = "stopped"
    container_id: Optional[str] = None


class BrokerManager:
    """Manage single MQTT broker instance."""

    def __init__(self, base_dir: Path = Path("/opt/nyamuk")):
        self.base_dir = base_dir
        self.brokers_dir = base_dir / "brokers"
        self.config_file = base_dir / "config" / "broker.json"
        self.port_scanner = PortScanner()
        self.config_generator = ConfigGenerator()

        # Create directories
        self.brokers_dir.mkdir(parents=True, exist_ok=True)
        self.config_file.parent.mkdir(parents=True, exist_ok=True)

    def get_broker_config(self) -> Optional[BrokerConfig]:
        """Get current broker configuration."""
        if not self.config_file.exists():
            return None

        try:
            with open(self.config_file, encoding="utf-8") as f:
                data = json.load(f)
            return BrokerConfig(**data)
        except Exception:
            return None

    def save_broker_config(self, config: BrokerConfig) -> bool:
        """Save broker configuration."""
        try:
            with open(self.config_file, "w", encoding="utf-8") as f:
                json.dump(asdict(config), f, indent=2)
            return True
        except Exception as e:
            print(f"Error saving config: {e}")
            return False

    def create_broker(
        self, name: str, port: Optional[int] = None, password: str = "", **kwargs
    ) -> Tuple[bool, str]:
        """Create a new broker instance."""
        # Check if broker already exists
        if self.get_broker_config():
            return False, "Broker already exists. Delete it first."

        # Auto-detect port if not specified
        if port is None:
            port = self.port_scanner.find_free_port()
            if port is None:
                return False, "No free ports available"

        # Validate port
        if not self.port_scanner.is_port_free(port):
            return False, f"Port {port} is already in use"

        # Create broker directory
        broker_dir = self.brokers_dir / name
        broker_dir.mkdir(parents=True, exist_ok=True)
        (broker_dir / "data").mkdir(exist_ok=True)

        # Generate password if not provided
        if not password:
            password = self._generate_password()

        # Create config
        config = BrokerConfig(
            name=name, port=port, password=password, created_at=datetime.now().isoformat(), **kwargs
        )

        # Generate mosquitto.conf (always listen on 1883 inside container)
        config_content = self.config_generator.generate(
            port=1883,
            allow_anonymous=config.allow_anonymous,
            persistence=config.persistence,
            persistence_location=config.persistence_location,
            log_dest=config.log_dest,
            max_connections=config.max_connections,
            password_file="/mosquitto/config/passwd",
        )

        config_file = broker_dir / "mosquitto.conf"
        with open(config_file, "w", encoding="utf-8") as f:
            f.write(config_content)

        # Create password file
        self._create_password_file(broker_dir / "passwd", "admin", password)

        # Save config
        if not self.save_broker_config(config):
            return False, "Failed to save broker configuration"

        return True, f"Broker '{name}' created on port {port}"

    def start_broker(self) -> Tuple[bool, str]:
        """Start the broker."""
        config = self.get_broker_config()
        if not config:
            return False, "No broker configured"

        try:
            # Check if already running
            if self._is_container_running():
                return False, "Broker is already running"

            # Run Docker container
            broker_dir = self.brokers_dir / config.name
            cmd = [
                "docker",
                "run",
                "-d",
                "--name",
                f"nyamuk_{config.name}",
                "-p",
                f"{config.port}:1883",
                "-v",
                f"{broker_dir}/mosquitto.conf:/mosquitto/config/mosquitto.conf:ro",
                "-v",
                f"{broker_dir}/passwd:/mosquitto/config/passwd:ro",
                "-v",
                f"{broker_dir}/data:/mosquitto/data",
                "--restart",
                "unless-stopped",
                "eclipse-mosquitto:2",
            ]

            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)

            if result.returncode == 0:
                config.status = "running"
                config.container_id = result.stdout.strip()[:12]
                self.save_broker_config(config)
                return True, f"Broker started on port {config.port}"
            else:
                return False, f"Failed to start broker: {result.stderr}"

        except Exception as e:
            return False, f"Error starting broker: {e}"

    def stop_broker(self) -> Tuple[bool, str]:
        """Stop the broker."""
        config = self.get_broker_config()
        if not config:
            return False, "No broker configured"

        try:
            cmd = ["docker", "stop", f"nyamuk_{config.name}"]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)

            if result.returncode == 0:
                config.status = "stopped"
                config.container_id = None
                self.save_broker_config(config)
                return True, "Broker stopped"
            else:
                return False, f"Failed to stop broker: {result.stderr}"

        except Exception as e:
            return False, f"Error stopping broker: {e}"

    def restart_broker(self) -> Tuple[bool, str]:
        """Restart the broker."""
        config = self.get_broker_config()
        if not config:
            return False, "No broker configured"

        try:
            cmd = ["docker", "restart", f"nyamuk_{config.name}"]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)

            if result.returncode == 0:
                config.status = "running"
                self.save_broker_config(config)
                return True, "Broker restarted"
            else:
                return False, f"Failed to restart broker: {result.stderr}"

        except Exception as e:
            return False, f"Error restarting broker: {e}"

    def delete_broker(self) -> Tuple[bool, str]:
        """Delete the broker and all its data."""
        config = self.get_broker_config()
        if not config:
            return False, "No broker configured"

        try:
            # Stop container if running
            if self._is_container_running():
                self.stop_broker()

            # Remove container
            cmd = ["docker", "rm", f"nyamuk_{config.name}"]
            subprocess.run(cmd, capture_output=True, text=True, timeout=30)

            # Remove broker directory
            broker_dir = self.brokers_dir / config.name
            if broker_dir.exists():
                shutil.rmtree(broker_dir)

            # Remove config file
            if self.config_file.exists():
                self.config_file.unlink()

            return True, f"Broker '{config.name}' deleted"

        except Exception as e:
            return False, f"Error deleting broker: {e}"

    def get_status(self) -> Dict[str, Any]:
        """Get broker status."""
        config = self.get_broker_config()
        if not config:
            return {"status": "not_configured"}

        is_running = self._is_container_running()
        config.status = "running" if is_running else "stopped"
        self.save_broker_config(config)

        return {
            "name": config.name,
            "status": config.status,
            "port": config.port,
            "created_at": config.created_at,
            "container_id": config.container_id,
        }

    def get_connection_info(self) -> Dict[str, str]:
        """Get connection information for clients."""
        config = self.get_broker_config()
        if not config:
            return {}

        return {
            "broker": f"{self._get_host_ip()}:{config.port}",
            "port": str(config.port),
            "username": "admin",
            "password": config.password,
            "topic_prefix": "nyamuk",
        }

    def _is_container_running(self) -> bool:
        """Check if Docker container is running."""
        config = self.get_broker_config()
        if not config:
            return False

        try:
            cmd = ["docker", "ps", "-q", "-f", f"name=nyamuk_{config.name}"]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
            return bool(result.stdout.strip())
        except Exception:
            return False

    def _get_host_ip(self) -> str:
        """Get host IP address."""
        try:
            import socket

            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            return ip
        except Exception:
            return "localhost"

    def _generate_password(self, length: int = 16) -> str:
        """Generate random password."""
        import secrets
        import string

        chars = string.ascii_letters + string.digits
        return "".join(secrets.choice(chars) for _ in range(length))

    def _create_password_file(self, filepath: Path, username: str, password: str):
        """Create Mosquitto password file."""
        try:
            # Use docker to create password file
            cmd = [
                "docker",
                "run",
                "--rm",
                "-v",
                f"{filepath.parent}:/tmp/passwd",
                "eclipse-mosquitto:2",
                "mosquitto_passwd",
                "-c",
                "-b",
                f"/tmp/passwd/{filepath.name}",
                username,
                password,
            ]
            subprocess.run(cmd, capture_output=True, text=True, timeout=30)

            # Fix permissions: mosquitto runs as uid 1883 inside container
            filepath.chmod(0o644)
        except Exception as e:
            print(f"Error creating password file: {e}")
