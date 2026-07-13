"""Log viewer widget."""

from textual.app import ComposeResult
from textual.widgets import Label, Static, TextArea


class LogViewer(Static):
    """Log file viewer widget."""

    CSS = """
    LogViewer {
        height: 1fr;
        border: solid $accent;
    }
    .viewer-header {
        text-style: bold;
        color: $primary;
        margin-bottom: 1;
    }
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._entries = []

    def compose(self) -> ComposeResult:
        yield Label("Log Viewer", classes="viewer-header")
        yield TextArea(id="log-textarea", read_only=True)

    def load_logs(self, entries: list):
        """Load log entries."""
        self._entries = entries
        formatted = []
        for entry in entries:
            formatted.append(f"[{entry.timestamp}] [{entry.level.value}] {entry.message}")
        try:
            self.query_one("#log-textarea", TextArea).text = "\n".join(formatted)
        except Exception:
            pass

    def clear(self):
        """Clear log display."""
        self._entries = []
        try:
            self.query_one("#log-textarea", TextArea).text = ""
        except Exception:
            pass
