"""CertifyAI CLI — attack runner, evidence vault, and compliance reporting."""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

import click
from rich.console import Console
from rich.logging import RichHandler
from rich.panel import Panel
from rich.progress import BarColumn, Progress, SpinnerColumn, TextColumn, TimeElapsedColumn
from rich.style import Style
from rich.table import Table
from rich.text import Text

from certifyai.engine.database.manager import DatabaseManager
from certifyai.engine.database.models import EvidenceChainRecord
from certifyai.engine.models import AttackCategory, AttackStatus, ProviderConfig, RunConfig
from certifyai.engine.runner import AttackRunner

console = Console()


@click.group()
@click.option(
    "-v",
    "--verbose",
    count=True,
    help="Increase verbosity (use -vv for debug).",
)
@click.version_option(package_name="certifyai", prog_name="certifyai")
def cli(verbose: int) -> None:
    """CertifyAI — Continuous Compliance Engine for AI Runtimes.

    Run a battery of red-team attacks against your LLM and generate
    audit-ready compliance evidence.
    """
    log_level = logging.WARNING
    if verbose >= 2:
        log_level = logging.DEBUG
    elif verbose == 1:
        log_level = logging.INFO

    logging.basicConfig(
        level=log_level,
        format="%(message)s",
        datefmt="[%X]",
        handlers=[RichHandler(rich_tracebacks=True)],
    )


async def _add_evidence_chain(db_mgr: DatabaseManager, run_id: str, vault: Any) -> None:
    """Compute and persist an evidence chain entry for the run."""
    import hashlib
    from datetime import UTC, datetime

    # Get previous chain entry for linking
    prev_entry = await db_mgr.get_latest_chain_entry()
    previous_hash = prev_entry.run_hash if prev_entry else "0" * 64

    # Compute run hash from vault evidence files
    run_verification = vault.verify_run(run_id)
    hashes_in_run = []
    run_dir = vault.vault_path / f"run_{run_id}"
    if run_dir.exists():
        for f in sorted(run_dir.glob("*.hash")):
            hashes_in_run.append(f.read_text(encoding="utf-8").strip())
    run_hash_content = "".join(hashes_in_run)

    run_hash = hashlib.sha256(run_hash_content.encode("utf-8")).hexdigest()

    chain = EvidenceChainRecord(
        run_id=run_id,
        previous_hash=previous_hash,
        run_hash=run_hash,
        timestamp=datetime.now(UTC).isoformat(),
        chain_metadata='{"verified": ' + str(run_verification.get("verified", False)).lower() + "}",
    )
    await db_mgr.save_evidence_chain(chain)


def _category_option(value: str | None) -> list[AttackCategory] | None:
    """Parse the --category option into a list of AttackCategory values."""
    if value is None or value.lower() == "all":
        return None
    categories: list[AttackCategory] = []
    for part in value.split(","):
        part = part.strip()
        try:
            categories.append(AttackCategory(part))
        except ValueError as exc:
            raise click.BadParameter(
                f"Invalid category '{part}'. Choices: {', '.join(c.value for c in AttackCategory)}"
            ) from exc
    return categories


def _status_style(status: AttackStatus) -> Style:
    """Return a Rich style for the given attack status."""
    palette = {
        AttackStatus.PASS: Style(color="green", bold=True),
        AttackStatus.FAIL: Style(color="red", bold=True),
        AttackStatus.ERROR: Style(color="yellow", bold=True),
        AttackStatus.SKIPPED: Style(color="grey58", bold=False),
    }
    return palette.get(status, Style())


def _severity_label(severity: str) -> Text:
    """Return a colored Text for severity level."""
    palette = {
        "critical": Text("CRITICAL", style="red bold"),
        "high": Text("HIGH", style="orange3 bold"),
        "medium": Text("MEDIUM", style="yellow bold"),
        "low": Text("LOW", style="green"),
        "info": Text("INFO", style="dim"),
    }
    return palette.get(severity.lower(), Text(severity))


