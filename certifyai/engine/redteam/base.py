"""Abstract base class for attack plugins."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from certifyai.engine.models import (
    AttackCategory,
    AttackResult,
    AttackScenario,
    AttackStatus,
)


class AttackPlugin(ABC):
    """Base class for all attack scenario plugins.

    Each plugin defines one or more attack scenarios and the logic to
    evaluate LLM responses against pass/fail criteria.
    """

    @property
    @abstractmethod
    def category(self) -> AttackCategory:
        """The category this plugin belongs to."""

    @abstractmethod
    def get_scenarios(self) -> list[AttackScenario]:
        """Return the attack scenarios this plugin provides."""

    @abstractmethod
    async def evaluate(
        self, scenario: AttackScenario, prompt: str, response: str
    ) -> dict[str, Any]:
        """Evaluate an LLM response against the scenario's pass criteria.

        Args:
            scenario: The attack scenario being tested.
            prompt: The prompt that was sent.
            response: The LLM's response.

        Returns:
            Evaluation dict with at minimum a 'passed' bool key,
            plus any supporting details.
        """

    async def run(
        self,
        scenario: AttackScenario,
        prompt: str,
        response: str | None,
        response_time_ms: int | None = None,
        error_message: str | None = None,
    ) -> AttackResult:
        """Execute a single attack and produce a result.

        Args:
            scenario: The attack scenario.
            prompt: The prompt that was sent.
            response: The LLM response (None if error).
            response_time_ms: Response time in milliseconds.
            error_message: Error message if the LLM call failed.

        Returns:
            A populated AttackResult.
        """
        if error_message or response is None:
            return AttackResult(
                run_id="",
                scenario_id=scenario.id,
                category=scenario.category,
                status=AttackStatus.ERROR,
                severity=scenario.severity,
                prompt=prompt,
                error_message=error_message,
                clause_refs=scenario.clause_refs,
            )

        evaluation = await self.evaluate(scenario, prompt, response)
        passed = evaluation.get("passed", False)

        return AttackResult(
            run_id="",
            scenario_id=scenario.id,
            category=scenario.category,
            status=AttackStatus.PASS if passed else AttackStatus.FAIL,
            severity=scenario.severity,
            prompt=prompt,
            response=response,
            response_time_ms=response_time_ms,
            evaluation=evaluation,
            clause_refs=scenario.clause_refs,
        )
