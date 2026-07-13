"""Tester Page - MQTT pub/sub testing."""

import json
from datetime import datetime
from typing import Any

from textual.app import ComposeResult
from textual.containers import Container, Horizontal, Vertical
from textual.widgets import Button, Input, Label, Log, Select

from nyamuk.core.broker_manager import BrokerManager
from nyamuk.core.mqtt_client import MQTTTestClient


class TesterPage(Vertical):
    """MQTT publish/subscribe testing page."""

    CSS = """
    TesterPage {
        padding: 1;
    }
    .tester-header {
        text-style: bold;
        color: $primary;
        margin-bottom: 1;
    }
    .publish-box, .subscribe-box {
        border: solid $accent;
        padding: 1;
        margin-bottom: 1;
    }
    .publish-box {
        width: 40%;
    }
    .subscribe-box {
        width: 58%;
    }
    .publish-box {
        height: auto;
    }
    .subscribe-box {
        height: 1fr;
    }
    .form-row {
        height: auto;
        margin-bottom: 1;
    }
    .form-label {
        width: 25%;
    }
    Input {
        width: 75%;
    }
    Select {
        width: 75%;
    }
    .button-row {
        height: 3;
        margin-top: 1;
    }
    Button {
        margin: 0 1;
    }
    #sub-log {
        height: 1fr;
        border: solid $primary;
        margin-top: 1;
    }
    .conn-status {
        color: $text-muted;
        text-style: italic;
    }
    .status-connected {
        color: $success;
    }
    .status-disconnected {
        color: $error;
    }
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.broker_manager = BrokerManager()
        self.test_client: MQTTTestClient | None = None

    def compose(self) -> ComposeResult:
        yield Label("MQTT Message Tester", classes="tester-header")
        yield Label("Not connected", id="conn-status", classes="conn-status")

        with Horizontal():
            with Container(classes="publish-box"):
                yield Label("Publisher", classes="section-title")

                with Horizontal(classes="form-row"):
                    yield Label("Topic:", classes="form-label")
                    yield Input(placeholder="nyamuk/test", id="pub-topic")

                with Horizontal(classes="form-row"):
                    yield Label("Payload:", classes="form-label")
                    yield Input(placeholder="Hello MQTT!", id="pub-payload")

                with Horizontal(classes="form-row"):
                    yield Label("Data Type:", classes="form-label")
                    yield Select(
                        [("String", "string"), ("JSON", "json"), ("Number", "number")],
                        value="string",
                        id="pub-type",
                    )

                with Horizontal(classes="form-row"):
                    yield Label("QOS:", classes="form-label")
                    yield Select(
                        [
                            ("0 - At most once", "0"),
                            ("1 - At least once", "1"),
                            ("2 - Exactly once", "2"),
                        ],
                        value="0",
                        id="pub-qos",
                    )

                with Horizontal(classes="button-row"):
                    yield Button("Connect", id="connect-btn", variant="primary")
                    yield Button("Publish", id="publish-btn", variant="success")
                    yield Button("Disconnect", id="disconnect-btn", variant="error")

            with Container(classes="subscribe-box"):
                yield Label("Subscriber", classes="section-title")

                with Horizontal(classes="form-row"):
                    yield Label("Topic:", classes="form-label")
                    yield Input(placeholder="#", id="sub-topic")
                    yield Button("Subscribe", id="subscribe-btn", variant="primary")
                    yield Button("Clear", id="clear-btn", variant="warning")

                yield Log(id="sub-log", highlight=True, max_lines=1000)

    def on_mount(self) -> None:
        """Initialize tester."""
        self._update_connection_status()

    def _get_client(self) -> MQTTTestClient | None:
        """Get or create test client."""
        if self.test_client is None or not self.test_client.is_connected:
            conn_info = self.broker_manager.get_connection_info()
            if not conn_info:
                self.notify("No broker configured", severity="error")
                return None

            host = conn_info.get("broker", "localhost").split(":")[0]
            port = int(conn_info.get("port", 1883))
            username = conn_info.get("username", "")
            password = conn_info.get("password", "")

            client = MQTTTestClient(
                broker=host,
                port=port,
                username=username,
                password=password,
                client_id="nyamuk_tester",
            )
            if not client.connect():
                self.notify("Failed to connect to broker", severity="error")
                return None

            client.on_message(self._on_mqtt_message)
            self.test_client = client
            self._update_connection_status()
        return self.test_client

    def _update_connection_status(self) -> None:
        """Update connection status display."""
        label = self.query_one("#conn-status", Label)
        if self.test_client and self.test_client.is_connected:
            label.update("Connected")
            label.classes = "conn-status status-connected"
        else:
            label.update("Not connected")
            label.classes = "conn-status status-disconnected"

    def _on_mqtt_message(self, msg: dict) -> None:
        """Handle incoming MQTT message."""
        log = self.query_one("#sub-log", Log)
        try:
            payload = msg["payload"]
            try:
                parsed = json.loads(payload)
                payload = json.dumps(parsed, indent=2)
            except (json.JSONDecodeError, TypeError):
                pass
            line = f"[{msg['timestamp'][11:19]}] {msg['topic']}: {payload}"
            self.app.call_from_thread(log.write, line)
        except Exception:
            pass

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses."""
        btn_id = event.button.id

        if btn_id == "connect-btn":
            client = self._get_client()
            if client:
                self.notify("Connected to broker", severity="information")
                self._update_connection_status()

        elif btn_id == "disconnect-btn":
            if self.test_client:
                self.test_client.disconnect()
                self.test_client = None
                self._update_connection_status()
                self.notify("Disconnected", severity="information")

        elif btn_id == "publish-btn":
            client = self._get_client()
            if not client:
                return

            topic = self.query_one("#pub-topic", Input).value.strip()
            if not topic:
                self.notify("Topic is required", severity="error")
                return

            payload = self.query_one("#pub-payload", Input).value
            data_type = str(self.query_one("#pub-type", Select).value)
            qos_val = self.query_one("#pub-qos", Select).value
            qos = int(str(qos_val))

            converted_payload: Any = payload
            if data_type == "json":
                try:
                    converted_payload = json.loads(payload)
                except json.JSONDecodeError:
                    self.notify("Invalid JSON payload", severity="error")
                    return
            elif data_type == "number":
                try:
                    if "." in payload:
                        converted_payload = float(payload)
                    else:
                        converted_payload = int(payload)
                except ValueError:
                    self.notify("Invalid number", severity="error")
                    return

            success = client.publish(topic, converted_payload, qos=qos)
            if success:
                self.notify(f"Published to {topic}", severity="information")
            else:
                self.notify("Publish failed", severity="error")

        elif btn_id == "subscribe-btn":
            client = self._get_client()
            if not client:
                return

            topic = self.query_one("#sub-topic", Input).value.strip()
            if not topic:
                topic = "#"

            success = client.subscribe(topic)
            if success:
                self.notify(f"Subscribed to {topic}", severity="information")
                log = self.query_one("#sub-log", Log)
                log.write(f"[{datetime.now().isoformat()[11:19]}] Subscribed to {topic}")
            else:
                self.notify("Subscribe failed", severity="error")

        elif btn_id == "clear-btn":
            log = self.query_one("#sub-log", Log)
            log.clear()
            if self.test_client:
                self.test_client.clear_messages()
