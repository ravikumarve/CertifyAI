"""CertifyAI Textual TUI — rich terminal dashboard for attack monitoring and reporting."""

from __future__ import annotations

import contextlib
import logging
import time
from pathlib import Path
from typing import Any, ClassVar

import yaml
from textual import work
from textual.app import App, ComposeResult
from textual.containers import Container, Horizontal, Vertical
from textual.message import Message
from textual.reactive import reactive
from textual.widgets import (
    Button,
    DataTable,
    Footer,
    Header,
    Input,
    Label,
    LoadingIndicator,
    ProgressBar,
    Select,
    Static,
    TabbedContent,
    TabPane,
)

from certifyai.engine.database.manager import DEFAULT_DB_PATH, DatabaseManager
from certifyai.engine.database.models import RunRecord
from certifyai.engine.evidence.vault import EvidenceVault
from certifyai.engine.models import (
    AttackCategory,
    AttackResult,
    AttackStatus,
    ProviderConfig,
    RunConfig,
    RunSummary,
)
from certifyai.engine.registry import PluginRegistry
from certifyai.engine.runner import AttackRunner

logger = logging.getLogger(__name__)

CONFIG_PATH = Path("certifyai.yaml")
DEFAULT_VAULT_PATH = Path("certifyai_vault")

CONFIG_TEMPLATE = {
    "provider": {"name": "openai", "model": "gpt-4o", "api_key": ""},
    "paths": {"vault": str(DEFAULT_VAULT_PATH), "database": DEFAULT_DB_PATH},
    "frameworks": ["eu_ai_act", "soc2", "nist_ai_rmf"],
}


def load_config() -> dict[str, Any]:
    """Load configuration from certifyai.yaml, returning defaults if not found."""
    if CONFIG_PATH.exists():
        with CONFIG_PATH.open() as f:
            return yaml.safe_load(f) or dict(CONFIG_TEMPLATE)
    return dict(CONFIG_TEMPLATE)


def save_config(cfg: dict[str, Any]) -> None:
    """Write configuration to certifyai.yaml."""
    with CONFIG_PATH.open("w") as f:
        yaml.safe_dump(cfg, f, default_flow_style=False)


# ---------------------------------------------------------------------------
# Custom messages
# ---------------------------------------------------------------------------


class AttackProgress(Message):
    """Sent during an attack run to report per-scenario progress."""

    def __init__(self, scenario_name: str, status: str) -> None:
        super().__init__()
        self.scenario_name = scenario_name
        self.status = status


class AttackFinished(Message):
    """Sent when an attack run completes."""

    def __init__(self, summary: RunSummary, results: list[AttackResult]) -> None:
        super().__init__()
        self.summary = summary
        self.results = results


class RunSelected(Message):
    """Sent when a user clicks a run in the results table."""

    def __init__(self, run_id: str) -> None:
        super().__init__()
        self.run_id = run_id


# ---------------------------------------------------------------------------
# Dashboard tab
# ---------------------------------------------------------------------------


