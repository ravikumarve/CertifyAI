# CertifyAI — Gumroad Product Listing

---

## — CertifyAI Pro ($149) —

### Product Title (60 char max)
**CertifyAI Pro** — Self-Hosted LLM Compliance Engine

### Subtitle (120 char max)
Test GPT-4o, Claude, Ollama, and 100+ models against 30 attack scenarios. Generate auditor-ready PDF reports mapped to EU AI Act, SOC 2, and NIST AI RMF. One-time payment. No subscription.

### Hero Description

Your LLM is going to be audited. Are you ready? The EU AI Act high-risk deadline is December 2027. SOC 2 auditors are starting to ask: "How do you test your AI system's behavior?" Vanta and Drata can tell you that your S3 buckets are encrypted, but they cannot send a single prompt to your model and check if it leaks PII or accepts a jailbreak. You need runtime evidence. CertifyAI gives it to you.

CertifyAI is a downloadable Python CLI + TUI (+ optional Web Dashboard) that runs 30 attack scenarios against your LLM endpoint — prompt injection, jailbreaking, PII leakage, policy violations, hallucination, and bias testing. Every result is logged with a SHA-256 hash chain, mapped to regulatory framework clauses (EU AI Act, SOC 2, NIST AI RMF, ISO 42001), and packaged into an auditor-ready PDF report. Bring your own API key. Run it on your machine. No data leaves your environment.

The EU AI Act high-risk deadline is 17 months away. Fines reach 35M or 7% of global turnover. 78% of organizations are not ready. You can spend $30K/year on a SaaS platform that doesn't actually test your model — or $149 for a tool that does, in 10 minutes, on your hardware. The choice is yours, but the clock is ticking.

### Feature Bullets

**Attack Engine**
- Run 30 battle-tested attack scenarios across 6 categories: prompt injection, jailbreaking, PII leakage, policy violations, hallucination, and bias testing — each with multiple prompt variants to catch edge cases
- Test any LLM provider via LiteLLM: OpenAI, Anthropic, Ollama, Gemini, Azure OpenAI, or any OpenAI-compatible endpoint — bring your own key, no vendor lock-in
- Execute attacks concurrently with configurable concurrency (default 5 parallel), completing a full battery in 2-5 minutes depending on provider latency
- Filter by attack category for targeted testing during development sprints — run only injection tests in 60 seconds while iterating on defenses

**Compliance Reports**
- Generate auditor-ready PDF reports with executive summary, per-attack evidence (full prompt + response + evaluation), and per-framework compliance scoring, ready to hand to your SOC 2 or EU AI Act auditor
- Map every attack result to specific regulatory clauses: EU AI Act Art. 9-15, SOC 2 CC6-CC9, NIST AI RMF MAP-MEASURE-MANAGE, ISO 42001 — with a compliance score per framework
- Export reports in PDF, JSON, and SARIF formats — SARIF integrates with GitHub CodeQL and VS Code for inline PR review annotations
- Generate differential reports comparing runs across deployments to catch regressions before they reach production

**Evidence Vault**
- Every attack result is recorded with its full prompt, response, evaluation verdict, and timestamp in an append-only evidence chain
- SHA-256 hash chain links every run to the previous run — tamper with one evidence file and the entire chain breaks from that point forward
- Verify integrity on demand: `certifyai vault --verify` walks the chain, recomputes hashes, and reports any tampering — gives auditors cryptographic proof
- Evidence files are plain JSON on the filesystem — readable by any text editor, no proprietary database viewer needed

**Web Dashboard (Pro)**
- Visual dashboard showing pass/fail metrics, compliance scores per framework, and recent run history — reads directly from the shared SQLite database
- Browse individual runs with per-attack breakdown, inspect prompts and responses, and download reports — all without touching the terminal
- Evidence chain visualizer with verification status — show auditors the integrity of your evidence at a glance
- Configure settings, manage API keys, and view compliance framework mappings through the GUI

**CLI & TUI (Free and Pro)**
- Interactive `certifyai init` wizard guides you through provider selection, API key entry, and model configuration — first attack run in under 3 minutes
- Rich terminal output with progress bars, color-coded pass/fail indicators, and real-time streaming during attack execution
- Full TUI (Textual-based) with dashboard, run explorer, vault screen, and config editor — stay in the terminal, never leave your workflow
- `certifyai watch` mode for continuous re-testing on a configurable interval

**Zero Ops**
- Single `pip install certifyai` — no Docker, no Node.js, no database server, no cloud account
- Works fully air-gapped with Ollama — no internet required at runtime
- All data stored in a single SQLite file at `~/.certifyai/certifyai.db` — backup is a `cp` command
- No servers to maintain, no SOC 2 certification to worry about, no renewal invoices

### Comparison Table

