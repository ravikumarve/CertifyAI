"""Attack runner — orchestrates execution of attack scenarios against an LLM."""

from __future__ import annotations

import asyncio
import logging
import time
from typing import Any

from certifyai.engine.lite_llm import LLMClient, MockLLMClient
from certifyai.engine.models import (
    AttackResult,
    AttackStatus,
    RunConfig,
    RunSummary,
)
from certifyai.engine.registry import PluginRegistry

logger = logging.getLogger(__name__)


class AttackRunner:
    """Orchestrates execution of attack scenarios against a configured LLM.

    Uses the plugin system for scenario definitions and evaluation,
    and the LLM client for sending prompts.

    If a ``db_manager`` is provided, results are persisted to SQLite
    automatically after execution.
    """

    def __init__(
        self,
        config: RunConfig,
        registry: PluginRegistry | None = None,
        db_manager: Any = None,
    ) -> None:
        self.config = config
        self.registry = registry or PluginRegistry()
        self.db_manager = db_manager

        self.registry.load_all()
        self.llm = self._build_llm_client()

    def _build_llm_client(self) -> LLMClient | MockLLMClient:
        """Build the appropriate LLM client based on config."""
        if self.config.dry_run:
            return MockLLMClient()
        return LLMClient(self.config.provider)

    async def run_all(self) -> tuple[RunSummary, list[AttackResult]]:
        """Execute all attack scenarios and return results.

        Returns:
            Tuple of (run_summary, list_of_results).
        """
        scenarios = self.registry.get_scenarios_by_category(
            self.config.attack_categories
        )

        if not scenarios:
            logger.warning("No attack scenarios matched the configured categories")
            return RunSummary(status=AttackStatus.SKIPPED), []

        summary = RunSummary(
            status=AttackStatus.PASS,
            total_attacks=len(scenarios),
            config_snapshot=self.config.model_dump(mode="json"),
        )

        results: list[AttackResult] = []
        semaphore = asyncio.Semaphore(self.config.concurrency)

        async def _run_one(scenario: Any) -> list[AttackResult]:
            """Execute all prompts for a single scenario."""
            plugin = self.registry.get_plugin(scenario.category)
            scenario_results: list[AttackResult] = []

            for prompt in scenario.prompts:
                async with semaphore:
                    start = time.monotonic()
                    try:
                        response = await self.llm.complete(prompt)
                        elapsed_ms = int((time.monotonic() - start) * 1000)
                        result = await plugin.run(
                            scenario=scenario,
                            prompt=prompt,
                            response=response,
                            response_time_ms=elapsed_ms,
                        )
                    except Exception as e:
                        elapsed_ms = int((time.monotonic() - start) * 1000)
                        result = await plugin.run(
                            scenario=scenario,
                            prompt=prompt,
                            response=None,
                            response_time_ms=elapsed_ms,
                            error_message=str(e),
                        )
                    result.run_id = summary.id
                    scenario_results.append(result)

            return scenario_results

        task_results = await asyncio.gather(
            *[_run_one(s) for s in scenarios], return_exceptions=True
        )

        for tr in task_results:
            if isinstance(tr, Exception):
                logger.error("Scenario execution failed: %s", tr)
                continue
            results.extend(tr)

        # Compute summary
        summary.total_attacks = len(results)
        summary.passed = sum(1 for r in results if r.status == AttackStatus.PASS)
        summary.failed = sum(1 for r in results if r.status == AttackStatus.FAIL)
        summary.errors = sum(1 for r in results if r.status == AttackStatus.ERROR)
        summary.completed_at = __import__(
            "datetime"
        ).datetime.now(__import__("datetime").timezone.utc).isoformat()

        if summary.total_attacks > 0:
            non_error = summary.total_attacks - summary.errors
            summary.overall_score = (
                round(summary.passed / non_error, 4) if non_error > 0 else 0.0
            )

        # Persist to database if configured
        if self.db_manager is not None:
            await self._persist_results(summary, results, scenarios)

        return summary, results

    async def _persist_results(
        self,
        summary: RunSummary,
        results: list[AttackResult],
        scenarios: list[Any],
    ) -> None:
        """Save run and results to the SQLite database."""
        from datetime import UTC, datetime
        from certifyai.engine.database.models import ResultRecord, RunRecord, APP_VERSION

        # Build scenario lookup: id -> name
        scenario_names = {s.id: s.name for s in scenarios}

        # Create run record
        run_record = RunRecord(
            id=summary.id,
            status=summary.status.value,
            started_at=summary.started_at,
            finished_at=summary.completed_at or datetime.now(UTC).isoformat(),
            config_json=summary.config_snapshot,
            total_attacks=summary.total_attacks,
            passed=summary.passed,
            failed=summary.failed,
            errors=summary.errors,
            overall_score=summary.overall_score,
            engine_version=APP_VERSION,
        )
        await self.db_manager.save_run(run_record)

        # Create result records
        result_records = []
        for r in results:
            result_records.append(
                ResultRecord(
                    id=r.id,
                    run_id=r.run_id or summary.id,
                    scenario_id=r.scenario_id,
                    attack_name=scenario_names.get(r.scenario_id, r.scenario_id),
                    category=r.category.value,
                    status=r.status.value,
                    severity=r.severity.value,
                    prompt_text=r.prompt,
                    response_text=r.response,
                    evaluation=r.evaluation,
                    response_time_ms=r.response_time_ms,
                    evidence_hash=r.evidence_hash,
                    clause_refs=str(r.clause_refs) if r.clause_refs else None,
                    error_message=r.error_message,
                )
            )
        await self.db_manager.save_results(result_records)

        logger.info(
            "Persisted run %s with %d results to database",
            summary.id,
            len(result_records),
        )