class DashboardContent(Vertical):
    """Dashboard tab — status cards, vault info, recent runs."""

    def compose(self) -> ComposeResult:
        with Container(id="dash-cards"):
            yield Static("Loading…", id="dash-last-run", classes="dash-card")
            yield Static("Loading…", id="dash-totals", classes="dash-card")
            yield Static("Loading…", id="dash-score", classes="dash-card")
            yield Static("Loading…", id="dash-vault", classes="dash-card")
        yield Static("Recent Runs", classes="section-title")
        yield LoadingIndicator(id="dash-loading")
        yield DataTable(id="dash-runs-table")
        yield Static("", id="dash-error", classes="error-text")

    async def on_mount(self) -> None:
        self.set_interval(5, self._refresh_dashboard)
        await self._refresh_dashboard()

    def _get_app(self) -> CertifyAIApp:
        return self.app  # type: ignore[return-value]

    async def _refresh_dashboard(self) -> None:
        error_label = self.query_one("#dash-error", Static)
        loading = self.query_one("#dash-loading", LoadingIndicator)
        db = self._get_app().db_manager

        try:
            if not db.is_initialized:
                await db.initialize()

            loading.display = True

            stats = await db.get_run_summary_stats()
            runs = await db.list_runs(limit=5)

            last_run = runs[0] if runs else None
            self._update_status_cards(stats, last_run)
            self._update_runs_table(runs)
            error_label.update("")
        except Exception as exc:
            logger.exception("Dashboard refresh failed")
            error_label.update(f"Dashboard error: {exc}")
        finally:
            loading.display = False

    def _update_status_cards(self, stats: dict[str, Any], last_run: RunRecord | None) -> None:
        self.query_one("#dash-last-run", Static).update(
            f"[bold]Last Run[/bold]\n{'Never' if last_run is None else last_run.started_at[:19]}"
        )

        t = stats["total_attacks"]
        p = stats["total_passed"]
        f = stats["total_failed"]
        e = stats["total_errors"]
        self.query_one("#dash-totals", Static).update(
            f"[bold]Attacks[/bold]\n"
            f"Total: {t}  [green]Pass: {p}[/green]  "
            f"[red]Fail: {f}[/red]  [yellow]Err: {e}[/yellow]"
        )

        if last_run is not None:
            score = last_run.overall_score
            score_str = f"{score:.0%}" if score is not None else "N/A"
            status_color = "green" if last_run.status == "completed" else "red"
            self.query_one("#dash-score", Static).update(
                f"[bold]Last Score[/bold]\n"
                f"[{status_color}]{last_run.status.upper()}[/{status_color}]  "
                f"Score: {score_str}"
            )
        else:
            self.query_one("#dash-score", Static).update("[bold]Last Score[/bold]\nNo runs yet")

        vault_dir = self._get_app().vault_path
        if vault_dir.exists():
            vault = EvidenceVault(vault_dir)
            v_result = vault.verify_all()
            integrity = "VERIFIED" if v_result["verified"] else "TAMPERED"
        else:
            integrity = "Not found"
        self.query_one("#dash-vault", Static).update(
            f"[bold]Vault[/bold]\nRuns: {stats['total_runs']}  Integrity: {integrity}"
        )

    def _update_runs_table(self, runs: list[RunRecord]) -> None:
        table = self.query_one("#dash-runs-table", DataTable)
        table.clear()
        if not table.columns:
            table.add_columns("ID", "Date", "Status", "Score", "Total", "Passed", "Failed")

        for r in runs:
            score = f"{r.overall_score:.0%}" if r.overall_score is not None else "-"
            status_icon = {
                "completed": "PASS",
                "failed": "FAIL",
                "running": "RUN",
                "pending": "--",
            }.get(r.status, "??")
            table.add_row(
                r.id[:8],
                r.started_at[:19],
                status_icon,
                score,
                str(r.total_attacks),
                str(r.passed),
                str(r.failed),
                key=r.id,
            )


# ---------------------------------------------------------------------------
# Run Attack tab
# ---------------------------------------------------------------------------


