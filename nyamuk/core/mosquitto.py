"""Mosquitto configuration file parser and manager."""

import re
import shutil
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime

from nyamuk.core.platform import Platform


class MosquittoManager:
    """Parse, modify, and manage mosquitto.conf files."""

    def __init__(self, config_path: Optional[Path] = None):
        self.config_path = config_path or Platform.get_config_path() / "mosquitto.conf"
        self._comments: List[str] = []
        self._config: Dict[str, Any] = {}

    def read(self) -> Dict[str, Any]:
        """Read and parse mosquitto.conf file."""
        if not self.config_path.exists():
            return self._default_config()

        self._config = {}
        self._comments = []

        with open(self.config_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                if line.startswith("#"):
                    self._comments.append(line)
                    continue

                # Parse key value pairs
                parts = line.split(None, 1)
                if len(parts) == 2:
                    key, value = parts
                    self._config[key] = self._parse_value(value)

        return self._config

    def _parse_value(self, value: str) -> Any:
        """Parse config value to appropriate type."""
        if value.lower() == "true":
            return True
        if value.lower() == "false":
            return False
        try:
            return int(value)
        except ValueError:
            try:
                return float(value)
            except ValueError:
                return value

    def _default_config(self) -> Dict[str, Any]:
        """Return default Mosquitto configuration."""
        return {
            "listener": 1883,
            "allow_anonymous": True,
            "persistence": True,
            "persistence_location": "/mosquitto/data/",
            "log_dest": "file /mosquitto/log/mosquitto.log",
        }

    def write(self, config: Dict[str, Any], backup: bool = True) -> bool:
        """Write configuration to mosquitto.conf file."""
        try:
            if backup and self.config_path.exists():
                backup_path = self.config_path.with_suffix(
                    f".conf.{datetime.now().strftime('%Y%m%d_%H%M%S')}.bak"
                )
                shutil.copy2(self.config_path, backup_path)

            self.config_path.parent.mkdir(parents=True, exist_ok=True)

            lines = []
            for key, value in config.items():
                lines.append(f"{key} {self._convert_value(value)}")

            with open(self.config_path, "w", encoding="utf-8") as f:
                f.write("\n".join(lines) + "\n")

            return True
        except Exception as e:
            print(f"Error writing config: {e}")
            return False

    def _convert_value(self, value: Any) -> str:
        """Convert Python value to Mosquitto config format."""
        if isinstance(value, bool):
            return "true" if value else "false"
        return str(value)

    def update(self, key: str, value: Any, backup: bool = True) -> bool:
        """Update a single configuration key."""
        config = self.read()
        config[key] = value
        return self.write(config, backup=backup)

    def get(self, key: str, default: Any = None) -> Any:
        """Get a single configuration value."""
        config = self.read()
        return config.get(key, default)

    def validate(self) -> Tuple[bool, List[str]]:
        """Validate current configuration."""
        errors = []
        config = self.read()

        # Port validation
        listener = config.get("listener", 1883)
        if not isinstance(listener, int) or not (1 <= listener <= 65535):
            errors.append(f"Invalid port: {listener} (must be 1-65535)")

        # Auth warning
        if config.get("allow_anonymous", True):
            errors.append("Warning: Anonymous access enabled")

        # TLS validation
        tls_keys = ["cafile", "certfile", "keyfile"]
        tls_present = [k for k in tls_keys if k in config]
        if tls_present and len(tls_present) < 3:
            errors.append("Warning: Incomplete TLS configuration")

        return len(errors) == 0, errors

    def get_raw_lines(self) -> List[str]:
        """Get raw configuration lines with comments."""
        lines = []
        if self.config_path.exists():
            with open(self.config_path, "r", encoding="utf-8") as f:
                lines = [line.rstrip() for line in f.readlines()]
        return lines

    def backup(self, backup_dir: Optional[Path] = None) -> Optional[Path]:
        """Create a backup of current configuration."""
        if not self.config_path.exists():
            return None

        if backup_dir is None:
            backup_dir = self.config_path.parent / "backups"
        backup_dir.mkdir(parents=True, exist_ok=True)

        backup_name = f"mosquitto.conf.{datetime.now().strftime('%Y%m%d_%H%M%S')}.bak"
        backup_path = backup_dir / backup_name

        shutil.copy2(self.config_path, backup_path)
        return backup_path

    def restore(self, backup_path: Path) -> bool:
        """Restore configuration from backup."""
        if not backup_path.exists():
            print(f"Backup file not found: {backup_path}")
            return False

        try:
            shutil.copy2(backup_path, self.config_path)
            return True
        except Exception as e:
            print(f"Error restoring backup: {e}")
            return False

    def list_backups(self, backup_dir: Optional[Path] = None) -> List[Path]:
        """List available configuration backups."""
        if backup_dir is None:
            backup_dir = self.config_path.parent / "backups"

        if not backup_dir.exists():
            return []

        return sorted(backup_dir.glob("*.bak"), reverse=True)
