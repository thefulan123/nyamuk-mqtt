"""Logs Page - Real-time log viewer."""

from textual.app import ComposeResult
from textual.containers import Container, Horizontal, Vertical
from textual.widgets import Button, Input, Label, Select, TextArea

from nyamuk.core.log_parser import LogLevel, LogParser


class LogsPage(Vertical):
    """Real-time log viewer page."""

    CSS = """
    LogsPage {
        padding: 1;
    }
    .logs-header {
        text-style: bold;
        color: $primary;
        margin-bottom: 1;
    }
    .filter-bar {
        height: auto;
        margin-bottom: 1;
    }
    .filter-row {
        height: auto;
        margin-bottom: 1;
    }
    .filter-label {
        width: 20%;
    }
    Select {
        width: 30%;
    }
    Input {
        width: 50%;
    }
    .button-row {
        height: 3;
        margin-top: 1;
    }
    Button {
        margin: 0 1;
    }
    #log-output {
        height: 1fr;
        border: solid $accent;
    }
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.log_parser = LogParser()
        self._log_entries = []

    def compose(self) -> ComposeResult:
        yield Label("Real-time Logs", classes="logs-header")

        with Container(classes="filter-bar"):
            with Horizontal(classes="filter-row"):
                yield Label("Level:", classes="filter-label")
                yield Select(
                    [
                        ("all", "All Levels"),
                        ("info", "Info"),
                        ("warning", "Warning"),
                        ("error", "Error"),
                        ("debug", "Debug"),
                    ],
                    value="all",
                    id="level-select",
                )

                yield Label("Search:", classes="filter-label")
                yield Input(placeholder="Filter logs...", id="search-input")

            with Horizontal(classes="button-row"):
                yield Button("Refresh", id="refresh-btn", variant="primary")
                yield Button("Clear", id="clear-btn", variant="warning")
                yield Button("Export", id="export-btn", variant="success")

        yield TextArea(id="log-output", read_only=True)

    def on_mount(self) -> None:
        """Load initial logs."""
        self._refresh_logs()

    def _refresh_logs(self):
        """Refresh log entries."""
        try:
            self._log_entries = self.log_parser.read_logs(tail=200)
            self._display_logs()
        except Exception as e:
            self.notify(f"Error loading logs: {e}", severity="error")

    def _display_logs(self):
        """Display filtered logs."""
        level_filter = self.query_one("#level-select", Select).value
        search = self.query_one("#search-input", Input).value.strip()

        # Apply filters
        filtered = self._log_entries
        if level_filter != "all":
            try:
                level = LogLevel(level_filter)
                filtered = [e for e in filtered if e.level == level]
            except ValueError:
                pass

        if search:
            filtered = [e for e in filtered if search.lower() in e.message.lower()]

        # Format and display
        output = []
        for entry in filtered:
            output.append(f"[{entry.timestamp}] [{entry.level.value.upper()}] {entry.message}")

        log_output = self.query_one("#log-output", TextArea)
        log_output.text = "\n".join(output) if output else "No logs found"

    def _clear_logs(self):
        """Clear log display."""
        self.query_one("#log-output", TextArea).text = ""

    def _export_logs(self):
        """Export logs to file."""
        try:
            import json
            from pathlib import Path

            export_path = Path("/tmp/nyamuk_logs_export.json")
            data = [entry.to_dict() for entry in self._log_entries]

            with open(export_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)

            self.notify(f"Logs exported to {export_path}", severity="success")
        except Exception as e:
            self.notify(f"Export error: {e}", severity="error")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses."""
        if event.button.id == "refresh-btn":
            self._refresh_logs()
        elif event.button.id == "clear-btn":
            self._clear_logs()
        elif event.button.id == "export-btn":
            self._export_logs()

    def on_select_changed(self, event: Select.Changed) -> None:
        """Handle filter changes."""
        self._display_logs()

    def on_input_changed(self, event: Input.Changed) -> None:
        """Handle search input changes."""
        self._display_logs()
