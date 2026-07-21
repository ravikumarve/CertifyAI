"""Compliance mapper — loads framework YAML files and maps attack results to clauses."""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

import yaml

from certifyai.engine.models import ComplianceClause, ComplianceReport, Severity

logger = logging.getLogger(__name__)

# Default framework definitions bundled with the package
FRAMEWORKS_DIR = Path(__file__).parent / "frameworks"


class ComplianceMapper:
    """Maps attack results to regulatory framework clauses.

    Loads framework definitions from YAML files and computes
    per-clause and overall compliance scores.
    """

    def __init__(self, frameworks_dir: Path | None = None) -> None:
        self.frameworks_dir = frameworks_dir or FRAMEWORKS_DIR
        self._frameworks: dict[str, list[ComplianceClause]] | None = None

    def load_frameworks(self) -> dict[str, list[ComplianceClause]]:
        """Load all framework YAML files from the frameworks directory.

        Returns:
            Dict mapping framework IDs to lists of ComplianceClause objects.
        """
        if self._frameworks is not None:
            return self._frameworks

        frameworks: dict[str, list[ComplianceClause]] = {}
        yaml_files = list(self.frameworks_dir.glob("*.yaml")) + list(
            self.frameworks_dir.glob("*.yml")
        )

        if not yaml_files:
            logger.warning(
                "No framework YAML files found in %s", self.frameworks_dir
            )
            self._frameworks = frameworks
            return frameworks

        for yaml_path in sorted(yaml_files):
            framework_id = yaml_path.stem
            try:
                data = yaml.safe_load(yaml_path.read_text(encoding="utf-8"))
                if not data or "clauses" not in data:
                    logger.warning("No clauses in %s", yaml_path.name)
                    continue

                clauses: list[ComplianceClause] = []
                for clause_data in data["clauses"]:
                    clauses.append(
                        ComplianceClause(
                            id=clause_data["id"],
                            framework=framework_id,
                            title=clause_data.get("title", ""),
                            description=clause_data.get("description", ""),
                            severity=Severity(clause_data.get("severity", "medium")),
                            attack_ids=clause_data.get("attack_ids", []),
                            evidence_requirements=clause_data.get(
                                "evidence_requirements", []
                            ),
                        )
                    )

                frameworks[framework_id] = clauses

            except Exception as e:
                logger.error("Failed to load %s: %s", yaml_path.name, e)

        self._frameworks = frameworks
        return frameworks

    def get_framework(self, framework_id: str) -> list[ComplianceClause]:
        """Get clauses for a specific framework.

        Args:
            framework_id: The framework identifier (e.g., 'eu_ai_act').

        Returns:
            List of ComplianceClause objects.

        Raises:
            KeyError: If the framework is not loaded.
        """
        frameworks = self.load_frameworks()
        if framework_id not in frameworks:
            raise KeyError(f"Framework not found: {framework_id}")
        return list(frameworks[framework_id])

    def list_frameworks(self) -> list[str]:
        """List all loaded framework IDs.

        Returns:
            Sorted list of framework identifiers.
        """
        return sorted(self.load_frameworks().keys())

    def generate_report(
        self,
        run_id: str,
        framework_id: str,
        attack_results: list[Any],
    ) -> ComplianceReport:
        """Generate a compliance report by mapping attack results to a framework.

        Args:
            run_id: The run ID these results belong to.
            framework_id: The framework to map against.
            attack_results: List of AttackResult objects.

        Returns:
            A ComplianceReport with per-clause scores.
        """
        from certifyai.engine.models import AttackStatus

        clauses = self.get_framework(framework_id)
        clause_scores: dict[str, float] = {}
        clause_results: dict[str, list[Any]] = {}

        # Build a lookup: scenario_id -> list of results
        results_by_scenario: dict[str, list[Any]] = {}
        for r in attack_results:
            results_by_scenario.setdefault(r.scenario_id, []).append(r)

        for clause in clauses:
            relevant_results: list[Any] = []
            for attack_id in clause.attack_ids:
                if attack_id in results_by_scenario:
                    relevant_results.extend(results_by_scenario[attack_id])

            if not relevant_results:
                clause_scores[clause.id] = 0.0
                clause_results[clause.id] = []
                continue

            passed = sum(
                1
                for r in relevant_results
                if r.status == AttackStatus.PASS
            )
            total = len(relevant_results)
            clause_scores[clause.id] = round(passed / total, 4) if total > 0 else 0.0
            clause_results[clause.id] = relevant_results

        overall = (
            round(sum(clause_scores.values()) / len(clause_scores), 4)
            if clause_scores
            else 0.0
        )

        return ComplianceReport(
            run_id=run_id,
            framework=framework_id,
            overall_score=overall,
            clause_scores=clause_scores,
            clause_results=clause_results,
        )
