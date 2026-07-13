"""Config Page - Broker configuration editor."""

from textual.app import ComposeResult
from textual.containers import Container, Horizontal, Vertical
from textual.widgets import Static, Label, Input, Button, Switch, TextArea
from textual.reactive import reactive

from nyamuk.core.mosquitto import MosquittoManager


class ConfigPage(Vertical):
    """Configuration editor page."""

    CSS = """
    ConfigPage {
        padding: 1;
    }
    .config-header {
        text-style: bold;
        color: $primary;
        margin-bottom: 1;
    }
    .config-section {
        margin-bottom: 1;
        border: solid $accent;
        padding: 1;
    }
    .config-row {
        height: auto;
        margin-bottom: 1;
    }
    .config-label {
        width: 35%;
    }
    Input {
        width: 65%;
    }
    Switch {
        width: 65%;
    }
    .button-row {
        height: 3;
        margin-top: 1;
    }
    Button {
        margin: 0 1;
    }
    #config-editor {
        height: 1fr;
    }
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.mosquitto_manager = MosquittoManager()

    def compose(self) -> ComposeResult:
        yield Label("Broker Configuration", classes="config-header")

        with Container(classes="config-section"):
            yield Label("Network Settings", classes="section-title")

            with Horizontal(classes="config-row"):
                yield Label("Port:", classes="config-label")
                yield Input(value="1883", id="port-input", placeholder="1883")

            with Horizontal(classes="config-row"):
                yield Label("Allow Anonymous:", classes="config-label")
                yield Switch(value=False, id="anonymous-switch")

        with Container(classes="config-section"):
            yield Label("Persistence Settings", classes="section-title")

            with Horizontal(classes="config-row"):
                yield Label("Enable Persistence:", classes="config-label")
                yield Switch(value=True, id="persistence-switch")

        with Container(classes="config-section"):
            yield Label("Raw Configuration", classes="section-title")
            yield TextArea(id="config-editor", language="yaml")

        with Horizontal(classes="button-row"):
            yield Button("Load Config", id="load-btn", variant="primary")
            yield Button("Save Config", id="save-btn", variant="success")
            yield Button("Validate", id="validate-btn", variant="warning")

    def on_mount(self) -> None:
        """Load current configuration."""
        self._load_config()

    def _load_config(self):
        """Load configuration from file."""
        try:
            config = self.mosquitto_manager.read()

            # Update UI elements
            if "listener" in config:
                self.query_one("#port-input", Input).value = str(config["listener"])

            if "allow_anonymous" in config:
                self.query_one("#anonymous-switch", Switch).value = config["allow_anonymous"]

            if "persistence" in config:
                self.query_one("#persistence-switch", Switch).value = config["persistence"]

            # Load raw config into editor
            raw_lines = self.mosquitto_manager.get_raw_lines()
            self.query_one("#config-editor", TextArea).text = "\n".join(raw_lines)

        except Exception as e:
            self.notify(f"Error loading config: {e}", severity="error")

    def _save_config(self):
        """Save configuration to file."""
        try:
            # Get values from UI
            port = int(self.query_one("#port-input", Input).value)
            anonymous = self.query_one("#anonymous-switch", Switch).value
            persistence = self.query_one("#persistence-switch", Switch).value

            config = {
                "listener": port,
                "allow_anonymous": anonymous,
                "persistence": persistence,
                "persistence_location": "/mosquitto/data/",
                "log_dest": "file /mosquitto/log/mosquitto.log",
            }

            if self.mosquitto_manager.write(config):
                self.notify("Configuration saved successfully!", severity="success")
            else:
                self.notify("Failed to save configuration", severity="error")

        except ValueError as e:
            self.notify(f"Invalid value: {e}", severity="error")
        except Exception as e:
            self.notify(f"Error saving config: {e}", severity="error")

    def _validate_config(self):
        """Validate current configuration."""
        try:
            is_valid, errors = self.mosquitto_manager.validate()
            if is_valid:
                self.notify("Configuration is valid!", severity="success")
            else:
                for error in errors:
                    self.notify(error, severity="warning")
        except Exception as e:
            self.notify(f"Validation error: {e}", severity="error")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses."""
        if event.button.id == "load-btn":
            self._load_config()
        elif event.button.id == "save-btn":
            self._save_config()
        elif event.button.id == "validate-btn":
            self._validate_config()
