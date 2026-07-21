# CertifyAI — Continuous Compliance Engine for AI Runtimes

**Category:** Developer Tool / Compliance Boilerplate
**Delivery Model:** Shippable product (PyPI + Gumroad), NOT SaaS
**Target Market:** AI/ML engineers, startup CTOs, compliance-conscious dev teams needing EU AI Act / SOC 2 / NIST AI RMF evidence without paying $30K+/yr for enterprise SaaS

---

## 1. Executive Summary

Traditional compliance software (Vanta, Drata) monitors static cloud infrastructure (S3 encryption, IAM policies) but cannot evaluate or audit the probabilistic behaviors of AI runtimes. Enterprise AI governance platforms (Credo AI, IBM watsonx) cost $30K–$150K+/yr and focus on documentation, not runtime testing.

**CertifyAI fills the gap:** A self-contained, downloadable compliance engine that continuously tests, evaluates, logs, and outputs audit-ready evidence for AI regulatory frameworks. Ships as CLI + TUI + optional Web Dashboard. Customer runs it on their own hardware. No subscription. No cloud dependency.

### Why Boilerplate (Not SaaS)

| SaaS Model (❌ Problems) | Boilerplate Model (✅ Solution) |
|-------------------------|-------------------------------|
| $30K–$150K/yr enterprise pricing → unaffordable for teams | **$79–$149 one-time** → affordable, no recurring burn |
| Multi-tenant infrastructure → ops burden for solo dev | **Self-hosted by customer** → zero ops for builder |
| SOC 2 certification required → barrier to entry | **No cert needed** (ship code, not service) |
| 6–18mo enterprise sales cycle → starvation risk | **Gumroad checkout** → revenue in week 1 |
| 24/7 enterprise SLA → impossible for solo dev | **Docs + email support** → sustainable |

---

## 2. Product Tiers

| Tier | Price | Contents | Buyer |
|------|-------|---------|-------|
| **Lite** (PyPI) | **Free** | CLI + TUI + 10 attack scenarios + basic JSON report + Apache 2.0 license | Solo devs evaluating |
| **Pro** (Gumroad) | **$149** | Lite + Web Dashboard + 30 attack scenarios + EU AI Act mapping + SOC 2 evidence pack + Full PDF reports + Commercial license | Teams prepping for audit |
| **Enterprise** (Gumroad) | **$499** | Pro + White-label reports + Priority updates + Source access + Custom framework mapping | Agencies, consultancies |

**Optional updates subscription:** $49/yr for new attack vectors & regulatory changes.

---

## 3. Architecture Overview

```
┌──────────────────────────────────────────────────────┐
│                CUSTOMER'S ENVIRONMENT                   │
│                                                        │
│  ┌─────────────────┐    ┌────────────────────┐        │
│  │  CLI (Click)     │    │  TUI (Textual)      │        │
│  │  certifyai run   │    │  Interactive        │        │
│  │  certifyai report│    │  Real-time attacks  │        │
│  │  certifyai watch │    │  Browse evidence    │        │
│  └────────┬────────┘    └────────┬───────────┘        │
│           │                      │                      │
│           ▼                      ▼                      │
│  ┌──────────────────────────────────────────────────┐  │
│  │              Core Engine (Python)                  │  │
│  │  ┌────────────┐  ┌────────────┐  ┌────────────┐  │  │
│  │  │ RedTeam     │  │ Evidence   │  │ Compliance │  │  │
│  │  │ Engine      │  │ Vault      │  │ Mapper     │  │  │
│  │  └────────────┘  └────────────┘  └────────────┘  │  │
│  │                                                    │  │
│  │  ┌──────────────────────────────────────────┐     │  │
│  │  │  LiteLLM (LLM Abstraction Layer)          │     │  │
│  │  │  → OpenAI / Anthropic / Ollama / Gemini   │     │  │
│  │  └──────────────────────────────────────────┘     │  │
│  └────────────────────┬───────────────────────────┘  │
│                       │                                │
│                       ▼                                │
│  ┌──────────────────────────────────────────────┐    │
│  │         SQLite (certifyai.db)                  │    │
│  │  (Evidence Logs · Attack Results · Config)     │    │
│  └──────────────────────────────────────────────┘    │
│                       │                                │
│                       ▼                                │
│  ┌──────────────────────────────────────────────┐    │
│  │  Web Dashboard (Next.js 14)  ← Optional       │    │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────┐      │    │
│  │  │ Reports  │ │ Explorer │ │ Settings │      │    │
│  │  └──────────┘ └──────────┘ └──────────┘      │    │
│  └──────────────────────────────────────────────┘    │
└──────────────────────────────────────────────────────┘
```

