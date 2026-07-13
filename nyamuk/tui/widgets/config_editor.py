"""Config editor widget."""

from textual.app import ComposeResult
from textual.widgets import Label, Static, TextArea


class ConfigEditor(Static):
    """Configuration file editor widget."""

    CSS = """
    ConfigEditor {
        height: 1fr;
        border: solid $accent;
    }
    .editor-header {
        text-style: bold;
        color: $primary;
        margin-bottom: 1;
    }
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._content: str = ""

    def compose(self) -> ComposeResult:
        yield Label("Configuration Editor", classes="editor-header")
        yield TextArea(id="config-textarea", language="yaml")

    def load_content(self, content: str):
        """Load content into editor."""
        self._content = content
        try:
            self.query_one("#config-textarea", TextArea).text = content
        except Exception:
            pass

    def get_content(self) -> str:
        """Get current editor content."""
        try:
            text: str = self.query_one("#config-textarea", TextArea).text
            return text
        except Exception:
            return self._content
