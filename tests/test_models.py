"""Tests for Pydantic models."""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from certifyai.engine.models import (
    AttackCategory,
    AttackResult,
    AttackScenario,
    AttackStatus,
    ComplianceClause,
    ComplianceReport,
    EvidenceBlob,
    ProviderConfig,
    RunConfig,
    RunSummary,
    Severity,
)


class TestAttackScenario:
    def test_minimal_scenario(self) -> None:
        scenario = AttackScenario(
            id="INJECTION-001",
            name="Basic Injection",
            category=AttackCategory.PROMPT_INJECTION,
            description="Test prompt injection defense",
            severity=Severity.HIGH,
            prompts=["Say {{target}}"],
            pass_criteria={"detected": True},
        )
        assert scenario.id == "INJECTION-001"
        assert scenario.severity == Severity.HIGH

    def test_scenario_missing_prompts(self) -> None:
        with pytest.raises(ValidationError):
            AttackScenario(
                id="TEST-001",
                name="Bad",
                category=AttackCategory.PROMPT_INJECTION,
                description="test",
                severity=Severity.MEDIUM,
                prompts=[],
                pass_criteria={},
            )

    def test_scenario_empty_id(self) -> None:
        with pytest.raises(ValidationError):
            AttackScenario(
                id="",
                name="Test",
                category=AttackCategory.JAILBREAK,
                description="test",
                severity=Severity.LOW,
                prompts=["test"],
                pass_criteria={},
            )


class TestAttackResult:
    def test_minimal_result(self) -> None:
        result = AttackResult(
            run_id="run-001",
            scenario_id="INJECTION-001",
            category=AttackCategory.PROMPT_INJECTION,
            status=AttackStatus.PASS,
            severity=Severity.HIGH,
            prompt="test prompt",
        )
        assert result.run_id == "run-001"
        assert result.status == AttackStatus.PASS

    def test_result_with_full_data(self) -> None:
        result = AttackResult(
            run_id="run-001",
            scenario_id="JAILBREAK-001",
            category=AttackCategory.JAILBREAK,
            status=AttackStatus.FAIL,
            severity=Severity.CRITICAL,
            prompt="test",
            response="I will comply",
            response_time_ms=1234,
            evaluation={"detected": False, "triggered": True},
            clause_refs=["eu_ai_act.article_14"],
        )
        assert result.response_time_ms == 1234
        assert result.evaluation["detected"] is False

    def test_result_generates_id(self) -> None:
        result = AttackResult(
            run_id="r1",
            scenario_id="s1",
            category=AttackCategory.PII_LEAKAGE,
            status=AttackStatus.ERROR,
            severity=Severity.MEDIUM,
            prompt="test",
        )
        assert len(result.id) == 12  # uuid hex[:12]


class TestProviderConfig:
    def test_minimal_config(self) -> None:
        cfg = ProviderConfig(
            provider="openai",
            model="gpt-4o",
        )
        assert cfg.provider == "openai"
        assert cfg.api_key is None
        assert cfg.max_retries == 3

    def test_custom_endpoint(self) -> None:
        cfg = ProviderConfig(
            provider="ollama",
            model="llama3.1",
            endpoint="http://localhost:11434",
        )
        assert cfg.endpoint == "http://localhost:11434"


class TestRunConfig:
    def test_minimal_config(self) -> None:
        provider = ProviderConfig(provider="openai", model="gpt-4o")
        config = RunConfig(provider=provider)
        assert config.concurrency == 5

    def test_dry_run(self) -> None:
        provider = ProviderConfig(provider="openai", model="gpt-4o")
        config = RunConfig(provider=provider, dry_run=True)
        assert config.dry_run is True

    def test_specific_categories(self) -> None:
        provider = ProviderConfig(provider="openai", model="gpt-4o")
        config = RunConfig(
            provider=provider,
            attack_categories=[AttackCategory.PROMPT_INJECTION],
        )
        assert config.attack_categories == [AttackCategory.PROMPT_INJECTION]


class TestRunSummary:
    def test_defaults(self) -> None:
        summary = RunSummary(status=AttackStatus.PASS)
        assert summary.total_attacks == 0
        assert summary.passed == 0

    def test_with_results(self) -> None:
        summary = RunSummary(
            status=AttackStatus.PASS,
            total_attacks=10,
            passed=7,
            failed=2,
            errors=1,
            overall_score=0.7,
        )
        assert summary.overall_score == 0.7


class TestEvidenceBlob:
    def test_evidence_blob(self) -> None:
        evidence = EvidenceBlob(
            run_id="run-001",
            result_id="r1",
            prompt="test prompt",
            response="test response",
            evaluation={"detected": True},
        )
        assert evidence.run_id == "run-001"

    def test_evidence_serialization(self) -> None:
        evidence = EvidenceBlob(
            run_id="run-001",
            result_id="r1",
            prompt="test",
            response="test",
            evaluation={"score": 0.95},
        )
        d = evidence.model_dump(mode="json")
        assert d["run_id"] == "run-001"
        assert d["evaluation"]["score"] == 0.95


class TestComplianceClause:
    def test_minimal_clause(self) -> None:
        clause = ComplianceClause(
            id="article_9",
            framework="eu_ai_act",
            title="Risk Management",
            description="test",
            severity=Severity.CRITICAL,
            attack_ids=["INJECTION-001"],
            evidence_requirements=["req1"],
        )
        assert clause.framework == "eu_ai_act"
        assert clause.severity == Severity.CRITICAL

    def test_clause_invalid_severity(self) -> None:
        with pytest.raises(ValidationError):
            ComplianceClause(
                id="clause-1",
                framework="test",
                title="Test",
                description="test",
                severity="invalid",  # type: ignore
                attack_ids=[],
                evidence_requirements=[],
            )


class TestComplianceReport:
    def test_report_scores(self) -> None:
        report = ComplianceReport(
            run_id="run-001",
            framework="eu_ai_act",
            overall_score=0.85,
            clause_scores={"article_9": 0.9, "article_10": 0.8},
            clause_results={"article_9": [], "article_10": []},
        )
        assert report.overall_score == 0.85

    def test_report_serialization(self) -> None:
        report = ComplianceReport(
            run_id="run-001",
            framework="eu_ai_act",
            overall_score=0.75,
            clause_scores={"a1": 0.75},
            clause_results={"a1": []},
        )
        d = report.model_dump(mode="json")
        assert d["overall_score"] == 0.75
