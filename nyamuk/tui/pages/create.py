"""Create Page - Create new broker instance."""

from textual.app import ComposeResult
from textual.containers import Container, Horizontal, Vertical
from textual.widgets import Static, Label, Input, Button, Switch, Password
from textual.reactive import reactive

from nyamuk.core.broker_manager import BrokerManager
from nyamuk.core.port_scanner import PortScanner


class CreatePage(Vertical):
    """Create new broker page."""

    CSS = """
    CreatePage {
        padding: 1;
    }
    .create-header {
        text-style: bold;
        color: $primary;
        margin-bottom: 1;
    }
    .create-form {
        border: solid $accent;
        padding: 1;
        margin-bottom: 1;
    }
    .form-row {
        height: auto;
        margin-bottom: 1;
    }
    .form-label {
        width: 35%;
    }
    Input, Password {
        width: 65%;
    }
    Switch {
        width: 65%;
    }
    .port-info {
        color: $text-muted;
        font-size: 0.9;
    }
    .button-row {
        height: 3;
        margin-top: 1;
    }
    Button {
        margin: 0 1;
    }
    .success-message {
        color: $success;
        text-style: bold;
    }
    .error-message {
        color: $error;
        text-style: bold;
    }
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.broker_manager = BrokerManager()
        self.port_scanner = PortScanner()

    def compose(self) -> ComposeResult:
        yield Label("➕ Create New Broker", classes="create-header")

        # Check if broker already exists
        existing = self.broker_manager.get_broker_config()
        if existing:
            yield Label(
                "⚠️ Broker already exists. Delete it first before creating a new one.",
                classes="error-message"
            )
            return

        with Container(classes="create-form"):
            yield Label("Broker Settings", classes="section-title")

            with Horizontal(classes="form-row"):
                yield Label("Broker Name:", classes="form-label")
                yield Input(placeholder="my_broker", id="name-input")

            with Horizontal(classes="form-row"):
                yield Label("Port:", classes="form-label")
                yield Input(value=str(self.port_scanner.suggest_port()), id="port-input")
                yield Label("(auto-detected)", classes="port-info")

            with Horizontal(classes="form-row"):
                yield Label("Password:", classes="form-label")
                yield Password(placeholder="Leave empty for auto-generate", id="password-input")

            with Horizontal(classes="form-row"):
                yield Label("Allow Anonymous:", classes="form-label")
                yield Switch(value=False, id="anonymous-switch")

            with Horizontal(classes="form-row"):
                yield Label("Enable Persistence:", classes="form-label")
                yield Switch(value=True, id="persistence-switch")

        with Horizontal(classes="button-row"):
            yield Button("Create Broker", id="create-btn", variant="success")
            yield Button("Check Port", id="check-btn", variant="primary")

    def _check_port(self):
        """Check if port is free."""
        port_str = self.query_one("#port-input", Input).value.strip()
        try:
            port = int(port_str)
            if self.port_scanner.is_port_free(port):
                self.notify(f"✅ Port {port} is available", severity="success")
            else:
                self.notify(f"❌ Port {port} is already in use", severity="error")
        except ValueError:
            self.notify("Invalid port number", severity="error")

    def _create_broker(self):
        """Create the broker."""
        name = self.query_one("#name-input", Input).value.strip()
        port_str = self.query_one("#port-input", Input).value.strip()
        password = self.query_one("#password-input", Password).value
        allow_anonymous = self.query_one("#anonymous-switch", Switch).value
        persistence = self.query_one("#persistence-switch", Switch).value

        if not name:
            self.notify("Broker name is required", severity="error")
            return

        try:
            port = int(port_str)
        except ValueError:
            self.notify("Invalid port number", severity="error")
            return

        # Create broker
        success, message = self.broker_manager.create_broker(
            name=name,
            port=port,
            password=password if password else None,
            allow_anonymous=allow_anonymous,
            persistence=persistence,
        )

        if success:
            self.notify(message, severity="success")
            # Auto-start broker
            start_success, start_msg = self.broker_manager.start_broker()
            if start_success:
                self.notify("Broker started automatically", severity="success")
            # Refresh page
            self.refresh()
        else:
            self.notify(message, severity="error")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses."""
        if event.button.id == "create-btn":
            self._create_broker()
        elif event.button.id == "check-btn":
            self._check_port()
