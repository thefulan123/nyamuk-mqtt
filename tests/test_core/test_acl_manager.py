"""Tests for ACLManager."""

import pytest
from nyamuk.core.acl_manager import ACLManager, ACLRule


class TestACLRule:
    """Test ACL Rule class."""

    def test_to_string(self):
        """Test converting rule to string."""
        rule = ACLRule(username="esp32", topic="nyamuk/esp32/#", access="readwrite")
        result = rule.to_string()
        
        assert "user esp32" in result
        assert "topic readwrite nyamuk/esp32/#" in result

    def test_from_string(self):
        """Test parsing rule from string."""
        text = "user esp32\ntopic readwrite nyamuk/esp32/#"
        rule = ACLRule.from_string(text)
        
        assert rule is not None
        assert rule.username == "esp32"
        assert rule.topic == "nyamuk/esp32/#"
        assert rule.access == "readwrite"

    def test_from_string_read_only(self):
        """Test parsing read-only rule."""
        text = "user guest\ntopic read nyamuk/public/#"
        rule = ACLRule.from_string(text)
        
        assert rule is not None
        assert rule.access == "read"

    def test_from_string_invalid(self):
        """Test parsing invalid rule."""
        text = "invalid format"
        rule = ACLRule.from_string(text)
        
        assert rule is None


class TestACLManager:
    """Test ACL manager."""

    def test_validate_topic_valid(self):
        """Test valid topic validation."""
        manager = ACLManager()
        
        valid, msg = manager.validate_topic("nyamuk/esp32/sensor")
        assert valid is True
        assert msg == "Valid"

    def test_validate_topic_empty(self):
        """Test empty topic."""
        manager = ACLManager()
        
        valid, msg = manager.validate_topic("")
        assert valid is False
        assert "empty" in msg.lower()

    def test_validate_topic_too_long(self):
        """Test topic too long."""
        manager = ACLManager()
        
        valid, msg = manager.validate_topic("a" * 65536)
        assert valid is False
        assert "long" in msg.lower()

    def test_validate_topic_wildcard(self):
        """Test topic with wildcard."""
        manager = ACLManager()
        
        valid, msg = manager.validate_topic("nyamuk/esp32/#")
        assert valid is True

    def test_get_rule_count(self):
        """Test getting rule count."""
        manager = ACLManager()
        
        # Mock the _run_command method
        original_run = manager._run_command
        manager._run_command = lambda cmd: (0, "user esp32\ntopic readwrite nyamuk/esp32/#\n")
        
        count = manager.get_rule_count()
        assert count == 1
        
        manager._run_command = original_run
