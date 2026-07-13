"""Tests for LogParser."""

from nyamuk.core.log_parser import LogEntry, LogLevel, LogParser


class TestLogParser:
    """Test log parser."""

    def test_parse_line_info(self):
        """Test parsing info log line."""
        parser = LogParser()

        line = "2024-01-15T10:30:00: Client connected"
        entry = parser._parse_line(line)

        assert entry is not None
        assert entry.timestamp == "2024-01-15T10:30:00"
        assert entry.message == "Client connected"
        assert entry.level == LogLevel.INFO

    def test_parse_line_error(self):
        """Test parsing error log line."""
        parser = LogParser()

        line = "2024-01-15T10:30:00: Error connection refused"
        entry = parser._parse_line(line)

        assert entry is not None
        assert entry.level == LogLevel.ERROR

    def test_parse_line_with_client(self):
        """Test parsing log with client ID."""
        parser = LogParser()

        line = "2024-01-15T10:30:00: Client ESP32-001 disconnected"
        entry = parser._parse_line(line)

        assert entry is not None
        assert entry.client_id == "ESP32-001"

    def test_parse_line_invalid(self):
        """Test parsing invalid log line."""
        parser = LogParser()

        line = "Invalid log line format"
        entry = parser._parse_line(line)

        assert entry is None

    def test_detect_level_error(self):
        """Test detecting error level."""
        parser = LogParser()

        assert parser._detect_level("Error occurred") == LogLevel.ERROR
        assert parser._detect_level("error in connection") == LogLevel.ERROR

    def test_detect_level_warning(self):
        """Test detecting warning level."""
        parser = LogParser()

        assert parser._detect_level("Warning: high memory") == LogLevel.WARNING
        assert parser._detect_level("Low disk space") == LogLevel.WARNING

    def test_detect_level_debug(self):
        """Test detecting debug level."""
        parser = LogParser()

        assert parser._detect_level("Debug message") == LogLevel.DEBUG

    def test_detect_level_info(self):
        """Test detecting info level."""
        parser = LogParser()

        assert parser._detect_level("Client connected") == LogLevel.INFO

    def test_extract_client_id(self):
        """Test extracting client ID."""
        parser = LogParser()

        message = "Client ESP32-001 connected"
        client_id = parser._extract_client_id(message)

        assert client_id == "ESP32-001"

    def test_extract_client_id_none(self):
        """Test extracting client ID when not present."""
        parser = LogParser()

        message = "No client info here"
        client_id = parser._extract_client_id(message)

        assert client_id is None

    def test_filter_logs_by_level(self):
        """Test filtering logs by level."""
        parser = LogParser()

        entries = [
            LogEntry(timestamp="2024-01-15T10:30:00", level=LogLevel.INFO, message="Info"),
            LogEntry(timestamp="2024-01-15T10:30:01", level=LogLevel.ERROR, message="Error"),
            LogEntry(timestamp="2024-01-15T10:30:02", level=LogLevel.INFO, message="Info2"),
        ]

        filtered = parser.filter_logs(entries, level=LogLevel.INFO)
        assert len(filtered) == 2

    def test_filter_logs_by_search(self):
        """Test filtering logs by search string."""
        parser = LogParser()

        entries = [
            LogEntry(
                timestamp="2024-01-15T10:30:00", level=LogLevel.INFO, message="Client connected"
            ),
            LogEntry(
                timestamp="2024-01-15T10:30:01", level=LogLevel.INFO, message="Client disconnected"
            ),
            LogEntry(
                timestamp="2024-01-15T10:30:02", level=LogLevel.INFO, message="Message published"
            ),
        ]

        filtered = parser.filter_logs(entries, search="connected")
        assert len(filtered) == 2

    def test_get_log_stats(self):
        """Test getting log statistics."""
        parser = LogParser()

        entries = [
            LogEntry(timestamp="2024-01-15T10:30:00", level=LogLevel.INFO, message="Info"),
            LogEntry(timestamp="2024-01-15T10:30:01", level=LogLevel.ERROR, message="Error"),
            LogEntry(timestamp="2024-01-15T10:30:02", level=LogLevel.INFO, message="Info2"),
        ]

        stats = parser.get_log_stats(entries)

        assert stats["total"] == 3
        assert stats["info"] == 2
        assert stats["error"] == 1

    def test_get_unique_clients(self):
        """Test getting unique client IDs."""
        parser = LogParser()

        entries = [
            LogEntry(
                timestamp="2024-01-15T10:30:00",
                level=LogLevel.INFO,
                message="Client connected",
                client_id="ESP32-001",
            ),
            LogEntry(
                timestamp="2024-01-15T10:30:01",
                level=LogLevel.INFO,
                message="Client connected",
                client_id="ESP32-002",
            ),
            LogEntry(
                timestamp="2024-01-15T10:30:02",
                level=LogLevel.INFO,
                message="Client connected",
                client_id="ESP32-001",
            ),
        ]

        clients = parser.get_unique_clients(entries)

        assert clients == ["ESP32-001", "ESP32-002"]
