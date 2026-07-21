# 🤖 CertifyAI — Project Command Center

**Project:** Continuous Compliance Engine for AI Runtimes
**Delivery Model:** Shippable Boilerplate (PyPI + Gumroad)
**Primary Stack:** Python 3.11+ (asyncio, Pydantic v2, LiteLLM, Click, Textual), Next.js 14 (Tailwind, motion, recharts), SQLite
**Host:** Dell Latitude 3460 (Ubuntu) — CPU-only, no heavy Docker/K8s

---

## 📋 Project State

| Attribute | Value |
|-----------|-------|
| **Phase** | Phase 4 — SQLite Database Layer Complete |
| **Code written** | ~4,000 lines |
| **Documents** | 17 docs in `docs/` (Waves 1-3) |
| **Git repo** | https://github.com/ravikumarve/CertifyAI |
| **Revenue** | $0 |
| **Next action** | Phase 5 — Begin Web Dashboard (Next.js 14 + Tailwind + recharts) OR TUI polish |

---

## 🧠 Architecture Decisions

### ADR-001: Boilerplate over SaaS
- **Context:** Original idea targeted enterprise B2B SaaS ($30K–$150K/yr). Solo dev cannot sustain enterprise sales cycles, lacks SOC 2 certification, and cannot provide 24/7 support.
- **Decision:** Pivot to downloadable boilerplate product. Ship as PyPI package (free CLI/TUI) + Gumroad bundle (paid Pro/Enterprise tiers with Web Dashboard, docs, commercial license).
- **Consequence:** Eliminates ops burden, certification barrier, and sales cycle. Revenue in weeks instead of months. Zero direct competitors in this category.

### ADR-002: Python monolith for engine + CLI + TUI
- **Context:** LLM ecosystem is Python-dominant (LiteLLM, LangChain eval tools, guardrails libraries). Solo dev needs one language to maintain.
- **Decision:** Core engine, CLI (Click), and TUI (Textual) all in Python 3.11+. Web Dashboard is the only non-Python component (Next.js 14).
- **Consequence:** Single language for 80% of the codebase. Faster development. Customer only needs Python installed for core functionality.

### ADR-003: SQLite as primary database
- **Context:** Boilerplate must be self-contained. PostgreSQL adds setup friction. VectorDB adds complexity.
- **Decision:** SQLite via SQLAlchemy 2.0 + aiosqlite. Single-file database. Evidence vault stored as filesystem directory with SHA-256 hash chain.
- **Consequence:** Zero-infra setup for customer. Easy backup/portability. Optional PostgreSQL for advanced users.

### ADR-004: LiteLLM as sole LLM abstraction
- **Context:** Original idea mentioned LangChain, LlamaIndex, and LiteLLM. Maintaining 3 SDK integrations is scope creep.
- **Decision:** LiteLLM only. Covers 100+ providers (OpenAI, Anthropic, Ollama, Gemini, any OpenAI-compatible endpoint).
- **Consequence:** Simpler codebase. Customer flexibility. Works air-gapped with Ollama.

### ADR-005: Shared SQLite file across all interfaces
- **Context:** CLI, TUI, and Web Dashboard all need access to attack results and evidence.
- **Decision:** All three read/write the same `certifyai.db` file. Web Dashboard uses `better-sqlite3` (synchronous Node.js binding) for direct reads. No API server.
- **Consequence:** Eliminates need for a separate backend server. Simplifies deployment. Shared state without sync complexity.

---

## 💾 Session Memory Ledger

### [2026-07-21 19:45] — Phase 4: SQLite Database Layer Complete
- **State:** Success — 13 new files, 88 tests passing, CLI wired end-to-end
- **MCP Data Used:** code_tree (project structure), direct file reads (models.py, runner.py, vault.py for cross-reference)
- **Agents Deployed:** Orchestrator (direct execution — all database code, runner wiring, CLI updates, tests)
- **Architectural Decisions:**
  - SQLAlchemy 2.0 async + aiosqlite with WAL mode for concurrent CLI+web reads
  - 5 tables: `runs`, `results`, `evidence_chain`, `config`, `_schema_version` — no `users` or `framework_cache` (added post-v1)
  - JSON evidence vault remains as parallel output system (dual-write for backwards compatibility)
  - Engine version embedded in `_schema_version` for migration tracking
  - Evidence chain entries computed from vault hash files and linked via SHA-256
