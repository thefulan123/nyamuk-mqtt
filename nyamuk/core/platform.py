"""Cross-platform detection and utilities."""

import os
import platform
import sys
from pathlib import Path


class Platform:
    """Detect and handle platform-specific operations."""

    SYSTEM = platform.system()  # 'Linux', 'Windows', 'Darwin'

    @classmethod
    def get_config_path(cls) -> Path:
        """Get Mosquitto config path based on OS."""
        paths = {
            "Linux": Path("/opt/mosquitto/config"),
            "Darwin": Path("/usr/local/etc/mosquitto"),
            "Windows": Path("C:/ProgramData/mosquitto"),
        }
        return paths.get(cls.SYSTEM, Path("/opt/mosquitto/config"))

    @classmethod
    def get_data_path(cls) -> Path:
        """Get Mosquitto data path based on OS."""
        paths = {
            "Linux": Path("/opt/mosquitto/data"),
            "Darwin": Path("/usr/local/var/lib/mosquitto"),
            "Windows": Path("C:/ProgramData/mosquitto/data"),
        }
        return paths.get(cls.SYSTEM, Path("/opt/mosquitto/data"))

    @classmethod
    def get_log_path(cls) -> Path:
        """Get Mosquitto log path based on OS."""
        paths = {
            "Linux": Path("/opt/mosquitto/log"),
            "Darwin": Path("/usr/local/var/log/mosquitto"),
            "Windows": Path("C:/ProgramData/mosquitto/log"),
        }
        return paths.get(cls.SYSTEM, Path("/opt/mosquitto/log"))

    @classmethod
    def is_root(cls) -> bool:
        """Check if running with admin privileges."""
        if cls.SYSTEM == "Windows":
            try:
                import ctypes

                result: bool = ctypes.windll.shell32.IsUserAnAdmin() != 0  # type: ignore[attr-defined]
                return result
            except Exception:
                return False
        return os.geteuid() == 0

    @classmethod
    def is_windows(cls) -> bool:
        """Check if running on Windows."""
        return cls.SYSTEM == "Windows"

    @classmethod
    def is_linux(cls) -> bool:
        """Check if running on Linux."""
        return cls.SYSTEM == "Linux"

    @classmethod
    def is_macos(cls) -> bool:
        """Check if running on macOS."""
        return cls.SYSTEM == "Darwin"

    @classmethod
    def get_line_ending(cls) -> str:
        """Get platform-appropriate line ending."""
        return "\r\n" if cls.SYSTEM == "Windows" else "\n"

    @classmethod
    def get_python_version(cls) -> tuple:
        """Get Python version as tuple."""
        return sys.version_info[:3]