| Feature | CertifyAI Pro ($149) | DIY Open Source | Vanta ($10K/yr) | Credo AI ($30K+/yr) |
|---------|---------------------|-----------------|-----------------|-------------------|
| **LLM red-teaming** | 30 attacks, 6 categories | Requires Garak + Rebuff + Guardrails AI (4-8 weeks integration) | Not capable — infra only | Document workflows only |
| **Compliance mapping** | EU AI Act, SOC 2, NIST AI RMF, ISO 42001 | You build it manually | SOC 2, ISO 27001 only (no AI clauses) | EU AI Act, NIST AI RMF (documentation) |
| **Evidence integrity** | SHA-256 hash chain, vault --verify | No cryptographic chain | Standard audit log | Documentation storage |
| **PDF reports** | Auditor-ready PDF with evidence chain certificate | You build it (WeasyPrint + Jinja2) | Included | Included |
| **Web Dashboard** | Included in Pro | Not included | Included (SaaS) | Included (SaaS) |
| **Self-hosted / air-gapped** | Yes — works offline with Ollama | Yes | No — SaaS only | No — SaaS only |
| **Multi-provider** | 100+ via LiteLLM | Partial | N/A | N/A |
| **Setup time** | 3 minutes | 4-8 weeks engineering | 2-6 months procurement | 6-12 months procurement |
| **Price** | **$149 one-time** | $12K-$32K in engineering time | $10K/yr | $30K+/yr |
| **Procurement needed** | No (Gumroad checkout) | No | Yes | Yes |

### FAQ

**Q: Do I need my own API key?**
Yes. CertifyAI does not include LLM access. You bring your own API key from OpenAI, Anthropic, Ollama, or any LiteLLM-supported provider. Your key is stored locally in `~/.certifyai/config.toml` with encryption at rest.

**Q: Is it production-ready?**
CertifyAI v1.0 is a v1.0 product built by a solo developer. It is tested against GPT-4o, Claude 4, Gemini 2.0, and Ollama (Llama 3). The evidence vault, hash chain, and PDF report generation are designed for real auditor submission. That said, this is not an enterprise GRC platform — it's a focused tool for teams that need AI runtime compliance evidence without the enterprise price tag.

**Q: Can I try before buying?**
Yes. `pip install certifyai` gives you the full CLI + TUI with 10 free attack scenarios and JSON report output. No time limit. No feature crippling. You can run it against your LLM today. When you need the full 30-attack battery, PDF reports, compliance framework mapping, and Web Dashboard, buy Pro.

**Q: What if I find a bug?**
Report it on GitHub Issues. Pro customers get email support with a 48-hour SLA. Critical bugs (evidence chain corruption, false negatives on core attacks) are prioritized and patched within days. You also get 1 year of updates with your Pro purchase.

**Q: Do I get updates?**
Pro includes 1 year of updates (new attack scenarios, framework mapping updates, bug fixes). After the first year, you can optionally renew updates for $49/yr. Your purchased version continues working forever — no forced upgrades.

**Q: Can I white-label reports?**
White-label branding is an Enterprise-tier feature ($499). Pro reports include "Generated with CertifyAI" in the report header.

**Q: Does it work with my model?**
If your model is accessible via an OpenAI-compatible API endpoint, Ollama, or any LiteLLM-supported provider (100+), it works. This includes GPT-4o, Claude, Gemini, Llama, Mistral, DeepSeek, and custom fine-tuned models hosted on your own infrastructure.

**Q: Can I run this in CI/CD?**
Not in v1.0. CI/CD plugins (GitHub Actions, GitLab CI) are planned for v2.0. For now, you can run `certifyai run` and `certifyai report --format sarif` manually or via a cron job. The SARIF output is ready for future CI integration.

**Q: What happens to my data?**
Nothing. CertifyAI runs entirely on your machine. No telemetry is sent (telemetry is opt-in and off by default). Your evidence, API keys, and reports never leave your filesystem. The only outbound network calls are the attack prompts sent to your configured LLM provider.

**Q: Can I get a refund if it doesn't work for my use case?**
Yes, within 14 days of purchase, no questions asked. See refund policy below.

### Who Is This For / Not For

**This is for you if:**
- You deploy LLMs in production and need compliance evidence for SOC 2, EU AI Act, NIST AI RMF, or ISO 42001
- You are a startup CTO who cannot justify $10K-$30K+/yr on enterprise compliance SaaS
- You are an ML engineer who wants to red-team your model before auditors ask
- You need to work air-gapped or in a regulated environment that does not allow cloud-based compliance tools
- You prefer CLI/TUI tools over web dashboards (but want the dashboard option)
- You want to own your compliance evidence — no vendor lock-in, no data leaving your machine

