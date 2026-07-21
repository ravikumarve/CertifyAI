"""SQLAlchemy 2.0 ORM models for CertifyAI's SQLite database.

Schema follows the design in docs/database-schema.md with 5 tables:
  - runs:           Attack run headers (1 row per execution)
  - results:        Individual attack results (many per run)
  - evidence_chain: Append-only SHA-256 hash chain (1 per run)
  - config:         Key-value application config store
  - _schema_version: Migration tracking (internal)

WAL mode is enabled for concurrent CLI + Dashboard reads.
"""

from __future__ import annotations

import json
from datetime import UTC, datetime
from typing import Any

from sqlalchemy import (
    CheckConstraint,
    Column,
    Float,
    ForeignKey,
    Index,
    Integer,
    Text,
    create_engine,
    event,
    text,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

# ---------------------------------------------------------------------------
# Base & engine helpers
# ---------------------------------------------------------------------------

APP_VERSION = "0.1.0"
SCHEMA_VERSION = 1


class Base(DeclarativeBase):
    pass


# ---------------------------------------------------------------------------
# Helper: JSON encoding / decoding
# ---------------------------------------------------------------------------


def _json_dumps(obj: Any) -> str:
    return json.dumps(obj, default=str, separators=(",", ":"))


# ---------------------------------------------------------------------------
# Table: runs
# ---------------------------------------------------------------------------


class RunRecord(Base):
    """Header record for each attack battery execution."""

    __tablename__ = "runs"

    id: Mapped[str] = mapped_column(Text, primary_key=True)
    status: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        default="pending",
    )
    started_at: Mapped[str] = mapped_column(Text, nullable=False)
    finished_at: Mapped[str | None] = mapped_column(Text, nullable=True)
    config_json: Mapped[str] = mapped_column(Text, nullable=False)
    total_attacks: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    passed: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    failed: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    errors: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    skipped: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    overall_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    engine_version: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[str] = mapped_column(
        Text, nullable=False, default=lambda: datetime.now(UTC).isoformat()
    )

    # Relationships
    results: Mapped[list["ResultRecord"]] = relationship(
        back_populates="run", cascade="all, delete-orphan", passive_deletes=True
    )
    evidence: Mapped[list["EvidenceChainRecord"]] = relationship(
        back_populates="run", cascade="all, delete-orphan", passive_deletes=True
    )

    __table_args__ = (
        CheckConstraint(
            "status IN ('pending', 'running', 'completed', 'failed', 'cancelled', 'pass', 'error', 'skipped')",
            name="ck_runs_status",
        ),
        Index("idx_runs_status", "status"),
        Index("idx_runs_started_at", text("started_at DESC")),
        Index("idx_runs_status_started", "status", text("started_at DESC")),
    )

    def __repr__(self) -> str:
        return f"<RunRecord id={self.id!r} status={self.status!r}>"


# ---------------------------------------------------------------------------
# Table: results
# ---------------------------------------------------------------------------