- **Files Created (4):**
  - `certifyai/engine/database/__init__.py` — Package init
  - `certifyai/engine/database/models.py` — 5 ORM tables with SQLAlchemy 2.0 mapped_column
  - `certifyai/engine/database/manager.py` — DatabaseManager class (init, CRUD, aggregation, chain)
  - `tests/test_database.py` — 20 tests (models, CRUD, aggregation, chain linking, schema version, WAL)
- **Files Modified (2):**
  - `certifyai/engine/runner.py` — `AttackRunner` accepts `db_manager` param, calls `_persist_results()` after run
  - `certifyai/cli/main.py` — `init` command creates DB schema, `run` command accepts `--db` and stores evidence chain
- **Test Results:** 88/88 tests passing (82 unit + 6 integration, 17 new database tests)
- **Build Status:** Pending push to GitHub
- **Next Turn Directive:** Phase 5 — Begin Web Dashboard (Next.js 14 + Tailwind + recharts) OR TUI polish

### [2026-07-21 19:15] — Phase 3: LiteLLM Integration Tests with NVIDIA NIM
- **State**: Success — 6 integration tests passing against live NVIDIA NIM API
- **MCP Data Used**: direct file reads (lite_llm.py, models.py for API config)
- **Agents Deployed**: Orchestrator (direct execution — conftest dotenv loading, integration test file)
- **Architectural Decisions**:
  - `.env` file auto-loaded via `python-dotenv` in `conftest.py` at module import time
  - Integration tests guarded by `--run-integration` flag + `pytest.mark.integration`
  - NVIDIA NIM free tier rate limits handled gracefully (tests skip on 429)
  - Only `prompt_injection` category used for attack-run tests (3 scenarios, 2 concurrency)
- **Files Created (1)**:
  - `tests/test_integration_llm.py` — 6 tests (basic completion, attack execution, performance)
- **Files Modified (2)**:
  - `tests/conftest.py` — Added automatic `.env` loading via `python-dotenv`
  - `.env` — Local only (gitignored), contains NVIDIA NIM API key
- **Test Results**: 71/71 passing — unit (65) + integration (6)
- **Build Status**: Pushed to GitHub (after next commit)
- **Next Turn Directive**: Phase 4 — Web Dashboard (Next.js 14 + Tailwind + recharts), OR SQLite database wiring

### [2026-07-21 18:30] — Phase 2: Plugin System Complete (6 categories, 18 scenarios, external loading)
- **State**: Success — 7 new/changed files, 65/65 tests passing
- **MCP Data Used**: code_tree (existing plugin structure), direct file reads (existing plugins for pattern matching)
- **Agents Deployed**: Orchestrator (direct execution — all plugin code, registry rewrite, CLI update, tests)
- **Architectural Decisions**:
  - 6 attack categories × 3 scenarios each = 18 built-in scenarios
  - External plugins load from user-specified directories via `--plugin-dir` (multiple allowed)
  - External plugins append scenarios to built-in ones (no override — all scenarios run)
  - `plugin_template.py` lives in the package but is excluded from production loading
  - `list-categories` CLI command for discovering available attacks
- **Files Created (5)**:
  - `certifyai/engine/redteam/policy_violation.py` — 3 scenarios (harmful content, ToS, impersonation)
  - `certifyai/engine/redteam/hallucination.py` — 3 scenarios (factual grounding, citations, statistics)
  - `certifyai/engine/redteam/bias.py` — 3 scenarios (stereotyping, allocation, cultural)
  - `certifyai/engine/redteam/plugin_template.py` — Annotated template with evaluation recipes
  - `tests/test_plugins.py` — 21 tests (registry, loading, external, integrity)
