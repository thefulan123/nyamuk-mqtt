"""Users Page - MQTT user management."""

from textual.app import ComposeResult
from textual.containers import Container, Horizontal, Vertical
from textual.widgets import Button, DataTable, Input, Label, Password

from nyamuk.core.user_manager import UserManager


class UsersPage(Vertical):
    """User management page."""

    CSS = """
    UsersPage {
        padding: 1;
    }
    .users-header {
        text-style: bold;
        color: $primary;
        margin-bottom: 1;
    }
    .add-user-form {
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
    Input, Password {
        width: 70%;
    }
    .button-row {
        height: 3;
        margin-top: 1;
    }
    Button {
        margin: 0 1;
    }
    #users-table {
        height: 1fr;
        border: solid $accent;
    }
    .no-broker {
        color: $warning;
        text-style: bold;
    }
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.user_manager = UserManager()

    def compose(self) -> ComposeResult:
        yield Label("MQTT User Management", classes="users-header")

        with Container(classes="add-user-form"):
            yield Label("Add New User", classes="section-title")

            with Horizontal(classes="form-row"):
                yield Label("Username:", classes="form-label")
                yield Input(placeholder="esp32_sensor", id="username-input")

            with Horizontal(classes="form-row"):
                yield Label("Password:", classes="form-label")
                yield Password(placeholder="Min 8 chars", id="password-input")

            with Horizontal(classes="form-row"):
                yield Label("Confirm:", classes="form-label")
                yield Password(placeholder="Confirm password", id="confirm-input")

            with Horizontal(classes="button-row"):
                yield Button("Add User", id="add-btn", variant="success")
                yield Button("Delete Selected", id="delete-btn", variant="error")
                yield Button("Refresh", id="refresh-btn", variant="primary")

        yield DataTable(classes="users-table", id="users-table")

    def on_mount(self) -> None:
        """Initialize users table."""
        table = self.query_one("#users-table", DataTable)
        table.add_columns("Username", "Status")
        table.cursor_type = "row"
        self._refresh_users()

    def _refresh_users(self):
        """Refresh users list."""
        try:
            table = self.query_one("#users-table", DataTable)
            table.clear()

            users = self.user_manager.list_users()
            for user in users:
                table.add_row(user, "Active")

        except Exception as e:
            self.notify(f"Error loading users: {e}", severity="error")

    def _add_user(self):
        """Add a new user."""
        username = self.query_one("#username-input", Input).value.strip()
        password = self.query_one("#password-input", Password).value
        confirm = self.query_one("#confirm-input", Password).value

        if not username:
            self.notify("Username is required", severity="error")
            return

        if password != confirm:
            self.notify("Passwords do not match", severity="error")
            return

        success, message = self.user_manager.add_user(username, password)
        if success:
            self.notify(message, severity="success")
            self._refresh_users()
            # Clear inputs
            self.query_one("#username-input", Input).value = ""
            self.query_one("#password-input", Password).value = ""
            self.query_one("#confirm-input", Password).value = ""
        else:
            self.notify(message, severity="error")

    def _delete_user(self):
        """Delete selected user."""
        table = self.query_one("#users-table", DataTable)
        if table.cursor_row is None:
            self.notify("No user selected", severity="warning")
            return

        username = table.get_row_at(table.cursor_row)[0]
        success, message = self.user_manager.delete_user(username)
        if success:
            self.notify(message, severity="success")
            self._refresh_users()
        else:
            self.notify(message, severity="error")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses."""
        if event.button.id == "add-btn":
            self._add_user()
        elif event.button.id == "delete-btn":
            self._delete_user()
        elif event.button.id == "refresh-btn":
            self._refresh_users()