class ResultRecord(Base):
    """Individual attack result — one row per LLM call."""

    __tablename__ = "results"

    id: Mapped[str] = mapped_column(Text, primary_key=True)
    run_id: Mapped[str] = mapped_column(
        Text,
        ForeignKey("runs.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    scenario_id: Mapped[str] = mapped_column(Text, nullable=False)
    attack_name: Mapped[str] = mapped_column(Text, nullable=False)
    category: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(Text, nullable=False)
    severity: Mapped[str] = mapped_column(Text, nullable=False, default="none")
    prompt_text: Mapped[str] = mapped_column(Text, nullable=False)
    response_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    evaluation: Mapped[str] = mapped_column(
        Text, nullable=False, default="{}"
    )
    response_time_ms: Mapped[int | None] = mapped_column(Integer, nullable=True)
    evidence_hash: Mapped[str | None] = mapped_column(Text, nullable=True)
    clause_refs: Mapped[str | None] = mapped_column(
        Text, nullable=True, comment="JSON array of clause refs"
    )
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    started_at: Mapped[str] = mapped_column(
        Text, nullable=False, default=lambda: datetime.now(UTC).isoformat()
    )
    duration_ms: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    # Relationships
    run: Mapped[RunRecord] = relationship(back_populates="results")

    __table_args__ = (
        CheckConstraint(
            "status IN ('pass', 'fail', 'error', 'skipped')",
            name="ck_results_status",
        ),
        Index("idx_results_run_status", "run_id", "status"),
        Index("idx_results_category", "category"),
        Index("idx_results_severity", "severity"),
        Index("idx_results_run_category_status", "run_id", "category", "status"),
        Index(
            "idx_results_failed",
            "run_id",
            "severity",
            sqlite_where=text("status = 'fail'"),
        ),
    )

    def __repr__(self) -> str:
        return (
            f"<ResultRecord id={self.id!r} scenario={self.scenario_id!r}"
            f" status={self.status!r}>"
        )


# ---------------------------------------------------------------------------
# Table: evidence_chain  (append-only)
# ---------------------------------------------------------------------------


class EvidenceChainRecord(Base):
    """Append-only SHA-256 hash chain linking every run."""

    __tablename__ = "evidence_chain"

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True
    )
    run_id: Mapped[str] = mapped_column(
        Text,
        ForeignKey("runs.id", ondelete="RESTRICT"),
        nullable=False,
        unique=True,
    )
    previous_hash: Mapped[str] = mapped_column(Text, nullable=False)
    run_hash: Mapped[str] = mapped_column(Text, nullable=False)
    timestamp: Mapped[str] = mapped_column(
        Text, nullable=False, default=lambda: datetime.now(UTC).isoformat()
    )
    chain_metadata: Mapped[str | None] = mapped_column("metadata", Text, nullable=True)
    verified_at: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Relationships
    run: Mapped[RunRecord] = relationship(back_populates="evidence")

    __table_args__ = (
        Index("idx_evidence_chain_timestamp", "timestamp"),
    )

    def __repr__(self) -> str:
        return f"<EvidenceChainRecord id={self.id} run_id={self.run_id!r}>"


# ---------------------------------------------------------------------------
# Table: config  (key-value)
# ---------------------------------------------------------------------------


class ConfigRecord(Base):
    """Simple key-value configuration store."""

    __tablename__ = "config"

    key: Mapped[str] = mapped_column(Text, primary_key=True)
    value: Mapped[str] = mapped_column(Text, nullable=False)
    category: Mapped[str] = mapped_column(Text, nullable=False, default="general")
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    updated_at: Mapped[str] = mapped_column(
        Text, nullable=False, default=lambda: datetime.now(UTC).isoformat()
    )

    def __repr__(self) -> str:
        return f"<ConfigRecord key={self.key!r} category={self.category!r}>"


# ---------------------------------------------------------------------------
# Table: _schema_version  (migration tracking)
# ---------------------------------------------------------------------------


class SchemaVersionRecord(Base):
    """Internal migration tracking — records every applied migration."""

    __tablename__ = "_schema_version"

    version: Mapped[int] = mapped_column(Integer, primary_key=True)
    applied_at: Mapped[str] = mapped_column(
        Text, nullable=False, default=lambda: datetime.now(UTC).isoformat()
    )
    script_name: Mapped[str] = mapped_column(Text, nullable=False)

    def __repr__(self) -> str:
        return f"<SchemaVersionRecord version={self.version}>"


# ---------------------------------------------------------------------------
# Schema creation helper
# ---------------------------------------------------------------------------

CREATE_TRIGGERS_SQL = """
-- Enforce append-only on evidence_chain
CREATE TRIGGER IF NOT EXISTS trg_evidence_chain_append_only
BEFORE UPDATE ON evidence_chain
BEGIN
    SELECT RAISE(ABORT, 'evidence_chain is append-only. UPDATE denied.');
END;

CREATE TRIGGER IF NOT EXISTS trg_evidence_chain_no_delete
BEFORE DELETE ON evidence_chain
BEGIN
    SELECT RAISE(ABORT, 'evidence_chain is append-only. DELETE denied.');
END;

-- Enable WAL mode for concurrent access
PRAGMA journal_mode=WAL;
PRAGMA synchronous=NORMAL;
PRAGMA foreign_keys=ON;
"""