class RunAttackContent(Vertical):
    """Run Attack tab — trigger runs, watch progress, see results."""

    running = reactive(False)

    def compose(self) -> ComposeResult:
        yield Static("Attack Run", classes="section-title")
        with Container(id="run-config-summary"):
            yield Static("PROVIDER: —", id="run-cfg-provider")
            yield Static("MODEL: —", id="run-cfg-model")
            yield Static("CONCURRENCY: —", id="run-cfg-concurrency")
        with Horizontal(id="run-buttons"):
            yield Button(" [ RUN_BATTERY ] ", id="run-start", variant="primary")
            yield Button(" [ DRY_RUN ] ", id="run-dry", variant="default")
            yield Button(" [ HALT ] ", id="run-halt")
        yield Static(id="run-progress-text", classes="status-text")
        yield ProgressBar(id="run-progress", total=100, show_percentage=False, show_eta=False)
        yield Static(id="run-elapsed")
        yield Static(id="run-current")
        yield Static(id="run-status", classes="section-title")
        yield DataTable(id="run-scenario-table")
        yield Static("", id="run-summary", classes="run-summary-box")
        yield Static("", id="run-error", classes="error-text")

    def on_mount(self) -> None:
        self._progress_updates: list[tuple[str, str]] = []
        self._start_time: float = 0.0
        self.set_interval(0.3, self._process_progress)
        self.set_interval(1.0, self._update_elapsed)
        self._load_config_summary()

    def _load_config_summary(self) -> None:
        cfg = load_config()
        prov = cfg.get("provider", {})
        self.query_one("#run-config-summary", Container).border_title = "EXECUTION_CONFIG"
        self.query_one("#run-cfg-provider", Static).update(
            f"PROVIDER: [bold]{prov.get('name', '—').upper()}[/bold]"
        )
        self.query_one("#run-cfg-model", Static).update(
            f"MODEL: [bold]{prov.get('model', '—').upper()}[/bold]"
        )
        self.query_one("#run-cfg-concurrency", Static).update(
            "CONCURRENCY: [bold]3 THREADS[/bold]"
        )

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "run-start":
            self._start_run(dry_run=False)
        elif event.button.id == "run-dry":
            self._start_run(dry_run=True)
        elif event.button.id == "run-halt":
            if self.running:
                self.app.notify("Halt requested — cancelling attack", severity="warning")
                self.running = False
                self.query_one("#run-current", Static).update("HALTED")
            else:
                self.app.notify("No attack running", severity="information")

    def _start_run(self, dry_run: bool) -> None:
        if self.running:
            self.app.notify("Attack run already in progress", severity="warning")
            return
        self.running = True
        self._progress_updates.clear()
        self._start_time = time.monotonic()
        self.query_one("#run-scenario-table", DataTable).clear()
        self.query_one("#run-summary", Static).update("")
        self.query_one("#run-error", Static).update("")
        self.query_one("#run-progress", ProgressBar).update(progress=0)
        self.query_one("#run-progress-text", Static).update("0% — 0/0 COMPLETE")
        self.query_one("#run-elapsed", Static).update("Elapsed: 00:00")
        self.query_one("#run-current", Static).update("Starting…")
        self.run_attack_worker(dry_run)

    @work(exclusive=True, group="attack")
    async def run_attack_worker(self, dry_run: bool) -> None:
        db = self._get_app().db_manager
        try:
            if not db.is_initialized:
                await db.initialize()

            cfg = load_config()
            prov_cfg = cfg.get("provider", {})
            frameworks = cfg.get("frameworks", ["eu_ai_act", "soc2", "nist_ai_rmf"])
            categories_str = cfg.get("attack_categories", None)

            attack_categories = None
            if categories_str:
                attack_categories = []
                for c in categories_str:
                    with contextlib.suppress(ValueError):
                        attack_categories.append(AttackCategory(c))

            provider = ProviderConfig(
                provider=prov_cfg.get("name", "openai"),
                model=prov_cfg.get("model", "gpt-4o"),
                api_key=prov_cfg.get("api_key", None) or None,
            )

            run_config = RunConfig(
                provider=provider,
                frameworks=frameworks,
                attack_categories=attack_categories,
                concurrency=5,
                dry_run=dry_run,
            )

            registry = PluginRegistry()
            vault_path = Path(cfg.get("paths", {}).get("vault", str(DEFAULT_VAULT_PATH)))
            vault = EvidenceVault(vault_path)

            runner = AttackRunner(
                config=run_config,
                registry=registry,
                db_manager=db,
                progress_callback=self._on_progress,
            )

            self.app.notify(
                f"Starting {'dry-run' if dry_run else 'full'} attack…",
                severity="information",
            )

            summary, results = await runner.run_all()

            for r in results:
                vault.store(r)

            self.post_message(AttackFinished(summary, results))

        except Exception as exc:
            logger.exception("Attack worker failed")
            self.app.notify(f"Attack failed: {exc}", severity="error")
            self.query_one("#run-error", Static).update(f"Error: {exc}")
        finally:
            self.running = False
            self.query_one("#run-current", Static).update("")

    def _on_progress(self, scenario_name: str, result: AttackResult) -> None:
        self._progress_updates.append((scenario_name, result.status.value))

    def _process_progress(self) -> None:
        table = self.query_one("#run-scenario-table", DataTable)
        if not table.columns:
            table.add_columns("Scenario", "Status", "Severity", "Time (ms)")

        while self._progress_updates:
            name, status = self._progress_updates.pop(0)
            status_display = {"pass": "PASS", "fail": "FAIL", "error": "ERROR"}.get(status, status.upper())
            table.add_row(name, status_display, "", "")
            self.query_one("#run-current", Static).update(f"Current: {name}")

        # Update progress text
        row_count = len(table.rows)
        total = row_count + len(self._progress_updates)
        pct = int((row_count / max(total, 1)) * 100)
        self.query_one("#run-progress", ProgressBar).update(progress=pct)
        self.query_one("#run-progress-text", Static).update(
            f"{pct}% — {row_count}/{total} COMPLETE"
        )

    def _update_elapsed(self) -> None:
        if not self.running:
            return
        elapsed = int(time.monotonic() - self._start_time)
        mins, secs = divmod(elapsed, 60)
        self.query_one("#run-elapsed", Static).update(f"Elapsed: {mins:02d}:{secs:02d}")

    def on_attack_finished(self, message: AttackFinished) -> None:
        summary = message.summary
        results = message.results
        total = summary.total_attacks
        passed = summary.passed
        failed = summary.failed
        errors = summary.errors
        score = summary.overall_score

        score_str = f"{score:.0%}" if score is not None else "N/A"
        summary_text = (
            f"[bold]Run Complete[/bold] — ID: {summary.id[:8]}\n"
            f"Total: {total}  [green]Passed: {passed}[/green]  "
            f"[red]Failed: {failed}[/red]  [yellow]Errors: {errors}[/yellow]\n"
            f"Score: {score_str}"
        )
        self.query_one("#run-summary", Static).update(summary_text)
        self.app.notify(
            f"Run complete: {passed}/{total} passed ({score_str})",
            severity="information",
        )

        # Update scenario table with full results
        table = self.query_one("#run-scenario-table", DataTable)
        table.clear()
        table.add_columns("Scenario", "Status", "Severity", "Time (ms)")
        for r in results:
            sev_icon = {"critical": "CRT", "high": "HIGH", "medium": "MED", "low": "LOW"}.get(
                r.severity.value, "---"
            )
            status_text = "PASS" if r.status == AttackStatus.PASS else "FAIL"
            table.add_row(
                r.scenario_id,
                status_text,
                sev_icon,
                str(r.response_time_ms or ""),
                key=r.id,
            )

        # Update progress bar
        pb = self.query_one("#run-progress", ProgressBar)
        pb.update(progress=100)
        pct_text = self.query_one("#run-progress-text", Static)
        pct_text.update(f"100% — {total}/{total} COMPLETE")

    def _get_app(self) -> CertifyAIApp:
        return self.app  # type: ignore[return-value]


