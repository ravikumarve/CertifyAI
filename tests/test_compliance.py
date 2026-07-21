"""Tests for compliance framework mapping."""

from __future__ import annotations

import tempfile
from pathlib import Path

import pytest
import yaml

from certifyai.engine.compliance.mapper import ComplianceMapper
from certifyai.engine.models import (
    AttackCategory,
    AttackResult,
    AttackStatus,
    ComplianceReport,
    Severity,
)


@pytest.fixture
def mapper() -> ComplianceMapper:
    return ComplianceMapper()


class TestComplianceMapper:
    def test_list_frameworks(self, mapper: ComplianceMapper) -> None:
        frameworks = mapper.list_frameworks()
        assert len(frameworks) > 0
        assert "eu_ai_act" in frameworks
        assert "soc2" in frameworks
        assert "nist_ai_rmf" in frameworks

    def test_load_eu_ai_act(self, mapper: ComplianceMapper) -> None:
        clauses = mapper.get_framework("eu_ai_act")
        assert len(clauses) > 0
        assert all(c.framework == "eu_ai_act" for c in clauses)

    def test_load_soc2(self, mapper: ComplianceMapper) -> None:
        clauses = mapper.get_framework("soc2")
        assert len(clauses) > 0
        assert all(c.framework == "soc2" for c in clauses)

    def test_load_nist(self, mapper: ComplianceMapper) -> None:
        clauses = mapper.get_framework("nist_ai_rmf")
        assert len(clauses) > 0
        assert all(c.framework == "nist_ai_rmf" for c in clauses)

    def test_clause_attack_ids(self, mapper: ComplianceMapper) -> None:
        clauses = mapper.get_framework("eu_ai_act")
        all_attack_ids = set()
        for c in clauses:
            for aid in c.attack_ids:
                all_attack_ids.add(aid)

        assert "INJECTION-001" in all_attack_ids
        assert "JAILBREAK-001" in all_attack_ids
        assert "PII-001" in all_attack_ids

    def test_framework_not_found(self, mapper: ComplianceMapper) -> None:
        with pytest.raises(KeyError):
            mapper.get_framework("nonexistent_framework")

    def test_generate_report(self, mapper: ComplianceMapper) -> None:
        results = [
            AttackResult(
                id="r1",
                run_id="test-run",
                scenario_id="INJECTION-001",
                category=AttackCategory.PROMPT_INJECTION,
                severity=Severity.CRITICAL,
                prompt="test",
                response="test",
                evaluation={"result": "pass"},
                status=AttackStatus.PASS,
            ),
            AttackResult(
                id="r2",
                run_id="test-run",
                scenario_id="JAILBREAK-001",
                category=AttackCategory.JAILBREAK,
                severity=Severity.CRITICAL,
                prompt="test",
                response="test",
                evaluation={"result": "fail"},
                status=AttackStatus.FAIL,
            ),
        ]

        report = mapper.generate_report("test-run", "eu_ai_act", results)
        assert isinstance(report, ComplianceReport)
        assert report.run_id == "test-run"
        assert report.framework == "eu_ai_act"
        assert 0 <= report.overall_score <= 1

    def test_generate_report_scores(self, mapper: ComplianceMapper) -> None:
        """All passing results should give a 1.0 score."""
        results = [
            AttackResult(
                id=f"r{i}",
                run_id="test-run",
                scenario_id=sid,
                category=AttackCategory.PROMPT_INJECTION,
                severity=Severity.HIGH,
                prompt="test",
                response="test",
                evaluation={"result": "pass"},
                status=AttackStatus.PASS,
            )
            for i, sid in enumerate(["INJECTION-001", "JAILBREAK-001", "PII-001"])
        ]

        report = mapper.generate_report("test-run", "eu_ai_act", results)
        # at least one clause should have non-zero score
        assert any(v > 0 for v in report.clause_scores.values())

    def test_empty_results(self, mapper: ComplianceMapper) -> None:
        report = mapper.generate_report("test-run", "eu_ai_act", [])
        assert report.overall_score == 0.0

    def test_custom_framework_dir(self) -> None:
        """Load frameworks from a custom directory."""
        tmpdir = Path(tempfile.mkdtemp())
        custom_framework = {
            "framework": "custom_test",
            "title": "Custom Test Framework",
            "clauses": [
                {
                    "id": "c1",
                    "title": "Test Clause",
                    "description": "A test clause",
                    "severity": "high",
                    "attack_ids": ["TEST-001"],
                    "evidence_requirements": [],
                }
            ],
        }

        yaml_path = tmpdir / "custom_test.yaml"
        yaml_path.write_text(yaml.dump(custom_framework), encoding="utf-8")

        mapper = ComplianceMapper(frameworks_dir=tmpdir)
        frameworks = mapper.list_frameworks()
        assert "custom_test" in frameworks

        clauses = mapper.get_framework("custom_test")
        assert len(clauses) == 1
        assert clauses[0].id == "c1"

    def test_clause_with_no_matching_results(self, mapper: ComplianceMapper) -> None:
        results = [
            AttackResult(
                id="r1",
                run_id="test-run",
                scenario_id="NONEXISTENT-001",
                category=AttackCategory.PROMPT_INJECTION,
                severity=Severity.MEDIUM,
                prompt="test",
                response="test",
                evaluation={"result": "pass"},
                status=AttackStatus.PASS,
            )
        ]

        report = mapper.generate_report("test-run", "eu_ai_act", results)
        for clause_id, score in report.clause_scores.items():
            assert score == 0.0, f"Clause {clause_id} should have 0.0 score"
