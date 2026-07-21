# CertifyAI — Technical Architecture Document

| Attribute | Value |
|-----------|-------|
| **Author** | Software Architect (The Agency) |
| **Status** | Draft v1 |
| **Version** | 1.0.0 |
| **Last Updated** | 2026-07-21 |
| **Scope** | System-wide architecture, container design, component internals, ADRs |

---

## Table of Contents

1. [Architecture Overview](#1-architecture-overview)
2. [Container Diagram](#2-container-diagram)
3. [Component Design: Engine Deep Dive](#3-component-design-engine-deep-dive)
4. [Data Model](#4-data-model)
5. [Key Design Decisions (ADRs)](#5-key-design-decisions-adrs)
6. [Quality Attributes](#6-quality-attributes)
7. [Trade-off Analysis](#7-trade-off-analysis)
8. [Evolution Strategy](#8-evolution-strategy)

---

## 1. Architecture Overview

### C4 Level 1: System Context

The system is **CertifyAI** — a downloadable continuous compliance engine for AI runtimes. It runs entirely on the customer's machine. The customer brings their own LLM API key. No cloud dependency.

```
┌─────────────────────────────────────────────────────────────────────────┐
│                                                                         │
│  [AI/ML Engineer]──────── ─────[Startup CTO]──── ────[External Auditor] │
│       ▲                                  │                    ▲         │
│       │ uses CLI/TUI                     │  reviews PDF       │ receives │
│       │ to run attacks                   │  reports,          │ reports  │
│       │                                  │  evidence chain    │ & chain  │
│       │    ┌─────────────────────────┐   │                    │          │
│       │    │                         │   │                    │          │
│       └────┤     CertifyAI System   ├───┘   ┌────────────────┘          │
│            │                         │       │                           │
│            │  (Customer's Machine)   │       │                           │
│            └──────────┬──────────────┘       │                           │
│                       │                      │                           │
│                       ▼                      ▼                           │
│            ┌─────────────────────────────────────────────┐               │
│            │         LLM Providers (External)            │               │
│            │  ┌──────┐ ┌──────┐ ┌──────┐ ┌─────────┐    │               │
│            │  │OpenAI│ │Anth- │ │Ollama│ │Gemini / │    │               │
│            │  │      │ │ropic │ │(local)│ │Compat.  │    │               │
│            │  └──────┘ └──────┘ └──────┘ └─────────┘    │               │
│            └─────────────────────────────────────────────┘               │
└─────────────────────────────────────────────────────────────────────────┘
```

**Key relationships:**

| Interaction | From | To | Protocol |
|-------------|------|----|----------|
| Run attack battery | CLI/TUI | Engine | In-process Python call |
| Send test prompts | Engine | LLM Providers | HTTPS (LiteLLM) |
| Read compliance evidence | Web Dashboard | SQLite | `better-sqlite3` (direct file read) |
| Copy reports | Any interface | Filesystem (`reports/`) | File I/O |
| Verify chain integrity | CLI/TUI | Evidence Vault | File I/O + SQLite |

### What the system does NOT do

Equally important: boundaries that define what's outside scope.

| Capability | Out of scope | Why |
|------------|-------------|-----|
| Multi-tenant hosting | ❌ | Boilerplate model — single-tenant by design |
| Cloud sync/backup | ❌ | Customer manages their own backups |
| SSO/OIDC auth | ❌ | Single-user tool; `next-auth` credentials only |
| Real-time LLM monitoring | ❌ | Scheduled/cron-driven runs, not streaming |
| Compliance filing | ❌ | Generates evidence, does not file with regulators |
| Incident response | ❌ | Detects issues, does not remediate |

---

## 2. Container Diagram

### C4 Level 2: Containers

```
┌────────────────────────────────────────────────────────────────────────────┐
│                     CERTIFYAI SYSTEM BOUNDARY                              │
│                                                                            │
│  ┌────────────────────┐    ┌────────────────────┐                         │
│  │   CLI Container    │    │   TUI Container    │                         │
│  │   (Click + Rich)   │    │   (Textual)        │                         │
│  │                    │    │                    │                         │
│  │  certifyai run     │    │  Dashboard Screen  │                         │
│  │  certifyai report  │    │  Explorer Screen   │                         │
│  │  certifyai watch   │    │  Vault Screen      │                         │
│  │  certifyai vault   │    │  Config Screen     │                         │
│  │  certifyai init    │    │  Preview Screen    │                         │
│  └────────┬───────────┘    └────────┬───────────┘                         │
│           │                         │                                      │
│           │     ┌───────────────────┴──────────────┐                      │
│           │     │                                  │                      │
│           └─────►      Engine Container           ◄─┘                      │
│                 │     (Python 3.11+)               │                      │
│                 │                                  │                      │
│                 │  ┌──────────────────────────┐   │                      │
│                 │  │     RedTeam Engine        │   │                      │
│                 │  │  ┌──────┐ ┌──────┐ ┌───┐ │   │                      │
│                 │  │  │Plugin │ │Plugin │ │...│ │   │                      │
│                 │  │  │Mgr    │ │Loader │ │   │ │   │                      │
│                 │  │  └──────┘ └──────┘ └───┘ │   │                      │
│                 │  └──────────┬───────────────┘   │                      │
│                 │             │                    │                      │
│                 │  ┌──────────▼───────────────┐   │                      │
│                 │  │   LiteLLM Abstraction     │   │                      │
│                 │  │   (100+ providers)        │   │                      │
│                 │  └──────────┬───────────────┘   │                      │
│                 │             │                    │                      │
│                 │  ┌──────────▼───────────────┐   │                      │
│                 │  │   Evidence Vault          │   │                      │
│                 │  │   (SHA-256 Hash Chain)   │   │                      │
│                 │  └──────────┬───────────────┘   │                      │
│                 │             │                    │                      │
│                 │  ┌──────────▼───────────────┐   │                      │
│                 │  │   Compliance Mapper       │   │                      │
│                 │  │   (Framework → Clause)   │   │                      │
│                 │  └──────────┬───────────────┘   │                      │
│                 │             │                    │                      │
│                 │  ┌──────────▼───────────────┐   │                      │
│                 │  │   Report Generator        │   │                      │
│                 │  │   (PDF / JSON / SARIF)   │   │                      │
│                 │  └──────────────────────────┘   │                      │
│                 └──────────────────────────────────┘                      │
│                                │                                           │
│                                ▼                                           │
│  ┌──────────────────────────────────────────────┐                        │
│  │           SQLite Database                     │                        │
│  │  certifyai.db (runs, results, config, meta)  │                        │
│  └────────────────────┬─────────────────────────┘                        │
│                       │                                                   │
│                       ▼ (Direct file read)                                │
│  ┌──────────────────────────────────────────────┐                        │
│  │    Web Dashboard Container (OPTIONAL)         │                        │
│  │    Next.js 14 + Tailwind + recharts           │                        │
│  │                                              │                        │
│  │  / → Dashboard overview                      │                        │
│  │  /runs → Run history                         │                        │
│  │  /runs/[id] → Run details                    │                        │
│  │  /compliance → Framework mapping             │                        │
│  │  /vault → Evidence chain viewer              │                        │
│  │  /reports → Report library                   │                        │
│  │  /settings → Configuration                   │                        │
│  └──────────────────────────────────────────────┘                        │
│                                                                            │
└────────────────────────────────────────────────────────────────────────────┘
```

### Container Specifications

#### 2.1 CLI Container

| Property | Value |
|----------|-------|
| **Technology** | Python 3.11+ — Click 8.x + Rich 13.x |
| **Process** | CLI process (short-lived commands) |
| **Responsibilities** | Command dispatch, terminal output, exit codes for CI/CD |
| **State** | Stateless (defers to Engine + SQLite) |
| **Key commands** | `init`, `run`, `report`, `watch`, `vault`, `list-attacks` |
| **Dependencies** | Engine container (in-process) |
| **Test strategy** | `click.testing.CliRunner` |
| **Distribution** | PyPI package `certifyai` |

**Interface contract:**

```python
# CLI calls Engine via direct import — no IPC, no network
from certifyai.engine import run_attack_battery

@click.command()
@click.option("--attack", default=None)
def run(attack):
    results = run_attack_battery(attack_filter=attack)
    # Render to terminal via Rich
```

#### 2.2 TUI Container

| Property | Value |
|----------|-------|
| **Technology** | Python 3.11+ — Textual 1.x + Rich |
| **Process** | Long-lived TUI process |
| **Responsibilities** | Real-time attack monitoring, interactive browsing, config editing |
| **State** | In-memory screen state, reads/writes SQLite via Engine |
| **Screens** | Dashboard, Explorer, Vault, Config Editor, Report Preview |
| **Dependencies** | Engine container (in-process) |
| **Test strategy** | `textual.testing` pilot-based testing |
| **Distribution** | PyPI package `certifyai` (same package) |

**Screen navigation map:**

```
Dashboard ──→ Explorer ──→ Run Detail
    │                            │
    │                            ▼
    │                      Evidence Viewer
    │                            │
    ▼                            ▼
Config Editor              Vault Screen
    │                            │
    ▼                            ▼
Settings                   Chain Verification
```

#### 2.3 Engine Container

| Property | Value |
|----------|-------|
| **Technology** | Python 3.11+ — asyncio, Pydantic v2, LiteLLM, SQLAlchemy 2.0 |
| **Process** | Imported as library by CLI/TUI; also callable from Python scripts |
| **Responsibilities** | Attack execution, evidence hashing, compliance mapping, report generation |
| **State** | Mostly stateless (reads config from SQLite on demand) |
| **Sub-components** | RedTeam Engine, Evidence Vault, Compliance Mapper, Report Generator |
| **Dependencies** | LLM providers (HTTPS), SQLite (filesystem), Jinja2 templates |
| **Test strategy** | `pytest` + `pytest-asyncio` + LiteLLM mock |
| **Distribution** | Part of `certifyai` PyPI package |

This is the largest and most complex container. See [Section 3](#3-component-design-engine-deep-dive) for the full deep dive.

#### 2.4 Web Dashboard Container

| Property | Value |
|----------|-------|
| **Technology** | Next.js 14 (App Router) + Tailwind CSS v4 + `motion/react` + `recharts` + `better-sqlite3` |
| **Process** | `next dev` or `next start` (port 3000) |
| **Responsibilities** | Visualization, report browsing, evidence chain explorer, settings UI |
| **State** | Reads-only from SQLite via `better-sqlite3` (synchronous Node.js binding). Writes config via Engine's SQLite connection. No API server. |
| **Pages** | 8 routes (dashboard, runs, run detail, compliance, vault, reports, settings) |
| **Auth** | `next-auth` credentials provider (SQLite-backed sessions) |
| **Dependencies** | SQLite file (direct read), Engine (optional: for triggering runs via subprocess) |
| **Test strategy** | Playwright E2E |
| **Distribution** | Included in Gumroad Pro/Enterprise tiers |

**Why no API server — see [ADR-008](#adr-008-direct-sqlite-reads-from-nextjs-why-no-api-server).**

---

## 3. Component Design: Engine Deep Dive

This section opens the Engine container and describes its four sub-components in detail.

### 3.1 RedTeam Engine

**Purpose:** Execute attack scenarios against LLM endpoints asynchronously, evaluate responses, produce evidence.

```
                        ┌─────────────────────────────┐
                        │    Plugin Registry            │
                        │  ┌─────────────────────────┐ │
                        │  │ PluginMetadata(name,     │ │
                        │  │  category, severity,    │ │
                        │  │  frameworks[])           │ │
                        │  └─────────────────────────┘ │
                        └────────────┬────────────────┘
                                     │ discovers
                                     ▼
┌──────────────┐    ┌─────────────────────────────┐
│  config.toml │───►│    Attack Scheduler           │
│  (filters,   │    │  (reads config, selects       │
│   concurrency│    │   plugins, builds plan)       │
│   settings)  │    └────────────┬────────────────┘
└──────────────┘                 │
                                 │ creates
                                 ▼
┌────────────────────────────────────────────────────┐
│              asyncio.TaskGroup                      │
│                                                     │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐         │
│  │ Plugin A │  │ Plugin B │  │ Plugin C │  ...     │
│  │ Task     │  │ Task     │  │ Task     │         │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘         │
│       │             │             │                  │
│       ▼             ▼             ▼                  │
│  ┌─────────────────────────────────────────┐       │
│  │      LiteLLM Completions API             │       │
│  │  (handles retries, rate limits, timeouts)│       │
│  └─────────────────────────────────────────┘       │
│                                                     │
│  Each Task (Plugin execution):                      │
│  1. Build prompt from template                      │
│  2. Send via LiteLLM                                │
│  3. Evaluate response against criteria              │
│  4. Package result + evidence                       │
│  5. Yield AttackResult                              │
└────────────────────────────────────────────────────┘
```

#### Plugin Architecture

**Design: Abstract base class + YAML-manifest discovery.**

```python
# certifyai/engine/plugins/base.py

class AttackPlugin(ABC):
    """Base class for all attack scenarios."""

    metadata: PluginMetadata  # name, category, severity, framework_refs

    @abstractmethod
    async def execute(
        self,
        llm_client: LiteLLMClient,
        config: AttackConfig,
    ) -> AttackResult:
        """Execute attack, return result with evidence."""
        ...

    @abstractmethod
    def evaluate(self, response: str, criteria: EvalCriteria) -> Evaluation:
        """Evaluate LLM response against attack-specific criteria."""
        ...

    def build_prompt(self, template: PromptTemplate) -> str:
        """Render prompt template with attack-specific variables."""
        return template.render(variables=self.metadata.prompt_vars)
```

**Plugin discovery mechanism:**

```
certifyai/
└── engine/
    └── plugins/
        ├── __init__.py          # PluginRegistry
        ├── base.py              # Abstract base
        ├── injection/           # Category directory
        │   ├── __init__.py
        │   ├── direct_injection.py
        │   ├── indirect_injection.py
        │   └── encoded_injection.py
        ├── jailbreak/
        │   ├── roleplay_jailbreak.py
        │   ├── multilingual_jailbreak.py
        │   └── token_manipulation.py
        ├── pii_leakage/
        │   ├── email_extraction.py
        │   ├── phone_extraction.py
        │   └── ssn_patterns.py
        ├── policy_violation/
        ├── hallucination/
        └── bias_testing/
```

**Plugin discovery (pseudocode):**

```python
class PluginRegistry:
    def __init__(self):
        self._plugins: dict[str, type[AttackPlugin]] = {}

    def discover(self, package: str = "certifyai.engine.plugins"):
        """Walk plugin directories, import, register."""
        for module_info in pkgutil.iter_modules(
            importlib.import_module(package).__path__
        ):
            if hasattr(module_info.module_finder, "path"):
                self._load_from_path(module_info)

    def get_plugins(
        self, categories: list[str] | None = None
    ) -> list[AttackPlugin]:
        """Filter by category. Returns fresh instances."""
        ...
```

**Why plugins over conditionals — see [ADR-006](#adr-006-plugin-based-attack-architecture).**

#### Async Execution Model

**Design choice:** `asyncio.TaskGroup` (Python 3.11+) for structured concurrency.

```python
# certifyai/engine/runner.py

async def run_attack_battery(
    plugins: list[AttackPlugin],
    llm_client: LiteLLMClient,
    config: AttackConfig,
    progress: ProgressCallback | None = None,
) -> AsyncIterator[AttackResult]:
    """Execute all plugins concurrently using structured concurrency.

    Design notes:
    - TaskGroup ensures all tasks complete or ALL are cancelled on error.
    - No orphaned tasks possible (unlike asyncio.gather with cancel).
    - Progress callback enables both CLI progress bars and TUI streaming.
    """

    semaphore = asyncio.Semaphore(config.max_concurrency)

    async def _run_one(plugin: AttackPlugin) -> AttackResult:
        async with semaphore:
            result = await plugin.execute(llm_client, config)
            if progress:
                await progress(result)
            return result

    async with asyncio.TaskGroup() as tg:
        tasks = [tg.create_task(_run_one(p)) for p in plugins]

    # All tasks complete at this point — TaskGroup guarantees it
    for task in tasks:
        yield task.result()
```

**Concurrency configuration:**

| Setting | Default | Range | Effect |
|---------|---------|-------|--------|
| `max_concurrency` | 5 | 1–50 | Parallel attack count |
| `request_timeout` | 30s | 5–300 | Per-LLM-call timeout |
| `max_retries` | 3 | 0–10 | LiteLLM retry on 429/5xx |
| `rate_limit_rpm` | 60 | 1–10000 | Requests per minute limit |

#### Evaluation Pipeline

Each plugin has its own evaluation logic, but follows a common pattern:

```
LLM Response String
       │
       ▼
┌─────────────────┐
│  Pattern Match   │  ── Regex, keyword, or semantic check
│  (Plugin-specific│
│   evaluator)     │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Severity        │  ── none / low / medium / high / critical
│  Classification  │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Evidence        │  ──  {prompt, response, eval_result,
│  Package         │       timestamp, plugin_version}
└────────┬────────┘
         │
         ▼
    AttackResult
    (Pydantic model)
```

### 3.2 Evidence Vault

**Purpose:** Immutable, cryptographically verifiable storage of all attack evidence.

#### Architecture

```
~/.certifyai/vault/
│
├── chain.db                     # SQLite — append-only hash chain index
│
├── run_a1b2c3d4/                # Per-run directory (run_id = nanoid)
│   ├── metadata.json            # Run metadata (start/end time, config, total attacks)
│   ├── attack_001.json          # Evidence blob: full prompt + response + evaluation
│   ├── attack_001.hash          # SHA-256 hex digest of attack_001.json
│   ├── attack_002.json
│   ├── attack_002.hash
│   ├── ...
│   └── run.hash                 # SHA-256 of all attack_NNN.hash concatenated
│
├── run_e5f6g7h8/
│   └── ...
│
└── chain.idx                   # Optional: index file for fast chain traversal
```

**Hash chain construction:**

```
    attack_001.json
         │
         ▼ SHA-256(attack_001.json)
    attack_001.hash ──────────────────────────────────┐
         │                                              │
    attack_002.json                                     │
         │                                              │
         ▼ SHA-256(attack_002.json)                     │
    attack_002.hash ───────────────┐                    │
         │                         │                    │
    ...                            │                    │
         │                         │                    │
         ▼                         ▼                    ▼
    run.hash = SHA-256( run.hash  run.hash    ...  run.hash   )
                       (001)  ||  (002)  ||       ||  (00N)
         │
         ▼
    INSERT INTO evidence_chain (run_id, previous_hash, run_hash, timestamp)
         │
         ▼
    chain.db  ← Append-only. Previous hash links every run to the last.
```

**Key properties:**

1. **Append-only:** `chain.db` only allows INSERTs. No UPDATEs, no DELETEs.
2. **Linked by hash:** Each row stores `previous_hash` — the SHA-256 of the previous run's metadata + hash. Tampering any evidence file changes its hash, which breaks the chain.
3. **Verifiable independently:** `certifyai vault --verify` walks the chain: reads each file, recomputes hashes, compares to stored values, and reports integrity status.

#### Chain DB Schema (see [Section 4](#4-data-model) for full schema)

```sql
CREATE TABLE evidence_chain (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    run_id      TEXT    NOT NULL UNIQUE,
    previous_hash TEXT  NOT NULL,          -- SHA-256 of previous row's run_hash
    run_hash    TEXT    NOT NULL,          -- SHA-256 of this run's evidence
    timestamp   TEXT    NOT NULL,          -- ISO 8601
    metadata    TEXT,                      -- JSON blob
    verified_at TEXT                       -- Last verification timestamp
);
```

#### Verification Algorithm

```python
def verify_chain(vault_path: Path) -> ChainVerification:
    """Walk the evidence chain and verify integrity.

    Returns: ChainVerification with:
      - status: 'valid' | 'tampered' | 'corrupt'
      - total_runs, verified_runs, failed_runs
      - first_tampered_run: Optional[str]
      - details: list[RunVerification]
    """
    chain_db = sqlite3.connect(vault_path / "chain.db")

    cursor = chain_db.execute(
        "SELECT run_id, previous_hash, run_hash FROM evidence_chain ORDER BY id"
    )
    rows = cursor.fetchall()

    expected_previous = "0" * 64  # Genesis block
    results = []

    for run_id, stored_previous, stored_run_hash in rows:
        # 1. Verify chain linkage
        if stored_previous != expected_previous:
            results.append(RunVerification(
                run_id=run_id, status="tampered",
                reason="Hash chain broken"
            ))
            continue

        # 2. Recompute run hash from files
        computed_run_hash = recompute_run_hash(vault_path / f"run_{run_id}")

        # 3. Compare
        if computed_run_hash != stored_run_hash:
            results.append(RunVerification(
                run_id=run_id, status="tampered",
                reason="Evidence file modified"
            ))
            continue

        results.append(RunVerification(run_id=run_id, status="valid"))
        expected_previous = stored_run_hash

    return ChainVerification(results=results)
```

**Why hybrid filesystem + SQLite — see [ADR-007](#adr-007-filesystem--sqlite-for-evidence-vault).**

### 3.3 Compliance Mapper

**Purpose:** Stateless, deterministic mapping from attack results to regulatory framework clauses.

#### Architecture

```
┌──────────────────────────────────────┐
│  Frameworks YAML Files                │
│                                      │
│  eu_ai_act.yaml      soc2.yaml       │
│  nist_ai_rmf.yaml    iso42001.yaml   │
│                                      │
│  Shipped with product. Customer can  │
│  add custom frameworks.              │
└──────────────┬───────────────────────┘
               │ loaded at runtime
               ▼
┌──────────────────────────────────────┐
│  FrameworkLoader                     │
│                                      │
│  - Reads YAML from frameworks/ dir   │
│  - Parses into Pydantic models       │
│  - Caches in memory (immutable)      │
│  - Validates structure on load       │
└──────────────┬───────────────────────┘
               │
               ▼
┌──────────────────────────────────────┐
│  ClauseMatcher                       │
│                                      │
│  Input:  AttackResult                │
│         (has .metadata.framework_refs)│
│                                      │
│  Logic:  Plugin declares which       │
│          framework clauses it tests  │
│          (static mapping in plugin   │
│           metadata).                  │
│                                      │
│  Output: list[MatchedClause]         │
│          each linking:               │
│            framework + clause +      │
│            evidence + status         │
└──────────────┬───────────────────────┘
               │
               ▼
┌──────────────────────────────────────┐
│  EvidenceLinker                      │
│                                      │
│  - Links MatchedClause → Evidence    │
│    Blob (SHA-256 hash)               │
│  - Assigns compliance status:        │
│    compliant / non_compliant /       │
│    needs_review / not_tested         │
│  - Output: ComplianceReport          │
│    (framework-wise clause coverage)  │
└──────────────────────────────────────┘
```

**Framework YAML format:**

```yaml
# frameworks/eu_ai_act.yaml
framework:
  id: eu_ai_act
  name: EU AI Act
  version: "2024-08"
  clauses:
    - id: art_14
      title: Human Oversight
      category: governance
      description: High-risk AI systems shall be designed for effective human oversight.
      severity: high
      tested_by:
        - injection.direct_injection    # Plugin ID
        - jailbreak.roleplay_jailbreak
    - id: art_15
      title: Accuracy, Robustness, Cybersecurity
      category: technical
      description: Systems shall be resilient to errors and attacks.
      severity: high
      tested_by:
        - hallucination.factual_claim
        - bias_testing.gender_bias
    # ... (15+ clauses mapped)
```

**Compliance coverage calculation:**

```python
class CoverageCalculator:
    """Deterministic. Same inputs → same outputs."""

    def calculate(
        self,
        framework: ComplianceFramework,
        results: list[AttackResult],
    ) -> FrameworkCoverage:
        tested_clauses: set[str] = set()
        passed_clauses: set[str] = set()

        for result in results:
            for ref in result.metadata.framework_refs:
                # ref format: "eu_ai_act.art_14"
                framework_id, clause_id = ref.split(".")
                if framework_id == framework.id:
                    tested_clauses.add(clause_id)
                    if result.evaluation.status == "pass":
                        passed_clauses.add(clause_id)

        total = len(framework.clauses)
        tested = len(tested_clauses)
        passed = len(passed_clauses)

        return FrameworkCoverage(
            framework=framework.id,
            total_clauses=total,
            tested_clauses=tested,
            passed_clauses=passed,
            untested_clauses=total - tested,
            coverage_pct=round(tested / total * 100, 1),
            pass_rate=round(passed / tested * 100, 1) if tested else 0.0,
            clause_details=[...],
        )
```

**Stateless by design:** The Compliance Mapper holds no mutable state. It reads YAML (immutable after load), receives `AttackResult` objects, and returns `ComplianceReport`. This makes it trivially testable, cacheable, and parallel-safe.

### 3.4 Report Generator

**Purpose:** Transform attack results + compliance mappings into exportable artifacts.

#### Output Formats

| Format | Use Case | Tech | File Size | Production Ready |
|--------|----------|------|-----------|-----------------|
| **JSON** | Machine parsing, CI/CD | `json.dump()` | Small | Yes — always |
| **PDF** | Auditor review, evidence package | Jinja2 → HTML → WeasyPrint | Medium | Yes — Pro tier |
| **SARIF** | IDE integration (VS Code, GitHub) | Custom SARIF builder | Medium | Yes — always |

#### PDF Pipeline

```
┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│  Attack      │    │  Jinja2      │    │  WeasyPrint   │
│  Results     │───►│  HTML        │───►│  PDF          │
│  (Pydantic)  │    │  Template    │    │  Renderer     │
└──────────────┘    └──────────────┘    └──────────────┘
                          │
                          ▼
                 ┌──────────────────┐
                 │  Report Styles   │
                 │  (CSS for print) │
                 └──────────────────┘
```

**Template structure:**

```
certifyai/engine/reporting/
├── templates/
│   ├── base.html           # Layout: header, footer, TOC
│   ├── summary.html        # Executive summary, compliance score
│   ├── attack_details.html # Per-attack breakdown
│   ├── compliance.html     # Framework → clause → evidence mapping
│   ├── evidence_chain.html # Hash chain visualization
│   └── appendix.html       # Raw data, config, timestamps
├── styles/
│   ├── print.css           # Paged media styles for PDF
│   └── screen.css          # For HTML preview in TUI
├── builder.py              # ReportBuilder class
├── sarif_builder.py        # SARIF 2.1 schema builder
└── json_exporter.py        # JSON serialization
```

**SARIF output example structure:**

```json
{
  "$schema": "https://schemastore.ast",chemas/sarif-2.1.0.json",
  "version": "2.1.0",
  "runs": [{
    "tool": {
      "driver": {
        "name": "CertifyAI",
        "version": "1.0.0",
        "rules": [{
          "id": "INJECTION-001",
          "name": "Direct Prompt Injection",
          "shortDescription": "Tests if system prompt can be overridden"
        }]
      }
    },
    "results": [{
      "ruleId": "INJECTION-001",
      "level": "error",
      "message": { "text": "Model accepted override instruction" },
      "locations": [{ "logicalLocations": [{ "name": "gpt-4o" }] }],
      "attachments": [{
        "description": "Evidence Blob SHA-256: abc123...",
        "artifactLocation": { "uri": "file:///vault/run_xxx/attack_001.json" }
      }]
    }]
  }]
}
```

#### Critical Design Decision: No Live Rendering

PDF generation via WeasyPrint is CPU-and-memory-intensive for large reports. The architecture treats PDF generation as an **offline, explicit action** — not automatic. The CLI command `certifyai report --format pdf` triggers it. The TUI shows a progress spinner. No background auto-generation.

---

## 4. Data Model

### 4.1 Entity Relationship Diagram

```
┌──────────────────┐       ┌──────────────────────┐
│      runs         │       │      results          │
│──────────────────│       │──────────────────────│
│ PK id: TEXT      │──┐    │ PK id: TEXT           │
│    status: TEXT   │  │    │ FK run_id: TEXT       │
│    started_at: DT│  ├───►│    plugin_id: TEXT     │
│    finished_at:DT│  │    │    status: TEXT        │
│    config_json:T │  │    │    severity: TEXT      │
│    total_attacks │  │    │    prompt: TEXT        │
│    passed: INT   │  │    │    response: TEXT      │
│    failed: INT   │  │    │    evaluation: TEXT    │
│    summary: TEXT │  │    │    evidence_ref: TEXT──┼──┐
│    engine_version│  │    │    started_at: DT      │  │
└──────────────────┘  │    │    duration_ms: INT    │  │
                       │    └──────────────────────┘  │
                       │                              │
                       │    ┌──────────────────────┐  │
                       │    │   evidence_chain      │  │
                       │    │──────────────────────│  │
                       │    │ PK id: INTEGER        │  │
                       └───►│    run_id: TEXT        │  │
                            │    previous_hash: TEXT │  │
                            │    run_hash: TEXT      │  │
                            │    timestamp: TEXT     │  │
                            │    metadata: TEXT      │  │
                            └──────────────────────┘  │
                                                      │
┌──────────────────┐        ┌──────────────────────┐  │
│    config         │        │  evidence_files       │  │
│──────────────────│        │  (filesystem, not DB) │  │
│ PK key: TEXT      │        └──────────────────────┘  │
│    value: TEXT    │                        │        │
│    category: TEXT │                        │        │
│    updated_at: DT │                        └────────┘
└──────────────────┘                     SHA-256 link
                                                  
┌──────────────────┐
│  framework_cache  │  (Denormalized for dashboard speed)
│──────────────────│
│ PK id: TEXT       │
│    name: TEXT     │
│    version: TEXT  │
│    clauses_json   │
│    cached_at: DT  │
└──────────────────┘
```

### 4.2 Complete SQLite Schema

```sql
-- ============================================================
-- Run Management
-- ============================================================

CREATE TABLE runs (
    id              TEXT    PRIMARY KEY,              -- nanoid (21 chars)
    status          TEXT    NOT NULL DEFAULT 'pending'
                    CHECK (status IN ('pending', 'running', 'completed', 'failed', 'cancelled')),
    started_at      TEXT    NOT NULL,                 -- ISO 8601
    finished_at     TEXT,                             -- ISO 8601, NULL until complete
    config_json     TEXT    NOT NULL,                 -- Snapshot of run config (Pydantic model dump)
    total_attacks   INTEGER NOT NULL DEFAULT 0,
    passed          INTEGER NOT NULL DEFAULT 0,
    failed          INTEGER NOT NULL DEFAULT 0,
    summary         TEXT,                             -- JSON summary blob
    engine_version  TEXT    NOT NULL,                 -- SemVer of certifyai engine
    created_at      TEXT    NOT NULL DEFAULT (datetime('now'))
);

CREATE INDEX idx_runs_status ON runs(status);
CREATE INDEX idx_runs_started_at ON runs(started_at DESC);

-- ============================================================
-- Attack Results
-- ============================================================

CREATE TABLE results (
    id              TEXT    PRIMARY KEY,              -- nanoid (21 chars)
    run_id          TEXT    NOT NULL REFERENCES runs(id) ON DELETE CASCADE,
    plugin_id       TEXT    NOT NULL,                 -- e.g. "injection.direct_injection"
    status          TEXT    NOT NULL
                    CHECK (status IN ('pass', 'fail', 'error', 'skipped')),
    severity        TEXT    NOT NULL DEFAULT 'none'
                    CHECK (severity IN ('none', 'low', 'medium', 'high', 'critical')),
    prompt          TEXT    NOT NULL,                 -- The actual prompt sent
    response        TEXT,                             -- LLM response (NULL on error/timeout)
    evaluation      TEXT    NOT NULL,                 -- JSON: evaluation criteria + result
    evidence_ref    TEXT,                             -- Relative path to evidence file in vault
    error_message   TEXT,                             -- Populated on 'error' status
    started_at      TEXT    NOT NULL,
    duration_ms     INTEGER NOT NULL DEFAULT 0,
    plugin_version  TEXT    NOT NULL DEFAULT '1.0.0'
);

CREATE INDEX idx_results_run_id ON results(run_id);
CREATE INDEX idx_results_plugin_id ON results(plugin_id);
CREATE INDEX idx_results_status ON results(status);
CREATE INDEX idx_results_severity ON results(severity);

-- ============================================================
-- Evidence Chain (Append-only; no UPDATE, no DELETE)
-- ============================================================

CREATE TABLE evidence_chain (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    run_id          TEXT    NOT NULL UNIQUE REFERENCES runs(id),
    previous_hash   TEXT    NOT NULL,                 -- SHA-256 of previous row's run_hash
    run_hash        TEXT    NOT NULL,                 -- SHA-256 of this run's evidence files
    timestamp       TEXT    NOT NULL,                 -- ISO 8601
    metadata        TEXT,                             -- JSON: run summary, engine version, plugin count
    verified_at     TEXT                              -- ISO 8601, last time this link was verified
);

CREATE INDEX idx_evidence_chain_timestamp ON evidence_chain(timestamp);

-- ============================================================
-- Key-Value Configuration
-- ============================================================

CREATE TABLE config (
    key             TEXT    PRIMARY KEY,              -- e.g. "llm.provider", "llm.api_key"
    value           TEXT    NOT NULL,                 -- Encrypted at rest for secrets
    category        TEXT    NOT NULL DEFAULT 'general'
                    CHECK (category IN ('general', 'llm', 'scheduling', 'reporting', 'compliance')),
    description     TEXT,                             -- Human-readable help text
    updated_at      TEXT    NOT NULL DEFAULT (datetime('now'))
);

-- ============================================================
-- Framework Cache (Denormalized for fast dashboard queries)
-- ============================================================

CREATE TABLE framework_cache (
    id              TEXT    PRIMARY KEY,              -- e.g. "eu_ai_act"
    name            TEXT    NOT NULL,
    version         TEXT    NOT NULL,
    clauses_json    TEXT    NOT NULL,                 -- Full clause definitions
    cached_at       TEXT    NOT NULL DEFAULT (datetime('now'))
);
```

### 4.3 Why SQLite is Sufficient

| Concern | SQLite Property | Why It Works Here |
|---------|----------------|-------------------|
| **Concurrent writers** | WAL mode allows concurrent reads + 1 writer | Single-user tool. Only one process writes at a time. |
| **Data volume** | Practical limit ~140TB | A compliance run produces ~100–500 results × ~5KB each = ~0.5–2.5MB. Even 1000 runs = ~2.5GB. Well within SQLite comfort. |
| **Query performance** | B-tree indexes, single-file | All queries are single-table lookups by `run_id` or `plugin_id`. No joins across millions of rows. Sub-millisecond. |
| **Portability** | Single `.db` file | Customer can `cp ~/.certifyai/certifyai.db /usb/backup/` for a complete audit trail. |
| **Zero ops** | Ships with Python stdlib | No PostgreSQL install, no Docker, no connection pooling, no configuration. |
| **Durability** | ACID with WAL mode | Writes are crash-safe. Evidence chain INSERTs are atomic. |
| **Dashboard reads** | `better-sqlite3` (synchronous) | Next.js reads from the same file. No race conditions in practice because reads are statement-level consistent in WAL mode. |

**When SQLite would break (and what we'd do):**

- **>10 concurrent writers:** Not applicable — single-user tool.
- **>100GB data:** Unlikely for compliance data. If reached, customer can migrate to PostgreSQL via SQLAlchemy swap.
- **High-availability / replication:** Not a goal. Boilerplate, not SaaS.

---

## 5. Key Design Decisions (ADRs)

This section codifies 8 Architecture Decision Records. Decisions 1–5 were established during project validation. Decisions 6–8 are new decisions derived from the detailed architecture design.

---

### ADR-001: Boilerplate over SaaS

| Attribute | Value |
|-----------|-------|
| **Status** | Accepted |
| **Date** | 2026-07-21 |
| **Scope** | Business model |

**Context:**
Original idea targeted enterprise B2B SaaS ($30K–$150K/yr). Solo dev cannot sustain enterprise sales cycles (6–18 months), lacks SOC 2 certification, and cannot provide 24/7 support. Enterprise AI governance incumbents (Vanta $350M, Credo AI $41M) already serve this market.

**Decision:**
Ship as downloadable boilerplate product. CLI + TUI are free (PyPI, Apache 2.0). Web Dashboard + full attack catalog + PDF reports are paid (Gumroad, $149 Pro / $499 Enterprise).

**Consequences:**
- ✅ Zero ops burden — no servers, no multi-tenancy, no uptime SLA
- ✅ Zero certification barrier — shipping code, not a service
- ✅ Revenue in weeks (Gumroad checkout) instead of months (enterprise sales)
- ✅ Customer owns their data entirely — no privacy compliance burden
- ❌ Revenue cap at ~$12K/mo instead of SaaS ARR potential
- ❌ No recurring revenue unless customer buys updates subscription ($49/yr)
- ❌ Piracy risk (cracked Gumroad downloads) — accepted, revenue from convenience

---

### ADR-002: Python Monolith for Engine + CLI + TUI

| Attribute | Value |
|-----------|-------|
| **Status** | Accepted |
| **Date** | 2026-07-21 |
| **Scope** | Language & packaging |

**Context:**
LLM ecosystem is Python-dominant (LiteLLM, LangChain eval tools, guardrails libraries). Solo dev needs to minimize language count.

**Decision:**
Core engine, CLI (Click), and TUI (Textual) are all Python 3.11+. Web Dashboard is the only non-Python component (Next.js 14). Engine is a Python library imported by CLI and TUI — no IPC, no subprocess, no network.

**Consequences:**
- ✅ Single language for 80% of the codebase
- ✅ Faster development — no cross-language type mapping
- ✅ Customer only needs `pip install certifyai` for core functionality
- ✅ In-process calls between CLI/TUI and Engine — zero serialization overhead
- ❌ TUI process shares memory with Engine — a plugin crash can bring down the TUI
- ❌ Harder to swap Engine for a different language later

---

### ADR-003: SQLite as Primary Database

| Attribute | Value |
|-----------|-------|
| **Status** | Accepted |
| **Date** | 2026-07-21 |
| **Scope** | Data storage |

**Context:**
Boilerplate must be self-contained. PostgreSQL adds setup friction (Docker, connection config, auth). VectorDB adds complexity with no clear need (no semantic search in v1).

**Decision:**
SQLite via SQLAlchemy 2.0 + `aiosqlite`. Single-file database. Evidence vault stored as filesystem directory with SHA-256 hash chain.

**Consequences:**
- ✅ Zero-infra setup — `sqlite3` ships with Python stdlib
- ✅ Single file backup — `cp certifyai.db backup.db` is a complete database backup
- ✅ SQLAlchemy abstraction — customers can swap to PostgreSQL if they outgrow SQLite
- ❌ No concurrent writer support (irrelevant — single-user tool)
- ❌ Less familiar operations tooling than PostgreSQL

---

### ADR-004: LiteLLM as Sole LLM Abstraction

| Attribute | Value |
|-----------|-------|
| **Status** | Accepted |
| **Date** | 2026-07-21 |
| **Scope** | LLM integration |

**Context:**
Original idea mentioned LangChain, LlamaIndex, and LiteLLM. Maintaining 3 SDK integrations is scope creep for a solo dev.

**Decision:**
LiteLLM only. Covers 100+ providers (OpenAI, Anthropic, Ollama, Gemini, any OpenAI-compatible endpoint). In v2, consider direct `httpx` for minimal-dependency customers.

**Consequences:**
- ✅ Single integration point — one API to learn, one set of error handling
- ✅ Customer flexibility — swap providers without changing tool
- ✅ Air-gapped capable — Ollama works without internet
- ❌ Dependency on LiteLLM's release cycle and API stability
- ❌ LiteLLM adds ~50MB of dependencies (mostly transitive). v2 could offer a lightweight mode.

---

### ADR-005: Shared SQLite File Across All Interfaces

| Attribute | Value |
|-----------|-------|
| **Status** | Accepted |
| **Date** | 2026-07-21 |
| **Scope** | Data sharing |

**Context:**
CLI, TUI, and Web Dashboard all need access to attack results and evidence. Options: API server, shared database, file-based IPC.

**Decision:**
All three read/write the same `certifyai.db` file. Engine writes via SQLAlchemy (async). Web Dashboard reads via `better-sqlite3` (synchronous Node.js binding). No API server. No IPC.

**Consequences:**
- ✅ Eliminates need for a separate backend server
- ✅ Simplifies deployment — no Docker Compose needed for core features
- ✅ Shared state without sync complexity — everyone reads the same file
- ❌ Web Dashboard must be careful not to write while Engine is writing (WAL mode helps)
- ❌ Web Dashboard cannot trigger engine runs natively — must spawn subprocess
- ❌ Network access to dashboard requires file system access (same machine)

---

### ADR-006: Plugin-Based Attack Architecture

| Attribute | Value |
|-----------|-------|
| **Status** | Proposed |
| **Date** | 2026-07-21 |
| **Scope** | Engine — attack execution |

**Context:**
The attack engine needs to support 30+ attack scenarios in v1, with ongoing additions. Two approaches: a monolithic evaluation pipeline with conditionals (`if attack_type == "injection": ...`), or a plugin system where each attack is a self-contained module.

**Decision:**
Use a plugin architecture. Each attack scenario is a class inheriting from `AttackPlugin`, discovered via filesystem scanning. A `PluginRegistry` handles loading, filtering, and instantiation.

**Consequences:**
- ✅ New attacks added by dropping a file in the plugin directory — no code changes to the runner
- ✅ Community contributions possible: third-party plugins without modifying core
- ✅ Plugin can be tested independently — each has its own `execute()` and `evaluate()` methods
- ✅ Clear separation of concerns — plugin knows its prompt template, evaluation criteria, and framework mappings
- ❌ Slightly more boilerplate per attack vs a monolithic condition chain (one class file vs one `if` branch)
- ❌ Plugin discovery has a startup cost (filesystem scan + import) — negligible for 30 plugins (<50ms)

**Trade-off accepted:** Slightly more code per attack in exchange for modularity and extensibility. For a boilerplate that will grow to 50+ attacks over time, the plugin boundary pays for itself.

**Rejected alternative — YAML-only attacks:**
Considered defining attacks purely in YAML (prompt template + evaluation regex). Rejected because:
- Some evaluations require semantic analysis (e.g., "did the model fabricate a citation?") that regex cannot express
- Plugin Python code enables integration with external tools (e.g., fact-checking APIs)
- YAML-only would limit attack sophistication

---

### ADR-007: Filesystem + SQLite for Evidence Vault

| Attribute | Value |
|-----------|-------|
| **Status** | Proposed |
| **Date** | 2026-07-21 |
| **Scope** | Engine — evidence storage |

**Context:**
Attack evidence (prompts, responses, evaluations) must be stored with tamper-evident integrity. Two natural approaches: store everything in SQLite as BLOBs, or store on filesystem with SQLite for indexing.

**Decision:**
**Hybrid approach.** Evidence blobs (JSON files) stored on filesystem in `vault/run_{id}/attack_{n}.json`. SQLite `evidence_chain` table stores cryptographic hashes and chain linkage. Filesystem stores the raw data.

**Rationale:**
- Storing large JSON blobs in SQLite as TEXT columns compresses poorly and makes backup/restore harder
- Filesystem evidence is directly readable by auditors without SQLite knowledge
- Filesystem evidence can be served directly by the Web Dashboard (static file read)
- SQLite chain provides integrity verification — tampering a file breaks the hash chain

**Consequences:**
- ✅ Evidence files are human-readable JSON — auditor-friendly
- ✅ SQLite queries are fast because they only store hashes + metadata, not full payloads
- ✅ `cp -r ~/.certifyai/vault` backs up all evidence independently
- ✅ Chain verification is O(n) on hash count, not evidence size
- ❌ Two storage systems to manage (filesystem + SQLite) instead of one
- ❌ File rename/move breaks vault structure (mitigated: path is relative to vault root)
- ❌ Slightly more code than pure-SQLite approach

**Rejected alternatives:**

| Alternative | Why Rejected |
|-------------|--------------|
| **Pure SQLite** (evidence as TEXT columns) | Larger DB size. Harder to inspect. Auditor needs DB tool to view evidence. |
| **Pure Filesystem** (no DB index) | O(n) scan to list runs. No querying. Harder to generate reports. |
| **Content-addressable storage** (hash as filename) | More complex. Overkill for append-only, single-writer scenario. |

---

### ADR-008: Direct SQLite Reads from Next.js (No API Server)

| Attribute | Value |
|-----------|-------|
| **Status** | Proposed |
| **Date** | 2026-07-21 |
| **Scope** | Web Dashboard — data access |

**Context:**
The Web Dashboard needs to display data from `certifyai.db`. Standard approach: build a REST/GraphQL API server (FastAPI/Express) that the dashboard calls. Alternative: read SQLite directly from Next.js.

**Decision:**
Use `better-sqlite3` (synchronous Node.js SQLite binding) in Next.js Server Components and Route Handlers. No dedicated API server. No network hop between dashboard and data.

**Architecture:**

```
Browser ──► Next.js Server ──► better-sqlite3 ──► certifyai.db
              (same machine)
```

**Why this works:**
- `better-sqlite3` is synchronous — no callback complexity in Server Components
- SQLite WAL mode allows concurrent reads with zero contention (Engine writes → Dashboard reads)
- All pages are Server Components (React Server Components) — data fetched at request time, zero client-side data fetching
- Route Handlers only needed for actions (trigger run, update config)

**Consequences:**
- ✅ Zero network latency for data access — database is on the same filesystem
- ✅ No API server to deploy, scale, or secure
- ✅ Simpler deployment — `npm run build && npm start` plus a path to `certifyai.db`
- ✅ Fewer moving parts = fewer failure modes
- ❌ Dashboard must run on the same machine as the SQLite file (cannot be remote)
- ❌ `better-sqlite3` requires native compilation — dependency pain for some platforms
- ❌ Cannot use async data fetching patterns (though synchronous is fine for this scale)

**Read vs Write distinction:**
- **Reads:** Dashboard reads freely via `better-sqlite3`. No issues. WAL mode guarantees consistent snapshots.
- **Writes:** Dashboard writes to `config` table directly via `better-sqlite3`. For triggering a new run, Dashboard spawns a CLI subprocess (`child_process.exec("certifyai run")`) — not a direct Engine call. This keeps the Engine in a separate process and prevents blocking the Next.js event loop.

**Rejected alternative — FastAPI backend:**
Building a FastAPI server between SQLite and Next.js would add ~500 lines of endpoint code, a new deployment artifact, and a network hop. The only benefit (multi-machine deployment) is irrelevant for a single-user boilerplate.

---

## 6. Quality Attributes

### 6.1 Security: Evidence Tampering

**Threat model:** An attacker who gains filesystem access wants to modify evidence to hide a compliance failure.

**Mitigations:**

| Layer | Mechanism | How It Works |
|-------|-----------|-------------|
| **Hash chain** | SHA-256 linkage | Each run's evidence hash includes the previous run's hash. Modifying one file breaks the entire chain from that point forward. |
| **Append-only DB** | SQLite trigger | `evidence_chain` has a trigger that rejects UPDATE/DELETE. Only INSERT is allowed. |
| **Verification** | `certifyai vault --verify` | Walk the entire chain, recompute hashes, report tampered entries. |
| **Config encryption** | `cryptography.fernet` | API keys and secrets in `config` table are encrypted at rest with a key derived from machine ID. |

**Residual risk:** An attacker with write access to both the vault files AND the chain database can modify evidence and recompute hashes to match. Mitigation: physical security of the machine is the customer's responsibility.

### 6.2 Performance: Concurrent Attacks

**Constraint:** The engine must run 30+ attacks against an LLM endpoint without unacceptable wall-clock time.

**Design choices:**

| Choice | Rationale |
|--------|-----------|
| `asyncio.TaskGroup` | Structured concurrency. 30 attacks at 5 concurrent = ~6 sequential batches. Average 5s per LLM call → ~30s total. |
| Configurable concurrency | `max_concurrency` (default 5) allows the customer to tune. Higher concurrency = faster but more API rate limit risk. |
| Semaphore | Prevents thundering herd on API rate limits. |
| LiteLLM built-in retry | Handles 429/5xx with exponential backoff. Prevents task failure on transient errors. |
| Timeout per call | 30s default. Prevents one stuck call from holding up the entire battery. |

**Expected performance (30 attacks, 5 concurrent):**

| LLM Provider | Avg Latency | Total Time | Worst Case (with retries) |
|-------------|-------------|------------|--------------------------|
| OpenAI GPT-4o | 3–5s | 18–30s | ~60s |
| Anthropic Claude 4 | 4–8s | 24–48s | ~90s |
| Ollama (local) | 1–3s | 6–18s | ~30s |
| Gemini 2.0 | 2–4s | 12–24s | ~45s |

### 6.3 Maintainability: Plugin System

**Goal:** Add a new attack scenario without modifying any existing code.

**Contract:**

```
To add a new attack:
1. Create file: certifyai/engine/plugins/<category>/my_attack.py
2. Inherit from AttackPlugin, implement execute() and evaluate()
3. Set metadata (name, category, severity, framework_refs)
4. Done. PluginRegistry discovers it automatically.
```

**Test isolation:** Each plugin is testable in isolation with a mock LLM client:

```python
@pytest.mark.asyncio
async def test_direct_injection():
    plugin = DirectInjectionPlugin()
    mock_llm = MockLLMClient(response="Sorry, I cannot override my instructions.")
    result = await plugin.execute(mock_llm, TEST_CONFIG)
    assert result.status == "pass"
    assert result.severity == "none"
```

### 6.4 Deployability: `pip install` Simplicity

**Deployment modes:**

| Mode | Command | What You Get |
|------|---------|-------------|
| **Core (Free)** | `pip install certifyai` | CLI + TUI + 10 attacks + JSON reports |
| **Pro (Gumroad)** | Download + `pip install certifyai-pro.zip` | All of the above + Web Dashboard + 30 attacks + PDF |
| **Enterprise (Gumroad)** | Same + license key | All Pro + white-label + source access |

**Zero dependencies beyond Python:**
- SQLite: ships with Python
- CLI: Click + Rich (pure Python)
- TUI: Textual (pure Python)
- Engine: Pydantic v2, SQLAlchemy, LiteLLM (all pip-installable)

**Docker (optional):** A `docker-compose.yml` is provided for customers who want the Web Dashboard without installing Node.js:

```yaml
services:
  engine:
    image: certifyai:latest
    volumes:
      - ~/.certifyai:/home/user/.certifyai
    command: certifyai watch

  dashboard:
    image: certifyai-dashboard:latest
    ports:
      - "3000:3000"
    volumes:
      - ~/.certifyai:/data
    environment:
      - CERTIFYAI_DB_PATH=/data/certifyai.db
```

---

## 7. Trade-off Analysis

This section presents three key architectural decisions where alternatives were seriously considered, explaining what was gained and what was sacrificed.

### 7.1 Trade-off #1: Plugin Architecture vs. Monolithic Condition Chain

**Decision:** Plugin-based attack architecture (ADR-006).

**The trade-off:**

| Dimension | Plugin Architecture (Chosen) | Monolithic Condition Chain (Rejected) |
|-----------|------------------------------|---------------------------------------|
| **Add new attack** | Create one file | Add one `elif` branch + update central evaluator |
| **Code readability** | Each attack is self-contained (~80 lines) | Single file grows to 3000+ lines |
| **Test isolation** | `pytest` per plugin, mock LLM | Must mock the entire evaluator |
| **Third-party contributions** | Drop a file in the right directory | Must understand the full pipeline |
| **Dispatch overhead** | Plugin discovery scan + import (~50ms for 30 plugins) | Zero — direct function call |
| **Indirection cost** | Abstract base class, registry pattern | No abstraction — straight-line code |
| **Cognitive load** | Developer must understand plugin contract | Developer reads one file with all attacks |

**What we gained:**
- Extensibility without risk of breaking existing attacks
- Community-contributable plugin ecosystem (future: pip-installable attack packs)
- Independent testing and documentation per attack

**What we gave up:**
- ~50ms startup overhead per command (negligible for a tool that runs for minutes)
- Slightly more total lines of code (30 attacks × ~30 extra lines of boilerplate = ~900 lines)
- Indirect control flow (plugin registry → dispatch → execute) vs straight-line code

**Verdict:** The plugin trade-off is strongly favorable for a tool that expects 50+ attacks over its lifetime and potential community contributions. For a 5-attack throwaway script, monolithic would be correct.

---

### 7.2 Trade-off #2: Hybrid Evidence Vault vs. Pure SQLite vs. Pure Filesystem

**Decision:** Hybrid filesystem + SQLite (ADR-007).

**The trade-off:**

| Dimension | Hybrid (Chosen) | Pure SQLite (Rejected) | Pure Filesystem (Rejected) |
|-----------|-----------------|----------------------|---------------------------|
| **Evidence inspectability** | ✅ Read JSON files directly | ❌ Need DB browser | ✅ Read files directly |
| **Query speed** | ✅ Fast (indexed hashes) | ✅ Fast (indexed) | ❌ O(n) scan for list/filter |
| **Backup granularity** | ✅ Can backup vault dir, or specific runs | ❌ Must backup entire DB | ✅ Can backup specific files |
| **Integrity verification** | ✅ Hash chain + DB linkage | ✅ Can compute hashes from DB | ❌ No chain — must verify each file |
| **System complexity** | ❌ Two layers to manage | ✅ One layer | ✅ One layer |
| **Tamper detection** | ✅ Hash chain + DB append-only | ✅ Hashes in same DB | ❌ No built-in chain |
| **Auditor experience** | ✅ Send them a run directory | ❌ Send them a .db file | ✅ Send them raw files, but no chain |

**What we gained:**
- Auditor-friendly evidence (raw JSON files they can open in any editor)
- Fast querying via SQLite index on run_id, plugin_id, timestamp
- Cryptographic chain verification that survives filesystem tampering
- Granular backup (copy specific runs, not the entire database)

**What we gave up:**
- Two storage systems to implement, test, and document
- Atomicity edge case: if filesystem write succeeds but DB INSERT fails, vault is orphaned (mitigated: write files first, then DB, with cleanup on failure)
- More total code (~200 lines extra vs pure SQLite)

**Verdict:** The hybrid approach is the right call for an **audit tool** where evidence inspectability matters. If this were an internal metrics store, pure SQLite would be simpler.

---

### 7.3 Trade-off #3: Direct SQLite Reads (No API Server) vs. FastAPI/Express Backend

**Decision:** Direct SQLite reads from Next.js via `better-sqlite3` (ADR-008).

**The trade-off:**

| Dimension | Direct SQLite (Chosen) | FastAPI Backend (Rejected) |
|-----------|------------------------|---------------------------|
| **Deployment complexity** | ✅ `npm run build && npm start` + path to DB | ❌ Python API server + Next.js = 2 processes |
| **Data access latency** | ✅ Zero network hop — reads are filesystem I/O | ❌ HTTP round-trip (~1–5ms localhost) |
| **Code to maintain** | ✅ ~0 lines of API endpoint code | ❌ ~500 lines of routes, serialization, error handling |
| **Data consistency** | ✅ Same-process reads are transaction-consistent | ❌ Potential staleness between API cache and DB |
| **Multi-machine deployment** | ❌ Must be same machine as SQLite file | ✅ Dashboard can run on different machine |
| **Write coordination** | ❌ Must use subprocess for Engine actions | ✅ API server can import Engine directly |
| **API reusability** | ❌ No API for third-party integrations | ✅ REST API could be used by other tools |

**What we gained:**
- Eliminated an entire deployment artifact (the API server)
- Faster page loads (no HTTP hop for data)
- Simpler mental model — "the dashboard reads the same file as the CLI"
- Faster development — no time spent on API design, just SQL queries

**What we gave up:**
- Multi-machine deployment (dashboard can't be on a different machine — irrelevant for single-user boilerplate)
- Programmatic API access (no REST endpoint for custom scripts — mitigated: they can use the Python Engine directly)
- Clean separation of concerns (dashboard now couples to SQLite schema — but it's the same schema used by the CLI/TUI)

**Verdict:** Direct SQLite is unambiguously correct for a single-user boilerplate. An API server would be pure overhead. Revisit this decision only if the product adds multi-user team features (not planned for v1).

---

## 8. Evolution Strategy

The architecture is designed to evolve without rewrites. This section describes how future capabilities map onto the existing design.

### 8.1 Custom Attack SDK (Post-v1.0)

**Goal:** Let customers write their own attack plugins without modifying the installed package.

**Design:**

```
~/.certifyai/custom_plugins/
├── my_company_attacks/
│   ├── __init__.py
│   ├── custom_injection.py
│   └── vertical_specific_test.py
└── attack_manifest.yaml    # Optional: metadata-only config
```

**How it works:**
- `PluginRegistry` already supports filesystem discovery
- Add a `CUSTOM_PLUGIN_DIR` config option (default: `~/.certifyai/custom_plugins/`)
- The registry scans both the built-in directory and the custom directory
- `AttackPlugin` base class is pip-installable as part of `certifyai` — customers import it

**Changes required:**
- Add custom plugin path to registry (config change only)
- Document the plugin API
- Add `certifyai plugin create my-attack` scaffolding command (nice-to-have)

**No architectural changes needed.** The plugin system was designed for this.

### 8.2 CI/CD Plugin (Post-v1.0)

**Goal:** Run attack battery in CI/CD pipelines (GitHub Actions, GitLab CI, pre-commit).

**The design maps naturally:**

```yaml
# .github/workflows/certifyai.yml
name: AI Compliance Check
on: [push]
jobs:
  compliance:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: pip install certifyai
      - run: certifyai run --config ci-config.toml
      - run: certifyai report --format sarif --output results.sarif
      - uses: github/codeql-action/upload-sarif@v3
        with:
          sarif_file: results.sarif
```

**Why SARIF matters:** SARIF is the standard format for static analysis results in CI/CD. GitHub CodeQL, GitHub Advanced Security, and VS Code all consume SARIF. By supporting SARIF output, CertifyAI results appear inline in pull requests and code reviews.

**Changes required:**
- CLI `--format sarif` already outputs SARIF
- Add `--exit-code` flag: exit with non-zero if any attack fails (CI integration)
- GitHub Action: Docker container that wraps the CLI

### 8.3 Multi-Modal Attacks (v2.0)

**Goal:** Test vision models (image prompt injection), audio models (speech jailbreak), and multi-modal reasoning.

**Design adaptation:**

```python
@dataclass
class AttackPayload:
    prompt: str
    images: list[bytes] = field(default_factory=list)
    audio: list[bytes] = field(default_factory=list)
    documents: list[bytes] = field(default_factory=list)
```

**How it fits:**
- `AttackPlugin.execute()` already accepts `AttackConfig` — add optional multi-modal fields
- Evidence blob stores base64-encoded images/audio along with prompt and response
- LiteLLM supports multi-modal payloads (OpenAI vision, Gemini multi-modal)
- Report templates can include image evidence in PDF

**Changes required:**
- Extend `AttackPayload` Pydantic model with optional multi-modal fields
- Add `tested_modalities` to `PluginMetadata`
- Some plugins become modal-specific (e.g., `vision.injection`)
- Evidence vault remains unchanged — filesystem storage handles any payload size

### 8.4 Team Collaboration Features (v2.0)

**Goal:** Multiple users share evidence, compare runs, assign compliance tasks.

**Design adaptation:**

```
Option A: Shared File System (NAS / Dropbox / S3)
  ~/.certifyai/ on a network drive
  Multiple dashboards read the same SQLite file
  CAUTION: SQLite concurrent writer limit → one writer at a time

Option B: Export / Import
  certifyai export --run <id> --format bundle.tar.gz
  certifyai import bundle.tar.gz
  Designed for auditor review, not live collaboration
```

**For v1, stick with Option B (export/import).** SQLite concurrent writer limitation makes live collaboration risky without a migration to PostgreSQL. If team features become the #1 requested feature, offer a `CERTIFYAI_DATABASE_URL=postgresql://...` config option that swaps the SQLAlchemy backend.

### 8.5 Update Distribution Pipeline

**How customers receive new attacks and framework mappings:**

```
                        ┌────────────────────┐
                        │  GitHub Releases    │
                        │                    │
                        │  certifyai v1.1.0  │
                        │  adds 5 new attacks│
                        │  updates EU AI Act │
                        └────────┬───────────┘
                                 │
                    ┌────────────┴────────────┐
                    │                         │
                    ▼                         ▼
              PyPI release              CertifyAI Updater
          (pip install --upgrade)     (built-in check command)
                    │                         │
                    └────────────┬────────────┘
                                 │
                                 ▼
                    ┌────────────────────────┐
                    │  certifyai update       │
                    │  - New attack plugins   │
                    │  - Updated framework    │
                    │    YAML files           │
                    │  - Report templates     │
                    └────────────────────────┘
```

**Design:**
- Framework YAML files are pip-installed as part of `certifyai` (in `certifyai/engine/frameworks/`)
- Updates are standard `pip install --upgrade certifyai`
- Built-in `certifyai update` command checks GitHub Releases for latest version
- Custom framework files in `~/.certifyai/frameworks/` are never overwritten by updates

---

## Appendix A: Glossary

| Term | Definition |
|------|-----------|
| **Attack Scenario** | A single test that sends a crafted prompt to an LLM and evaluates the response |
| **Attack Battery** | A collection of attack scenarios run as a group |
| **Plugin** | Self-contained Python class implementing one attack scenario |
| **Evidence Blob** | JSON file containing the full prompt, response, and evaluation for one attack |
| **Hash Chain** | Cryptographic linkage where each run's hash includes the previous run's hash |
| **Framework Mapping** | Association between attack results and regulatory framework clauses |
| **Compliance Score** | Percentage of tested clauses that passed |
| **SARIF** | Static Analysis Results Interchange Format (OASIS standard) |
| **TUI** | Terminal User Interface (Textual) |
| **WAL Mode** | Write-Ahead Logging — SQLite mode allowing concurrent reads during writes |

## Appendix B: References

- [C4 Model for Visualising Software Architecture](https://c4model.com/) by Simon Brown
- [Python 3.11+ asyncio.TaskGroup](https://docs.python.org/3/library/asyncio-task.html#asyncio.TaskGroup)
- [LiteLLM Documentation](https://docs.litellm.ai/)
- [Textual Framework](https://textual.textualize.io/)
- [SARIF v2.1.0 OASIS Standard](https://docs.oasis-open.org/sarif/sarif/v2.1.0/sarif-v2.1.0.html)
- [SQLite WAL Mode](https://www.sqlite.org/wal.html)
- [WeasyPrint Documentation](https://doc.courtbouillon.org/weasyprint/stable/)
- [Pydantic v2](https://docs.pydantic.dev/latest/)
- EU AI Act (Regulation 2024/1689) — effective August 2026
- NIST AI Risk Management Framework (AI RMF 1.0)
- SOC 2 Trust Services Criteria (2024 edition)