---

## 4. Complete Tech Stack

### Core Engine — Python 3.11+

| Component | Technology | Purpose |
|-----------|-----------|---------|
| Language | Python 3.11+ | Async-native, rich ML/LLM ecosystem |
| Async runtime | `asyncio` + `TaskGroup` | Structured concurrency for parallel attacks |
| LLM abstraction | **LiteLLM** | 100+ providers (OpenAI, Anthropic, Ollama, Gemini). Customer brings their own key. |
| Data models | **Pydantic v2** | Type-safe configs, attack specs, compliance mappings |
| Database | **SQLAlchemy 2.0** + `aiosqlite` | Async ORM, SQLite-first, optional PostgreSQL |
| Attack engine | Custom Python + `httpx` | Async HTTP calls to LLM endpoints. Modular plugin architecture. |
| Crypto vault | `hashlib` + `hmac` | SHA-256 hash chain for tamper-proof evidence logs |
| Report generation | `Jinja2` + `WeasyPrint` | HTML → PDF compliance reports |
| Config management | `pydantic-settings` | YAML/TOML config with schema validation |

### CLI — Python (Click + Rich)

```
Commands:
  certifyai init           Interactive setup wizard
  certifyai run            Execute full attack battery
  certifyai run --attack injection   Specific attack category
  certifyai report         Generate compliance report (JSON/PDF/SARIF)
  certifyai watch          Continuous monitoring mode
  certifyai vault --verify Verify evidence chain integrity
  certifyai list-attacks   Show available attack scenarios
```

### TUI — Python (Textual)

| Screen | Purpose |
|--------|---------|
| Dashboard | Real-time attack progress, pass/fail metrics |
| Explorer | Browse past runs, filter by date/attack type |
| Evidence Vault | View cryptographic hash chain, verify integrity |
| Config Editor | TUI-based settings (LLM endpoint, frameworks, schedule) |
| Report Preview | Scroll through generated PDF before export |

### Web Dashboard — Next.js 14 + Tailwind CSS (Optional, Pro Tier)

| Route | Component | Purpose |
|-------|-----------|---------|
| `/` | Dashboard overview | Attack summary, compliance score |
| `/runs` | Run history table | Filter, sort, compare past runs |
| `/runs/[id]` | Single run details | Attack-by-attack breakdown |
| `/compliance` | Framework mapping view | EU AI Act / SOC 2 / NIST RMF |
| `/compliance/[framework]` | Clause-specific evidence | Evidence mapped to each regulation |
| `/vault` | Evidence chain explorer | Cryptographic verification UI |
| `/reports` | Generated report library | Download PDF/SARIF/JSON |
| `/settings` | LLM config, auth, schedule | Dashboard settings |

**Tech:** Next.js 14 App Router · `motion/react` · Tailwind CSS v4 · `recharts` · `next-auth`

**Key design:** The dashboard reads from the SAME SQLite file as the CLI/TUI. No API server needed. `better-sqlite3` reads directly.

### Database — SQLite (Primary)

```
~/.certifyai/
├── config.toml                 # User config (LLM provider, schedule, frameworks)
├── certifyai.db                # SQLite (results, runs, evidence index)
├── vault/
│   ├── run_abc123/
│   │   ├── attack_001.json     # Raw prompt + response + metadata
│   │   ├── attack_001.hash     # SHA-256 of evidence blob
│   │   └── ...
│   └── chain.db                # Append-only hash chain
├── reports/
│   ├── report_2026-07-21.pdf
│   └── report_2026-07-21.sarif
└── frameworks/
    ├── eu_ai_act.yaml           # Shipped with product
    ├── nist_ai_rmf.yaml
    └── soc2.yaml
```

**Why SQLite:**
- ✅ Zero setup — `sqlite3` ships with Python
- ✅ Single file — easy to backup, share with auditors
- ✅ Performance — sufficient for single-tenant compliance data
- ✅ Portability — customer can `cp -r ~/.certifyai` their entire audit trail

### Auth Model

| Interface | Method |
|-----------|--------|
| CLI | API key in `~/.certifyai/config.toml` |
| TUI | Same key, entered on first launch |
| Web Dashboard | `next-auth` with credentials provider (SQLite-backed) |

### LLM Integration — LiteLLM

