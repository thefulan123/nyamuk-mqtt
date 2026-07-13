"""Dashboard page - broker status overview."""

from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical
from textual.timer import Timer
from textual.widgets import DataTable, Label, Static

from nyamuk.core.docker_manager import DockerManager


class StatusCard(Static):
    """Status card widget."""

    def __init__(self, title: str, value: str = "Loading...", **kwargs):
        super().__init__(**kwargs)
        self.title_text = title
        self.value_text = value

    def compose(self) -> ComposeResult:
        yield Label(self.title_text, classes="card-title")
        yield Label(self.value_text, id="card-value", classes="card-value")

    def update_value(self, value: str):
        """Update the card value."""
        self.value_text = value
        self.query_one("#card-value", Label).update(value)


class DashboardPage(Vertical):
    """Dashboard page showing broker status."""

    CSS = """
    DashboardPage {
        padding: 1;
    }
    .status-grid {
        height: auto;
        margin-bottom: 1;
    }
    .status-row {
        height: auto;
        margin-bottom: 1;
    }
    StatusCard {
        width: 1fr;
        height: 5;
        border: solid $primary;
        padding: 1;
        margin: 0 1;
    }
    .card-title {
        text-style: bold;
        color: $primary;
    }
    .card-value {
        text-style: bold;
    }
    #connected {
        color: $success;
    }
    #disconnected {
        color: $error;
    }
    .clients-table {
        height: 1fr;
        border: solid $accent;
    }
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.docker_manager = DockerManager()
        self._refresh_timer: Timer | None = None
        self._status_card: StatusCard | None = None
        self._uptime_card: StatusCard | None = None
        self._clients_card: StatusCard | None = None
        self._messages_card: StatusCard | None = None

    def compose(self) -> ComposeResult:
        yield Label("Nyamuk Dashboard", classes="title")

        with Horizontal(classes="status-grid"):
            self._status_card = StatusCard("Status", "Checking...")
            self._uptime_card = StatusCard("Uptime", "N/A")
            self._clients_card = StatusCard("Clients", "0")
            self._messages_card = StatusCard("Messages", "0")

            yield self._status_card
            yield self._uptime_card
            yield self._clients_card
            yield self._messages_card

        yield DataTable(classes="clients-table", id="clients-table")

    def on_mount(self) -> None:
        """Initialize and start refresh timer."""
        self._refresh_timer = self.set_interval(5.0, self._refresh_status)

        # Setup clients table
        table = self.query_one("#clients-table", DataTable)
        table.add_columns("Client ID", "IP Address", "Connected", "Subscriptions")

        self._refresh_status()

    def _refresh_status(self):
        """Refresh broker status."""
        try:
            status = self.docker_manager.get_status()

            if status.get("status") == "running":
                self._status_card.update_value("Running")
                self._status_card.id = "connected"
                self._uptime_card.update_value(status.get("started_at", "N/A")[:19])
            else:
                self._status_card.update_value("Stopped")
                self._status_card.id = "disconnected"
                self._uptime_card.update_value("N/A")

            # Get container stats
            stats = self.docker_manager.get_stats()
            if "error" not in stats:
                cpu = stats.get("cpu_percent", 0)
                mem = stats.get("memory_percent", 0)
                self._clients_card.update_value(f"CPU: {cpu}%\nRAM: {mem}%")

        except Exception as e:
            self._status_card.update_value(f"Error: {str(e)[:20]}")
