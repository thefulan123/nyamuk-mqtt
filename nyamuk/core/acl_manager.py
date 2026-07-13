"""Mosquitto ACL (Access Control List) management."""

from pathlib import Path
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
import shutil


@dataclass
class ACLRule:
    """Represents a single ACL rule."""
    username: str
    topic: str
    access: str = "readwrite"  # read, write, readwrite

    def to_string(self) -> str:
        """Convert rule to Mosquitto ACL format."""
        return f"user {self.username}\ntopic {self.access} {self.topic}\n"

    @classmethod
    def from_string(cls, text: str) -> Optional["ACLRule"]:
        """Parse a rule from Mosquitto ACL format."""
        lines = text.strip().split("\n")
        username = None
        topic = None
        access = "readwrite"

        for line in lines:
            line = line.strip()
            if line.startswith("user "):
                username = line[5:].strip()
            elif line.startswith("topic "):
                parts = line[6:].strip().split(None, 1)
                if len(parts) == 2:
                    access = parts[0]
                    topic = parts[1]
                elif len(parts) == 1:
                    topic = parts[0]

        if username and topic:
            return cls(username=username, topic=topic, access=access)
        return None


class ACLManager:
    """Manage Mosquitto ACL configuration file."""

    VALID_ACCESS = ["read", "write", "readwrite"]

    def __init__(self, container_name: str = "mosquitto", acl_file: str = "/mosquitto/config/aclfile"):
        self.container_name = container_name
        self.acl_file = acl_file

    def _run_command(self, command: str) -> Tuple[int, str]:
        """Execute command in Mosquitto container."""
        import subprocess
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

    def read_rules(self) -> List[ACLRule]:
        """Read all ACL rules from file."""
        cmd = f"cat {self.acl_file}"
        exit_code, output = self._run_command(cmd)

        if exit_code != 0:
            return []

        rules = []
        current_block = []

        for line in output.split("\n"):
            line = line.strip()
            if not line or line.startswith("#"):
                if current_block:
                    rule = ACLRule.from_string("\n".join(current_block))
                    if rule:
                        rules.append(rule)
                    current_block = []
                continue

            current_block.append(line)

        if current_block:
            rule = ACLRule.from_string("\n".join(current_block))
            if rule:
                rules.append(rule)

        return rules

    def write_rules(self, rules: List[ACLRule], backup: bool = True) -> bool:
        """Write ACL rules to file."""
        try:
            if backup:
                cmd = f"cp {self.acl_file} {self.acl_file}.bak 2>/dev/null || true"
                self._run_command(cmd)

            # Build ACL content
            content = "# Nyamuk MQTT ACL Configuration\n"
            content += f"# Generated: {datetime.now().isoformat()}\n\n"

            for rule in rules:
                content += rule.to_string() + "\n"

            # Write to temp file then copy to container
            import tempfile
            with tempfile.NamedTemporaryFile(mode="w", suffix=".acl", delete=False) as f:
                f.write(content)
                temp_path = f.name

            try:
                cmd = f"cp {temp_path} {self.acl_file}"
                exit_code, _ = self._run_command(cmd)
                return exit_code == 0
            finally:
                Path(temp_path).unlink(missing_ok=True)

        except Exception as e:
            print(f"Error writing ACL: {e}")
            return False

    def add_rule(self, username: str, topic: str, access: str = "readwrite") -> Tuple[bool, str]:
        """Add a new ACL rule."""
        if access not in self.VALID_ACCESS:
            return False, f"Invalid access type: {access}. Must be one of: {self.VALID_ACCESS}"

        if not username or not topic:
            return False, "Username and topic cannot be empty"

        rules = self.read_rules()

        # Check if rule already exists
        for rule in rules:
            if rule.username == username and rule.topic == topic:
                return False, f"Rule already exists for user '{username}' on topic '{topic}'"

        new_rule = ACLRule(username=username, topic=topic, access=access)
        rules.append(new_rule)

        if self.write_rules(rules):
            return True, f"Rule added: {username} -> {topic} ({access})"
        else:
            return False, "Failed to write ACL rules"

    def delete_rule(self, username: str, topic: str) -> Tuple[bool, str]:
        """Delete an ACL rule."""
        rules = self.read_rules()
        original_count = len(rules)

        rules = [r for r in rules if not (r.username == username and r.topic == topic)]

        if len(rules) == original_count:
            return False, f"No rule found for user '{username}' on topic '{topic}'"

        if self.write_rules(rules):
            return True, f"Rule deleted: {username} -> {topic}"
        else:
            return False, "Failed to write ACL rules"

    def get_user_rules(self, username: str) -> List[ACLRule]:
        """Get all rules for a specific user."""
        rules = self.read_rules()
        return [r for r in rules if r.username == username]

    def get_rule_count(self) -> int:
        """Get total number of ACL rules."""
        return len(self.read_rules())

    def validate_topic(self, topic: str) -> Tuple[bool, str]:
        """Validate MQTT topic pattern."""
        if not topic:
            return False, "Topic cannot be empty"
        if len(topic) > 65535:
            return False, "Topic too long (max 65535 characters)"
        # Check for invalid characters
        invalid_chars = ["\0", "\r", "\n"]
        for char in invalid_chars:
            if char in topic:
                return False, f"Topic contains invalid character: {repr(char)}"
        return True, "Valid"
