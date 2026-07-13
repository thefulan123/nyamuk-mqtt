"""ACL Page - Access Control List management."""

from textual.app import ComposeResult
from textual.containers import Container, Horizontal, Vertical
from textual.widgets import Button, DataTable, Input, Label, Select

from nyamuk.core.acl_manager import ACLManager


class ACLPage(Vertical):
    """ACL management page."""

    CSS = """
    ACLPage {
        padding: 1;
    }
    .acl-header {
        text-style: bold;
        color: $primary;
        margin-bottom: 1;
    }
    .add-rule-form {
        border: solid $accent;
        padding: 1;
        margin-bottom: 1;
        height: auto;
    }
    .form-row {
        height: auto;
        margin-bottom: 1;
    }
    .form-label {
        width: 30%;
    }
    Input {
        width: 70%;
    }
    Select {
        width: 70%;
    }
    .button-row {
        height: 3;
        margin-top: 1;
    }
    Button {
        margin: 0 1;
    }
    #acl-table {
        height: 1fr;
        border: solid $accent;
    }
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.acl_manager = ACLManager()

    def compose(self) -> ComposeResult:
        yield Label("Access Control List", classes="acl-header")

        with Container(classes="add-rule-form"):
            yield Label("Add New Rule", classes="section-title")

            with Horizontal(classes="form-row"):
                yield Label("Username:", classes="form-label")
                yield Input(placeholder="esp32_sensor", id="username-input")

            with Horizontal(classes="form-row"):
                yield Label("Topic:", classes="form-label")
                yield Input(placeholder="nyamuk/esp32/#", id="topic-input")

            with Horizontal(classes="form-row"):
                yield Label("Access:", classes="form-label")
                yield Select(
                    [
                        ("Read/Write", "readwrite"),
                        ("Read Only", "read"),
                        ("Write Only", "write"),
                    ],
                    value="readwrite",
                    id="access-select",
                )

            with Horizontal(classes="button-row"):
                yield Button("Add Rule", id="add-btn", variant="success")
                yield Button("Delete Selected", id="delete-btn", variant="error")
                yield Button("Refresh", id="refresh-btn", variant="primary")

        yield DataTable(classes="acl-table", id="acl-table")

    def on_mount(self) -> None:
        """Initialize ACL table."""
        table = self.query_one("#acl-table", DataTable)
        table.add_columns("Username", "Topic", "Access")
        table.cursor_type = "row"
        self._refresh_rules()

    def _refresh_rules(self):
        """Refresh ACL rules list."""
        try:
            table = self.query_one("#acl-table", DataTable)
            table.clear()

            rules = self.acl_manager.read_rules()
            for rule in rules:
                table.add_row(rule.username, rule.topic, rule.access)

        except Exception as e:
            self.notify(f"Error loading ACL rules: {e}", severity="error")

    def _add_rule(self):
        """Add a new ACL rule."""
        username = self.query_one("#username-input", Input).value.strip()
        topic = self.query_one("#topic-input", Input).value.strip()
        access = self.query_one("#access-select", Select).value

        if not username or not topic:
            self.notify("Username and topic are required", severity="error")
            return

        # Validate topic
        valid, msg = self.acl_manager.validate_topic(topic)
        if not valid:
            self.notify(f"Invalid topic: {msg}", severity="error")
            return

        success, message = self.acl_manager.add_rule(username, topic, access)
        if success:
            self.notify(message, severity="information")
            self._refresh_rules()
            # Clear inputs
            self.query_one("#username-input", Input).value = ""
            self.query_one("#topic-input", Input).value = ""
        else:
            self.notify(message, severity="error")

    def _delete_rule(self):
        """Delete selected rule."""
        table = self.query_one("#acl-table", DataTable)
        if table.cursor_row is None:
            self.notify("No rule selected", severity="warning")
            return

        row = table.get_row_at(table.cursor_row)
        username, topic = row[0], row[1]

        success, message = self.acl_manager.delete_rule(username, topic)
        if success:
            self.notify(message, severity="information")
            self._refresh_rules()
        else:
            self.notify(message, severity="error")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses."""
        if event.button.id == "add-btn":
            self._add_rule()
        elif event.button.id == "delete-btn":
            self._delete_rule()
        elif event.button.id == "refresh-btn":
            self._refresh_rules()