**This is NOT for you if:**
- You need a managed SaaS platform with 24/7 uptime SLA, SSO, RBAC, and enterprise support — buy Vanta or Credo AI
- You expect a no-code, click-only interface — CertifyAI is primarily a CLI tool with an optional TUI and Web Dashboard
- You need someone else to manage your compliance program — CertifyAI generates evidence, it does not file regulatory documents
- You don't have any compliance requirements and just want to red-team your model for fun — the free CLI tier is great for that
- You need CI/CD integration, scheduled monitoring, or team collaboration features — these are coming in v2.0

### Refund Policy

**14-day, no-questions-asked refund.** If CertifyAI Pro doesn't work for your use case, email us within 14 days of purchase and you'll get a full refund.

**What triggers a refund:**
- The tool doesn't work with your LLM provider (after we confirm the provider is supported by LiteLLM)
- The evidence vault or report generation has a defect we cannot resolve within 7 days
- You bought the wrong tier and want to switch to Enterprise

**What does NOT trigger a refund:**
- "I changed my mind" — this is covered by the 14-day policy anyway
- "My auditor rejected the report format" — we provide PDF, JSON, and SARIF; if your auditor requires a specific format, check with Enterprise tier (custom branding may help)
- "I found a free alternative" — you already had the free CLI tier to evaluate before buying Pro

### License Terms Summary

**Pro License — Single Team:**
- You purchase one license per team (up to 5 users within the same legal entity)
- You may install CertifyAI Pro on multiple machines owned by your team
- You may NOT redistribute, resell, or sublicense the software
- You may NOT remove CertifyAI branding from reports (white-label requires Enterprise)
- Source code access is NOT included (Enterprise tier only)
- Updates included for 1 year from purchase date

### Call-to-Action

**Buy CertifyAI Pro — $149**

Your LLM will be audited. Be ready with cryptographic evidence.

Guarantee: 14-day, no-questions-asked refund. If it doesn't work for your use case, you pay nothing.

---

## — CertifyAI Enterprise ($499) —

### Product Title (60 char max)
**CertifyAI Enterprise** — White-Label AI Compliance Suite

### Subtitle (120 char max)
Everything in Pro, plus white-label reports, full source access, unlimited team members, custom compliance frameworks, and priority support.

### Hero Description

You audit 15 clients per year. Each one needs a compliance report with your branding, your methodology, your framework mappings. You currently spend 3-4 days per client manually crafting test prompts, copy-pasting results into Google Docs, and generating PDFs. That's 45-60 days of billable time lost to manual compliance work.

CertifyAI Enterprise automates the entire pipeline. Run the same standardized attack battery across every client environment. Generate white-labeled PDF reports with your logo, your company name, your disclaimer page. Customize compliance framework mappings when regulations change. Access the full source code to build custom integrations. All for a single $499 payment — commercial license included.

You bill $250/hour. If Enterprise saves you even 2 days of manual work per client, that's $4,000 in reclaimed billable time. The tool pays for itself on the first client.

### Feature Bullets

**Everything in Pro, plus:**

**White-Label Reports**
- Replace "CertifyAI" with your company name in report headers, footers, and metadata
- Add your logo to the cover page and every page header
- Include custom disclaimer pages, legal notices, and methodology descriptions
- Remove "Generated with CertifyAI" watermark from all outputs

**Full Source Code Access**
- Access and modify the complete Python source code
- Extend framework mappings (YAML files) for emerging regulations like Colorado AI Act, HIPAA AI guidance, or client-specific frameworks
- Build custom integrations with your existing toolchain
- No code obfuscation — everything is readable, editable, and auditable

**Custom Compliance Frameworks**
- Create and ship your own framework YAML files to clients
- Modify existing framework mappings when regulations change
- Map client-specific requirements to attack categories
- Framework files survive product updates (never overwritten)

**Priority Support**
- Email support with 24-hour SLA (vs. 48-hour for Pro)
- Direct line to the developer for urgent issues
- Priority bug fixes and feature requests
- Help with custom integrations and white-label setup

**Unlimited Team Members**
- One Enterprise license covers your entire organization
- No per-seat pricing
- Deploy across unlimited machines within your company

**Lifetime Updates**
- All updates included for the lifetime of the product — no annual renewal fee
- New attack scenarios, framework updates, and features as they ship
- Your purchase never expires

### Comparison Table

| Feature | Pro ($149) | Enterprise ($499) |
|---------|-----------|-------------------|
| Attack scenarios | 30 | 30 |
| Compliance frameworks | EU AI Act, SOC 2, NIST AI RMF, ISO 42001 | Same + custom frameworks |
| Report formats | JSON, PDF, SARIF | JSON, PDF, SARIF |
| Web Dashboard | Included | Included |
| White-label / custom branding | Not available | Full branding (logo, name, disclaimer) |
| Source code access | Not included | Full source code |
| Custom framework YAML | Read-only | Create and modify |
| Team members | Up to 5 | Unlimited |
| Support | Email, 48hr SLA | Email, 24hr SLA + priority |
| Updates | 1 year | Lifetime |
| License | Single team | Entire organization, commercial |
| Refund period | 14 days | 14 days |

