"""CertifyAI Textual TUI — rich terminal dashboard for attack monitoring and reporting."""

from __future__ import annotations

from textual.app import App, ComposeResult
from textual.containers import Container, Horizontal
from textual.screen import Screen
from textual.widgets import Footer, Header, Static, TabbedContent, TabPane


class DashboardScreen(Screen):
    """Main dashboard showing attack status and report summaries."""

    def compose(self) -> ComposeResult:
        yield Header()
        yield Container(
            Static("CertifyAI — Continuous Compliance Engine", classes="title"),
            Horizontal(
                Static("Status: Ready", classes="status"),
                Static("Last Run: Never", classes="status"),
                Static("Vault: certifyai_vault/", classes="status"),
                classes="status-bar",
            ),
            TabbedContent(
                TabPane("Dashboard", id="dashboard"),
                TabPane("Attack Logs", id="logs"),
                TabPane("Compliance Reports", id="reports"),
                TabPane("Settings", id="settings"),
            ),
        )
        yield Footer()


class CertifyAIApp(App):
    """CertifyAI TUI application."""

    TITLE = "CertifyAI"
    SUB_TITLE = "Continuous Compliance Engine for AI Runtimes"
    CSS = """
    Screen {
        background: $surface;
    }
    .title {
        text-align: center;
        padding: 1;
        text-style: bold;
        color: $primary-lighten-2;
    }
    .status-bar {
        height: 3;
        padding: 0 1;
        background: $panel;
        border-bottom: solid $primary;
    }
    .status {
        width: 1fr;
        padding: 0 1;
    }
    """

    def compose(self) -> ComposeResult:
        yield Header()
        yield DashboardScreen()
        yield Footer()


def run() -> None:
    """Launch the TUI application."""
    app = CertifyAIApp()
    app.run()


if __name__ == "__main__":
    run()