# ---------------------------------------------------------------------------
# Results tab
# ---------------------------------------------------------------------------


class ResultsContent(Vertical):
    """Results tab — historical runs table and per-run detail."""

    def compose(self) -> ComposeResult:
        yield Static("Historical Runs", classes="section-title")
        yield LoadingIndicator(id="results-loading")
        yield DataTable(id="results-runs-table")
        yield Static("", id="results-detail-title", classes="section-title")
        yield DataTable(id="results-detail-table")
        yield Static("", id="results-error", classes="error-text")

    async def on_mount(self) -> None:
        await self._load_runs()

    def _get_app(self) -> CertifyAIApp:
        return self.app  # type: ignore[return-value]

    async def _load_runs(self) -> None:
        loading = self.query_one("#results-loading", LoadingIndicator)
        error_label = self.query_one("#results-error", Static)
        db = self._get_app().db_manager

        try:
            if not db.is_initialized:
                await db.initialize()

            loading.display = True
            runs = await db.list_runs(limit=100)
            table = self.query_one("#results-runs-table", DataTable)
            table.clear()
            if not table.columns:
                table.add_columns(
                    "Run ID", "Date", "Status", "Score", "Total", "Passed", "Failed", "Errors"
                )

            for r in runs:
                score = f"{r.overall_score:.0%}" if r.overall_score is not None else "-"
                status_icon = {
                    "completed": "PASS",
                    "failed": "FAIL",
                    "running": "RUN",
                    "pending": "--",
                }.get(r.status, "??")
                table.add_row(
                    r.id[:12],
                    r.started_at[:19],
                    status_icon,
                    score,
                    str(r.total_attacks),
                    str(r.passed),
                    str(r.failed),
                    str(r.errors),
                    key=r.id,
                )

            error_label.update("")
        except Exception as exc:
            logger.exception("Failed to load results list")
            error_label.update(f"Error loading runs: {exc}")
        finally:
            loading.display = False

    def on_data_table_row_selected(self, event: DataTable.RowSelected) -> None:
        if event.row_key.value is None:
            return
        table_id = event.data_table.id
        if table_id == "results-runs-table":
            run_id = str(event.row_key.value)
            self._load_detail(run_id)

    async def _load_detail(self, run_id: str) -> None:
        db = self._get_app().db_manager
        error_label = self.query_one("#results-error", Static)
        try:
            results = await db.get_results_by_run(run_id)
            detail_table = self.query_one("#results-detail-table", DataTable)
            detail_table.clear()
            if not detail_table.columns:
                detail_table.add_columns(
                    "Scenario", "Attack", "Category", "Status", "Severity", "Time (ms)"
                )

            for r in results:
                status_text = "PASS" if r.status == "pass" else "FAIL"
                detail_table.add_row(
                    r.scenario_id,
                    r.attack_name,
                    r.category,
                    status_text,
                    r.severity,
                    str(r.response_time_ms or ""),
                )

            self.query_one("#results-detail-title", Static).update(
                f"Run Detail: {run_id[:12]} ({len(results)} attacks)"
            )
            error_label.update("")
        except Exception as exc:
            logger.exception("Failed to load run detail")
            error_label.update(f"Error loading detail: {exc}")