```
Customer Config:
  provider: openai | anthropic | ollama | gemini | openai-compatible
  model: gpt-4o | claude-4 | llama3.1 | gemini-2.0
  api_key: ${YOUR_KEY}   ← customer provides their own
  endpoint: (optional for self-hosted)
         │
         ▼
    ┌──────────┐
    │ LiteLLM  │  ← Handles routing, retries, rate limits
    └──────────┘
         │
         ▼
  [Attack Engine → sends test prompts → evaluates responses against compliance criteria]
```

---

## 5. Attack Scenarios (v1.0 Catalog)

| Category | Scenarios | What It Tests |
|----------|-----------|---------------|
| **Prompt Injection** | Direct injection, indirect injection, encoded injection | Can attacker override system prompt? |
| **Jailbreaking** | Role-play, hypotheticals, multi-language, token manipulation | Can attacker bypass safety filters? |
| **PII Leakage** | Email extraction, phone extraction, SSN patterns | Does model leak training data PII? |
| **Policy Violation** | Hate speech, dangerous content, financial advice | Does model follow content policy? |
| **Hallucination** | Factual claim verification, citation fabrication | Does model generate false information? |
| **Bias Testing** | Gender, racial, socioeconomic bias in outputs | Does model show demographic bias? |

Each attack returns: `{pass: bool, severity: str, evidence: dict, clause_refs: [str]}`

---

## 6. Compliance Framework Mapping

| Framework | Articles/Controls Mapped | Example |
|-----------|------------------------|---------|
| **EU AI Act** | Art. 9–15 (High-risk), Art. 50 (Transparency) | Art. 14 → Human Oversight tests |
| **SOC 2 Type II** | CC1–CC9 (Common Criteria) | CC6 → Access control evidence |
| **NIST AI RMF** | Govern, Map, Measure, Manage | MEASURE → Bias & hallucination tests |
| **ISO 42001** | Clause 6–10 (AI Management System) | Clause 7 → Support evidence |

---

## 7. Testing Strategy

| Layer | Tool | Target Coverage |
|-------|------|----------------|
| Unit (Engine) | `pytest` + `pytest-asyncio` | 90%+ |
| Integration | `pytest` + LiteLLM mock | Runs in CI, no API key needed |
| CLI | `pytest` + `click.testing` | 85%+ |
| TUI | `pytest` + `textual.testing` | 75%+ |
| Web Dashboard | `Playwright` | E2E critical paths |
| Property-based | `hypothesis` | Compliance mapping exhaustiveness |
| Evidence integrity | Custom test suite | Chain verification, tamper detection |

---

## 8. Build Plan — 8–10 Weeks (Solo Dev)

### Phase 1: Engine Core (Weeks 1–3)
- [ ] Project scaffold: pyproject.toml, ruff, mypy, pytest config
- [ ] Pydantic models: AttackScenario, AttackResult, EvidenceBlob, ComplianceMapping
- [ ] LiteLLM integration layer (provider abstraction, retry, rate limiting)
- [ ] Attack engine: plugin system, scenario runner, result collector
- [ ] Attack plugins: injection, jailbreak, PII leakage (10 scenarios)
- [ ] SQLite schema: runs table, results table, evidence index
- [ ] Evidence vault: hashing, chain, verify command
- [ ] Compliance mapper: YAML framework loader, clause matcher
- [ ] Report generator: JSON output, Jinja2 templates, PDF pipeline

### Phase 2: CLI + TUI (Weeks 4–5)
- [ ] CLI: `init`, `run`, `report`, `watch`, `vault`, `list-attacks`
- [ ] Rich output: colored terminal, progress bars, tables
- [ ] TUI: Dashboard screen (real-time attack progress)
- [ ] TUI: Explorer screen (browse past runs)
- [ ] TUI: Evidence Vault screen (hash chain viewer)
- [ ] TUI: Config Editor screen
- [ ] TUI: Report Preview screen

### Phase 3: Web Dashboard (Weeks 6–7)
- [ ] Next.js 14 project scaffold with App Router
- [ ] SQLite read layer (better-sqlite3, shared DB file)
- [ ] Dashboard overview page (metrics, charts)
- [ ] Run history page (table, filter, sort)
- [ ] Run detail page (attack breakdown, severity)
- [ ] Compliance mapping page (framework → clause → evidence)
- [ ] Evidence vault page (crypto chain visualizer)
- [ ] Reports library page (download PDF/SARIF)
- [ ] Settings page (config editor, auth setup)
- [ ] next-auth integration (credentials provider)

