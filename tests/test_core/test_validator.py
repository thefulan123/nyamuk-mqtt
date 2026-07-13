"""Tests for ConfigValidator."""

import pytest
from nyamuk.core.validator import MosquittoConfig, NyamukConfig


class TestMosquittoConfig:
    """Test Mosquitto configuration validator."""

    def test_default_values(self):
        """Test default configuration values."""
        config = MosquittoConfig()
        
        assert config.listener == 1883
        assert config.allow_anonymous is True
        assert config.persistence is True
        assert config.persistence_location == "/mosquitto/data/"
        assert config.log_dest == "file /mosquitto/log/mosquitto.log"

    def test_valid_port(self):
        """Test valid port number."""
        config = MosquittoConfig(listener=8883)
        assert config.listener == 8883

    def test_invalid_port_low(self):
        """Test invalid low port number."""
        with pytest.raises(ValueError):
            MosquittoConfig(listener=0)

    def test_invalid_port_high(self):
        """Test invalid high port number."""
        with pytest.raises(ValueError):
            MosquittoConfig(listener=99999)

    def test_valid_inflight_messages(self):
        """Test valid max inflight messages."""
        config = MosquittoConfig(max_inflight_messages=50)
        assert config.max_inflight_messages == 50

    def test_unlimited_inflight_messages(self):
        """Test unlimited inflight messages (-1)."""
        config = MosquittoConfig(max_inflight_messages=-1)
        assert config.max_inflight_messages == -1

    def test_invalid_inflight_messages(self):
        """Test invalid max inflight messages."""
        with pytest.raises(ValueError):
            MosquittoConfig(max_inflight_messages=-2)

    def test_valid_message_size(self):
        """Test valid message size limit."""
        config = MosquittoConfig(message_size_limit=1024)
        assert config.message_size_limit == 1024

    def test_unlimited_message_size(self):
        """Test unlimited message size (0)."""
        config = MosquittoConfig(message_size_limit=0)
        assert config.message_size_limit == 0

    def test_invalid_message_size(self):
        """Test invalid message size limit."""
        with pytest.raises(ValueError):
            MosquittoConfig(message_size_limit=-1)


class TestNyamukConfig:
    """Test Nyamuk application configuration."""

    def test_default_values(self):
        """Test default configuration values."""
        config = NyamukConfig()
        
        assert config.mqtt_broker == "localhost"
        assert config.mqtt_port == 1883
        assert config.topic_prefix == "nyamuk"
        assert config.web_port == 8080
        assert config.web_admin_user == "admin"
        assert config.web_admin_pass == "nyamuk123"

    def test_valid_topic_prefix(self):
        """Test valid topic prefix."""
        config = NyamukConfig(topic_prefix="myiot")
        assert config.topic_prefix == "myiot"

    def test_invalid_topic_prefix(self):
        """Test invalid topic prefix with slash."""
        with pytest.raises(ValueError):
            NyamukConfig(topic_prefix="my/iot")

    def test_valid_web_port(self):
        """Test valid web port."""
        config = NyamukConfig(web_port=9090)
        assert config.web_port == 9090

    def test_invalid_web_port(self):
        """Test invalid web port."""
        with pytest.raises(ValueError):
            NyamukConfig(web_port=99999)

    def test_valid_mqtt_port(self):
        """Test valid MQTT port."""
        config = NyamukConfig(mqtt_port=8883)
        assert config.mqtt_port == 8883

    def test_invalid_mqtt_port(self):
        """Test invalid MQTT port."""
        with pytest.raises(ValueError):
            NyamukConfig(mqtt_port=0)
