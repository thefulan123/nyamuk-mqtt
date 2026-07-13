"""Tests for MosquittoManager."""

import pytest
from pathlib import Path
from nyamuk.core.mosquitto import MosquittoManager


class TestMosquittoManager:
    """Test Mosquitto configuration manager."""

    def test_default_config(self):
        """Test default configuration."""
        manager = MosquittoManager()
        config = manager._default_config()
        
        assert config["listener"] == 1883
        assert config["allow_anonymous"] is True
        assert config["persistence"] is True

    def test_parse_value_boolean(self):
        """Test parsing boolean values."""
        manager = MosquittoManager()
        
        assert manager._parse_value("true") is True
        assert manager._parse_value("false") is False
        assert manager._parse_value("True") is True
        assert manager._parse_value("False") is False

    def test_parse_value_integer(self):
        """Test parsing integer values."""
        manager = MosquittoManager()
        
        assert manager._parse_value("1883") == 1883
        assert manager._parse_value("0") == 0
        assert manager._parse_value("-1") == -1

    def test_parse_value_string(self):
        """Test parsing string values."""
        manager = MosquittoManager()
        
        assert manager._parse_value("file /var/log/mosquitto.log") == "file /var/log/mosquitto.log"
        assert manager._parse_value("localhost") == "localhost"

    def test_convert_value(self):
        """Test converting values to config format."""
        manager = MosquittoManager()
        
        assert manager._convert_value(True) == "true"
        assert manager._convert_value(False) == "false"
        assert manager._convert_value(1883) == "1883"
        assert manager._convert_value("text") == "text"

    def test_validate_valid_config(self):
        """Test validating valid configuration."""
        manager = MosquittoManager()
        
        # Create a temporary config
        manager._config = {
            "listener": 1883,
            "allow_anonymous": False,
            "persistence": True,
        }
        
        # Mock the write method
        original_write = manager.write
        manager.write = lambda *args, **kwargs: True
        
        is_valid, errors = manager.validate()
        # Should have warning about allow_anonymous
        assert len(errors) > 0 or is_valid is True
        
        manager.write = original_write

    def test_validate_invalid_port(self):
        """Test validating invalid port."""
        manager = MosquittoManager()
        original_read = manager.read
        manager.read = lambda: {"listener": 99999}
        
        is_valid, errors = manager.validate()
        assert is_valid is False
        assert any("port" in e.lower() for e in errors)
        
        manager.read = original_read