# ---------------------------------------------------------------------------
# Settings tab
# ---------------------------------------------------------------------------


class SettingsContent(Vertical):
    """Settings tab — configure provider, paths, frameworks."""

    def compose(self) -> ComposeResult:
        yield Static("Provider Configuration", classes="section-title")
        yield Label("Provider (openai / anthropic / ollama)")
        yield Input(id="cfg-provider", placeholder="openai")
        yield Label("Model (e.g. gpt-4o, claude-4, llama3.1)")
        yield Input(id="cfg-model", placeholder="gpt-4o")
        yield Label("API Key")
        yield Input(id="cfg-api-key", placeholder="sk-...", password=True)

        yield Static("Paths", classes="section-title")
        yield Label("Vault Directory")
        yield Input(id="cfg-vault-path", placeholder=str(DEFAULT_VAULT_PATH))
        yield Label("Database Path")
        yield Input(id="cfg-db-path", placeholder=DEFAULT_DB_PATH)

        yield Static("Compliance Framework", classes="section-title")
        yield Select(
            id="cfg-framework",
            options=[
                ("EU AI Act", "eu_ai_act"),
                ("SOC 2 Type II", "soc2"),
                ("NIST AI RMF", "nist_ai_rmf"),
                ("All Frameworks", "all"),
            ],
            value="all",
        )

        yield Button("Save Configuration", id="cfg-save", variant="primary")
        yield Static("", id="cfg-status", classes="status-text")

    def on_mount(self) -> None:
        self._load_settings()

    def _load_settings(self) -> None:
        cfg = load_config()
        prov = cfg.get("provider", {})
        paths = cfg.get("paths", {})

        self.query_one("#cfg-provider", Input).value = prov.get("name", "openai")
        self.query_one("#cfg-model", Input).value = prov.get("model", "gpt-4o")
        self.query_one("#cfg-api-key", Input).value = prov.get("api_key", "")
        self.query_one("#cfg-vault-path", Input).value = paths.get("vault", str(DEFAULT_VAULT_PATH))
        self.query_one("#cfg-db-path", Input).value = paths.get("database", DEFAULT_DB_PATH)

        # Set framework
        frameworks = cfg.get("frameworks", ["eu_ai_act", "soc2", "nist_ai_rmf"])
        if len(frameworks) == 1:
            self.query_one("#cfg-framework", Select).value = frameworks[0]
        else:
            self.query_one("#cfg-framework", Select).value = "all"

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "cfg-save":
            self._save_settings()

    def _save_settings(self) -> None:
        provider_name = self.query_one("#cfg-provider", Input).value.strip()
        model = self.query_one("#cfg-model", Input).value.strip()
        api_key = self.query_one("#cfg-api-key", Input).value.strip()
        vault_path = self.query_one("#cfg-vault-path", Input).value.strip()
        db_path = self.query_one("#cfg-db-path", Input).value.strip()
        framework_value = self.query_one("#cfg-framework", Select).value

        if not provider_name:
            self.query_one("#cfg-status", Static).update("Provider is required")
            return
        if not model:
            self.query_one("#cfg-status", Static).update("Model is required")
            return

        if framework_value == "all" or framework_value is None:
            frameworks = ["eu_ai_act", "soc2", "nist_ai_rmf"]
        else:
            frameworks = [str(framework_value)]

        cfg = {
            "provider": {
                "name": provider_name,
                "model": model,
                "api_key": api_key,
            },
            "paths": {
                "vault": vault_path or str(DEFAULT_VAULT_PATH),
                "database": db_path or DEFAULT_DB_PATH,
            },
            "frameworks": frameworks,
        }

        try:
            save_config(cfg)
            self.query_one("#cfg-status", Static).update(
                "[green]Configuration saved to certifyai.yaml[/green]"
            )
            self.app.notify("Configuration saved", severity="information")
        except Exception as exc:
            logger.exception("Failed to save config")
            self.query_one("#cfg-status", Static).update(f"[red]Save failed: {exc}[/red]")


