"""CertifyAI CLI — attack runner, evidence vault, and compliance reporting."""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

import click
from rich.console import Console
from rich.logging import RichHandler

from certifyai.engine.models import AttackCategory, ProviderConfig, RunConfig
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


def _category_option(value: str | None) -> list[AttackCategory] | None:
    """Parse the --category option into a list of AttackCategory values."""
    if value is None or value.lower() == "all":
        return None
    categories: list[AttackCategory] = []
    for part in value.split(","):
        part = part.strip()
        try:
            categories.append(AttackCategory(part))
        except ValueError:
            raise click.BadParameter(
                f"Invalid category '{part}'. Choices: {', '.join(c.value for c in AttackCategory)}"
            )
    return categories


@cli.command()
@click.option("-p", "--provider", default="openai", help="LLM provider (e.g., openai, anthropic, ollama).")
@click.option("-m", "--model", default="gpt-4o", help="Model name.")
@click.option("-k", "--api-key", envvar="CERTIFYAI_API_KEY", help="API key (or set CERTIFYAI_API_KEY).")
@click.option("-e", "--endpoint", help="Custom API endpoint (for Ollama / OpenAI-compatible).")
@click.option("--category", help="Attack categories to run (comma-separated), or 'all'.")
@click.option("--plugin-dir", multiple=True, help="Directory with custom attack plugins (can be specified multiple times).", type=click.Path(exists=True, file_okay=False, dir_okay=True))
@click.option("--vault", default="./certifyai_vault", help="Path to evidence vault directory.", show_default=True)
@click.option("--report", help="Output compliance report to file (JSON).")
@click.option("--framework", default="eu_ai_act", help="Compliance framework for reporting.")
@click.option("--dry-run/--no-dry-run", default=False, help="Simulate without calling LLM.")
def run(
    provider: str,
    model: str,
    api_key: str | None,
    endpoint: str | None,
    category: str | None,
    plugin_dir: tuple[str, ...],
    vault: str,
    report: str | None,
    framework: str,
    dry_run: bool,
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
    )

    # Build registry with optional external plugin directories
    from certifyai.engine.registry import PluginRegistry

    plugin_dirs_list = [Path(d) for d in plugin_dir] if plugin_dir else []
    registry = PluginRegistry(plugin_dirs=plugin_dirs_list)

    console.print("[bold cyan]CertifyAI[/] — Running attack battery")
    console.print(f"  Provider: {provider} | Model: {model}")
    console.print(f"  Vault:    {vault}")
    if category:
        console.print(f"  Categories: {category}")
    if plugin_dirs_list:
        console.print(f"  Custom plugins: {', '.join(str(d) for d in plugin_dirs_list)}")
    console.print()

    runner = AttackRunner(config, registry=registry)
    summary, results = asyncio.run(runner.run_all())

    # Store results in evidence vault
    if results:
        from certifyai.engine.evidence.vault import EvidenceVault

        vault_path = Path(vault)
        vault_path.mkdir(parents=True, exist_ok=True)
        evidence_vault = EvidenceVault(vault_path)
        evidence_vault.store_batch(results)
        console.print(f"  Evidence stored in: {vault}")

    console.print(f"\n[bold]Results:[/] {summary.total_attacks} total | "
                  f"[green]{summary.passed} passed[/] | "
                  f"[red]{summary.failed} failed[/] | "
                  f"[yellow]{summary.errors} errors[/]")

    if summary.overall_score is not None:
        console.print(f"  Score: {summary.overall_score:.1%}")

    if report and results:
        from certifyai.engine.compliance.mapper import ComplianceMapper

        mapper = ComplianceMapper()
        compliance_report = mapper.generate_report(
            run_id=summary.id,
            framework_id=framework,
            attack_results=results,
        )
        import json

        report_path = Path(report)
        report_path.write_text(
            json.dumps(compliance_report.model_dump(mode="json"), indent=2, default=str),
            encoding="utf-8",
        )
        console.print(f"  Compliance report saved to: {report_path}")


@cli.command()
@click.argument("path", type=click.Path(exists=True), default="./certifyai_vault")
def verify(path: str) -> None:
    """Verify the integrity of the evidence vault."""
    from certifyai.engine.evidence.vault import EvidenceVault

    vault = EvidenceVault(Path(path))
    result = vault.verify_all()

    if result["verified"]:
        console.print("[bold green]Vault integrity verified \u2713[/]")
    else:
        console.print("[bold red]Vault integrity verification FAILED \u2717[/]")

    for run_id, run_result in result.get("runs", {}).items():
        status = "\u2713" if run_result.get("verified") else "\u2717"
        console.print(f"  Run {run_id}: {status} ({run_result.get('total_files', 0)} files)")
        for mismatch in run_result.get("mismatches", []):
            console.print(f"    [red]! {mismatch}[/]")


@cli.command(name="list-categories")
@click.option("--plugin-dir", multiple=True, help="Directory with custom attack plugins.", type=click.Path(exists=True, file_okay=False, dir_okay=True))
def list_categories(plugin_dir: tuple[str, ...]) -> None:
    """List all available attack categories and their scenario counts."""
    from certifyai.engine.registry import PluginRegistry

    plugin_dirs_list = [Path(d) for d in plugin_dir] if plugin_dir else []
    registry = PluginRegistry(plugin_dirs=plugin_dirs_list)

    console.print("[bold cyan]Available Attack Categories[/]\n")
    for cat in registry.list_categories():
        scenarios = registry.get_scenarios_by_category([cat])
        console.print(f"  [bold]{cat.value}[/] — {len(scenarios)} scenario(s)")
        for s in scenarios:
            console.print(f"    └ {s.id}: {s.name} [{s.severity.value}]")
    console.print()


@cli.command()
@click.option("--framework", default="eu_ai_act", help="Compliance framework.")
@click.option("--provider", default="openai", help="LLM provider.")
@click.option("--model", default="gpt-4o", help="Model name.")
def init(framework: str, provider: str, model: str) -> None:
    """Initialize a CertifyAI project configuration."""
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
    }

    import yaml

    cfg_path.write_text(yaml.dump(cfg, default_flow_style=False), encoding="utf-8")
    console.print(f"[green]\u2713[/] Created {cfg_path}")
    console.print(f"  Provider: {provider}")
    console.print(f"  Model:    {model}")
    console.print(f"  Framework: {framework}")
    console.print()
    console.print("Run [bold]certifyai run[/] to start the attack battery.")


if __name__ == "__main__":
    cli()
