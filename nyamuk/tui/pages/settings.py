"""Settings Page - Application settings."""

import json
from pathlib import Path

from textual.app import ComposeResult
from textual.containers import Container, Horizontal, Vertical
from textual.widgets import Button, Input, Label, Select


class SettingsPage(Vertical):
    """Application settings page."""

    CSS = """
    SettingsPage {
        padding: 1;
    }
    .settings-header {
        text-style: bold;
        color: $primary;
        margin-bottom: 1;
    }
    .settings-section {
        border: solid $accent;
        padding: 1;
        margin-bottom: 1;
        height: auto;
    }
    .section-title {
        text-style: bold;
        margin-bottom: 1;
    }
    .settings-row {
        height: auto;
        margin-bottom: 1;
    }
    .settings-label {
        width: 35%;
    }
    Input {
        width: 65%;
    }
    Select {
        width: 65%;
    }
    .button-row {
        height: 3;
        margin-top: 1;
    }
    Button {
        margin: 0 1;
    }
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.config_path = Path("config.json")

    def compose(self) -> ComposeResult:
        yield Label("Settings", classes="settings-header")

        with Container(classes="settings-section"):
            yield Label("MQTT Broker", classes="section-title")

            with Horizontal(classes="settings-row"):
                yield Label("Broker Host:", classes="settings-label")
                yield Input(value="localhost", id="broker-input")

            with Horizontal(classes="settings-row"):
                yield Label("Broker Port:", classes="settings-label")
                yield Input(value="1883", id="port-input")

            with Horizontal(classes="settings-row"):
                yield Label("Topic Prefix:", classes="settings-label")
                yield Input(value="nyamuk", id="prefix-input")

        with Container(classes="settings-section"):
            yield Label("Web Dashboard", classes="section-title")

            with Horizontal(classes="settings-row"):
                yield Label("Admin Username:", classes="settings-label")
                yield Input(value="admin", id="admin-user-input")

            with Horizontal(classes="settings-row"):
                yield Label("Admin Password:", classes="settings-label")
                yield Input(value="nyamuk123", id="admin-pass-input")

            with Horizontal(classes="settings-row"):
                yield Label("Web Port:", classes="settings-label")
                yield Input(value="8080", id="web-port-input")

        with Container(classes="settings-section"):
            yield Label("Application", classes="section-title")

            with Horizontal(classes="settings-row"):
                yield Label("Log Level:", classes="settings-label")
                yield Select(
                    [
                        ("Debug", "DEBUG"),
                        ("Info", "INFO"),
                        ("Warning", "WARNING"),
                        ("Error", "ERROR"),
                    ],
                    value="INFO",
                    id="log-level-select",
                )

        with Horizontal(classes="button-row"):
            yield Button("Load Settings", id="load-btn", variant="primary")
            yield Button("Save Settings", id="save-btn", variant="success")
            yield Button("Reset Defaults", id="reset-btn", variant="warning")

    def on_mount(self) -> None:
        """Load current settings."""
        self._load_settings()

    def _load_settings(self):
        """Load settings from config file."""
        try:
            if self.config_path.exists():
                with open(self.config_path, encoding="utf-8") as f:
                    config = json.load(f)

                self.query_one("#broker-input", Input).value = config.get(
                    "mqtt_broker", "localhost"
                )
                self.query_one("#port-input", Input).value = str(config.get("mqtt_port", 1883))
                self.query_one("#prefix-input", Input).value = config.get("topic_prefix", "nyamuk")
                self.query_one("#admin-user-input", Input).value = config.get(
                    "web_admin_user", "admin"
                )
                self.query_one("#admin-pass-input", Input).value = config.get(
                    "web_admin_pass", "nyamuk123"
                )
                self.query_one("#web-port-input", Input).value = str(config.get("web_port", 8080))
                self.query_one("#log-level-select", Select).value = config.get("log_level", "INFO")

        except Exception as e:
            self.notify(f"Error loading settings: {e}", severity="error")

    def _save_settings(self):
        """Save settings to config file."""
        try:
            config = {
                "mqtt_broker": self.query_one("#broker-input", Input).value,
                "mqtt_port": int(self.query_one("#port-input", Input).value),
                "topic_prefix": self.query_one("#prefix-input", Input).value,
                "web_admin_user": self.query_one("#admin-user-input", Input).value,
                "web_admin_pass": self.query_one("#admin-pass-input", Input).value,
                "web_port": int(self.query_one("#web-port-input", Input).value),
                "log_level": self.query_one("#log-level-select", Select).value,
            }

            with open(self.config_path, "w", encoding="utf-8") as f:
                json.dump(config, f, indent=2)

            self.notify("Settings saved successfully!", severity="information")

        except ValueError as e:
            self.notify(f"Invalid value: {e}", severity="error")
        except Exception as e:
            self.notify(f"Error saving settings: {e}", severity="error")

    def _reset_defaults(self):
        """Reset to default settings."""
        defaults = {
            "mqtt_broker": "localhost",
            "mqtt_port": 1883,
            "topic_prefix": "nyamuk",
            "web_admin_user": "admin",
            "web_admin_pass": "nyamuk123",
            "web_port": 8080,
            "log_level": "INFO",
        }

        self.query_one("#broker-input", Input).value = defaults["mqtt_broker"]
        self.query_one("#port-input", Input).value = str(defaults["mqtt_port"])
        self.query_one("#prefix-input", Input).value = defaults["topic_prefix"]
        self.query_one("#admin-user-input", Input).value = defaults["web_admin_user"]
        self.query_one("#admin-pass-input", Input).value = defaults["web_admin_pass"]
        self.query_one("#web-port-input", Input).value = str(defaults["web_port"])
        self.query_one("#log-level-select", Select).value = defaults["log_level"]

        self.notify("Settings reset to defaults", severity="info")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses."""
        if event.button.id == "load-btn":
            self._load_settings()
        elif event.button.id == "save-btn":
            self._save_settings()
        elif event.button.id == "reset-btn":
            self._reset_defaults()