# ---------------------------------------------------------------------------
# Main App
# ---------------------------------------------------------------------------


class CertifyAIApp(App):
    """CertifyAI TUI — continuous compliance engine for AI runtimes."""

    TITLE = "CertifyAI"
    SUB_TITLE = "Continuous Compliance Engine for AI Runtimes"
    CSS = """
    /* ── Stealth Brutalism Theme ── */

    Screen {
        background: #000000;
        border: solid #090909;
    }

    /* Override Textual theme variables */
    $primary: #D4FF00;
    $secondary: #00E5FF;
    $error: #FF0055;
    $surface: #090909;
    $panel: #121212;
    $boost: #222222;
    $text: #FFFFFF;
    $text-muted: #888888;
    $border: #222222;

    /* ── Typography ── */

    .section-title {
        text-style: bold;
        padding: 1 0 0 1;
        color: #D4FF00;
        border-bottom: solid #444444;
    }

    .error-text {
        color: #FF0055;
        padding: 0 1;
    }

    .status-text {
        padding: 1;
    }

    .run-summary-box {
        padding: 1;
        margin: 1 0;
        border: solid #444444;
        background: #121212;
    }

    /* ── Dashboard Cards ── */

    #dash-cards {
        layout: grid;
        grid-size: 2 2;
        grid-gutter: 1;
        height: auto;
        padding: 1;
    }

    .dash-card {
        height: 5;
        border: solid #222222;
        background: #090909;
        padding: 1;
    }

    .dash-card:hover {
        border: solid #444444;
        background: #121212;
    }

    #dash-runs-table {
        height: 12;
    }

    /* ── Run Attack Tab ── */

    #run-config-summary {
        layout: horizontal;
        height: 3;
        background: #121212;
        border: solid #222222;
    }

    #run-config-summary > Static {
        width: 1fr;
        padding: 1;
        color: #888888;
        text-style: bold;
    }

    #run-buttons {
        padding: 1;
        height: auto;
    }

    #run-buttons Button {
        width: 18;
        margin: 0 1 0 0;
    }

    #run-halt {
        background: #090909;
        color: #FF0055;
        border: solid #FF0055;
        text-style: bold;
        dock: right;
    }

    #run-halt:hover {
        background: #FF0055;
        color: #000000;
    }

    Button {
        height: 3;
        background: #090909;
        color: #FFFFFF;
        border: solid #222222;
        text-style: bold;
    }

    Button:hover {
        background: #121212;
        border: solid #444444;
    }

    Button.-primary {
        background: #090909;
        color: #D4FF00;
        border: solid #D4FF00;
    }

    Button.-primary:hover {
        background: #D4FF00;
        color: #000000;
    }

    #run-elapsed, #run-current {
        padding: 0 1;
        color: #888888;
    }

    #run-scenario-table {
        height: 12;
    }

    /* ── Progress Bar ── */

    ProgressBar {
        height: 1;
        margin: 1 0;
    }

    ProgressBar > .bar {
        background: #222222;
        color: #D4FF00;
    }

    /* ── Results Tab ── */

    #results-runs-table {
        height: 14;
    }

    #results-detail-table {
        height: 10;
    }

    /* ── Settings Tab ── */

    SettingsContent Input, SettingsContent Select {
        margin: 0 1 0 1;
    }

    Input, Select {
        background: #090909;
        color: #FFFFFF;
        border: solid #222222;
    }

    Input:focus, Select:focus {
        border: solid #444444;
    }

    SettingsContent Label {
        padding: 1 1 0 1;
        color: #888888;
    }

    #cfg-save {
        margin: 1;
        width: 24;
    }

    /* ── Data Tables ── */

    DataTable {
        background: #090909;
        border: solid #222222;
    }

    DataTable > .datatable--header {
        background: #121212;
        color: #888888;
        text-style: bold;
    }

    DataTable > .datatable--row:hover {
        background: #121212;
    }

    DataTable > .datatable--row-highlight {
        background: #1a1a1a;
    }

    /* ── Tab Content ── */

    Vertical {
        padding: 0 1;
    }

    TabbedContent {
        background: #000000;
    }

    TabPane {
        background: #000000;
    }

    Tabs {
        background: #090909;
    }

    Tabs Tab {
        height: 3;
        background: #090909;
        color: #888888;
        border: solid #222222;
        text-style: bold;
        padding: 0 2;
    }

    Tabs Tab:hover {
        background: #121212;
        color: #FFFFFF;
    }

    Tabs Tab.-active {
        background: #000000;
        color: #D4FF00;
        border: solid #444444;
        border-bottom: solid #D4FF00;
    }

    /* ── Header & Footer ── */

    Header {
        background: #090909;
        color: #D4FF00;
        border-bottom: solid #222222;
    }

    Footer {
        background: #121212;
        color: #888888;
        border-top: solid #222222;
    }

    Footer > .footer--key {
        background: #000000;
        color: #D4FF00;
        border: solid #222222;
    }

    /* ── Loading Indicator ── */

    LoadingIndicator {
        height: 1;
    }

    /* ── Select / Dropdown ── */

    Select > .select-current {
        background: #090909;
        color: #FFFFFF;
    }

    Select > .select-menu {
        background: #121212;
        border: solid #222222;
    }

    Select > .select-menu > .select-item:hover {
        background: #1a1a1a;
        color: #D4FF00;
    }
    """

    BINDINGS: ClassVar[list[tuple[str, str, str]]] = [
        ("d", "switch_tab('dashboard')", "Dashboard"),
        ("r", "switch_tab('run')", "Run Attack"),
        ("t", "switch_tab('results')", "Results"),
        ("s", "switch_tab('settings')", "Settings"),
        ("q", "quit", "Quit"),
    ]

    def __init__(self, db_path: str = DEFAULT_DB_PATH) -> None:
        super().__init__()
        self.db_manager = DatabaseManager(db_path)
        cfg = load_config()
        vault_str = cfg.get("paths", {}).get("vault", str(DEFAULT_VAULT_PATH))
        self.vault_path = Path(vault_str)

    def compose(self) -> ComposeResult:
        yield Header()
        with TabbedContent(initial="dashboard"):
            with TabPane("DASHBOARD", id="dashboard"):
                yield DashboardContent()
            with TabPane("RUN_ATTACK", id="run"):
                yield RunAttackContent()
            with TabPane("RESULTS", id="results"):
                yield ResultsContent()
            with TabPane("SETTINGS", id="settings"):
                yield SettingsContent()
        yield Footer()

    async def on_mount(self) -> None:
        try:
            await self.db_manager.initialize()
        except Exception as exc:
            logger.exception("Database init failed")
            self.notify(f"Database init warning: {exc}", severity="warning")

    async def on_unmount(self) -> None:
        await self.db_manager.close()

    def action_switch_tab(self, tab: str) -> None:
        """Switch to a named tab."""
        tc = self.query_one(TabbedContent)
        tc.active = tab


def run() -> None:
    """Launch the TUI application."""
    app = CertifyAIApp()
    app.run()


if __name__ == "__main__":
    run()
