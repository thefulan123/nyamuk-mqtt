"""Mosquitto log file parser and viewer."""

import re
from pathlib import Path
from typing import List, Dict, Optional, Tuple
from datetime import datetime
from dataclasses import dataclass
from enum import Enum


class LogLevel(Enum):
    """Mosquitto log levels."""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    DEBUG = "debug"
    SUBSCRIBE = "subscribe"
    UNSUBSCRIBE = "unsubscribe"


@dataclass
class LogEntry:
    """Represents a single log entry."""
    timestamp: str
    level: LogLevel
    message: str
    client_id: Optional[str] = None

    def to_dict(self) -> Dict[str, str]:
        """Convert to dictionary."""
        return {
            "timestamp": self.timestamp,
            "level": self.level.value,
            "message": self.message,
            "client_id": self.client_id or "",
        }


class LogParser:
    """Parse and filter Mosquitto log files."""

    # Mosquitto log pattern: 2024-01-15T10:30:00: message
    LOG_PATTERN = re.compile(
        r"^(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2})\s+(.+)$"
    )

    # Client-related patterns
    CLIENT_PATTERN = re.compile(r"Client\s+(\S+)")
    NEW_CLIENT_PATTERN = re.compile(r"New client connected.*?Client\s+(\S+)")

    def __init__(self, container_name: str = "mosquitto", log_file: str = "/mosquitto/log/mosquitto.log"):
        self.container_name = container_name
        self.log_file = log_file

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

    def read_logs(self, tail: int = 100) -> List[LogEntry]:
        """Read recent log entries."""
        cmd = f"tail -n {tail} {self.log_file}"
        exit_code, output = self._run_command(cmd)

        if exit_code != 0:
            return []

        entries = []
        for line in output.strip().split("\n"):
            entry = self._parse_line(line)
            if entry:
                entries.append(entry)

        return entries

    def _parse_line(self, line: str) -> Optional[LogEntry]:
        """Parse a single log line."""
        match = self.LOG_PATTERN.match(line.strip())
        if not match:
            return None

        timestamp, message = match.groups()
        level = self._detect_level(message)
        client_id = self._extract_client_id(message)

        return LogEntry(
            timestamp=timestamp,
            level=level,
            message=message,
            client_id=client_id,
        )

    def _detect_level(self, message: str) -> LogLevel:
        """Detect log level from message content."""
        msg_lower = message.lower()
        if "error" in msg_lower:
            return LogLevel.ERROR
        if "warning" in msg_lower or "warn" in msg_lower:
            return LogLevel.WARNING
        if "subscribe" in msg_lower:
            return LogLevel.SUBSCRIBE
        if "unsubscribe" in msg_lower:
            return LogLevel.UNSUBSCRIBE
        if "debug" in msg_lower:
            return LogLevel.DEBUG
        return LogLevel.INFO

    def _extract_client_id(self, message: str) -> Optional[str]:
        """Extract client ID from log message."""
        match = self.CLIENT_PATTERN.search(message)
        return match.group(1) if match else None

    def filter_logs(
        self,
        entries: List[LogEntry],
        level: Optional[LogLevel] = None,
        client_id: Optional[str] = None,
        search: Optional[str] = None,
    ) -> List[LogEntry]:
        """Filter log entries by criteria."""
        filtered = entries

        if level:
            filtered = [e for e in filtered if e.level == level]

        if client_id:
            filtered = [e for e in filtered if e.client_id == client_id]

        if search:
            search_lower = search.lower()
            filtered = [e for e in filtered if search_lower in e.message.lower()]

        return filtered

    def get_log_stats(self, entries: List[LogEntry]) -> Dict[str, int]:
        """Get statistics about log entries."""
        stats = {"total": len(entries)}
        for level in LogLevel:
            stats[level.value] = len([e for e in entries if e.level == level])
        return stats

    def get_unique_clients(self, entries: List[LogEntry]) -> List[str]:
        """Get list of unique client IDs from logs."""
        clients = set()
        for entry in entries:
            if entry.client_id:
                clients.add(entry.client_id)
        return sorted(clients)

    def search_logs(self, entries: List[LogEntry], pattern: str) -> List[LogEntry]:
        """Search logs using regex pattern."""
        try:
            regex = re.compile(pattern, re.IGNORECASE)
            return [e for e in entries if regex.search(e.message)]
        except re.error:
            return []