- **Files Modified (2)**:
  - `certifyai/engine/registry.py` — Added `_load_external_plugins()`, `reload()`, `list_categories()`
  - `certifyai/cli/main.py` — Added `--plugin-dir`, `list-categories` command
- **Test Results**: 65/65 passing — models (17), evidence (10), compliance (11), plugins (21), hasher (6)
- **Build Status**: Pushed to GitHub (`4729cc6`)
- **Next Turn Directive**: Phase 3 — LiteLLM integration tests with real provider, OR begin Web Dashboard (Next.js 14 + Tailwind + recharts), OR SQLite database wiring

### [2026-07-21 16:30] — Engine Core Phase 1 Complete (Models + CLI + Evidence + Compliance + 44 Tests)
- **State**: Success — Phase 1 implementation complete. 26 new files created.
- **MCP Data Used**: code_tree (AST verification for existing file structure), direct file reads (models.py, runner.py for cross-reference consistency)
- **Agents Deployed**: Orchestrator (direct execution — wrote all engine core files, CLI, tests)
- **Architectural Decisions**:
  - `AttackResult` requires `category` and `severity` as mandatory fields (reflects real model schema)
  - Evidence vault uses append-only SHA-256 hash chain with per-file `.hash` sidecar files
  - Compliance mapper supports pluggable YAML framework definitions in a `frameworks/` dir
  - CLI uses `RunConfig` + `ProviderConfig` (not the deprecated `AttackConfig`)
  - MockLLMClient returns predetermined responses for dry-run testing
- **Files Created (26)**:
  - `certifyai/engine/evidence/__init__.py`, `hasher.py`, `vault.py`
  - `certifyai/engine/compliance/__init__.py`, `mapper.py`
  - `certifyai/engine/compliance/frameworks/eu_ai_act.yaml`, `soc2.yaml`, `nist_ai_rmf.yaml`
  - `certifyai/cli/__init__.py`, `main.py`
  - `certifyai/tui/__init__.py`, `app.py`
  - `tests/__init__.py`, `conftest.py`, `test_models.py`, `test_evidence.py`, `test_compliance.py`
- **Test Results**: 44/44 tests passing — models (17), evidence (10), compliance (11), hasher (6)
- **Build Status**: `pip install -e ".[dev]"` works in venv. CLI `--help` responds. 52 ruff warnings (mostly line-length) — not blocking for alpha.
- **Next Turn Directive**: Phase 2 — Plugin system completion (scenario registry + attack plugin template), LiteLLM integration tests with real provider, or begin Web Dashboard (Next.js)

### [2026-07-21 15:00] — GitHub Repository Created & Initial Commit Pushed
- **State:** Success — Repo created at `https://github.com/ravikumarve/CertifyAI`
- **Description:** "Continuous compliance engine for AI runtimes. Self-hosted CLI + TUI + Web Dashboard that tests LLMs against 30+ attack scenarios and generates audit-ready evidence for EU AI Act, SOC 2 Type II, and NIST AI RMF. No subscription. No cloud dependency. Bring your own LLM key."
- **Files pushed:** 21 files — README.md, idea.md, AGENTS.md, .gitignore, and 17 docs
- **Commit message:** "Initial commit: complete documentation suite for CertifyAI"
- **Branch:** main
- **Next Turn Directive:** Begin implementation — pyproject.toml scaffold, Pydantic models, LiteLLM integration, attack plugin system