def _build_results_table(
    results: list[Any],
    title: str = "Attack Results",
) -> Table:
    """Build a Rich Table of attack results."""
    table = Table(
        title=title,
        title_style="bold cyan",
        border_style="cyan",
        header_style="bold white on #1a1a2e",
    )
    table.add_column("#", style="dim", width=4)
    table.add_column("Category", style="cyan", no_wrap=True)
    table.add_column("Attack", style="white")
    table.add_column("Status", width=8)
    table.add_column("Severity", width=10)
    table.add_column("Time", justify="right", width=8)
    table.add_column("Evidence", width=10)

    for i, r in enumerate(results, 1):
        status_style = _status_style(r.status)
        status_text = Text(r.status.value.upper(), style=status_style)
        severity = _severity_label(
            r.severity.value if hasattr(r.severity, "value") else str(r.severity)
        )
        time_ms = f"{r.response_time_ms}ms" if r.response_time_ms else "-"
        ev = "stored" if r.evidence_hash else "-"
        table.add_row(
            str(i),
            r.category.value if hasattr(r.category, "value") else str(r.category),
            r.scenario_id,
            status_text,
            severity,
            time_ms,
            ev,
        )
    return table


@cli.command()
@click.option(
    "-p", "--provider", default="openai", help="LLM provider (e.g., openai, anthropic, ollama)."
)
@click.option("-m", "--model", default="gpt-4o", help="Model name.")
@click.option(
    "-k", "--api-key", envvar="CERTIFYAI_API_KEY", help="API key (or set CERTIFYAI_API_KEY)."
)
@click.option("-e", "--endpoint", help="Custom API endpoint (for Ollama / OpenAI-compatible).")
@click.option("--category", help="Attack categories to run (comma-separated), or 'all'.")
@click.option(
    "--plugin-dir",
    multiple=True,
    help="Directory with custom attack plugins (can be specified multiple times).",
    type=click.Path(exists=True, file_okay=False, dir_okay=True),
)
@click.option(
    "--vault",
    default="./certifyai_vault",
    help="Path to evidence vault directory.",
    show_default=True,
)
@click.option("--db", default="certifyai.db", help="Path to SQLite database.", show_default=True)
@click.option("--report", help="Output compliance report to file (JSON).")
@click.option("--framework", default="eu_ai_act", help="Compliance framework for reporting.")
@click.option("--dry-run/--no-dry-run", default=False, help="Simulate without calling LLM.")
@click.option(
    "--concurrency", default=3, help="Number of concurrent LLM calls.", show_default=True, type=int
)
def run(
    provider: str,
    model: str,
    api_key: str | None,
    endpoint: str | None,
    category: str | None,
    plugin_dir: tuple[str, ...],
    vault: str,
    db: str,
    report: str | None,
    framework: str,
    dry_run: bool,
    concurrency: int,
) -> None:
    """Run the attack battery against an LLM endpoint."""
    import asyncio

    provider_cfg = ProviderConfig(
        provider=provider,
        model=model,
        api_key=api_key or "",
        endpoint=endpoint or "",
    )
    config = RunConfig(
        provider=provider_cfg,
        attack_categories=_category_option(category),
        dry_run=dry_run,
        concurrency=concurrency,
    )

    # Build registry with optional external plugin directories
    from certifyai.engine.registry import PluginRegistry

    plugin_dirs_list = [Path(d) for d in plugin_dir] if plugin_dir else []
    registry = PluginRegistry(plugin_dirs=plugin_dirs_list)

    # Header panel
    config_lines = [
        f"[bold cyan]Provider:[/] {provider}",
        f"[bold cyan]Model:[/]    {model}",
        f"[bold cyan]Vault:[/]    {vault}",
        f"[bold cyan]DB:[/]       {db}",
        f"[bold cyan]Dry-run:[/]  {'yes' if dry_run else 'no'}",
    ]
    if category:
        config_lines.append(f"[bold cyan]Categories:[/] {category}")
    if plugin_dirs_list:
        config_lines.append(f"[bold cyan]Plugins:[/] {', '.join(str(d) for d in plugin_dirs_list)}")
    if concurrency:
        config_lines.append(f"[bold cyan]Concurrency:[/] {concurrency}")

    console.print()
    console.print(Panel("\n".join(config_lines), title="[bold]CertifyAI[/]", border_style="cyan"))
    console.print()

    # Initialize database
    db_mgr = DatabaseManager(db)
    asyncio.run(db_mgr.initialize())

    # Progress tracking
    all_results: list[Any] = []
    completed_count = 0

    progress = Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
        TimeElapsedColumn(),
        console=console,
    )

    def _on_progress(scenario_name: str, result: Any) -> None:
        nonlocal completed_count
        completed_count += 1
        all_results.append(result)
        progress.update(task_id, completed=completed_count, description=f"Testing: {scenario_name}")

    # Get scenario count for progress bar
    scenarios = registry.get_scenarios_by_category(config.attack_categories)
    total_prompts = sum(len(s.prompts) for s in scenarios)

    with progress:
        task_id = progress.add_task(
            "[cyan]Running attacks...[/]",
            total=total_prompts or 1,
        )

        runner = AttackRunner(
            config,
            registry=registry,
            db_manager=db_mgr,
            progress_callback=_on_progress,
        )
        if total_prompts == 0:
            console.print("[yellow]No attack scenarios matched the configured categories[/]")
            summary, results_list = asyncio.run(runner.run_all())
        else:
            summary, results_list = asyncio.run(runner.run_all())
            all_results = results_list

    # Store results in evidence vault
    if all_results:
        from certifyai.engine.evidence.vault import EvidenceVault

        vault_path = Path(vault)
        vault_path.mkdir(parents=True, exist_ok=True)
        evidence_vault = EvidenceVault(vault_path)
        evidence_vault.store_batch(all_results)
        console.print(f"  [green]\u2713[/] Evidence stored in: {vault}")

        # Add evidence chain entry to database
        try:
            asyncio.run(_add_evidence_chain(db_mgr, summary.id, evidence_vault))
        except Exception:
            console.print("[yellow]Warning: Could not add evidence chain entry[/]")

    # Close database
    asyncio.run(db_mgr.close())

    # Results summary panel
    summary_lines = [
        f"[bold]Total:[/]  {summary.total_attacks}",
        f"[green]Passed:[/]  {summary.passed}",
        f"[red]Failed:[/]  {summary.failed}",
        f"[yellow]Errors:[/]  {summary.errors}",
    ]
    if summary.overall_score is not None:
        score_color = (
            "green"
            if summary.overall_score >= 0.8
            else "yellow"
            if summary.overall_score >= 0.5
            else "red"
        )
        summary_lines.append(f"\n[bold]Score:[/] [{score_color}]{summary.overall_score:.1%}[/]")

    console.print()
    console.print(
        Panel("\n".join(summary_lines), title="[bold]Run Summary[/]", border_style="green")
    )

    # Per-result table
    if all_results:
        console.print()
        console.print(_build_results_table(all_results))

    # Compliance report
    if report and all_results:
        from certifyai.engine.compliance.mapper import ComplianceMapper

        mapper = ComplianceMapper()
        compliance_report = mapper.generate_report(
            run_id=summary.id,
            framework_id=framework,
            attack_results=all_results,
        )
        import json

        report_path = Path(report)
        report_path.write_text(
            json.dumps(compliance_report.model_dump(mode="json"), indent=2, default=str),
            encoding="utf-8",
        )
        console.print(f"  [green]\u2713[/] Compliance report saved to: {report_path}")
        console.print()


