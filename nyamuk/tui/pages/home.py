"""Home Page - Broker status and connection info."""

from textual.app import ComposeResult
from textual.containers import Container, Horizontal, Vertical
from textual.widgets import Button, Label

from nyamuk.core.broker_manager import BrokerManager


class HomePage(Vertical):
    """Home page showing broker status and connection info."""

    CSS = """
    HomePage {
        padding: 1;
    }
    .home-header {
        text-style: bold;
        color: $primary;
        margin-bottom: 1;
    }
    .status-section {
        border: solid $primary;
        padding: 1;
        margin-bottom: 1;
    }
    .status-row {
        height: auto;
        margin-bottom: 1;
    }
    .status-label {
        width: 30%;
        text-style: bold;
    }
    .connection-section {
        border: solid $accent;
        padding: 1;
        margin-bottom: 1;
    }
    .connection-info {
        background: $surface;
        padding: 1;
        margin-bottom: 1;
        font-family: monospace;
    }
    .esp32-section {
        border: solid $warning;
        padding: 1;
        margin-bottom: 1;
    }
    .esp32-code {
        background: $surface;
        padding: 1;
        font-family: monospace;
        font-size: 0.9;
    }
    .button-row {
        height: 3;
        margin-top: 1;
    }
    Button {
        margin: 0 1;
    }
    .not-configured {
        color: $warning;
        text-style: bold;
    }
    .tester-hint {
        color: $primary;
        text-style: bold;
        margin-top: 1;
        text-align: center;
    }
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.broker_manager = BrokerManager()

    def compose(self) -> ComposeResult:
        yield Label("Nyamuk - MQTT Broker Factory", classes="home-header")

        # Broker Status
        with Container(classes="status-section"):
            yield Label("Broker Status", classes="section-title")
            yield Label("Checking...", id="status-text", classes="status-row")
            yield Label("Port: --", id="port-text", classes="status-row")
            yield Label("Created: --", id="created-text", classes="status-row")

        # Connection Info
        with Container(classes="connection-section"):
            yield Label("Connection Info", classes="section-title")
            yield Label("Broker: --:--", id="broker-addr", classes="connection-info")
            yield Label("Username: --", id="broker-user", classes="connection-info")
            yield Label("Password: --", id="broker-pass", classes="connection-info")
            yield Label("Topic: nyamuk/#", id="broker-topic", classes="connection-info")

        # ESP32 Config
        with Container(classes="esp32-section"):
            yield Label("ESP32 Configuration", classes="section-title")
            yield Label(
                "// Copy this to your Arduino sketch", id="esp32-config", classes="esp32-code"
            )

        # Action Buttons
        with Horizontal(classes="button-row"):
            yield Button("Start", id="start-btn", variant="success")
            yield Button("Stop", id="stop-btn", variant="error")
            yield Button("Restart", id="restart-btn", variant="warning")
            yield Button("Delete", id="delete-btn", variant="error")

        yield Label("Press t to test MQTT pub/sub", classes="tester-hint")

    def on_mount(self) -> None:
        """Load broker status."""
        self._refresh_status()

    def _refresh_status(self):
        """Refresh broker status."""
        config = self.broker_manager.get_broker_config()

        if not config:
            self.query_one("#status-text", Label).update("No broker configured")
            self.query_one("#status-text", Label).add_class("not-configured")
            self.query_one("#port-text", Label).update("Port: --")
            self.query_one("#created-text", Label).update("Created: --")
            self.query_one("#broker-addr", Label).update("Broker: --:--")
            self.query_one("#broker-user", Label).update("Username: --")
            self.query_one("#broker-pass", Label).update("Password: --")
            self.query_one("#esp32-config", Label).update(
                "// No broker configured. Go to Create page."
            )
            return

        # Get status
        status = self.broker_manager.get_status()

        # Update status
        status_icon = "+" if status["status"] == "running" else "-"
        self.query_one("#status-text", Label).update(f"{status_icon} {status['status'].upper()}")
        self.query_one("#port-text", Label).update(f"Port: {status['port']}")
        self.query_one("#created-text", Label).update(f"Created: {status['created_at'][:19]}")

        # Update connection info
        conn_info = self.broker_manager.get_connection_info()
        if conn_info:
            self.query_one("#broker-addr", Label).update(f"Broker: {conn_info['broker']}")
            self.query_one("#broker-user", Label).update(f"Username: {conn_info['username']}")
            self.query_one("#broker-pass", Label).update(f"Password: {conn_info['password']}")
            self.query_one("#broker-topic", Label).update(f"Topic: {conn_info['topic_prefix']}/#")

            # Generate ESP32 config
            from nyamuk.core.provisioning import ESP32Provisioning

            ip = conn_info["broker"].split(":")[0]
            provisioning = ESP32Provisioning(ip, int(conn_info["port"]))
            esp32_config = provisioning.generate_arduino_snippet(
                device_id="esp32_001",
                username=conn_info["username"],
                password=conn_info["password"],
            )
            self.query_one("#esp32-config", Label).update(esp32_config)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses."""
        if event.button.id == "start-btn":
            success, msg = self.broker_manager.start_broker()
            self.notify(msg, severity="information" if success else "error")
            self._refresh_status()
        elif event.button.id == "stop-btn":
            success, msg = self.broker_manager.stop_broker()
            self.notify(msg, severity="information" if success else "error")
            self._refresh_status()
        elif event.button.id == "restart-btn":
            success, msg = self.broker_manager.restart_broker()
            self.notify(msg, severity="information" if success else "error")
            self._refresh_status()
        elif event.button.id == "delete-btn":
            success, msg = self.broker_manager.delete_broker()
            self.notify(msg, severity="information" if success else "error")
            self._refresh_status()
