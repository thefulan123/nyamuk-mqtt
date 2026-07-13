"""TUI Dashboard for Nyamuk MQTT Manager."""

from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.theme import Theme

from nyamuk.tui.pages.dashboard import DashboardPage
from nyamuk.tui.pages.config import ConfigPage
from nyamuk.tui.pages.users import UsersPage
from nyamuk.tui.pages.acl import ACLPage
from nyamuk.tui.pages.logs import LogsPage
from nyamuk.tui.pages.settings import SettingsPage


NYAMUK_THEME = Theme(
    name="nyamuk",
    primary="#3cb371",
    secondary="#2e8b57",
    accent="#228b22",
    background="#1e1e2e",
    surface="#2d2d44",
    panel="#1e1e2e",
    success="#3cb371",
    warning="#ffa500",
    error="#ff6347",
    text="#ffffff",
    text-muted="#888888",
)


class NyamukTUI(App):
    """Nyamuk TUI Application."""

    TITLE = "🦟 Nyamuk - MQTT Manager"
    SUB_TITLE = "Mosquitto Configuration & Monitoring"

    CSS = """
    Screen {
        background: $background;
    }
    """

    BINDINGS = [
        Binding("q", "quit", "Quit"),
        Binding("d", "switch_page('dashboard')", "Dashboard"),
        Binding("c", "switch_page('config')", "Config"),
        Binding("u", "switch_page('users')", "Users"),
        Binding("a", "switch_page('acl')", "ACL"),
        Binding("l", "switch_page('logs')", "Logs"),
        Binding("s", "switch_page('settings')", "Settings"),
    ]

    def compose(self) -> ComposeResult:
        yield DashboardPage(id="dashboard")
        yield ConfigPage(id="config")
        yield UsersPage(id="users")
        yield ACLPage(id="acl")
        yield LogsPage(id="logs")
        yield SettingsPage(id="settings")

    def on_mount(self) -> None:
        self.switch_page("dashboard")

    def action_switch_page(self, page_name: str) -> None:
        self.switch_page(page_name)


def main():
    """Run the TUI application."""
    app = NyamukTUI(theme=NYAMUK_THEME)
    app.run()


if __name__ == "__main__":
    main()
