# 🤖 CertifyAI — Project Command Center

**Project:** Continuous Compliance Engine for AI Runtimes
**Delivery Model:** Shippable Boilerplate (PyPI + Gumroad)
**Primary Stack:** Python 3.11+ (asyncio, Pydantic v2, LiteLLM, Click, Textual), Next.js 14 (Tailwind, motion, recharts), SQLite
**Host:** Dell Latitude 3460 (Ubuntu) — CPU-only, no heavy Docker/K8s

---

## 📋 Project State

| Attribute | Value |
|-----------|-------|
| **Phase** | Pre-code (idea validated, tech stack finalized) |
| **Code written** | 0 lines |
| **Documents** | `idea.md` (updated with boilerplate positioning), `AGENTS.md` (this file) |
| **Git repo** | No |
| **Revenue** | $0 |
| **Next action** | Phase 1 implementation or pre-build demand validation |

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

### Key Commands (once built)
```bash
# Install
pip install certifyai

# Quick start
certifyai init                              # Setup wizard
certifyai run --provider openai --model gpt-4o  # Run attack battery
certifyai report --format pdf               # Generate compliance report
certifyai vault --verify                    # Verify evidence integrity
```

### Directory Structure (proposed)
```
certifyai/
├── cli/                  # Click commands
├── tui/                  # Textual screens
├── engine/               # Core logic
│   ├── redteam/          # Attack scenarios
│   ├── evidence/         # Vault & hash chain
│   └── compliance/       # Framework mapper
├── web/                  # Next.js dashboard
├── docs/                 # MkDocs documentation
├── tests/                # pytest + Playwright
├── pyproject.toml
└── README.md
```