### Phase 4: Polish & Ship (Weeks 8–10)
- [ ] Full test suite (unit + integration + E2E)
- [ ] Documentation: MkDocs site with quickstart, usage, compliance guide
- [ ] PyPI packaging: certifyai (CLI+TUI+Engine)
- [ ] Docker Compose: Python engine + Next.js dashboard
- [ ] Gumroad listing: Pro tier ($149), Enterprise tier ($499)
- [ ] GitHub release: tags, changelog, binary builds
- [ ] Launch: Product Hunt, Hacker News, r/MachineLearning, Dev.to posts

---

## 9. Distribution & Revenue Model

```
PyPI (Free)                    Gumroad ($149/$499)
  │                                │
  ▼                                ▼
pip install certifyai          Download full bundle
  │                                │
  ▼                                ▼
CLI + TUI + 10 attacks        + Web Dashboard + 30 attacks
+ JSON reports                 + PDF reports + Compliance mappings
+ Apache 2.0 license           + Commercial license + Docs + Updates
```

### Revenue Projection

| Month | Event | Free Users | Pro Sales | Enterprise Sales | Net Revenue |
|-------|-------|-----------|-----------|-----------------|-------------|
| 1–2 | Build | — | — | — | $0 |
| 3 | Product Hunt + HN launch | 500–1K | 20–40 ($149) | 3–5 ($499) | **$4,500–$8,500** |
| 4 | Organic + Dev.to posts | 2K–5K | 10–20 | 2–3 | **$2,500–$4,500** |
| 5 | Community growth | 5K–10K | 15–25 | 3–5 | **$3,700–$6,200** |
| 6 | Steady state | 10K+ | 30–50/mo | 5–10/mo | **$7,000–$12,000/mo** |

---

## 10. Market Context (2026)

### Regulatory Urgency
- **EU AI Act high-risk deadline:** August 2, 2026 — 78% of orgs not ready
- **Maximum fines:** €35M or 7% of global annual turnover
- **50%+ of organizations lack a basic AI inventory**

### Competitive Gap
| Competitor | AI Runtime Testing? | Pricing | Self-Hosted? |
|-----------|-------------------|---------|-------------|
| Vanta | ❌ (static infra only) | $7.5K–$10K+/yr | ❌ SaaS only |
| Credo AI | ❌ (documentation only) | $30K–$150K+/yr | ❌ SaaS only |
| Drata | ❌ (SOC 2 infra) | $15K–$60K+/yr | ❌ SaaS only |
| IBM watsonx | ⚠️ (drift only) | Enterprise | ❌ Cloud |
| **CertifyAI** | ✅ **Continuous red-teaming** | **$79–$499 one-time** | **✅ Self-hosted** |

### Market Size
- AI Governance & Compliance market: **$3.4B (2026)** → **$68.2B (2035)** — 39.4% CAGR
- GRC platform market: **$65.86B (2026)** — 12.5% CAGR
- Gartner: **$492M in AI governance platform spend (2026)**

---

## 11. Key Design Principles

1. **CLI/TUI works 100% standalone** — No web dashboard required. Value from minute one.
2. **Single SQLite file** — No database server. No Docker needed for core functionality.
3. **Bring your own LLM** — Customer uses their existing provider/API key.
4. **Mutable by design** — Attack scenarios, compliance mappings, and dashboard are editable. It's a boilerplate, not a black box.
5. **Auditor-ready output** — PDF reports, SARIF files, cryptographically verified evidence chains.
6. **Evidence integrity** — SHA-256 hash chain. `certifyai vault --verify` proves no tampering.
7. **No cloud dependency** — Everything runs on the customer's machine. Air-gapped compliance possible with Ollama.

---

## 12. Risk Assessment

| Risk | Impact | Mitigation |
|------|--------|-----------|
| Incumbents add runtime testing | Medium | They're SaaS-only at $30K+. Boilerplate is different category. |
| Regulatory delay (Digital Omnibus) | Low–Medium | Reduces urgency 12–18 months but doesn't eliminate compliance need. |
| LLM API cost for customer testing | Low | Customer controls their own keys and usage. LiteLLM batching minimizes calls. |
| Support burden as solo dev | Medium | Self-serve docs + focused email hours. Pro/Enterprise pays for support. |
| Pirates crack Gumroad DRM | Low | Commercial license is honor-based. Revenue comes from convenience, not enforcement. |

---

## 13. Future Roadmap (Post-v1.0)

- Custom attack authoring SDK (write your own scenarios in Python)
- RAG-specific attack vectors (context poisoning, retrieval manipulation)
- Multi-modal attacks (vision prompt injection, audio jailbreaks)
- CI/CD plugins (GitHub Actions orb, GitLab CI template)
- Team collaboration features (multi-user vault, shared evidence)
- Additional frameworks: HIPAA AI, FDA AI/ML, Canada AIDA
