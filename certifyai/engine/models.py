"""Pydantic models for attack scenarios, results, evidence, and compliance."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from enum import StrEnum
from typing import Any

from pydantic import BaseModel, Field


class Severity(StrEnum):
    """Severity level of an attack scenario or finding."""

    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class AttackStatus(StrEnum):
    """Outcome of a single attack execution."""

    PASS = "pass"
    FAIL = "fail"
    ERROR = "error"
    SKIPPED = "skipped"


class AttackCategory(StrEnum):
    """Category of attack scenario."""

    PROMPT_INJECTION = "prompt_injection"
    JAILBREAK = "jailbreak"
    PII_LEAKAGE = "pii_leakage"
    POLICY_VIOLATION = "policy_violation"
    HALLUCINATION = "hallucination"
    BIAS = "bias"


class ProviderConfig(BaseModel):
    """Configuration for an LLM provider."""

    provider: str = Field(description="Provider name (openai, anthropic, ollama, etc.)")
    model: str = Field(description="Model name (gpt-4o, claude-4, llama3.1, etc.)")
    api_key: str | None = Field(default=None, description="API key (resolved from env or config)")
    endpoint: str | None = Field(default=None, description="Custom endpoint URL")
    max_retries: int = Field(default=3, ge=0)
    timeout_seconds: int = Field(default=60, ge=1)


class AttackScenario(BaseModel):
    """Definition of an attack scenario that can be executed against an LLM."""

    id: str = Field(min_length=1, description="Unique scenario identifier, e.g. INJECTION-001")
    name: str = Field(description="Human-readable name")
    category: AttackCategory
    description: str = Field(description="What the attack simulates and why it matters")
    severity: Severity
    prompts: list[str] = Field(description="Test prompt templates to send")
    pass_criteria: dict[str, Any] = Field(
        description="Criteria to determine pass/fail: trigger phrases, regex patterns, thresholds"
    )
    clause_refs: list[str] = Field(
        default_factory=list,
        description="Regulatory clause references (e.g. 'eu_ai_act.article_14')",
    )
    tags: list[str] = Field(default_factory=list)

    def model_post_init(self, __context: Any) -> None:
        """Validate that prompts are non-empty after initialization."""
        if not self.prompts:
            raise ValueError(f"AttackScenario {self.id} must have at least one prompt")


class AttackResult(BaseModel):
    """Result of executing a single attack scenario against an LLM."""

    id: str = Field(default_factory=lambda: uuid.uuid4().hex[:12])
    run_id: str
    scenario_id: str
    category: AttackCategory
    status: AttackStatus
    severity: Severity
    prompt: str = Field(description="The actual prompt sent")
    response: str | None = Field(default=None, description="Raw LLM response")
    response_time_ms: int | None = Field(default=None)
    error_message: str | None = Field(default=None)
    evaluation: dict[str, Any] = Field(
        default_factory=dict,
        description="Structured evaluation details: which criteria fired, scores, flags",
    )
    evidence_hash: str | None = Field(default=None, description="SHA-256 of evidence blob")
    clause_refs: list[str] = Field(default_factory=list)
    created_at: str = Field(
        default_factory=lambda: datetime.now(UTC).isoformat()
    )


class EvidenceBlob(BaseModel):
    """Cryptographically verifiable evidence record stored in the vault."""

    run_id: str
    result_id: str
    prompt: str
    response: str | None
    evaluation: dict[str, Any]
    timestamp: str = Field(
        default_factory=lambda: datetime.now(UTC).isoformat()
    )


class RunConfig(BaseModel):
    """Configuration for a single attack run."""

    provider: ProviderConfig
    frameworks: list[str] = Field(
        default_factory=lambda: ["eu_ai_act", "soc2", "nist_ai_rmf"]
    )
    attack_categories: list[AttackCategory] | None = Field(
        default=None, description="None = run all available categories"
    )
    concurrency: int = Field(default=5, ge=1, le=20)
    dry_run: bool = Field(default=False, description="Simulate without calling LLM")


class RunSummary(BaseModel):
    """Summary of a completed attack run."""

    id: str = Field(default_factory=lambda: uuid.uuid4().hex[:12])
    status: AttackStatus
    started_at: str = Field(
        default_factory=lambda: datetime.now(UTC).isoformat()
    )
    completed_at: str | None = Field(default=None)
    total_attacks: int = 0
    passed: int = 0
    failed: int = 0
    errors: int = 0
    overall_score: float | None = Field(default=None, ge=0.0, le=1.0)
    config_snapshot: dict[str, Any] = Field(default_factory=dict)


class ComplianceClause(BaseModel):
    """A single regulatory clause with associated evidence requirements."""

    id: str
    framework: str
    title: str
    description: str
    severity: Severity
    attack_ids: list[str] = Field(description="Attack scenario IDs that provide evidence")
    evidence_requirements: list[str] = Field(
        description="What evidence must be captured for this clause"
    )


class ComplianceReport(BaseModel):
    """Compliance report mapping attack results to regulatory frameworks."""

    run_id: str
    framework: str
    overall_score: float = Field(ge=0.0, le=1.0)
    clause_scores: dict[str, float] = Field(
        description="Per-clause compliance scores (0.0 to 1.0)"
    )
    clause_results: dict[str, list[AttackResult]] = Field(
        description="Attack results mapped to each clause"
    )
    generated_at: str = Field(
        default_factory=lambda: datetime.now(UTC).isoformat()
    )