### FAQ (Enterprise-Specific)

**Q: Can I use Enterprise to generate compliance reports for my consulting clients?**
Yes. The commercial license explicitly allows you to use CertifyAI Enterprise as a tool in your consulting practice. You can generate branded reports for any number of clients. You may NOT resell the CertifyAI software itself — your client should buy their own license if they want to run it themselves.

**Q: What does "source code access" actually mean?**
You get the complete Python source tree — the engine, CLI, TUI, plugins, compliance mapper, report generator, and Web Dashboard. You can read it, modify it for your use case, and build custom integrations. You may NOT redistribute the modified source code as a competing product.

**Q: Can I add my own compliance frameworks?**
Yes. Enterprise includes the ability to create new framework YAML files from scratch, modify existing ones, and ship them as part of your client deliverables. The YAML schema is documented and Pydantic-validated.

**Q: Do I really get lifetime updates?**
Yes. No subscription, no renewal notice. You get all updates for as long as CertifyAI is developed. This includes new attack scenarios, framework mapping updates, bug fixes, and new features.

**Q: What if I need on-call support for a client audit?**
Enterprise includes priority email support with 24-hour SLA. If you need faster response for an active audit, we can discuss a support retainer. But for 99% of cases, the 24-hour SLA covers audit timelines.

**Q: Can I install this on my client's machine?**
Yes. The Enterprise commercial license covers deployment on client machines for the purpose of running compliance tests and generating reports. Your client does not need to buy their own license.

### Who Is This For / Not For

**This is for you if:**
- You run an AI compliance consultancy and audit 5+ clients per year
- You need white-label reports with your branding for client delivery
- You want to customize framework mappings for emerging regulations or client-specific requirements
- You need source code access to build custom integrations or verify security
- You want a single license that covers your entire organization
- You want lifetime updates with no recurring fees

**This is NOT for you if:**
- You are a solo developer or single team who just needs compliance evidence for your own LLM — Pro is the right tier
- You plan to resell CertifyAI as a SaaS product — the commercial license explicitly excludes this
- You don't need white-label reports or source access — save $350 and buy Pro
- You want to redistribute modified source code as a competing product — also excluded

### Refund Policy

**14-day, no-questions-asked refund.** Same as Pro. If Enterprise doesn't work for your use case, email us within 14 days and you'll get a full refund.

**Additional Enterprise-specific refund triggers:**
- The white-label feature does not produce acceptable report branding (after we help with setup)
- Source code access reveals that the codebase does not support your intended customization

**Additional Enterprise-specific refund exclusions:**
- You modified the source code and broke something — that's on you
- You expected unlimited redistribution rights — the commercial license covers use, not resale

### License Terms Summary

**Enterprise License — Unlimited Organization + Commercial Use:**
- Covers all employees and contractors within your legal entity
- Licensed per company, not per seat
- Commercial use allowed: generate reports for clients, use as a tool in consulting practice
- White-label: You may replace CertifyAI branding with your own
- Source code: You may read, modify, and build custom integrations
- You may NOT redistribute the software (modified or unmodified) as a standalone product
- You may NOT sublicense, resell, or offer CertifyAI as a SaaS service
- Lifetime updates included for as long as the product is developed

### Call-to-Action

**Buy CertifyAI Enterprise — $499**

From manual Google Docs compliance to automated, white-label client reports. One payment. Lifetime updates.

Guarantee: 14-day, no-questions-asked refund. If it doesn't save you billable hours on your first client audit, you pay nothing.

---

## — Appendix: Quick Comparison —

| | Free (PyPI) | Pro ($149) | Enterprise ($499) |
|---|---|---|---|
| Attack scenarios | 10 | 30 | 30 |
| Report formats | JSON | JSON + PDF + SARIF | JSON + PDF + SARIF |
| Compliance frameworks | None (raw results) | EU AI Act, SOC 2, NIST AI RMF, ISO 42001 | Same + custom frameworks |
| Web Dashboard | — | Included | Included |
| White-label | — | — | Full branding |
| Source code | — | — | Full access |
| Team members | 1 | Up to 5 | Unlimited |
| Support | GitHub Issues | Email, 48hr SLA | Email, 24hr SLA + priority |
| Updates | — | 1 year | Lifetime |
| License | Apache 2.0 | Commercial (single team) | Commercial (unlimited org) |
| **Price** | **$0** | **$149 one-time** | **$499 one-time** |
