"""Tests for Platform utilities."""

import platform

from nyamuk.core.platform import Platform


class TestPlatform:
    """Test platform detection utilities."""

    def test_system_detection(self):
        """Test system detection."""
        system = Platform.SYSTEM
        assert system in ["Linux", "Windows", "Darwin"]

    def test_get_config_path(self):
        """Test getting config path."""
        path = Platform.get_config_path()
        assert path is not None
        assert "mosquitto" in str(path).lower() or "config" in str(path).lower()

    def test_get_data_path(self):
        """Test getting data path."""
        path = Platform.get_data_path()
        assert path is not None
        assert "mosquitto" in str(path).lower() or "data" in str(path).lower()

    def test_get_log_path(self):
        """Test getting log path."""
        path = Platform.get_log_path()
        assert path is not None
        assert "mosquitto" in str(path).lower() or "log" in str(path).lower()

    def test_is_windows(self):
        """Test Windows detection."""
        result = Platform.is_windows()
        assert isinstance(result, bool)
        assert result == (platform.system() == "Windows")

    def test_is_linux(self):
        """Test Linux detection."""
        result = Platform.is_linux()
        assert isinstance(result, bool)
        assert result == (platform.system() == "Linux")

    def test_is_macos(self):
        """Test macOS detection."""
        result = Platform.is_macos()
        assert isinstance(result, bool)
        assert result == (platform.system() == "Darwin")

    def test_get_line_ending(self):
        """Test line ending detection."""
        ending = Platform.get_line_ending()
        assert ending in ["\n", "\r\n"]

    def test_get_python_version(self):
        """Test Python version detection."""
        version = Platform.get_python_version()
        assert isinstance(version, tuple)
        assert len(version) == 3
        assert all(isinstance(v, int) for v in version)