@cli.command()
@click.argument("path", type=click.Path(exists=True), default="./certifyai_vault")
def verify(path: str) -> None:
    """Verify the integrity of the evidence vault."""
    from certifyai.engine.evidence.vault import EvidenceVault

    vault = EvidenceVault(Path(path))
    result = vault.verify_all()

    # Build verification table
    table = Table(
        title="Evidence Vault Verification",
        title_style="bold cyan",
        border_style="cyan",
        header_style="bold white on #1a1a2e",
    )
    table.add_column("Run ID", style="cyan")
    table.add_column("Status", width=10)
    table.add_column("Files", justify="right")
    table.add_column("Mismatches", width=20)

    for run_id, run_result in result.get("runs", {}).items():
        verified = run_result.get("verified", False)
        status = (
            Text("\u2713", style="green bold") if verified else Text("\u2717", style="red bold")
        )
        mismatches = run_result.get("mismatches", [])
        mismatch_text = ", ".join(mismatches[:3]) if mismatches else "-"
        table.add_row(
            run_id,
            status,
            str(run_result.get("total_files", 0)),
            mismatch_text,
        )

    if result.get("verified"):
        console.print(
            f"\n[bold green]\u2713 Vault integrity verified[/] — {result.get('total_runs', 0)} run(s) checked\n"
        )
    else:
        console.print("\n[bold red]\u2717 Vault integrity verification FAILED[/]\n")
    console.print(table)
    console.print()


