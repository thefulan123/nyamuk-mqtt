"""Nyamuk TUI Application - v2.0 Single Broker Focus."""

from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.theme import Theme

from nyamuk.tui.pages.acl import ACLPage
from nyamuk.tui.pages.config import ConfigPage
from nyamuk.tui.pages.create import CreatePage
from nyamuk.tui.pages.home import HomePage
from nyamuk.tui.pages.logs import LogsPage
from nyamuk.tui.pages.users import UsersPage

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
)

PAGE_IDS = ["home", "create", "users", "acl", "config", "logs"]


class NyamukTUI(App):
    """Nyamuk TUI Application - v2.0."""

    TITLE = "Nyamuk - MQTT Broker Factory"
    SUB_TITLE = "Create your MQTT broker in 30 seconds"

    CSS = """
    Screen {
        background: $background;
    }
    #home, #create, #users, #acl, #config, #logs {
        display: none;
    }
    #home.active, #create.active, #users.active, #acl.active, #config.active, #logs.active {
        display: block;
    }
    """

    BINDINGS = [
        Binding("q", "quit", "Quit"),
        Binding("h", "switch_page('home')", "Home"),
        Binding("c", "switch_page('create')", "Create"),
        Binding("u", "switch_page('users')", "Users"),
        Binding("a", "switch_page('acl')", "ACL"),
        Binding("s", "switch_page('config')", "Config"),
        Binding("l", "switch_page('logs')", "Logs"),
    ]

    def compose(self) -> ComposeResult:
        yield HomePage(id="home")
        yield CreatePage(id="create")
        yield UsersPage(id="users")
        yield ACLPage(id="acl")
        yield ConfigPage(id="config")
        yield LogsPage(id="logs")

    def on_mount(self) -> None:
        self.action_switch_page("home")

    def action_switch_page(self, page_name: str) -> None:
        for pid in PAGE_IDS:
            widget = self.query_one(f"#{pid}")
            if pid == page_name:
                widget.add_class("active")
            else:
                widget.remove_class("active")


def main():
    """Run the TUI application."""
    app = NyamukTUI(theme=NYAMUK_THEME)
    app.run()


if __name__ == "__main__":
    main()
