"""Config Generator - Generate Mosquitto configuration files."""

from typing import Optional


class ConfigGenerator:
    """Generate Mosquitto configuration files."""

    def generate(
        self,
        port: int = 1883,
        allow_anonymous: bool = False,
        persistence: bool = True,
        persistence_location: str = "/mosquitto/data/",
        log_dest: str = "file /mosquitto/log/mosquitto.log",
        log_type: str = "all",
        max_connections: int = -1,
        max_inflight_messages: int = 20,
        max_queued_messages: int = 1000,
        message_size_limit: int = 0,
        password_file: Optional[str] = None,
        acl_file: Optional[str] = None,
        cafile: Optional[str] = None,
        certfile: Optional[str] = None,
        keyfile: Optional[str] = None,
    ) -> str:
        """Generate Mosquitto configuration content."""
        lines = []

        # Listener
        lines.append(f"listener {port}")
        lines.append("")

        # Authentication
        if allow_anonymous:
            lines.append("allow_anonymous true")
        else:
            lines.append("allow_anonymous false")

        if password_file:
            lines.append(f"password_file {password_file}")
        lines.append("")

        # Persistence
        if persistence:
            lines.append("persistence true")
            lines.append(f"persistence_location {persistence_location}")
        else:
            lines.append("persistence false")
        lines.append("")

        # Logging
        lines.append(f"log_dest {log_dest}")
        lines.append(f"log_type {log_type}")
        lines.append("")

        # Connection limits
        if max_connections > 0:
            lines.append(f"max_connections {max_connections}")

        if max_inflight_messages != 20:
            lines.append(f"max_inflight_messages {max_inflight_messages}")

        if max_queued_messages != 1000:
            lines.append(f"max_queued_messages {max_queued_messages}")

        if message_size_limit > 0:
            lines.append(f"message_size_limit {message_size_limit}")
        lines.append("")

        # ACL
        if acl_file:
            lines.append(f"acl_file {acl_file}")
            lines.append("")

        # TLS/SSL
        if cafile:
            lines.append(f"cafile {cafile}")
        if certfile:
            lines.append(f"certfile {certfile}")
        if keyfile:
            lines.append(f"keyfile {keyfile}")

        return "\n".join(lines)

    def generate_basic(self, port: int = 1883, password_file: str = None) -> str:
        """Generate basic Mosquitto configuration."""
        return self.generate(
            port=port,
            allow_anonymous=False,
            persistence=True,
            password_file=password_file,
        )

    def generate_secure(
        self,
        port: int = 8883,
        password_file: str = None,
        cafile: str = None,
        certfile: str = None,
        keyfile: str = None,
    ) -> str:
        """Generate secure Mosquitto configuration with TLS."""
        return self.generate(
            port=port,
            allow_anonymous=False,
            persistence=True,
            password_file=password_file,
            cafile=cafile,
            certfile=certfile,
            keyfile=keyfile,
        )

    def generate_permissive(self, port: int = 1883) -> str:
        """Generate permissive configuration (no auth, for testing)."""
        return self.generate(
            port=port,
            allow_anonymous=True,
            persistence=True,
        )
