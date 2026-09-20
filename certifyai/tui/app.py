"""CertifyAI Textual TUI — rich terminal dashboard for attack monitoring and reporting."""

from __future__ import annotations

import contextlib
import logging
import time
from pathlib import Path
from typing import Any, ClassVar

import yaml
from rich.text import Text
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
            with Vertical(classes="dash-card"):
                yield Static("Last Run", classes="dc-label")
                yield Static("—", id="dash-last-run", classes="dc-value fg-blue")
                yield Static("No runs yet", id="dash-last-date", classes="dc-sub")
            with Vertical(classes="dash-card"):
                yield Static("Attacks", classes="dc-label")
                yield Static("0", id="dash-totals", classes="dc-value")
                yield Static("6 categories // 18 scenarios", id="dash-totals-desc", classes="dc-sub")
            with Vertical(classes="dash-card"):
                yield Static("Last Score", classes="dc-label")
                yield Static("—", id="dash-score", classes="dc-value fg-red")
                yield Static("— passed // — failed", id="dash-score-desc", classes="dc-sub")
            with Vertical(classes="dash-card"):
                yield Static("Vault", classes="dc-label")
                yield Static("—", id="dash-vault", classes="dc-value fg-green")
                yield Static("SHA-256 chain intact", id="dash-vault-desc", classes="dc-sub")
        yield Static("RECENT RUNS", classes="section-title")
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
        # Card 1: Last Run
        if last_run is not None:
            self.query_one("#dash-last-run", Static).update(f"{last_run.id[:8]}")
            self.query_one("#dash-last-date", Static).update(
                last_run.started_at[:19] if last_run.started_at else "No date"
            )
        else:
            self.query_one("#dash-last-run", Static).update("—")
            self.query_one("#dash-last-date", Static).update("No runs yet")

        # Card 2: Attacks
        t = stats["total_attacks"]
        self.query_one("#dash-totals", Static).update(f"{t}")

        # Card 3: Last Score
        if last_run is not None:
            score = last_run.overall_score
            score_str = f"{score:.0%}" if score is not None else "N/A"
            score_widget = self.query_one("#dash-score", Static)
            score_widget.update(score_str)
            # Color-coded: red for low, green for high
            if score is not None and score >= 0.7:
                score_widget.remove_class("fg-red")
                score_widget.add_class("fg-green")
            else:
                score_widget.remove_class("fg-green")
                score_widget.add_class("fg-red")
            self.query_one("#dash-score-desc", Static).update(
                f"{last_run.passed} passed // {last_run.failed} failed"
            )
        else:
            self.query_one("#dash-score", Static).update("—")
            self.query_one("#dash-score-desc", Static).update("No runs yet")

        # Card 4: Vault
        vault_dir = self._get_app().vault_path
        if vault_dir.exists():
            vault = EvidenceVault(vault_dir)
            v_result = vault.verify_all()
            integrity = "VERIFIED" if v_result["verified"] else "TAMPERED"
        else:
            integrity = "Not found"
        self.query_one("#dash-vault", Static).update(integrity)

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
        # Main panel: config + buttons + progress bar
        with Container(id="run-config-panel"):
            with Horizontal(id="run-cfg-row"):
                yield Static("PROVIDER: —", id="run-cfg-provider")
                yield Static("MODEL: —", id="run-cfg-model")
                yield Static("CONCURRENCY: —", id="run-cfg-concurrency")
            with Horizontal(id="run-buttons"):
                yield Button(Text(" [ RUN_BATTERY ] "), id="run-start", variant="primary")
                yield Button(Text(" [ DRY_RUN ] "), id="run-dry", variant="default")
                yield Button(Text(" [ HALT ] "), id="run-halt")
            with Horizontal(id="run-progress-row"):
                yield Static("0%", id="run-progress-pct")
                yield ProgressBar(id="run-progress", total=100, show_percentage=False, show_eta=False)
                yield Static("0/0 COMPLETE", id="run-progress-count")
        # Data table panel
        yield DataTable(id="run-scenario-table")
        yield Static(id="run-elapsed")
        yield Static(id="run-current")
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
        self.query_one("#run-config-panel", Container).border_title = " EXECUTION_CONFIG "
        self.query_one("#run-cfg-provider", Static).update(
            f"[#888888]PROVIDER:[/#888888] [bold white]{prov.get('name', '—').upper()}[/bold white]"
        )
        self.query_one("#run-cfg-model", Static).update(
            f"[#888888]MODEL:[/#888888] [bold white]{prov.get('model', '—').upper()}[/bold white]"
        )
        self.query_one("#run-cfg-concurrency", Static).update(
            "[#888888]CONCURRENCY:[/#888888] [bold white]3 THREADS[/bold white]"
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
        self.query_one("#run-scenario-table", DataTable).clear(columns=True)
        self.query_one("#run-summary", Static).update("")
        self.query_one("#run-error", Static).update("")
        self.query_one("#run-progress", ProgressBar).update(progress=0)
        self.query_one("#run-progress-pct", Static).update("0%")
        self.query_one("#run-progress-count", Static).update("0/0 COMPLETE")
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
        category = result.category.value if result.category else "—"
        self._progress_updates.append((scenario_name, result.status.value, category))

    def _process_progress(self) -> None:
        table = self.query_one("#run-scenario-table", DataTable)
        if not table.columns:
            table.add_columns("ID", "SCENARIO", "CATEGORY", "STATUS")

        while self._progress_updates:
            name, status, category = self._progress_updates.pop(0)
            status_colors = {"pass": "green", "fail": "red", "error": "red", "skipped": "grey58"}
            status_color = status_colors.get(status, "white")
            status_display = {"pass": "PASS", "fail": "FAIL", "error": "ERROR", "skipped": "SKIP"}.get(
                status, status.upper()
            )
            row_id = len(table.rows) + 1
            category_display = category.replace("_", " ").upper() if category and category != "—" else "—"
            table.add_row(
                str(row_id).zfill(2),
                name,
                category_display,
                f"[{status_color}]{status_display}[/{status_color}]",
            )
            self.query_one("#run-current", Static).update(f"Current: {name}")

        # Update progress text
        row_count = len(table.rows)
        total = row_count + len(self._progress_updates)
        pct = int((row_count / max(total, 1)) * 100)
        self.query_one("#run-progress", ProgressBar).update(progress=pct)
        self.query_one("#run-progress-pct", Static).update(f"{pct}%")
        self.query_one("#run-progress-count", Static).update(f"{row_count}/{total} COMPLETE")

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
        table.clear(columns=True)
        table.add_columns("ID", "SCENARIO", "CATEGORY", "STATUS")
        for i, r in enumerate(results, 1):
            category_display = r.category.value.replace("_", " ").upper() if r.category else "—"
            status_text = "[green]PASS[/green]" if r.status == AttackStatus.PASS else "[red]FAIL[/red]"
            table.add_row(
                str(i).zfill(2),
                r.scenario_id,
                category_display,
                status_text,
                key=r.id,
            )

        # Update progress bar
        self.query_one("#run-progress", ProgressBar).update(progress=100)
        self.query_one("#run-progress-pct", Static).update("100%")
        self.query_one("#run-progress-count", Static).update(f"{total}/{total} COMPLETE")

    def _get_app(self) -> CertifyAIApp:
        return self.app  # type: ignore[return-value]


# ---------------------------------------------------------------------------
# Results tab
# ---------------------------------------------------------------------------


class ResultsContent(Vertical):
    """Results tab — historical runs table and per-run detail."""

    def compose(self) -> ComposeResult:
        yield Static("HISTORICAL RUNS", classes="section-title")
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
        yield Static("PROVIDER CONFIGURATION", classes="section-title")
        yield Label("Provider (openai / anthropic / ollama)")
        yield Input(id="cfg-provider", placeholder="openai")
        with Container(id="settings-field-row"):
            with Vertical():
                yield Label("Model (e.g. gpt-4o, claude-4, llama3.1)")
                yield Input(id="cfg-model", placeholder="gpt-4o")
            with Vertical():
                yield Label("API Key")
                yield Input(id="cfg-api-key", placeholder="sk-...", password=True)

        yield Static("PATHS", classes="section-title")
        with Container(id="settings-field-row-paths", classes="field-row"):
            with Vertical():
                yield Label("Vault Directory")
                yield Input(id="cfg-vault-path", placeholder=str(DEFAULT_VAULT_PATH))
            with Vertical():
                yield Label("Database Path")
                yield Input(id="cfg-db-path", placeholder=DEFAULT_DB_PATH)

        yield Static("COMPLIANCE FRAMEWORK", classes="section-title")
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

        with Horizontal(id="run-buttons"):
            yield Button("[ SAVE_CONFIGURATION ]", id="cfg-save", variant="primary")
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
    /* ── Stealth Brutalism Theme — Windowed Terminal ── */

    Screen {
        background: #000000;
        layout: vertical;
    }

    /* ── Theme Variables ── */
    $primary: #D4FF00;
    $secondary: #00E5FF;
    $error: #FF0055;
    $surface: #090909;
    $panel: #121212;
    $border: #222222;
    $border-focus: #444444;
    $text: #FFFFFF;
    $text-muted: #888888;
    $text-faint: #444444;

    /* Force auto-height for containers — allows TabPane to size to its content,
       so TabbedContent (overflow-y: auto) can scroll long pages like Settings */
    Container, Vertical {
        height: auto;
    }

    /* ── Outer Frame (windowed terminal with 2px border like mockup) ── */

    #outer-frame {
        border: heavy #444444;
        margin: 1 2;
        background: #000000;
        height: 1fr;
    }

    /* ── TUI Header (prompt + tabs + version — single row, 2px bottom border) ── */

    #tui-header {
        background: #090909;
        border-bottom: heavy #444444;
        height: 3;
        layout: horizontal;
    }

    #header-prompt {
        background: #121212;
        color: #D4FF00;
        text-style: bold;
        width: 5;
        text-align: center;
        padding: 0 1;
        border-right: heavy #444444;
    }

    #header-version {
        color: #444444;
        text-style: bold;
        width: 1fr;
        text-align: right;
        padding: 0 2;
    }

    /* Header tab buttons — styled like mockup tabs (no button chrome) */
    Button.header-tab {
        background: #090909;
        color: #888888;
        border: none;
        border-right: heavy #444444;
        height: 3;
        padding: 0 2;
        text-style: bold;
        min-width: 0;
        margin: 0;
    }

    Button.header-tab:hover {
        background: #121212;
        color: #FFFFFF;
    }

    Button.header-tab.active-tab {
        background: #000000;
        color: #FFFFFF;
        border: none;
        border-bottom: heavy #D4FF00;
        border-right: heavy #444444;
    }

    /* ── Hide TabbedContent's own Tabs (we use custom header buttons) ── */

    TabbedContent {
        background: #000000;
        overflow-y: auto;
    }

    TabPane {
        background: #000000;
        padding: 2 2;
    }

    Tabs {
        height: 0;
        overflow: hidden;
        margin: 0;
        padding: 0;
        border: none;
    }

    /* ── Section Labels (acid green, underlined, like mockup) ── */

    .section-title {
        text-style: bold;
        padding: 0 0 1 0;
        color: #D4FF00;
        border-bottom: heavy #222222;
        margin: 1 0;
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

    /* ── Dashboard Cards (2x2 grid with label/value/sub) ── */

    #dash-cards {
        layout: grid;
        grid-size: 2 2;
        grid-gutter: 2;
        height: auto;
    }

    .dash-card {
        height: 7;
        border: heavy #444444;
        background: #090909;
        padding: 1 2;
    }

    .dc-label {
        color: #888888;
        text-style: bold;
        padding: 0 0 1 0;
    }

    .dc-value {
        text-style: bold;
        color: #FFFFFF;
    }

    .dc-value.fg-blue { color: #00E5FF; }
    .dc-value.fg-green { color: #D4FF00; }
    .dc-value.fg-red { color: #FF0055; }

    .dc-sub {
        color: #444444;
        padding: 1 0 0 0;
    }

    #dash-runs-table {
        height: 14;
        margin: 1 0;
    }

    /* ── Attack Info Grid (PROVIDER / MODEL / CONCURRENCY) ── */

    #run-cfg-row {
        layout: horizontal;
        height: 3;
    }

    #run-cfg-row > Static {
        width: 1fr;
        padding: 1;
        color: #888888;
        text-style: bold;
    }

    /* ── Run Attack Panel (border: solid #D4FF00 with title) ── */

    #run-config-panel {
        border: heavy #D4FF00;
        border-title-color: #D4FF00;
        border-title-style: bold;
        background: #090909;
        padding: 2;
        margin: 1 0;
    }

    /* ── TUI Buttons (match mockup with box-shadow effect) ── */

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

    #run-buttons {
        padding: 1 0;
        height: auto;
    }

    #run-buttons Button {
        width: 24;
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

    /* ── Progress Row (match mockup) ── */

    #run-progress-row {
        height: 3;
        margin: 1 0 0 0;
    }

    #run-progress-pct {
        color: #D4FF00;
        text-style: bold;
        width: 8;
        text-align: center;
    }

    #run-progress-count {
        color: #FFFFFF;
        text-style: bold;
        width: 18;
        text-align: center;
    }

    ProgressBar {
        height: 1;
        margin: 1;
    }

    ProgressBar > .bar {
        background: #222222;
        color: #D4FF00;
    }

    /* ── Run Status / Elapsed / Current ── */

    #run-elapsed, #run-current {
        padding: 0 1;
        color: #888888;
    }

    #run-scenario-table {
        height: 12;
        margin: 1 0;
    }

    /* ── Results Tab Tables ── */

    #results-runs-table {
        height: 14;
        margin: 1 0;
    }

    #results-detail-table {
        height: 10;
        margin: 1 0;
    }

    /* ── Settings Tab (match mockup form layout) ── */

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

    #settings-field-row, .field-row {
        layout: grid;
        grid-size: 2;
        grid-gutter: 2;
        height: auto;
        padding: 0 1;
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

    /* ── Footer (hotkey bar, inside terminal window boundary, 2px top border) ── */

    Footer {
        background: #121212;
        color: #888888;
        border-top: heavy #444444;
        text-style: bold;
        height: 3;
    }

    Footer > .footer--key {
        background: #000000;
        color: #D4FF00;
        text-style: bold;
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
        # Outer frame: windowed terminal with border sitting on black screen
        with Container(id="outer-frame"):
            # Custom header/tab row — prompt, tabs, version in one horizontal bar
            with Container(id="tui-header"):
                yield Static(">_", id="header-prompt")
                # The Tabs widget from TabbedContent is hidden (height:0);
                # these Buttons mirror the mockup's tab bar visually + are clickable
                yield Button("Dashboard", id="tab-dash", classes="header-tab")
                yield Button("Run_Attack", id="tab-run", classes="header-tab")
                yield Button("Results", id="tab-res", classes="header-tab")
                yield Button("Settings", id="tab-set", classes="header-tab")
                yield Static("certifyai-tui // v1.0.4", id="header-version")
            # TabbedContent for automatic content switching (its Tabs are hidden)
            with TabbedContent(initial="dashboard"):
                with TabPane("DASHBOARD", id="dashboard"):
                    yield DashboardContent()
                with TabPane("RUN_ATTACK", id="run"):
                    yield RunAttackContent()
                with TabPane("RESULTS", id="results"):
                    yield ResultsContent()
                with TabPane("SETTINGS", id="settings"):
                    yield SettingsContent()
        # Footer hotkey bar (outside the outer frame to avoid border overlap)
        yield Footer()

    async def on_mount(self) -> None:
        # Mark initial tab as active visually
        with contextlib.suppress(Exception):
            self.query_one("#tab-dash", Button).add_class("active-tab")
        try:
            await self.db_manager.initialize()
        except Exception as exc:
            logger.exception("Database init failed")
            self.notify(f"Database init warning: {exc}", severity="warning")

    async def on_unmount(self) -> None:
        await self.db_manager.close()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle header tab clicks to switch views."""
        tab_ids = {"tab-dash", "tab-run", "tab-res", "tab-set"}
        if event.button.id in tab_ids:
            tab_map = {
                "tab-dash": "dashboard",
                "tab-run": "run",
                "tab-res": "results",
                "tab-set": "settings",
            }
            self.action_switch_tab(tab_map[event.button.id])
            event.stop()

    def action_switch_tab(self, tab: str) -> None:
        """Switch to a named tab and update active visual."""
        tc = self.query_one(TabbedContent)
        tc.active = tab

        # Update header tab active class
        tab_id_map = {
            "dashboard": "tab-dash",
            "run": "tab-run",
            "results": "tab-res",
            "settings": "tab-set",
        }
        for btn_id in tab_id_map.values():
            with contextlib.suppress(Exception):
                self.query_one(f"#{btn_id}", Button).remove_class("active-tab")
        active_id = tab_id_map[tab]
        self.query_one(f"#{active_id}", Button).add_class("active-tab")


def run() -> None:
    """Launch the TUI application."""
    app = CertifyAIApp()
    app.run()


if __name__ == "__main__":
    run()
