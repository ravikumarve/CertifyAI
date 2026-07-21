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
    """

    def __init__(
        self, config: RunConfig, registry: PluginRegistry | None = None
    ) -> None:
        self.config = config
        self.registry = registry or PluginRegistry()

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

        return summary, results
