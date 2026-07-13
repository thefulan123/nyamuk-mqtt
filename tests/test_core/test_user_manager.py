"""Tests for UserManager."""

import pytest
from nyamuk.core.user_manager import UserManager


class TestUserManager:
    """Test MQTT user manager."""

    def test_validate_username_valid(self):
        """Test valid username validation."""
        manager = UserManager()
        
        valid, msg = manager.validate_username("esp32_sensor")
        assert valid is True
        assert msg == "Valid"

    def test_validate_username_too_short(self):
        """Test username too short."""
        manager = UserManager()
        
        valid, msg = manager.validate_username("ab")
        assert valid is False
        assert "3 characters" in msg

    def test_validate_username_too_long(self):
        """Test username too long."""
        manager = UserManager()
        
        valid, msg = manager.validate_username("a" * 21)
        assert valid is False
        assert "20 characters" in msg

    def test_validate_username_invalid_chars(self):
        """Test username with invalid characters."""
        manager = UserManager()
        
        valid, msg = manager.validate_username("user name")
        assert valid is False
        assert "letters, numbers, and underscores" in msg

    def test_validate_password_valid(self):
        """Test valid password validation."""
        manager = UserManager()
        
        valid, msg = manager.validate_password("SecurePass123")
        assert valid is True
        assert msg == "Valid"

    def test_validate_password_too_short(self):
        """Test password too short."""
        manager = UserManager()
        
        valid, msg = manager.validate_password("short")
        assert valid is False
        assert "8 characters" in msg

    def test_validate_password_no_letter(self):
        """Test password without letters."""
        manager = UserManager()
        
        valid, msg = manager.validate_password("12345678")
        assert valid is False
        assert "letter" in msg

    def test_validate_password_no_number(self):
        """Test password without numbers."""
        manager = UserManager()
        
        valid, msg = manager.validate_password("NoNumbersHere")
        assert valid is False
        assert "number" in msg

    def test_user_exists(self):
        """Test user exists check."""
        manager = UserManager()
        
        # Mock the _run_command method
        original_run = manager._run_command
        manager._run_command = lambda cmd: (0, "user1:$6$salt$hash\nuser2:$6$salt$hash\n")
        
        assert manager.user_exists("user1") is True
        assert manager.user_exists("user3") is False
        
        manager._run_command = original_run

    def test_list_users(self):
        """Test listing users."""
        manager = UserManager()
        
        # Mock the _run_command method
        original_run = manager._run_command
        manager._run_command = lambda cmd: (0, "user1:$6$salt$hash\nuser2:$6$salt$hash\n")
        
        users = manager.list_users()
        assert users == ["user1", "user2"]
        
        manager._run_command = original_run

    def test_get_user_count(self):
        """Test getting user count."""
        manager = UserManager()
        
        # Mock the _run_command method
        original_run = manager._run_command
        manager._run_command = lambda cmd: (0, "user1:$6$salt$hash\nuser2:$6$salt$hash\n")
        
        count = manager.get_user_count()
        assert count == 2
        
        manager._run_command = original_run
