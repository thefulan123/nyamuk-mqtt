"""Status card widget."""

from textual.widgets import Static, Label
from textual.containers import Vertical
from textual.app import ComposeResult


class StatusCard(Static):
    """Reusable status card widget."""

    CSS = """
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
    """

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
        try:
            self.query_one("#card-value", Label).update(value)
        except Exception:
            pass
