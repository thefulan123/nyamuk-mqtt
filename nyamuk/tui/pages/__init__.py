"""TUI pages package."""

from nyamuk.tui.pages.dashboard import DashboardPage
from nyamuk.tui.pages.config import ConfigPage
from nyamuk.tui.pages.users import UsersPage
from nyamuk.tui.pages.acl import ACLPage
from nyamuk.tui.pages.logs import LogsPage
from nyamuk.tui.pages.settings import SettingsPage

__all__ = [
    "DashboardPage",
    "ConfigPage",
    "UsersPage",
    "ACLPage",
    "LogsPage",
    "SettingsPage",
]