### [2026-07-21 14:30] — Wave 3 Docs Complete (GTM Suite + Commercial License)
- **State:** Success — All 17 docs complete (Waves 1-3), 20,668 total lines, 1.1MB
- **MCP Data Used:** direct file reads (agent profiles, existing docs for cross-reference consistency)
- **Agency Agents Deployed:** @pricing-analyst (pricing-strategy.md), @content-creator (gumroad-listing.md + devto-content-plan.md), @growth-hacker (producthunt-launch-kit.md), @social-media-strategist (community-launch-strategy.md), @support-responder (support-plan.md), @legal-compliance-checker (commercial-license.md)
- **Docs Created in Wave 3:**
  - `docs/pricing-strategy.md` — 729 lines, value quantification ($12K–$32K DIY vs $149), WTP by 5 segments, 12-month revenue projections ($78K–$665K), $149 recommended
  - `docs/gumroad-listing.md` — 312 lines, full Pro + Enterprise listing copy, comparison table, FAQ, refund policy
  - `docs/producthunt-launch-kit.md` — 956 lines, tagline, 18 target makers, hour-by-hour schedule, 8 comment templates, cross-promotion with HN/Reddit
  - `docs/devto-content-plan.md` — 612 lines, 8 article plan with headlines, structures, code snippets, Reddit blurbs
  - `docs/community-launch-strategy.md` — 1,088 lines, 4 Reddit post drafts, 18-tweet X thread, LinkedIn posts, platform-specific norms
  - `docs/support-plan.md` — 1,027 lines, tier definitions, 10 email templates, self-service architecture, 90% ticket deflection target
  - `docs/commercial-license.md` — 351 lines, Apache 2.0 vs Pro vs Enterprise, plain-English EULA, India governing law, explicit compliance disclaimer
- **Key Business Decisions:** $149 Pro / $499 Enterprise confirmed with sensitivity analysis. India jurisdiction for licensing. No Discord for v1 (GitHub Discussions only). Support hard-walled by tier. 14-day no-questions refund.
- **Next Turn Directive:** Phase 1 — Begin coding (Engine Core: pyproject.toml → Pydantic models → LiteLLM integration → Attack plugin system)

### [2026-07-21 13:00] — Wave 2 Docs Complete (UX Flows + Test Strategy + Attack Catalog + Compliance Spec + Security + DB Schema)
- **State:** Success — All 10 docs complete (Wave 1 + Wave 2), 15,593 total lines, 836KB
- **MCP Data Used:** code_tree (structure verification), direct file reads (agent profiles, existing docs for context)
- **Agency Agents Deployed:** @ux-architect (ux-flows.md), @test-automation-engineer (test-strategy.md), @model-qa-specialist (attack-scenario-catalog.md), @compliance-auditor (compliance-framework-spec.md), @security-architect (security-architecture.md), @database-optimizer (database-schema.md)
- **Docs Created in Wave 2:**
  - `docs/ux-flows.md` — 2,343 lines, 3 persona journeys, 7 CLI flowcharts, 6 TUI screens, 8 dashboard pages, 9 error recovery flows
  - `docs/test-strategy.md` — 2,924 lines, pyramid strategy, Playwright E2E, property-based tests (hypothesis), CI pipeline with flake quarantine
  - `docs/attack-scenario-catalog.md` — 2,136 lines, 36 attack scenarios (6 categories × 6 each), plugin interface spec, scoring methodology
  - `docs/compliance-framework-spec.md` — 1,670 lines, EU AI Act Art. 9-15 deep map, SOC 2 CC3-CC9, NIST AI RMF 4 functions, ISO 42001, report JSON Schema
  - `docs/security-architecture.md` — 1,253 lines, STRIDE threat model (36 attack scenarios), evidence vault adversarial analysis, API key management, supply chain risk, 5-phase security roadmap
  - `docs/database-schema.md` — 1,752 lines, 7 tables with full CREATE TABLE SQL, 15 query patterns, index strategy, WAL mode config, PostgreSQL migration path, query cookbook
- **Key Architectural Decisions:** Evidence chain is detect-only (not prevent-only) — cross-DB commitment needed pre-v1. LiteLLM flagged as highest supply chain risk. WAL mode for concurrent CLI+Dashboard SQLite reads. 13 high-value attacks serving all 4 frameworks identified.
- **Next Turn Directive:** Wave 3 — GTM documents (Pricing, Gumroad Listing, PH Launch Kit, Dev.to Content Plan, Community Strategy, Support Plan) OR begin Phase 1 coding

