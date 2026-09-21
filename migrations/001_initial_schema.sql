-- CertifyAI migration 001 — initial schema (fresh-install baseline).
-- Mirrors certifyai/engine/database/models.py (SCHEMA_VERSION = 1) plus the
-- append-only triggers in CREATE_TRIGGERS_SQL. DatabaseManager applies this
-- automatically via Base.metadata.create_all on first connect, then records
-- version 1 in _schema_version. Future schema changes MUST ship as
-- 002_<name>.sql and bump SCHEMA_VERSION — never edit this file.
-- To migrate an existing DB forward, run: certifyai healthcheck --db <path>
-- (it reports the recorded version) or apply the next script with sqlite3.

PRAGMA journal_mode=WAL;
PRAGMA synchronous=NORMAL;
PRAGMA foreign_keys=ON;

CREATE TABLE IF NOT EXISTS runs (
    id            TEXT PRIMARY KEY,
    status        TEXT NOT NULL DEFAULT 'pending',
    started_at    TEXT NOT NULL,
    finished_at   TEXT,
    config_json   TEXT NOT NULL,
    total_attacks INTEGER NOT NULL DEFAULT 0,
    passed        INTEGER NOT NULL DEFAULT 0,
    failed        INTEGER NOT NULL DEFAULT 0,
    errors        INTEGER NOT NULL DEFAULT 0,
    skipped       INTEGER NOT NULL DEFAULT 0,
    overall_score REAL,
    engine_version TEXT NOT NULL,
    created_at    TEXT NOT NULL,
    CONSTRAINT ck_runs_status CHECK (
        status IN ('pending','running','completed','failed','cancelled','pass','error','skipped')
    )
);
CREATE INDEX IF NOT EXISTS idx_runs_status ON runs (status);
CREATE INDEX IF NOT EXISTS idx_runs_started_at ON runs (started_at DESC);
CREATE INDEX IF NOT EXISTS idx_runs_status_started ON runs (status, started_at DESC);

CREATE TABLE IF NOT EXISTS results (
    id              TEXT PRIMARY KEY,
    run_id          TEXT NOT NULL REFERENCES runs (id) ON DELETE CASCADE,
    scenario_id     TEXT NOT NULL,
    attack_name     TEXT NOT NULL,
    category        TEXT NOT NULL,
    status          TEXT NOT NULL,
    severity        TEXT NOT NULL DEFAULT 'none',
    prompt_text     TEXT NOT NULL,
    response_text   TEXT,
    evaluation      TEXT NOT NULL DEFAULT '{}',
    response_time_ms INTEGER,
    evidence_hash   TEXT,
    clause_refs     TEXT,
    error_message   TEXT,
    started_at      TEXT NOT NULL,
    duration_ms     INTEGER NOT NULL DEFAULT 0,
    CONSTRAINT ck_results_status CHECK (status IN ('pass','fail','error','skipped'))
);
CREATE INDEX IF NOT EXISTS idx_results_run_status ON results (run_id, status);
CREATE INDEX IF NOT EXISTS idx_results_category ON results (category);
CREATE INDEX IF NOT EXISTS idx_results_severity ON results (severity);
CREATE INDEX IF NOT EXISTS idx_results_run_category_status ON results (run_id, category, status);
CREATE INDEX IF NOT EXISTS idx_results_failed ON results (run_id, severity) WHERE status = 'fail';

CREATE TABLE IF NOT EXISTS evidence_chain (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    run_id        TEXT NOT NULL UNIQUE REFERENCES runs (id),
    previous_hash TEXT NOT NULL,
    run_hash      TEXT NOT NULL,
    timestamp     TEXT NOT NULL,
    metadata      TEXT,
    verified_at   TEXT
);
CREATE INDEX IF NOT EXISTS idx_evidence_chain_timestamp ON evidence_chain (timestamp);

CREATE TABLE IF NOT EXISTS config (
    key         TEXT PRIMARY KEY,
    value       TEXT NOT NULL,
    category    TEXT NOT NULL DEFAULT 'general',
    description TEXT,
    updated_at  TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS _schema_version (
    version      INTEGER PRIMARY KEY,
    applied_at   TEXT NOT NULL,
    script_name  TEXT NOT NULL
);

-- Append-only enforcement for the evidence chain (court-admissible trail).
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