@cli.command(name="list-categories")
@click.option(
    "--plugin-dir",
    multiple=True,
    help="Directory with custom attack plugins.",
    type=click.Path(exists=True, file_okay=False, dir_okay=True),
)
def list_categories(plugin_dir: tuple[str, ...]) -> None:
    """List all available attack categories and their scenario counts."""
    from certifyai.engine.registry import PluginRegistry

    plugin_dirs_list = [Path(d) for d in plugin_dir] if plugin_dir else []
    registry = PluginRegistry(plugin_dirs=plugin_dirs_list)

    table = Table(
        title="Available Attack Categories",
        title_style="bold cyan",
        border_style="cyan",
        header_style="bold white on #1a1a2e",
    )
    table.add_column("Category", style="cyan bold", width=22)
    table.add_column("# Scenarios", justify="right", width=12)
    table.add_column("Scenarios")

    for cat in registry.list_categories():
        scenarios = registry.get_scenarios_by_category([cat])
        scenario_list = ", ".join(f"{s.id} [{s.severity.value}]" for s in scenarios)
        table.add_row(
            cat.value,
            str(len(scenarios)),
            scenario_list,
        )

    console.print()
    console.print(table)
    console.print()


@cli.command()
@click.option("--framework", default="eu_ai_act", help="Compliance framework.")
@click.option("--provider", default="openai", help="LLM provider.")
@click.option("--model", default="gpt-4o", help="Model name.")
@click.option("--db", default="certifyai.db", help="Path to SQLite database.", show_default=True)
def init(framework: str, provider: str, model: str, db: str) -> None:
    """Initialize a CertifyAI project configuration and database."""
    import asyncio

    async def _init_db() -> None:
        db_mgr = DatabaseManager(db)
        await db_mgr.initialize()
        await db_mgr.close()

    asyncio.run(_init_db())
    console.print(f"[green]\u2713[/] Initialized database: {db}")

    # Create config file
    cfg_path = Path("certifyai.yaml")
    if cfg_path.exists():
        console.print("[yellow]certifyai.yaml already exists[/]")
        return

    cfg: dict[str, Any] = {
        "version": "1",
        "provider": provider,
        "model": model,
        "default_framework": framework,
        "vault_path": "./certifyai_vault",
        "database": db,
    }

    import yaml

    cfg_path.write_text(yaml.dump(cfg, default_flow_style=False), encoding="utf-8")

    # Config summary panel
    config_lines = [
        f"[bold cyan]Provider:[/]   {provider}",
        f"[bold cyan]Model:[/]      {model}",
        f"[bold cyan]Framework:[/]  {framework}",
        f"[bold cyan]Database:[/]   {db}",
    ]
    console.print()
    console.print(
        Panel(
            "\n".join(config_lines),
            title="[bold green]CertifyAI Initialized[/]",
            border_style="green",
        )
    )
    console.print("  Run [bold]certifyai run[/] to start the attack battery.")
    console.print()


if __name__ == "__main__":
    cli()
