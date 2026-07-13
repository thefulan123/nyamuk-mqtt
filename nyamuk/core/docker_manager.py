"""Docker container management for Mosquitto."""

from typing import Any, Dict, List

import docker
from docker.errors import DockerException, NotFound


class DockerManager:
    """Manage Mosquitto Docker container."""

    def __init__(self, container_name: str = "mosquitto"):
        self.container_name = container_name
        self._client = None

    @property
    def client(self):
        """Lazy init Docker client."""
        if self._client is None:
            try:
                self._client = docker.from_env()
            except DockerException as err:
                raise ConnectionError("Cannot connect to Docker daemon. Is Docker running?") from err
        return self._client

    def get_container(self):
        """Get Mosquitto container."""
        try:
            return self.client.containers.get(self.container_name)
        except NotFound as err:
            raise FileNotFoundError(f"Container '{self.container_name}' not found") from err

    def is_running(self) -> bool:
        """Check if Mosquitto container is running."""
        try:
            container = self.get_container()
            return container.status == "running"
        except (FileNotFoundError, DockerException):
            return False

    def get_status(self) -> Dict[str, Any]:
        """Get container status information."""
        try:
            container = self.get_container()
            container.reload()
            return {
                "name": container.name,
                "status": container.status,
                "image": str(container.image.tags[0]) if container.image.tags else "unknown",
                "created": container.attrs.get("Created", "unknown"),
                "started_at": container.attrs.get("State", {}).get("StartedAt", "unknown"),
                "restart_count": container.attrs.get("RestartCount", 0),
                "ports": container.ports,
                "mounts": [
                    {"source": m["Source"], "destination": m["Destination"]}
                    for m in container.attrs.get("Mounts", [])
                ],
            }
        except FileNotFoundError:
            return {"status": "not_found", "error": f"Container '{self.container_name}' not found"}
        except DockerException as e:
            return {"status": "error", "error": str(e)}

    def start(self) -> bool:
        """Start Mosquitto container."""
        try:
            container = self.get_container()
            container.start()
            return True
        except (FileNotFoundError, DockerException) as e:
            print(f"Error starting container: {e}")
            return False

    def stop(self, timeout: int = 10) -> bool:
        """Stop Mosquitto container."""
        try:
            container = self.get_container()
            container.stop(timeout=timeout)
            return True
        except (FileNotFoundError, DockerException) as e:
            print(f"Error stopping container: {e}")
            return False

    def restart(self, timeout: int = 10) -> bool:
        """Restart Mosquitto container."""
        try:
            container = self.get_container()
            container.restart(timeout=timeout)
            return True
        except (FileNotFoundError, DockerException) as e:
            print(f"Error restarting container: {e}")
            return False

    def exec_command(self, command: str) -> tuple:
        """Execute command inside Mosquitto container."""
        try:
            container = self.get_container()
            result = container.exec_run(command, stream=False)
            return result.exit_code, result.output.decode("utf-8")
        except (FileNotFoundError, DockerException) as e:
            return 1, str(e)

    def get_logs(self, tail: int = 100, follow: bool = False) -> str:
        """Get container logs."""
        try:
            container = self.get_container()
            logs = container.logs(tail=tail, follow=follow, timestamps=True)
            return logs.decode("utf-8")
        except (FileNotFoundError, DockerException) as e:
            return f"Error getting logs: {e}"

    def get_stats(self) -> Dict[str, Any]:
        """Get container resource usage stats."""
        try:
            container = self.get_container()
            stats = container.stats(stream=False)

            # Parse CPU stats
            cpu_delta = stats["cpu_stats"]["cpu_usage"]["total_usage"] - \
                       stats["precpu_stats"]["cpu_usage"]["total_usage"]
            system_delta = stats["cpu_stats"]["system_cpu_usage"] - \
                          stats["precpu_stats"]["system_cpu_usage"]
            cpu_percent = (cpu_delta / system_delta * 100.0) if system_delta > 0 else 0.0

            # Parse memory stats
            memory_usage = stats["memory_stats"].get("usage", 0)
            memory_limit = stats["memory_stats"].get("limit", 0)
            memory_percent = (memory_usage / memory_limit * 100.0) if memory_limit > 0 else 0.0

            return {
                "cpu_percent": round(cpu_percent, 2),
                "memory_usage": memory_usage,
                "memory_limit": memory_limit,
                "memory_percent": round(memory_percent, 2),
                "network_rx": stats.get("networks", {}).get("eth0", {}).get("rx_bytes", 0),
                "network_tx": stats.get("networks", {}).get("eth0", {}).get("tx_bytes", 0),
            }
        except (FileNotFoundError, DockerException) as e:
            return {"error": str(e)}

    def pull_image(self, image: str = "eclipse-mosquitto:2") -> bool:
        """Pull Docker image."""
        try:
            self.client.images.pull(image)
            return True
        except DockerException as e:
            print(f"Error pulling image: {e}")
            return False

    def list_containers(self, all_containers: bool = False) -> List[Dict[str, Any]]:
        """List all containers."""
        try:
            containers = self.client.containers.list(all=all_containers)
            return [
                {
                    "id": c.id[:12],
                    "name": c.name,
                    "status": c.status,
                    "image": str(c.image.tags[0]) if c.image.tags else "unknown",
                }
                for c in containers
            ]
        except DockerException as e:
            return [{"error": str(e)}]
