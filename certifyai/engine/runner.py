"""Attack runner — orchestrates execution of attack scenarios against an LLM."""

from __future__ import annotations

import asyncio
import collections.abc
import json
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
        progress_callback: collections.abc.Callable[[str, AttackResult], None] | None = None,
    ) -> None:
        self.config = config
        self.registry = registry or PluginRegistry()
        self.db_manager = db_manager
        self.progress_callback = progress_callback

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
        scenarios = self.registry.get_scenarios_by_category(self.config.attack_categories)

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

            # Fire progress callback for this scenario
            if self.progress_callback is not None:
                for r in scenario_results:
                    self.progress_callback(scenario.name, r)

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
        summary.completed_at = (
            __import__("datetime").datetime.now(__import__("datetime").timezone.utc).isoformat()
        )

        if summary.total_attacks > 0:
            non_error = summary.total_attacks - summary.errors
            summary.overall_score = round(summary.passed / non_error, 4) if non_error > 0 else 0.0

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

        from certifyai.engine.database.models import APP_VERSION, EvidenceChainRecord, ResultRecord, RunRecord

        # Build scenario lookup: id -> name
        scenario_names = {s.id: s.name for s in scenarios}

        # Create run record
        run_record = RunRecord(
            id=summary.id,
            status=summary.status.value,
            started_at=summary.started_at,
            finished_at=summary.completed_at or datetime.now(UTC).isoformat(),
            config_json=json.dumps(summary.config_snapshot, default=str),
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
            # Serialize evaluation to JSON string if it's a dict
            evaluation = r.evaluation
            if isinstance(evaluation, dict):
                evaluation = json.dumps(evaluation, default=str)

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
                    evaluation=evaluation,
                    response_time_ms=r.response_time_ms,
                    evidence_hash=r.evidence_hash,
                    clause_refs=json.dumps(r.clause_refs) if r.clause_refs else None,
                    error_message=r.error_message,
                )
            )
        await self.db_manager.save_results(result_records)

        # Persist evidence chain entry
        from hashlib import sha256
        from datetime import UTC, datetime

        # Compute a run-level hash from all result hashes
        combined = "".join(r.evidence_hash or r.id for r in results)
        run_hash = sha256(combined.encode()).hexdigest()

        # Get previous chain entry for linked-list integrity
        prev = await self.db_manager.get_latest_chain_entry()
        previous_hash = prev.run_hash if prev else sha256(b"genesis").hexdigest()

        passed_count = summary.passed
        failed_count = summary.failed
        total_count = summary.total_attacks
        status_label = "PASS" if failed_count == 0 else "FAIL"
        chain_record = EvidenceChainRecord(
            run_id=summary.id,
            previous_hash=previous_hash,
            run_hash=run_hash,
            timestamp=datetime.now(UTC).isoformat(),
            chain_metadata=json.dumps({
                "message": f"Run {summary.id[:8]} — {passed_count}/{total_count} passed, score {summary.overall_score:.0%}",
                "level": status_label,
                "total_attacks": total_count,
                "passed": passed_count,
                "failed": failed_count,
                "overall_score": summary.overall_score,
                "scenario": "batch_complete",
            }),
        )
        await self.db_manager.save_evidence_chain(chain_record)

        logger.info(
            "Persisted run %s with %d results + evidence chain to database",
            summary.id,
            len(result_records),
        )