### [2026-07-21 12:00] — Wave 1 Docs Complete (Market Research + Competitive Analysis + PRD + Technical Architecture)
- **State:** Success — All 4 foundation documents created, 3,515 total lines
- **MCP Data Used:** websearch (competitor research, EU AI Act timeline, market sizing data), code_tree (project structure verification)
- **Agency Agents Deployed:** @trend-researcher (market-research-report.md), @business-strategist (competitive-analysis.md), @product-manager (PRD.md), @software-architect (technical-architecture.md)
- **Docs Created:**
  - `docs/market-research-report.md` — 357 lines, $492M TAM analysis, 25 sources, 4 customer segments, risk-adjusted entry recommendation
  - `docs/competitive-analysis.md` — 721 lines, 8 competitor deep-dives, positioning maps, Porter's Five Forces, 12-18 month competitive window assessment
  - `docs/PRD.md` — 863 lines, 3 personas (Priya/Marcus/Elena), 13 user stories, 7 non-goals with rationale, 3-phase launch plan
  - `docs/technical-architecture.md` — 1,574 lines, C4 architecture model, 8 ADRs, complete SQLite schema, plugin attack architecture, evolution strategy
- **Key Architectural Decisions:** ADR-006 (plugin attack architecture), ADR-007 (hybrid filesystem+SQLite evidence vault), ADR-008 (direct SQLite reads from Next.js, no API server)
- **Next Turn Directive:** Wave 2 — UX Flows, Test Strategy, Attack Scenario Catalog, Compliance Framework Spec, Security Architecture, Database Schema

### [2026-07-21 10:00] — CertifyAI Idea Validation & Pivot
- **State:** Success — Idea validated, pivoted from enterprise SaaS to boilerplate product
- **MCP Data Used:** websearch (competitor analysis: Vanta, Credo AI, Drata, IBM watsonx, Holistic AI), websearch (regulatory landscape: EU AI Act enforcement 2026, fines up to €35M/7%, Digital Omnibus delay), websearch (market size: $3.4B AI governance market at 39.4% CAGR)
- **Agents Deployed:** Orchestrator (direct execution — competitive research, regulatory analysis, feasibility assessment)
- **Architectural Decisions:** ADR-001 through ADR-005 (see above)
- **Key Findings:**
  - 78% of orgs not ready for EU AI Act (Aug 2026 deadline)
  - No competitor ships a downloadable AI compliance engine
  - Incumbents (Vanta $350M, Credo AI $41M) are SaaS-only at $30K+/yr
  - Boilerplate model eliminates all 5 critical risks for solo dev
- **Build Status:** Pre-code phase complete. idea.md rewritten with full tech stack + 8-week build plan. AGENTS.md created.
- **Next Turn Directive:** Begin Phase 1 implementation (Engine Core — weeks 1-3) OR validate demand first (write Dev.to posts, launch waitlist, gauge community response before writing code)

---

## 🎯 Quick Reference

### Key Commands (for development)
```bash
# Run all tests
pytest tests/ -v

# Run unit tests only (skip integration)
pytest tests/ -v -m "not integration"

# Run integration tests (requires .env with NVIDIA NIM key)
pytest tests/ -v -m integration --run-integration

# CLI
python -m certifyai.cli.main init --db /path/to/certifyai.db
python -m certifyai.cli.main run --provider openai --model gpt-4o --db /path/to/certifyai.db
```

### Directory Structure
```
certifyai/
├── cli/                  # Click commands
├── tui/                  # Textual screens
├── engine/               # Core logic
│   ├── redteam/          # Attack scenarios (6 categories, 18 scenarios)
│   ├── evidence/         # Vault & SHA-256 hash chain
│   ├── compliance/       # Framework mapper (EU AI Act, SOC 2, NIST AI RMF)
│   └── database/         # SQLAlchemy 2.0 ORM + async DatabaseManager
├── web/                  # Next.js dashboard (future)
├── docs/                 # MkDocs documentation
├── tests/                # pytest (88 tests — 82 unit + 6 integration)
├── pyproject.toml
└── README.md
```
