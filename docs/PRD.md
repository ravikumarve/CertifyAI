# CertifyAI — Product Requirements Document

**Document Status:** Draft v1.0
**Author:** Alex (Product Manager)
**Date:** 2026-07-21
**Product:** Continuous Compliance Engine for AI Runtimes
**Delivery Model:** Shippable Boilerplate (PyPI + Gumroad), NOT SaaS

---

## Table of Contents

1. [Problem Statement](#1-problem-statement)
2. [Goals & Success Metrics](#2-goals--success-metrics)
3. [Non-Goals (v1.0 Explicit Exclusions)](#3-non-goals-v10-explicit-exclusions)
4. [User Personas & Stories](#4-user-personas--stories)
5. [Solution Overview](#5-solution-overview)
6. [Technical Considerations](#6-technical-considerations)
7. [Launch Plan](#7-launch-plan)
8. [Appendix](#8-appendix)

---

## 1. Problem Statement

### The Compliance Gap

Every organization deploying LLMs in production faces a growing regulatory imperative. The EU AI Act's high-risk deadline is August 2, 2026 — 78% of organizations are not ready. SOC 2 audits increasingly ask: "How do you test your AI system's behavior?" NIST AI RMF requires continuous measurement. Yet the tooling landscape is a wasteland.

### The Three Failures of Current Tooling

**Failure 1: Enterprise SaaS pricing locks out the teams who need it most.**

Vanta ($7.5K-$10K+/yr), Drata ($15K-$60K+/yr), and Credo AI ($30K-$150K+/yr) price for enterprises with compliance budgets and dedicated GRC staff. A 15-person startup preparing for a SOC 2 Type II cannot justify $30K/yr on compliance software — that's a full engineering salary in many markets. These platforms are designed for Fortune 500 procurement cycles, not for teams that move fast.

**Failure 2: "Compliance" tools don't test AI behavior.**

Vanta and Drata are excellent at monitoring cloud infrastructure — S3 bucket encryption, IAM role configuration, SOC 2 CC6 access controls. But they cannot send a prompt to an LLM, evaluate whether the response contains PII, or determine if a jailbreak succeeded. They are static infrastructure monitors applying to a dynamic, probabilistic runtime. The core artifact they need to audit — the AI's behavior — is invisible to them.

**Failure 3: Open-source pieces are fragmented and require assembly.**

There are excellent OSS components: Garak for LLM red-teaming, Guardrails AI for output validation, LangChain's evaluation frameworks. But stitching them into a compliance pipeline requires significant engineering investment. You need to build your own evidence vault, your own compliance mapping layer, your own report generation, your own scheduling. Each piece is maintained by a different community with different release cadences. The integration surface area is large and fragile.

### The Opportunity

Teams need a **single, self-contained, downloadable tool** that:

- Tests LLM endpoints against comprehensive attack scenarios (injection, jailbreak, PII, bias, hallucination, policy violation)
- Logs every test with cryptographic evidence (SHA-256 hash chain)
- Maps results directly to regulatory frameworks (EU AI Act, SOC 2, NIST AI RMF, ISO 42001)
- Generates auditor-ready reports (PDF, SARIF, JSON)
- Can be air-gapped with local models (Ollama)
- Costs less than a good mechanical keyboard

This is CertifyAI.

### Why Boilerplate, Not SaaS

This is arguably the most important product decision we made. CertifyAI ships as a Python package. The customer runs it on their own hardware. We do not operate servers, store customer data, or require internet access at runtime.

**Trade-off acknowledged:** We give up recurring revenue, usage-based pricing, and the "sticky" economics of SaaS. We accept this because the alternative — building a multi-tenant SaaS with SOC 2 compliance, 24/7 uptime SLAs, and enterprise sales — is structurally impossible for a solo developer and would price out exactly the teams that need this tool.

The boilerplate model aligns incentives: the customer gets a zero-ops, one-time-purchase tool that works forever. We get revenue without infrastructure liability.

---

## 2. Goals & Success Metrics

### Product Goals

| Goal | Rationale |
|------|-----------|
| **G1: Time-to-value under 5 minutes** | A senior engineer should go from `pip install certifyai` to their first compliance report in under 5 minutes. This is the metric that determines whether a casual evaluation converts to a Pro purchase. |
| **G2: Zero-dependency core for 80% of users** | The CLI + TUI must run with only Python installed. No Docker, no Node.js, no database server. The Web Dashboard (Pro tier) is the only component with additional dependencies. |
| **G3: Evidence integrity must be cryptographically verifiable** | Every attack result must produce a SHA-256 hash that chains to previous results. An auditor should be able to run `certifyai vault --verify` and prove no evidence was tampered with since creation. |
| **G4: Framework mappings must be auditable and extensible** | Customers must be able to read, understand, and modify the compliance mappings (YAML files shipped with the product). The boilerplate is not a black box. |

### Success Metrics

**Adoption Metrics (North Stars)**

| Metric | Target | Measurement |
|--------|--------|-------------|
| Free-tier activation rate | >60% of pip installs result in `certifyai init` completion | Telemetry (opt-in) |
| First-report generation | >40% of activations generate a report within 24h | Telemetry |
| Pro tier conversion rate | >5% of active free users convert to Pro | Gumroad analytics |
| Pro user engagement | >3 reports generated in first 90 days | Telemetry |
| Net Promoter Score (free tier) | NPS >40 | Quarterly survey |

**Quality Metrics**

| Metric | Target | Measurement |
|--------|--------|-------------|
| Attack success rate (known-good model) | Jailbreak tests should correctly FAIL on Claude 4, PASS on weak models — verifies test validity | CI benchmark suite |
| False positive rate (policy tests) | <5% on curated test set | Manual review per release |
| Report generation success | >99% of `certifyai report` commands complete without error | Telemetry |
| Evidence chain verification | 100% of generated chains pass `vault --verify` | Automated test suite |

**Business Metrics**

| Metric | Target (Month 6 steady state) | Measurement |
|--------|-------------------------------|-------------|
| Free monthly active users | 1,000+ | PyPI download stats + opt-in telemetry |
| Pro sales | 30-50/month | Gumroad |
| Enterprise sales | 5-10/month | Gumroad |
| Monthly revenue | $7,000-$12,000 | Gumroad |
| Gross margin | ~90% (no hosting costs, only payment processing) | Accounting |

### Why These Metrics Matter

The most important metric for a boilerplate product is **time-to-first-value**. Unlike SaaS, where we can use free trials and onboarding sequences to demonstrate value, a PyPI package has approximately 30 seconds of the user's attention after `pip install` completes. If `certifyai run` doesn't produce compelling output immediately, the user moves on and never converts.

The conversion rate from free to Pro (>5%) is the critical viability metric. At 5% conversion and $149 ASP, we need approximately 670 monthly free active users to sustain $5K/mo revenue. This is achievable with a single Product Hunt launch and ongoing organic growth.

---

## 3. Non-Goals (v1.0 Explicit Exclusions)

Every product fails by what it chooses not to do. These are the capabilities we are explicitly deferring to v2.0 or later.

### No Multi-Tenancy

- v1.0 assumes a single user per installation
- No user roles (admin, viewer, auditor)
- No organization accounts
- **Why deferred:** Multi-tenancy adds authentication complexity, requires a session management layer, and increases the support surface. Our target buyer (startup CTO, solo ML engineer) is the only user.

### No Cloud Sync or Collaboration

- No shared evidence vaults across machines
- No team dashboards
- No comment/annotation features on reports
- **Why deferred:** Collaboration features require a server-side component, which reintroduces the ops burden we deliberately eliminated with the boilerplate model. For v1.0, sharing means "email the PDF."

### No CI/CD Plugins

- No GitHub Actions orb
- No GitLab CI template
- No Jenkins plugin
- No `certifyai run` in CI pipelines
- **Why deferred:** CI plugins require maintaining integrations across multiple CI platforms and handling non-interactive execution environments. This is the single most requested feature for v2.0, but adds 2-3 weeks of build and testing effort per integration. We ship v1.0 without them and validate that demand exists.

### No Custom Attack Authoring SDK

- v1.0 ships with 30 attack scenarios (Pro) / 10 (Free)
- Users cannot write their own attack plugins without modifying source code
- **Why deferred:** A plugin SDK requires designing a stable public API, writing documentation, and maintaining backward compatibility. For v1.0, the built-in attack catalog covers the OWASP LLM Top 10 plus regulatory-specific tests. Custom attacks can be contributed via pull requests.

### No API Server

- The Web Dashboard reads SQLite directly via `better-sqlite3`
- No REST API, no GraphQL, no WebSocket server
- No programmatic access to results
- **Why deferred:** An API server would become the single most complex component to maintain (auth, rate limiting, versioning, documentation). The direct SQLite read approach works for single-user access and eliminates an entire class of bugs.

### No Scheduled/Continuous Monitoring

- v1.0 is primarily `certifyai run` on demand
- No cron/daemon mode
- No alerting (email, Slack, webhook)
- **Why deferred:** Scheduled execution depends on the host OS and requires handling edge cases (sleep/wake, network interruptions, credential rotation). We ship a manual trigger in v1.0 and add scheduling in v2.0 once we understand common failure modes.

### No Third-Party Integrations

- No Jira, Slack, Teams, or email notifications
- No evidence export to Vanta/Drata/Sprout
- **Why deferred:** Each integration adds ongoing maintenance cost. We need to validate that customers want these integrations before committing to them.

### No Mobile Experience

- Web Dashboard is desktop-only (Next.js, not responsive for mobile)
- **Why deferred:** Compliance report review on a phone is a poor experience. If users demand mobile access, we'll add it in v2.0.

---

## 4. User Personas & Stories

### Persona 1: Priya, Startup CTO

**Background:** Priya is CTO of a 25-person health-tech startup building a clinical decision support tool. They raised a $5M Seed round 8 months ago. SOC 2 Type II is a requirement for their first enterprise customer (a hospital network). Priya's engineering team is 8 people, none of whom are compliance specialists.

**Technical context:**
- LLM: GPT-4o via Azure OpenAI (HIPAA BAA in place)
- Infrastructure: AWS, Terraform, Docker
- Current compliance tool: None — using Google Sheets to track controls
- Budget: Has budget for compliance tools but cannot justify $30K+/yr
- Pain: External auditor asked "How do you test your AI system for PII leakage and biased outputs?" and Priya had no answer

**Core Needs:**
1. Generate audit-ready evidence that SOC 2 auditors will accept
2. Demonstrate that the AI system has been tested against a known attack taxonomy
3. Prove evidence integrity (tamper-proof logs)
4. Do this without hiring a compliance engineer

#### Priya's Stories

**Story P1: Initial Compliance Baseline**

> **Title:** Run first compliance sweep for SOC 2 evidence
>
> **As a** startup CTO preparing for SOC 2 Type II,
> **I want** to run a complete attack battery against my LLM endpoint and get a compliance report mapped to SOC 2 controls,
> **So that** I can provide auditors with documented evidence of AI red-teaming.
>
> **Acceptance Criteria (Given/When/Then):**
> - Given I have my Azure OpenAI endpoint and API key configured
> - When I run `certifyai run --provider azure --model gpt-4o --framework soc2`
> - Then all 30 attack scenarios execute against my endpoint
> - And each result is logged to `~/.certifyai/certifyai.db` with a SHA-256 hash
> - And a SOC 2 compliance report is generated at `~/.certifyai/reports/report_soc2_latest.pdf`
> - And the report maps each attack result to specific CC (Common Criteria) controls

**Story P2: Evidence Chain Verification**

> **Title:** Verify evidence integrity before auditor review
>
> **As a** startup CTO who needs to present evidence to external auditors,
> **I want** to cryptographically verify that no evidence has been tampered with since creation,
> **So that** auditors can trust the integrity of our compliance documentation.
>
> **Acceptance Criteria:**
> - Given I have completed at least one attack run
> - When I run `certifyai vault --verify`
> - Then the tool checks the SHA-256 hash chain from the first evidence entry to the last
> - And outputs a report showing all entries verified (or tampered entries flagged)
> - And the exit code is 0 if the chain is intact, non-zero if tampering is detected

**Story P3: Differential Report for Remediation**

> **Title:** Compare compliance posture between deployments
>
> **As a** startup CTO deploying model updates weekly,
> **I want** to compare compliance reports across runs to see if regressions were introduced,
> **So that** I can catch compliance issues before they reach production.
>
> **Acceptance Criteria:**
> - Given I have at least two previous attack runs in the database
> - When I run `certifyai report --diff run_abc123 run_def456`
> - Then I see a side-by-side comparison showing passed/failed tests in each run
> - And new failures (regressions) are highlighted in red
> - And new passes (fixes) are highlighted in green

**Story P4: Quick Configuration**

> **Title:** Set up the tool with minimal friction
>
> **As a** time-constrained CTO,
> **I want** to configure my LLM endpoint through an interactive wizard,
> **So that** I can get to the first attack run in under 3 minutes.
>
> **Acceptance Criteria:**
> - Given I have installed certifyai via pip
> - When I run `certifyai init`
> - Then I am guided through an interactive setup (provider selection, API key, model name)
> - And my configuration is saved to `~/.certifyai/config.toml`
> - And the wizard offers to run the first attack sweep immediately after configuration

---

### Persona 2: Marcus, ML Engineer

**Background:** Marcus is an ML engineer at a 10-person AI startup building a code generation copilot. His background is in NLP research. He's responsible for the model's safety and reliability. He needs to red-team their fine-tuned Llama 3 model hosted on their own GPU server (Ollama).

**Technical context:**
- LLM: Fine-tuned Llama 3 70B via Ollama (self-hosted, air-gapped)
- Infrastructure: On-prem GPU server, no cloud
- Current tool: Manual testing with Python scripts
- Budget: No budget — needs free tier
- Pain: His CTO mentioned they need "some kind of compliance testing" but hasn't made it a priority. Marcus needs to demonstrate value before asking for budget.

#### Marcus's Stories

**Story M1: Air-Gapped Red-Teaming**

> **Title:** Run attack battery against self-hosted model with no internet
>
> **As an** ML engineer working with a self-hosted model on an air-gapped network,
> **I want** to run the full attack battery against my Ollama endpoint,
> **So that** I can identify vulnerabilities in our fine-tuned model without sending data to external APIs.
>
> **Acceptance Criteria:**
> - Given my Ollama server is running at `http://localhost:11434`
> - And the machine has no internet access to external LLM providers
> - When I run `certifyai run --provider ollama --model llama3-custom`
> - Then all attacks execute using only the local Ollama endpoint
> - And results are stored locally with no outbound network calls (except LiteLLM -> Ollama on localhost)
> - And a JSON report is generated at `~/.certifyai/reports/report_latest.json`

**Story M2: Targeted Attack by Category**

> **Title:** Run only prompt injection tests during development sprints
>
> **As an** ML engineer iterating on prompt injection defenses,
> **I want** to run only the prompt injection attack category without waiting for the full battery,
> **So that** I can quickly validate whether my latest defense works.
>
> **Acceptance Criteria:**
> - Given I have configured my endpoint
> - When I run `certifyai run --attack injection`
> - Then only prompt injection scenarios execute (direct injection, indirect injection, encoded injection)
> - And results are stored in the same database format as a full run
> - And a summary is printed to stdout showing pass/fail per scenario
> - And the run completes in under 60 seconds (vs. potentially minutes for full battery)

**Story M3: TUI-Based Investigation**

> **Title:** Browse and analyze past attack results interactively
>
> **As an** ML engineer investigating a specific failure pattern,
> **I want** to browse past attack runs in a terminal UI,
> **So that** I can compare results across runs and dive into specific attack evidence without leaving the terminal.
>
> **Acceptance Criteria:**
> - Given I have multiple attack runs in the database
> - When I launch `certifyai tui`
> - Then I see a dashboard showing overall pass/fail metrics across all runs
> - And I can navigate to an Explorer screen to filter runs by date, attack type, or severity
> - And I can select a specific attack result to view the full prompt, response, and evidence
> - And the UI updates in real-time if a new run is started from another terminal

**Story M4: Free Tier Evaluation**

> **Title:** Evaluate tool with free tier before requesting purchase
>
> **As an** ML engineer who needs to convince my CTO to buy the Pro tier,
> **I want** to use the free CLI with 10 attack scenarios and generate basic reports,
> **So that** I can demonstrate concrete value before asking for budget.
>
> **Acceptance Criteria:**
> - Given I have installed certifyai from PyPI (free tier)
> - When I run `certifyai list-attacks`
> - Then I see 10 available attack scenarios (not 30)
> - And when I run an attack sweep, all 10 scenarios execute
> - And I can generate a JSON report
> - And the report footer includes a note: "Generated with CertifyAI Lite. Upgrade to Pro for 30 attack scenarios, PDF reports, and compliance mapping."
> - And no functionality is broken or restricted — only the attack count and report formats differ

---

### Persona 3: Elena, Compliance Consultant

**Background:** Elena runs a boutique AI compliance consultancy. She has 15 clients, mostly startups preparing for EU AI Act compliance. She audits their AI systems and produces compliance documentation. She needs a tool that generates standardized, auditor-acceptable evidence across multiple client environments.

**Technical context:**
- Operations: Runs audits on client machines (brings her laptop, connects to their LLM endpoints)
- Reporting: Produces PDF compliance reports for each client
- Scale: 15 clients, each needing quarterly audits
- Current tool: Manually crafting test prompts and screenshots in Google Docs
- Budget: $499 Enterprise tier + commercial license is a no-brainer for her billable rate ($250/hr)
- Pain: Manual testing doesn't scale. Each client audit takes 3-4 days of prompt crafting, testing, and report writing.

#### Elena's Stories

**Story E1: Multi-Framework Compliance Report**

> **Title:** Generate auditor-ready report mapped to multiple frameworks
>
> **As a** compliance consultant auditing a client's AI system,
> **I want** to generate a single report that maps attack results to EU AI Act articles and NIST AI RMF categories,
> **So that** I can deliver comprehensive, auditor-acceptable evidence without manual mapping.
>
> **Acceptance Criteria:**
> - Given I have configured my client's LLM endpoint
> - When I run `certifyai run --framework eu_ai_act --framework nist_ai_rmf`
> - Then all attacks execute and results are stored with timestamps
> - And when I run `certifyai report --format pdf --frameworks eu_ai_act,nist_ai_rmf`
> - Then the generated PDF includes:
>   - Executive summary (overall compliance score per framework)
>   - Per-attack evidence (prompt, response, verdict, severity)
>   - Framework mapping section (article/clause -> evidence reference)
>   - Evidence integrity certificate (hash chain root)

**Story E2: White-Label Reports**

> **Title:** Generate branded compliance reports for client delivery
>
> **As a** compliance consultant who needs to deliver professional reports to clients,
> **I want** to generate compliance reports with my own branding (logo, colors, disclaimer),
> **So that** the report appears as my own work product, not a third-party tool output.
>
> **Acceptance Criteria:**
> - Given I have a brand configuration file (`brand.yaml`)
> - When I run `certifyai report --format pdf --brand brand.yaml`
> - Then the PDF includes my logo on the cover page and header
> - And my company name replaces "CertifyAI" in the report header
> - And a custom disclaimer/disclosure page is included
> - And the evidence integrity certificate is still present (trust layer is preserved)

**Story E3: Batch Processing Multiple Clients**

> **Title:** Run standard attack battery across multiple client environments
>
> **As a** compliance consultant managing 15 client audits per quarter,
> **I want** to run the same standardized attack battery across different client endpoints,
> **So that** I ensure consistent testing methodology across all clients.
>
> **Acceptance Criteria:**
> - Given I have configuration files for multiple clients in `~/.certifyai/profiles/`
> - When I run `certifyai run --profile client_acme_corp`
> - Then the tool loads that client's LLM configuration from the profile
> - And executes the same attack battery as for all other clients
> - And results are stored in a client-specific database or tagged by client
> - And reports are generated with the client's name in the filename

**Story E4: Source Access for Custom Mappings**

> **Title:** Extend compliance framework mappings for emerging regulations
>
> **As a** compliance consultant staying ahead of regulatory changes,
> **I want** to access, modify, and add new framework mapping YAML files,
> **So that** I can update mappings when regulations change or add custom client-specific frameworks (e.g., HIPAA AI guidance).
>
> **Acceptance Criteria:**
> - Given I have Enterprise-tier source access
> - When I navigate to `~/.certifyai/frameworks/`
> - Then I see YAML files for EU AI Act, SOC 2, NIST AI RMF, ISO 42001
> - And each YAML file follows a documented schema (framework name, articles, clauses, associated attack categories)
> - And when I modify a mapping file and re-run a report, the new mappings appear
> - And invalid YAML produces a clear error message indicating the schema violation

---

## 5. Solution Overview

### The Full Pipeline

CertifyAI is a pipeline. Data flows from configuration through execution through evidence storage through compliance mapping through report generation.

```
┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐
│  INIT    │ →  │  CONFIG  │ →  │  ATTACK  │ →  │   VAULT  │ →  │  REPORT  │
│  Setup   │    │  YAML    │    │  ENGINE  │    │  EVIDENCE│    │  GENERATE│
│  Wizard  │    │  TOML    │    │  30+     │    │  SHA-256 │    │  PDF     │
│          │    │          │    │  attacks │    │  Chain   │    │  SARIF   │
└──────────┘    └──────────┘    └──────────┘    └──────────┘    └──────────┘
                                      │
                                      ▼
                               ┌──────────────┐
                               │   LiteLLM    │
                               │  (100+ LLM   │
                               │  providers)  │
                               └──────────────┘
```

### Step-by-Step Walkthrough

#### Step 1: `certifyai init` (Setup Wizard)

The user runs `certifyai init` once after installation. An interactive wizard collects:

- LLM provider (OpenAI, Anthropic, Azure OpenAI, Ollama, Gemini, or any OpenAI-compatible endpoint)
- Model name (e.g., `gpt-4o`, `claude-4-sonnet`, `llama3.1`, `gemini-2.0-flash`)
- API key (stored in `~/.certifyai/config.toml`, permissions: 600)
- Optional: custom endpoint URL for self-hosted or proxy setups
- Optional: compliance frameworks to map (defaults to all shipped frameworks)

The wizard validates the connection by sending a simple test prompt before proceeding. If validation fails, the user gets immediate feedback and can correct credentials.

**Why interactive?** The first-run experience is the highest-leverage moment in the product. A wizard reduces cognitive load and increases activation rate. Power users can skip the wizard and edit `config.toml` directly.

#### Step 2: Configuration File

Written to `~/.certifyai/config.toml`:

```toml
[llm]
provider = "openai"
model = "gpt-4o"
api_key = "${OPENAI_API_KEY}"  # Can use env var references
endpoint = ""                   # Optional: for self-hosted/proxy

[compliance]
frameworks = ["eu_ai_act", "nist_ai_rmf", "soc2", "iso42001"]

[behavior]
auto_update = true              # Check for new attack scenarios on run
telemetry = false               # Opt-in usage data
max_concurrent = 5              # Parallel attack execution
```

#### Step 3: `certifyai run` (Attack Execution)

This is the core execution engine. When the user runs:

```bash
certifyai run --provider openai --model gpt-4o
```

The engine:

1. **Loads all attack scenarios** from the built-in catalog (10 for Free, 30 for Pro/Enterprise). Each scenario is a Pydantic-validated specification containing:
   - Attack name and description
   - Category (injection, jailbreak, PII, policy, hallucination, bias)
   - One or more prompt templates (with optional randomization/permutations)
   - Expected behavior criteria (what constitutes a "pass")
   - Severity rating (critical, high, medium, low, info)
   - Framework clause references

2. **Executes attacks** against the configured LLM endpoint via LiteLLM. Attacks within a category run sequentially to avoid cross-contamination. Categories run concurrently using `asyncio.TaskGroup` (up to `max_concurrent` categories at once).

3. **Evaluates responses** against criteria:
   - Injection: Did the response follow the injected instruction?
   - Jailbreak: Did the model refuse or comply with the prohibited request?
   - PII: Does the response contain patterns matching email, phone, SSN, credit card?
   - Policy: Does the response contain hate speech, dangerous content, etc.?
   - Hallucination: Does the response claim facts that contradict known ground truth?
   - Bias: Does the response show statistically significant demographic bias?

4. **Records results** to SQLite. Each result record includes:
   - UUID, timestamp, attack ID, provider, model
   - Full prompt sent to the LLM
   - Full response received
   - Pass/fail verdict with confidence score
   - Severity level
   - Evidence metadata (hash, chain reference)

5. **Streams progress** to stdout (with Rich progress bars) or the TUI (real-time dashboard).

**Execution time estimate:** A full battery of 30 attacks against GPT-4o takes approximately 2-5 minutes depending on API latency and network conditions.

#### Step 4: Evidence Vault (Cryptographic Integrity)

Every attack result feeds into an append-only evidence chain. The vault lives at `~/.certifyai/vault/` on the filesystem.

**Chain structure:**
- Each attack result generates a JSON evidence blob
- The blob is hashed (SHA-256) producing `evidence_hash`
- Each new entry references the previous entry's hash: `chain[n] = HASH(evidence_blob[n] || chain[n-1])`
- The chain root hash represents the complete integrity of all evidence

```
chain.db (append-only):
┌─────────────────────────────────────────────┐
│ Entry 0 (genesis)                          │
│  prev_hash: 0000000000000000...             │
│  evidence_hash: a1b2c3d4e5f6...            │
│  chain_hash: HASH(ev_0 || prev_0)          │
│  timestamp: 2026-07-21T10:00:00Z           │
├─────────────────────────────────────────────┤
│ Entry 1                                    │
│  prev_hash: a1b2c3d4e5f6...  ← Entry 0    │
│  evidence_hash: f6e5d4c3b2a1...            │
│  chain_hash: HASH(ev_1 || prev_1)          │
│  timestamp: 2026-07-21T10:00:05Z           │
├─────────────────────────────────────────────┤
│ ...                                         │
└─────────────────────────────────────────────┘
```

**Verification:** `certifyai vault --verify` walks the chain from genesis to tip, recomputing each `chain_hash` and confirming it matches the stored value. Any discrepancy is flagged immediately.

**Why this matters for auditors:** A SOC 2 auditor can request the evidence chain, run `verify`, and confirm that no results were inserted, deleted, or modified after the fact. This is stronger evidence than a database dump.

#### Step 5: `certifyai report` (Compliance Report Generation)

The user generates a compliance report:

```bash
certifyai report --format pdf --framework eu_ai_act
```

The report generator:

1. **Queries the database** for all attack results
2. **Loads the requested framework mappings** from YAML (EU AI Act articles mapped to attack categories)
3. **Aggregates results** by framework clause:
   - Which attacks map to which articles/controls
   - Pass/fail status per article
   - Severity distribution
   - Evidence references (hashes, timestamps)
4. **Generates the report** using Jinja2 templates -> HTML -> WeasyPrint -> PDF

**Report structure (PDF):**
- Cover page (project name, date, framework, tool version)
- Executive summary (compliance score, pass rate, critical findings)
- Methodology overview (attack catalog, model tested, configuration)
- Per-framework findings:
  - Article/clause header
  - Overall verdict (compliant / non-compliant / needs review)
  - Associated attack results with evidence
- Evidence integrity certificate (chain root hash, verification status)
- Appendix: Full attack logs (prompt + response for every test)

**SARIF output** (for integration with code quality tools):
- Each attack result becomes a SARIF "result"
- Severity maps to SARIF level (critical=error, high=warning, medium=note)
- Framework mappings in SARIF properties

#### Step 6: Web Dashboard (Pro Tier, Optional)

The Web Dashboard provides GUI access to the same data. It reads directly from the shared SQLite database using `better-sqlite3`. No API server.

**Pages:**
- `/` — Dashboard overview: pass/fail metrics, compliance scores, recent runs
- `/runs` — Run history: table with filtering, sorting, comparison
- `/runs/[id]` — Run detail: attack-by-attack breakdown with evidence
- `/compliance` — Framework mapping: tree view of articles → evidence
- `/compliance/[framework]` — Per-framework evidence organized by clause
- `/vault` — Evidence chain visualizer with verification status
- `/reports` — Report library: download generated PDF/SARIF/JSON
- `/settings` — Configuration editor, next-auth credential management

**Technical note:** Because there is no API server, the Web Dashboard and CLI/TUI operate on the same SQLite file. Concurrent reads are safe (SQLite supports multiple readers). Concurrent writes are not expected (single user). If both CLI and Dashboard are writing simultaneously, SQLite's WAL mode handles contention gracefully.

### Tier Differentiation

| Feature | Free (PyPI) | Pro ($149) | Enterprise ($499) |
|---------|-------------|------------|-------------------|
| Attack scenarios | 10 | 30 | 30 |
| Report formats | JSON | JSON + PDF + SARIF | JSON + PDF + SARIF + Custom |
| Compliance frameworks | 0 (raw results only) | EU AI Act + SOC 2 + NIST AI RMF + ISO 42001 | Same + custom frameworks |
| Web Dashboard | — | Included | Included |
| Branding/White-label | — | — | Custom branding |
| Source access | — | — | Full source code |
| License | Apache 2.0 | Commercial | Commercial |
| Support | GitHub Issues | Email (48hr SLA) | Email (24hr SLA) + Priority |
| Updates | — | 1 year | Lifetime |

**Why these tiers?** The free tier exists to demonstrate value — it's genuinely useful, not artificially crippled. The Pro tier adds the features that turn "interesting tool" into "compliance solution" (PDF reports, framework mapping, Web Dashboard). Enterprise tier is for consultants and agencies who need to customize and resell.

---

## 6. Technical Considerations

### Core Dependencies

| Dependency | Version | Purpose | Risk |
|------------|---------|---------|------|
| Python | 3.11+ | Runtime | Widespread, low risk |
| LiteLLM | Latest | LLM provider abstraction | **Medium risk:** Breaking changes in LiteLLM API could require emergency patches |
| SQLAlchemy | 2.0+ | ORM, DB agnosticism | Low risk, mature library |
| aiosqlite | Latest | Async SQLite driver | Low risk, thin wrapper over sqlite3 |
| Click | 8.x | CLI framework | Low risk, stable API |
| Textual | 0.52+ | TUI framework | Medium risk: Pre-1.0, API churn possible |
| Rich | 13.x | Terminal formatting | Low risk |
| Pydantic | 2.x | Data models, config validation | Low risk |
| Jinja2 | 3.x | Report templates | Low risk |
| WeasyPrint | 61+ | HTML to PDF | **Medium risk:** Complex system dependency (Cairo, Pango, libxml) |
| httpx | 0.27+ | Async HTTP | Low risk |
| Next.js | 14 (LTS) | Web Dashboard | Low risk (separate package) |
| better-sqlite3 | Latest | Node.js SQLite reads | Low risk (thin binding) |

**Key risk: LiteLLM stability.** LiteLLM is maintained by a small team and has experienced breaking changes between minor versions. Mitigation: pin LiteLLM version in `pyproject.toml`, maintain our own thin wrapper layer that abstracts the LiteLLM interface, and test upgrades in a dedicated integration suite before shipping.

**Key risk: Textual pre-1.0.** Textual hit 1.0 in late 2024, but later API changes could affect our TUI screens. Mitigation: minimize direct Textual API surface area in our code, wrap interactions in our own screen abstractions.

**Key risk: WeasyPrint system deps.** WeasyPrint requires system libraries (Cairo, Pango, GDK-Pixbuf) that are not always available in minimal Docker images or CI environments. Mitigation: make PDF generation gracefully degrade — if WeasyPrint fails, offer HTML download as fallback. Also provide a Docker image with all system deps pre-installed.

### Known Risks & Mitigations

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| LLM API rate limiting during attacks | High (threshold-based providers) | Medium — attacks fail or timeout | Implement LiteLLM's built-in rate limiting with exponential backoff. Allow user to configure `max_concurrent` per provider. Pre-warm with provider limit queries where API supports it. |
| SQLite concurrent access (CLI + Dashboard) | Medium | Low — WAL mode handles contention | Use SQLite WAL (Write-Ahead Logging) mode. The Dashboard is read-only for most operations. If contention occurs, SQLite serializes writes with a short timeout. |
| Large evidence vault performance | Low-Medium | Medium — slow queries | SQLite handles millions of rows for this use case. Index on `run_id`, `timestamp`, `attack_category`. Archive old evidence to separate DB files if vault exceeds 1GB (unlikely in v1.0). |
| API key security (plaintext in config) | Medium | High — exposed keys | Store config with `chmod 600`. Document keychain/credential helper integration. Support environment variable references in config file (e.g., `api_key = "${OPENAI_API_KEY}"`). |
| False positives in policy/bias testing | Medium | Medium — user trust erosion | Each attack includes confidence scoring. Results below 0.7 confidence are marked "needs review" rather than pass/fail. Allow users to override verdicts with annotations. |
| Python 3.11+ requirement | Low | Low — most users have 3.11+ | Python 3.11 is now 2.5 years old and widespread. Document the requirement clearly. Offer Docker image for users stuck on older Python versions. |
| Dependency conflicts with user's projects | Medium | Medium — installation friction | Pin all dependencies with ranges (not exact versions). Test in clean venv. Consider providing a Docker image for users who want isolated installation. |

### Open Questions (for Engineering Review)

The following questions need resolution during Phase 1 implementation:

1. **Attack randomization strategy:** How should we vary prompt permutations within each attack scenario to avoid deterministic false negatives? Options: fixed seed (reproducible), random seed per run, or n-shot variants. Each has trade-offs between reproducibility and coverage.

2. **Evaluation methodology for hallucination tests:** Hallucination detection is the hardest attack category. We need ground truth data for factual claims. Options: use a known dataset (e.g., SimpleQA, TruthfulQA), use an LLM judge (gpt-4o-mini evaluating hallucination), or implement fact-verification pipeline (e.g., retrieve-then-verify). Each has different accuracy and latency profiles.

3. **Bias testing statistical methodology:** Bias detection requires enough trials to reach statistical significance. How many prompts per bias category? What statistical test (e.g., chi-squared, exact binomial)? How should we present "borderline" results?

4. **SARIF format fidelity:** Some compliance concepts don't map cleanly to SARIF's security-vulnerability model. How should framework clause references be encoded in SARIF properties? Should we use SARIF's `taxonomies` extension?

5. **LiteLLM error behavior:** Different providers have different error modes (rate limits, quota exhaustion, model overload, content filtering). What is the default retry strategy? How should we surface provider-specific errors to the user?

6. **Telemetry design:** Opt-in telemetry is critical for understanding adoption and conversion. What minimal data should we collect? How do we ensure privacy compliance? Options: no telemetry (privacy-first), basic version + error reporting, or full usage analytics.

7. **Web Dashboard auth:** next-auth with credentials provider works for single-user, but what about users who want to expose the dashboard to their team? Defer to v2.0? Or support basic auth nginx proxy pattern in v1.0 docs?

### Architecture Principles

These principles should guide all technical decisions:

1. **CLI/TUI is always the primary interface.** The Web Dashboard is an optional accessory. Every feature must be accessible from the terminal first. If a feature only works in the dashboard, it doesn't exist.

2. **SQLite is the source of truth.** The database is the authoritative record. Reports are derived. The evidence vault is cryptographically anchored to the database. No dual-state allowed.

3. **Fail gracefully, not silently.** If an attack fails (timeout, rate limit, invalid key), the result should record the failure clearly — not suppress it. Users need to know their compliance pipeline is broken.

4. **The product is a boilerplate, not a black box.** Configuration files are editable YAML/TOML. Compliance mappings are editable YAML. The user should feel empowered to modify, customize, and extend, not locked into our decisions.

5. **Zero assumptions about internet connectivity.** The tool must work fully offline with local models (Ollama). Telemetry must be opt-in and non-blocking. No "phone home" required.

---

## 7. Launch Plan

### Phase 0: Internal Alpha (Weeks 1-7 of build)

**Who:** Just you (the solo developer)

**Duration:** During active development

**What happens:**
- You build and test every feature against your own LLM endpoints
- You run the full attack battery against GPT-4o, Claude 4, and Ollama (Llama 3) weekly
- You verify that `certifyai vault --verify` works correctly
- You generate PDF reports and review them for quality
- You identify any usability friction that would block a first-time user

**Exit criteria:**
- Full attack battery (30 scenarios) executes successfully against at least 3 providers
- PDF reports render correctly with all sections populated
- `certifyai vault --verify` passes on all generated evidence
- Free-tier functionality is stable and usable
- No P0 (security, data loss) or P1 (core feature broken) bugs open

### Phase 1: Closed Beta — 5 Design Partners (Week 8)

**Who:** 5 invited design partners recruited from Dev.to, r/MachineLearning, or personal network

**Duration:** 2 weeks

**Selection criteria:**
- Must be actively deploying LLMs in a production or pre-production context
- Must have a genuine compliance need (SOC 2 prep, EU AI Act, or internal audit)
- Must be willing to provide structured feedback (weekly 15-min call + written form)
- Must represent at least 2 of our 3 target personas
- No close friends/family — need objective feedback

**What design partners get:**
- Free Pro tier license (perpetual, even after beta)
- Direct communication channel (email or Discord)
- Named in "Thanks to our beta testers" section of launch materials (with permission)
- Early access to all updates

**What we ask of design partners:**
- Install and configure the tool within 48 hours of receiving access
- Run at least 3 attack sweeps during the beta period
- Generate at least 1 compliance report
- Complete a 20-question feedback survey at the end
- 15-minute feedback call each week

**What we learn:**
- Does `certifyai init` successfully guide users through setup?
- Do users understand the attack results and report output?
- Are there any installation or dependency issues?
- What's the single biggest missing feature?
- Would they pay $149 for the Pro tier? (We don't ask them to buy — we ask if they would.)

**Exit criteria:**
- At least 4 of 5 design partners successfully generate a compliance report
- At least 3 report "critical" or "blocking" bugs identified and fixed
- No design partner reports the tool "not useful"
- Clear signal on whether $149 price point feels fair

### Phase 2: GA Launch (Week 9-10)

**Who:** General public

**Launch channels (prioritized):**

| Channel | Reach | Effort | Expected Impact |
|---------|-------|--------|-----------------|
| **Product Hunt** | 50K-100K views | Medium (listing + assets + demo) | Highest — single best launch channel for developer tools |
| **Hacker News** | 100K+ views | High (must be genuine, no gaming) | High if it takes off, unpredictable |
| **r/MachineLearning** | 150K subscribers | Low (text post) | Medium — targeted audience |
| **Dev.to** | 1M+ monthly dev audience | Medium (tutorial-style post) | Medium — good for SEO |
| **Twitter/X** | (Your followers) | Low | Low unless goes viral |

**Launch materials to prepare:**
- Product Hunt listing: tagline, description, 5 screenshots/GIFs, first comment
- HN Show post: "Show HN: CertifyAI — Self-hosted LLM compliance testing (EU AI Act, SOC 2)"
- Dev.to blog post: "I built a free, self-hosted AI compliance checker. Here's why."
- Demo video: 90-second terminal-to-PDF walkthrough (optional but recommended)
- Landing page at certifyai.dev (link to Gumroad, GitHub, docs)

**Launch week goals:**
- 500+ free-tier installs
- 20+ Pro sales ($149)
- 3-5 Enterprise sales ($499)
- First-week revenue: $4,500-$8,500

**Post-launch (Month 2+):**
- Monitor conversion funnel: install -> init -> first run -> report -> Pro purchase
- Ship v1.1 with top 3 user-requested features
- Write 3 blog posts on Dev.to targeting different personas:
  - "How we prepared for SOC 2 Type II with 8 engineers" (Priya's story)
  - "Red-teaming our Llama 3 model: A practical guide" (Marcus's story)
  - "From Google Docs to automated compliance: How I audit 15 AI clients" (Elena's story)

### Pricing Launch Strategy

We launch with the final pricing from Day 1 of GA. No "introductory pricing" or discounts. Rationale:
- Boilerplate products have thin margins at $149 — discounting signals low confidence
- Early adopters are price-insensitive (they have the problem, they've been waiting)
- Raising prices later ($149 -> $199) is easier than raising from a discounted base

---

## 8. Appendix

### A. Competitive Analysis

| Competitor | AI Runtime Testing? | Pricing | Self-Hosted? | Key Weakness |
|-----------|-------------------|---------|-------------|--------------|
| Vanta | ❌ (static infra only) | $7.5K-$10K+/yr | ❌ SaaS only | Cannot test AI behavior |
| Drata | ❌ (SOC 2 infra) | $15K-$60K+/yr | ❌ SaaS only | AI-invisible |
| Credo AI | ❌ (documentation) | $30K-$150K+/yr | ❌ SaaS only | Documentation, not testing |
| IBM watsonx.governance | ⚠️ (drift only) | Enterprise | ❌ Cloud only | Vendor lock-in |
| Holistic AI | ❌ (risk docs) | Custom pricing | ❌ SaaS only | Enterprise-only pricing |
| Garak (OSS) | ✅ (red-teaming) | Free | ✅ Self-hosted | No compliance mapping, no reports, no vault |
| **CertifyAI** | ✅ **Continuous red-teaming** | **$79-$499 one-time** | **✅ Self-hosted** | **New entrant, smaller attack catalog** |

**Key insight:** No competitor combines red-teaming, compliance mapping, evidence vault, and report generation in a self-hosted package. The existing OSS tools (Garak, LangChain eval) are components, not products. The existing SaaS tools are platforms, not tools for engineers.

### B. Market Research Summary

- **AI Governance & Compliance market:** $3.4B (2026) -> $68.2B (2035), 39.4% CAGR
- **EU AI Act enforcement:** High-risk deadline August 2, 2026
- **Market readiness:** 78% of organizations not ready for EU AI Act
- **SOC 2 demand:** SOC 2 is the most common compliance framework for startups; Type II reports increasingly ask about AI/ML testing
- **Willingness to pay:** Developer tool surveys show $100-$200 is the sweet spot for a one-time purchase tool that solves a specific pain point

### C. Architecture Documentation References

See the following documents in the project repository:

| Document | Location | Content |
|----------|----------|---------|
| `AGENTS.md` | `[project root]/AGENTS.md` | Project context, ADRs, team instructions |
| `idea.md` | `[project root]/idea.md` | Original concept, tech stack, build plan, distribution model |
| `competitive-analysis.md` | `docs/competitive-analysis.md` | In-depth competitor profiles, positioning maps, Porter's Five Forces |
| `market-research-report.md` | `docs/market-research-report.md` | TAM/SAM/SOM analysis, customer segmentation, growth drivers |
| `ARCHITECTURE.md` | `docs/ARCHITECTURE.md` (planned) | System architecture, data flow, component diagram |
| `ROADMAP.md` | `docs/ROADMAP.md` (planned) | Phase breakdown, milestones, v2.0 planning |

### D. Glossary

| Term | Definition |
|------|-----------|
| **Attack scenario** | A single test case: a prompt template + expected behavior criteria + severity rating |
| **Attack battery** | The full set of attack scenarios executed in a single run |
| **Evidence chain** | An append-only SHA-256 hash chain proving evidence integrity |
| **Compliance framework mapping** | YAML file mapping regulatory articles/controls to attack categories |
| **Evidence vault** | Filesystem directory (`~/.certifyai/vault/`) containing raw evidence blobs and hash chain |
| **Cli** | Command-line interface (Click-based) for running attacks and generating reports |
| **Tui** | Terminal user interface (Textual-based) for interactive browsing and monitoring |
| **Boilerplate** | A downloadable, self-hosted product that the customer runs on their own infrastructure |
| **SARIF** | Static Analysis Results Interchange Format — an OASIS standard for sharing analysis results |
| **WAL mode** | SQLite Write-Ahead Logging — allows concurrent reads during writes |
| **LiteLLM** | Python library providing a unified interface to 100+ LLM providers |
| **OWASP LLM Top 10** | OWASP's list of the 10 most critical security risks for LLM applications |

### E. Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| v1.0 | 2026-07-21 | Alex (PM) | Initial PRD draft |
| — | — | — | — |

---

*This document is a living artifact. It will be updated as we learn from design partners, gather user feedback, and make technical trade-offs during implementation. Revisions will be tracked in the Revision History section above.*
