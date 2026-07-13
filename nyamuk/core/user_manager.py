"""MQTT user management via Docker exec."""

import re
import subprocess
from typing import List, Tuple


class UserManager:
    """Manage Mosquitto MQTT users via mosquitto_passwd."""

    # Username validation: alphanumeric, underscore, 3-20 chars
    USERNAME_PATTERN = re.compile(r"^[a-zA-Z0-9_]{3,20}$")

    def __init__(self, container_name: str = "mosquitto", password_file: str = "/mosquitto/config/passwd"):
        self.container_name = container_name
        self.password_file = password_file

    def _run_command(self, command: str) -> Tuple[int, str]:
        """Execute command in Mosquitto container."""
        try:
            result = subprocess.run(
                ["docker", "exec", self.container_name] + command.split(),
                capture_output=True,
                text=True,
                timeout=30,
            )
            return result.returncode, result.stdout + result.stderr
        except subprocess.TimeoutExpired:
            return 1, "Command timed out"
        except FileNotFoundError:
            return 1, "Docker not found"

    def validate_username(self, username: str) -> Tuple[bool, str]:
        """Validate MQTT username format."""
        if not username:
            return False, "Username cannot be empty"
        if len(username) < 3:
            return False, "Username must be at least 3 characters"
        if len(username) > 20:
            return False, "Username must be at most 20 characters"
        if not self.USERNAME_PATTERN.match(username):
            return False, "Username can only contain letters, numbers, and underscores"
        return True, "Valid"

    def validate_password(self, password: str) -> Tuple[bool, str]:
        """Validate password strength."""
        if not password:
            return False, "Password cannot be empty"
        if len(password) < 8:
            return False, "Password must be at least 8 characters"
        if not any(c.isalpha() for c in password):
            return False, "Password must contain at least one letter"
        if not any(c.isdigit() for c in password):
            return False, "Password must contain at least one number"
        return True, "Valid"

    def add_user(self, username: str, password: str) -> Tuple[bool, str]:
        """Add a new MQTT user."""
        valid, msg = self.validate_username(username)
        if not valid:
            return False, msg

        valid, msg = self.validate_password(password)
        if not valid:
            return False, msg

        # Use -b flag for batch mode (no interactive prompt)
        cmd = f"mosquitto_passwd -b -c {self.password_file} {username} {password}"
        exit_code, output = self._run_command(cmd)

        if exit_code == 0:
            return True, f"User '{username}' added successfully"
        else:
            return False, f"Failed to add user: {output}"

    def delete_user(self, username: str) -> Tuple[bool, str]:
        """Delete an MQTT user."""
        if not username:
            return False, "Username cannot be empty"

        cmd = f"mosquitto_passwd -b -D {self.password_file} {username}"
        exit_code, output = self._run_command(cmd)

        if exit_code == 0:
            return True, f"User '{username}' deleted successfully"
        else:
            return False, f"Failed to delete user: {output}"

    def change_password(self, username: str, new_password: str) -> Tuple[bool, str]:
        """Change user password."""
        if not username:
            return False, "Username cannot be empty"

        valid, msg = self.validate_password(new_password)
        if not valid:
            return False, msg

        cmd = f"mosquitto_passwd -b {self.password_file} {username} {new_password}"
        exit_code, output = self._run_command(cmd)

        if exit_code == 0:
            return True, f"Password for '{username}' changed successfully"
        else:
            return False, f"Failed to change password: {output}"

    def list_users(self) -> List[str]:
        """List all MQTT users from password file."""
        cmd = f"cat {self.password_file}"
        exit_code, output = self._run_command(cmd)

        if exit_code != 0:
            return []

        users = []
        for line in output.strip().split("\n"):
            line = line.strip()
            if line and not line.startswith("#") and ":" in line:
                username = line.split(":")[0]
                users.append(username)

        return users

    def user_exists(self, username: str) -> bool:
        """Check if a user exists."""
        return username in self.list_users()

    def get_user_count(self) -> int:
        """Get total number of users."""
        return len(self.list_users())
