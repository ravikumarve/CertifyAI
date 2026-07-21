# CertifyAI — Support Plan

**Document Status:** Final v1.0
**Author:** Support Responder (The Agency)
**Date:** 2026-07-21
**Product:** Continuous Compliance Engine for AI Runtimes (Boilerplate)
**Support Team Size:** 1 person (the builder)
**Tone:** Honest about limits. Clear about expectations. Helpful within constraints.

---

## Table of Contents

1. [Philosophy](#1-philosophy)
2. [Support Tiers](#2-support-tiers)
3. [Response SLAs](#3-response-slas)
4. [Email Templates](#4-email-templates)
5. [Self-Service Architecture](#5-self-service-architecture)
6. [Escalation Path](#6-escalation-pathsolo-dev-edition)
7. [Refund Handling](#7-refund-handling)
8. [Feedback Loop](#8-feedback-loop)
9. [Hours & Boundaries](#9-hours--boundaries)
10. [Proactive Monitoring](#10-proactive-monitoring)
11. [Tools & Stack](#11-tools--stack)
12. [Appendix: Quick-Reference Cheat Sheet](#12-appendix-quick-reference-cheat-sheet)

---

## 1. Philosophy

CertifyAI is a self-hosted boilerplate sold to technical buyers (ML engineers, startup CTOs). The support model must match the product:

- **The product is self-service by design.** Customers install it themselves, bring their own API keys, and run it on their own hardware. Most issues are configuration problems, not product bugs.
- **The support team is one person.** Pretending otherwise creates resentment and burnout. We optimize for clarity, boundaries, and leverage (docs > templates > personal replies).
- **Free users get community + docs.** Pro/Enterprise buyers pay for access to the builder's attention. That attention is finite and must be protected.
- **The best support outcome is the one the customer didn't need.** Invest in docs, error messages, and onboarding. Every hour spent on self-service infrastructure saves 10 hours of email replies.

---

## 2. Support Tiers

### Free Tier (Community Support)

| Channel | Availability | SLA | Notes |
|---------|--------------|-----|-------|
| GitHub Discussions | Always | Best-effort, no commitment | Public only. Answers help everyone. |
| Documentation | Always | N/A | Primary support channel. Link-first. |
| GitHub Issues (bugs) | Always | Triage within 7 days | Only for confirmed bugs. Feature requests redirected to Discussions. |

**What free users do NOT get:**
- Email support
- Direct messages (Twitter, LinkedIn, email)
- Custom configuration help
- Report interpretation assistance
- Priority bug fixes

**Why:** Free users have not transacted. Their support is the community and the docs. This is standard for open-source-adjacent boilerplate products (see: Django, Tailwind UI, every PyPI package ever). Free users who need more support are exactly the audience who should convert to Pro.

### Pro Tier ($149 — Email Support)

| Channel | Availability | SLA | Notes |
|---------|--------------|-----|-------|
| Email (support@certifyai.dev) | Business hours | 48h response | One conversation per ticket |
| GitHub Issues (bugs) | Always | Triage within 48h | Marked with `pro-user` label for priority |
| GitHub Discussions | Always | Best-effort | Same as free (public discussions) |

**Included:**
- 1 support conversation per purchase (resolves or escalates to bug)
- Configuration help (API keys, LiteLLM providers, SQLite setup)
- Report interpretation (what does this result mean for SOC 2?)
- Installation troubleshooting
- Bug confirmation and workaround

**Not included:**
- Custom attack scenario authoring
- Custom framework mappings
- Integration with proprietary internal tools
- Training/onboarding sessions
- Phone/video calls

### Enterprise Tier ($499 — Priority Email Support)

| Channel | Availability | SLA | Notes |
|---------|--------------|-----|-------|
| Email (support@certifyai.dev) | Extended hours | 24h response | Priority queue |
| GitHub Issues (bugs) | Always | Triage within 24h | `enterprise` label |
| GitHub Discussions | Always | Same-day (if relevant) | Public |
| Security reports | Encrypted only | 72h to acknowledge | See escalation section |

**Additional:**
- Same-day bug fix or workaround commitment (critical severity)
- Custom report format requests (e.g., specific PDF template for their auditor)
- Configuration review call (1x, 30min, calendar-scheduled, asynchronous — Loom or written summary)
- Direct line to builder (still email, but flagged as enterprise — no Slack, no phone)

**Still not included:**
- 24/7 support
- Phone/video support
- SLA guaranteeing a fix (only a response/triage SLA)
- Custom development

### Summary Matrix

| Capability | Free | Pro ($149) | Enterprise ($499) |
|------------|------|------------|-------------------|
| Docs & guides | ✅ | ✅ | ✅ |
| GitHub Discussions | ✅ | ✅ | ✅ |
| GitHub Issues | ✅ (7d triage) | ✅ (48h triage) | ✅ (24h triage) |
| Email support | ❌ | ✅ (48h) | ✅ (24h) |
| Bug workaround | ❌ | ✅ | ✅ |
| Priority queue | ❌ | ❌ | ✅ |
| Config review call | ❌ | ❌ | ✅ (1x, async) |
| Custom report templates | ❌ | ❌ | ✅ |
| Security vuln reporting | ❌ | ❌ | ✅ (72h) |

---

## 3. Response SLAs

All SLAs are **business days, best-effort, based on receipt timestamp in the builder's timezone (UTC+5:30 IST)**. Weekends and public holidays do not count toward SLA time.

### Severity Levels

| Severity | Definition | Examples | SLA (Pro) | SLA (Enterprise) |
|----------|------------|----------|-----------|-------------------|
| **Critical** | Cannot install or run the product. Blocking path. | `pip install` fails with cryptic error. CLI crashes on `init`. SQLite permission error on fresh install. | 24h | 12h |
| **Normal** | Product runs but has a question or minor issue. | How to configure Azure OpenAI? What does this attack result mean? Can I run only injection tests? | 48h | 24h |
| **Low** | Feature request, suggestion, or feedback. | "It would be great if you supported Gemini." "I found a typo in the docs." | 72h (acknowledgement only) | 48h (acknowledgement only) |
| **Security** | Vulnerability in the product or dependencies. | Prompt injection in dashboard UI. LiteLLM dependency with CVE. SHA-256 chain broken. | See escalation section | See escalation section |

### SLA Clock Rules

- **Starts:** When the email arrives in the support inbox
- **Pauses:** When the builder asks a clarifying question and awaits a reply
- **Resets:** If the customer sends a follow-up before the builder responds (counted as new ticket — reply to latest, not oldest)
- **Stops:** When a human response (not auto-reply) is sent
- **Excludes:** Weekends, Indian public holidays (pre-published list on certifyai.dev/support), and the builder's published off-hours

### SLA Miss Protocol

If an SLA is missed (it will happen — solo dev, sick days, life):

1. **Auto-acknowledgement** after SLA expiry: "We're sorry for the delay. Your ticket is important to us and will be answered shortly."
2. **SLA miss credit:** Pro users get a 20% discount code for their next purchase. Enterprise users get a 30% discount code or a 30-day extension on the 14-day refund window.
3. **Post-mortem (internal):** Why was the SLA missed? Was it preventable? Adjust capacity or SLAs if pattern emerges.
4. **Transparency:** If the builder is sick or on an unplanned break, update the status page (certifyai.dev/status) and auto-respond with expected delay.

**Important:** SLA misses are expected occasionally. The goal is not 100% compliance (unrealistic for solo dev). The goal is honesty, apology, and compensation when it happens.

---

## 4. Email Templates

### 4.1 Welcome + Getting Started (Pro/Enterprise Purchase)

```
Subject: Welcome to CertifyAI — Your Compliance Engine Awaits

Hi {name},

Thanks for purchasing CertifyAI {tier}. You now have a permanent license
to run compliance attacks against your AI systems.

Here's your 5-minute setup:

1. Install: pip install certifyai
2. Configure: certifyai init
3. Run: certifyai run --provider openai --model gpt-4o
4. Report: certifyai report --format pdf

Quick links:
- Quickstart guide: https://certifyai.dev/docs/quickstart
- Provider setup: https://certifyai.dev/docs/providers
- Troubleshooting: https://certifyai.dev/docs/troubleshooting
- Full documentation: https://certifyai.dev/docs

{tier === 'Enterprise' ? 'Your purchase includes priority support. Reply to this email
with any questions and we'll respond within 24 hours.' : 'Your purchase includes email
support. Reply to this email with any questions (48h response time).'}

For bugs, please open a GitHub issue: https://github.com/certifyai/certifyai/issues

Happy compliance testing,
{builder_name}
```

### 4.2 Install Troubleshooting

```
Subject: Re: Installation Issue — {summary}

Hi {name},

Thanks for reaching out. Let's get you up and running.

Most install issues fall into one of these buckets:

1. Python version: CertifyAI requires Python 3.11+
   Check: python3 --version

2. pip version: Upgrade pip first
   Run: pip install --upgrade pip && pip install certifyai

3. Platform-specific:
   - Linux: If you see "externally managed environment" error,
     use: pip install --user certifyai
   - macOS: If you see xcode-select errors, run: xcode-select --install
   - Windows: Use Python from python.org (not Microsoft Store)

4. Dependency conflict: Try a fresh virtual environment
   python3 -m venv certifyai-env
   source certifyai-env/bin/activate
   pip install certifyai

Please try the steps above and let me know what you see.
If still stuck, please share:
- Output of: python3 --version && pip list | grep certifyai
- Your OS: (Linux/macOS/Windows + version)
- The full error output (paste, not screenshot)

{canned_fixes_link}
```

### 4.3 API Key Configuration

```
Subject: Re: API Key Setup — {summary}

Hi {name},

CertifyAI doesn't store your API keys in the cloud — they stay in
~/.certifyai/config.toml on your machine.

To configure your provider:

1. Run: certifyai init
   This will prompt you for provider, model, and API key.

2. Or edit the config file directly:
   ~/.certifyai/config.toml

   [provider]
   name = "openai"  # or azure, anthropic, ollama, google, any LiteLLM provider
   model = "gpt-4o"
   api_key = "sk-..."  # your key here
   # For OpenAI-compatible endpoints:
   # api_base = "https://your-endpoint.com/v1"

3. Verify with: certifyai run --dry-run
   This tests your connection without running attacks.

Provider-specific notes:
- OpenAI: Your key starts with "sk-". Ensure billing is active.
- Azure: You need api_base, deployment_id, api_key, api_version.
- Ollama: No API key needed. Ensure server is running.
- Anthropic: Starting with "sk-ant-". Ensure model access is granted.

For full provider docs: https://certifyai.dev/docs/providers

If you're still having issues, please share:
- Which provider you're using
- The exact error message
- Whether `certifyai run --dry-run` succeeded or failed
```

### 4.4 SQLite Issues

```
Subject: Re: Database Issue — {summary}

Hi {name},

CertifyAI uses SQLite stored at ~/.certifyai/certifyai.db.
Most SQLite issues have simple fixes.

**Permission denied / Can't write to database:**
  Solution: Ensure ~/.certifyai/ directory is writable.
  Run: chmod -R 755 ~/.certifyai

**Database is locked:**
  Cause: Another certifyai process is running, or the Web Dashboard
  has the database open.
  Solution: Close all certifyai processes and the dashboard.
  Run: pkill -f certifyai  # Linux/macOS
  Then retry.

**Corrupted database / "database disk image is malformed":**
  This is rare. Usually caused by killing a running attack.
  Solution (recovery):
  1. Backup: cp ~/.certifyai/certifyai.db ~/.certifyai/certifyai.db.bak
  2. Recover: sqlite3 ~/.certifyai/certifyai.db ".recover" | sqlite3 ~/.certifyai/certifyai_recovered.db
  3. Replace: mv ~/.certifyai/certifyai_recovered.db ~/.certifyai/certifyai.db
  4. Verify: certifyai vault --verify

**WAL mode (Web Dashboard users):**
  If you use the dashboard, ensure SQLite is in WAL mode:
  sqlite3 ~/.certifyai/certifyai.db "PRAGMA journal_mode=WAL;"
  This allows concurrent reads from the dashboard while the CLI writes.

For persistent issues: https://certifyai.dev/docs/troubleshooting#sqlite
```

### 4.5 Report Interpretation

```
Subject: Re: Report Interpretation — {summary}

Hi {name},

Great question. Here's how to read your CertifyAI report.

**The short version:**
- Green = passed (no vulnerability detected)
- Red = failed (vulnerability detected)
- Yellow = inconclusive (model returned unexpected output)

**What passed/failed actually means:**

"Passed" means the model did NOT exhibit the problematic behavior.
For example, a prompt injection attack that the model correctly refused
is a PASS — the model is compliant for that attack.

"Failed" means the model DID exhibit the problematic behavior.
This is NOT necessarily bad — it tells you where to improve.

**Mapping to your framework:**

Your report includes a compliance mapping section that shows:
- Which specific regulation clauses (e.g., EU AI Act Article 9,
  SOC 2 CC7.1) each attack maps to
- A compliance score for each clause
- Recommended remediation steps per failed test

**Example: SOC 2 CC7.1 (Identification of vulnerabilities)**
  If you run 30 attacks across 6 categories and 3 fail (e.g., 2 PII
  leaks, 1 jailbreak), your CC7.1 score would be 90% (27/30 passed).
  SOC 2 auditors typically look for: documented evidence that you
  HAVE tested, not that you passed every test. The key deliverable
  is the evidence chain proving tests were run.

**For auditors:**
  Your auditor can verify evidence integrity with:
  certifyai vault --verify
  This proves no results were tampered with since recording.

For a full guide: https://certifyai.dev/docs/interpreting-reports

If you'd like me to look at a specific result, please share the
attack name and the model's response (or a hash of the evidence entry).
```

### 4.6 Refund Request

```
Subject: Re: Refund Request — CertifyAI

Hi {name},

I'm sorry CertifyAI isn't working for you. Refunds are handled
immediately, no questions asked, within 14 days of purchase.

Your refund has been processed. You should see the funds returned
within 5-10 business days (depending on your payment provider).

Your license key has been deactivated. You may keep the software
installed but will not receive updates or support after the refund
date.

If you're willing to share, I'd love to know why it didn't work for
you — it helps me improve the product:
[ ] Didn't meet my needs / not what I expected
[ ] Technical issues I couldn't resolve
[ ] Too difficult to set up
[ ] Missing features I need
[ ] Found a different solution (please share: ______)
[ ] Other: ______

No pressure to respond — the refund is yours regardless.

Thank you for giving CertifyAI a try.

{builder_name}
```

### 4.7 "I Need a Feature" Response

```
Subject: Re: Feature Request — {summary}

Hi {name},

Thanks for the thoughtful suggestion. I appreciate you taking the
time to share it.

I've added this to the feature tracker:
https://github.com/certifyai/certifyai/issues/{issue_number}

**A few notes on timing:**

As a solo developer, I have to prioritize carefully. Here's how
I decide what to build next:

1. Security fixes and critical bugs always come first
2. Features that benefit the most users
3. Features that unblock Enterprise customers
4. Everything else

Your feature request is in the queue. If it gains traction (other
users upvote it, or it becomes a blocker for multiple customers),
it moves up.

**You can speed this up:**
- Upvote the GitHub issue
- Share your use case in the discussion thread
- If you're an Enterprise customer, this qualifies for a custom
  report template (see your plan benefits)

I can't commit to a timeline, but I promise it's been heard.

{builder_name}
```

### 4.8 "I Found a Bug" Response

```
Subject: Re: Bug Report — {summary}

Hi {name},

Thanks for reporting this. Here's what we know so far:

**Bug:** {summary}
**Confirmed:** {Yes/No/Investigating}
**Workaround:** {workaround if available}
**Target fix:** {version number or "Next release"}

To help me investigate, could you please share:
- CertifyAI version: certifyai --version
- Python version: python3 --version
- OS: {Linux/macOS/Windows}
- Steps to reproduce (exact commands, not description)
- Full error output (paste is fine, screenshot is okay if text is
  not possible)
- Any custom configuration (sanitize API keys before sharing)

Bug tracker: https://github.com/certifyai/certifyai/issues/{issue_number}

**What to expect:**
1. I'll confirm the bug and add it to the tracker
2. You'll get notified when a fix is released
3. If it's a critical bug (crash, data loss, security), expect a
   patch release within 72h. For minor bugs, it'll go in the next
   regular release.

Thank you for helping make CertifyAI better. Your bug report
improves the product for everyone.

{builder_name}
```

### 4.9 OOO / Delay Auto-Response

```
Subject: Re: {ticket_subject} — Acknowledged (Response Delayed)

Hi {name},

Your message has been received and is important to us.

I'm currently away from the office {or: experiencing higher-than-normal
volume}. I'll respond to your ticket by {expected_response_date}.

**While you wait:**
- Quickstart guide: https://certifyai.dev/docs/quickstart
- Troubleshooting: https://certifyai.dev/docs/troubleshooting
- Known issues: https://github.com/certifyai/certifyai/issues

If this is a critical issue (can't install or run the product),
and you haven't heard back within 48h, please reply with "URGENT"
in the subject line.

Thank you for your patience.

{builder_name}
```

### 4.10 Post-Resolution Check-In (Enterprise Only)

```
Subject: Checking in — Did {summary} resolve your issue?

Hi {name},

It's been a few days since we last corresponded about {summary}.
I wanted to check — did the solution work for you?

If everything's good: No need to reply. Consider this closed.

If you're still stuck: Reply with what's happening and I'll take
another look.

If something else came up: Feel free to start a new thread.

Your feedback helps me improve the product. If you have a moment,
I'd appreciate knowing what almost made you give up on CertifyAI
before reaching out — I want to fix that friction point.

{builder_name}
```

---

## 5. Self-Service Architecture

Self-service is the most important "feature" of the support system. Every support interaction that could have been avoided by better docs is a failure of product design, not customer diligence.

### 5.1 Must-Build Documentation (Pre-Launch)

| Document | Priority | What It Covers | Deflects What % of Tickets? |
|----------|----------|----------------|---------------------------|
| Quickstart Guide | P0 | Install → configure → first report in 5 steps | 30% |
| Provider Configuration | P0 | OpenAI, Azure, Anthropic, Ollama, Google, custom endpoints | 25% |
| Troubleshooting Guide | P0 | Top 15 errors with exact fix commands | 20% |
| Known Issues Page | P0 | Active bugs, platform quirks, LiteLLM compatibility | 10% |
| Framework Interpretation Guide | P1 | How to read results, what passed/failed means for each framework | 5% |
| FAQ | P1 | 20 most common questions with one-paragraph answers | 5% |
| Video Walkthrough (3-5 min) | P1 | "Watch me install, configure, and run CertifyAI" | 2% |
| Security & Privacy FAQ | P1 | Where keys are stored, telemetry, air-gap capabilities | 2% |
| Refund Policy | P1 | 14-day policy, how to request | 1% |

**Target: 90% of support tickets deflected by self-service.**

### 5.2 Error Message Design (In-Product)

Every error message in CertifyAI should answer three questions:
1. **What happened?** (one sentence, plain English)
2. **Why did it happen?** (the most likely cause)
3. **What do I do now?** (the exact command or config change)

**Example (good):**

```
Error: Could not connect to OpenAI API.
Why: Your API key in ~/.certifyai/config.toml may be invalid,
or your OpenAI account has no active billing.
Fix: Run `certifyai init` to reconfigure your provider, or
visit https://platform.openai.com/account/billing to check your
account status.
Docs: https://certifyai.dev/docs/providers/openai
```

**Example (bad — what we're avoiding):**

```
Error: HTTP 401
Traceback (most recent call last):
...
```

### 5.3 In-App Help Commands

```
certifyai help                 # General help
certifyai help providers       # Provider-specific help
certifyai help attacks         # Attack scenario documentation
certifyai help compliance      # Framework mapping documentation
certifyai help troubleshooting # Common issues
certifyai help vault           # Evidence vault documentation
```

### 5.4 Proactive Self-Service Prompts

When an error is detected, the CLI should prompt:

```
It looks like you're having trouble with {specific_error}.
Would you like to:
1. Open the troubleshooting guide (browser)
2. Run the diagnostic tool: certifyai doctor
3. Contact support (Pro/Enterprise only)
```

The `certifyai doctor` command is a diagnostic tool that:
- Checks Python version compatibility
- Verifies SQLite write permissions
- Tests API key validity (no cost, just a ping)
- Reports disk space for evidence vault
- Outputs a shareable diagnostic ID for support

---

## 6. Escalation Path (Solo Dev Edition)

### 6.1 The Reality

There is no Level 1 / Level 2 / Level 3. There is only the builder. Escalation does not mean "escalate to someone more senior." It means:
- **Bug escalation:** From "I help you debug" to "I fix the code"
- **Security escalation:** From "public issue" to "encrypted channel"
- **Feature escalation:** From "I acknowledge" to "I build it"

### 6.2 Escalation Flow

```
                     ┌──────────────────┐
                     │  Customer Issue  │
                     └────────┬─────────┘
                              │
                     ┌────────▼─────────┐
                     │   Triage (Self)  │
                     │  ─────────────── │
                     │ • Config issue?  │──→ Fix in email (5-15 min)
                     │ • Bug?           │──→ Create GitHub issue
                     │ • Feature req?   │──→ Create GitHub issue + template
                     │ • Security?      │──→ Encrypted channel
                     │ • Refund?        │──→ Process immediately
                     └──────────────────┘
```

### 6.3 Bug Path

1. Customer reports bug (email or GitHub)
2. Builder confirms bug (reproduce locally with their config or generic setup)
3. GitHub issue created with `bug` label, severity, and workaround (if any)
4. Customer subscribed to issue for updates
5. Fix delivered in next release (critical: patch release within 72h; normal: next regular release)
6. Customer notified via GitHub + email

### 6.4 Security Vulnerability Path

| Step | Action | SLA |
|------|--------|-----|
| 1 | Reporter sends encrypted email (GPG key published at certifyai.dev/.well-known/gpg.asc) | N/A |
| 2 | Builder acknowledges receipt | 72h |
| 3 | Builder triages severity (Critical/High/Medium/Low) | 7 days |
| 4 | Builder develops fix | Critical: 7 days. High: 14 days. Medium: next release. Low: next release. |
| 5 | Builder releases patch with security advisory | 14 days from triage (coordinated disclosure) |
| 6 | Builder publishes CVE (if applicable) | Within 30 days of patch |

**Responsible disclosure policy:** Public disclosure before a patch is available will result in removal from the security notification list. We commit to fixing confirmed vulnerabilities within 14 days of triage for Critical/High severity.

**What constitutes a security issue:**
- Remote code execution in the processing of attack results
- SHA-256 hash chain collision or bypass
- Exposure of API keys from config.toml or SQLite
- Cross-site scripting in the Web Dashboard
- Dependency with known CVE >7.5 CVSS

**What does NOT constitute a security issue:**
- The tool failing to protect the user from their own API provider (we test compliance, we don't secure OpenAI)
- SQL injection in the CLI (not exposed to network)
- Weak encryption in evidence vault (it's SHA-256, not encryption — by design, evidence is tamper-proof, not secret)

### 6.5 No Further Escalation

There is no one above the builder. If the builder is unavailable (sick, emergency, sabbatical), the auto-responder explains the situation and sets expectations. There is no backup. This is explicitly communicated in the product's README and support page.

---

## 7. Refund Handling

### 7.1 Policy

**14-day, no-questions-asked refund on Pro and Enterprise purchases.**

- Counted from purchase timestamp (Gumroad provides this)
- After 14 days: no refunds (the product works as advertised)
- Exception: If a critical bug makes the product unusable and remains unfixed for 30+ days, a refund is offered even beyond 14 days
- Free tier: no refunds (nothing was purchased)

### 7.2 Refund Process

1. Customer requests refund (email or Gumroad message)
2. Builder processes immediately — NO troubleshooting, NO persuasion, NO "are you sure?"
3. Refund issued via Gumroad (instant for Stripe payments, 5-10 business days for PayPal)
4. License key deactivated
5. Template email sent (see Section 4.6)
6. Refund reason tracked (if customer provides it)

**Important rule:** Never try to convince a customer to stay. A customer who needs convincing will be a net-negative support drain. Process the refund cheerfully and move on.

### 7.3 Refund Tracking

Track each refund with these fields (simple Google Sheet or Airtable):

| Field | Description | Example |
|-------|-------------|---------|
| Date | Refund date | 2026-08-15 |
| Tier | Pro or Enterprise | Pro |
| Days since purchase | How long they had it | 3 days |
| Reason (if provided) | Customer's stated reason | "Decided to build in-house" |
| Refund category | Categorize for trends | Competitive loss / Feature gap / Config difficulty |
| Preventable? | Could this have been avoided? | Yes — failed to configure Azure provider |
| Action item | What to improve | Improve Azure setup wizard |

### 7.4 Refund Categories (for Trend Analysis)

| Category | Example | Action if Trending |
|----------|---------|-------------------|
| Configuration difficulty | "Couldn't set up my provider" | Improve `certifyai init` wizard + provider docs |
| Feature gap | "No Gemini support" | Prioritize in roadmap |
| Competitive loss | "Using [competitor] instead" | Investigate competitor features |
| Budget | "Can't justify the expense" | Nothing (not a product problem) |
| No need | "Don't need compliance testing" | Improve marketing targeting |
| Technical issue | "Crashes on my system" | Fix the bug, improve compatibility |
| Unsupported use case | "Needs multi-user support" | Acknowledge, defer to v2 |
| Silent | No reason given | N/A |

Target: Refund rate < 10% of Pro sales, < 5% of Enterprise sales.

---

## 8. Feedback Loop

### 8.1 Tagging System

Every support ticket should be tagged on close (three tags max):

```
[Category]     [Severity]    [Preventable?]
───────────    ──────────    ──────────────
config         critical      yes | no | maybe
bug            normal
feature-req    low
install
provider
report
security
refund
docs
other
```

Tags are stored in the support tool (see Section 11). Monthly, these are reviewed.

### 8.2 Monthly Review (20 Minutes, Calendar-Blocked)

The builder spends 20 minutes per month reviewing:

1. **Refund reasons** — Any patterns? Is a specific provider causing issues?
2. **Most common ticket category** — Is there a doc that should exist?
3. **SLA misses** — How many? Why? Should SLAs be adjusted?
4. **Feature request volume** — Any request appearing 3+ times?
5. **Self-service deflection rate** — Are people using the docs?

**Format:** Open support tool → Export last 30 days of tickets → Read top 3 trends → Update roadmap or docs → Done.

### 8.3 Feedback → Product Pipeline

```
                     ┌──────────────────┐
                     │  Support Ticket  │
                     └────────┬─────────┘
                              │
                     ┌────────▼─────────┐
                     │  Tag & Categorize │
                     └────────┬─────────┘
                              │
              ┌───────────────┼───────────────┐
              │               │               │
     ┌────────▼────┐  ┌──────▼──────┐  ┌─────▼─────┐
     │   Bug fix   │  │ Doc update  │  │ Roadmap   │
     │ (PR #)      │  │ (PR to docs)│  │ (v2 idea) │
     └─────────────┘  └─────────────┘  └───────────┘
```

- **Bug tickets** → GitHub issue → Fix in next release
- **Config difficulty tickets** → Doc update or improved error message
- **Feature requests** → GitHub issue → Roadmap prioritization
- **Repeated questions** → FAQ entry or quickstart improvement

### 8.4 Feedback Sources (Beyond Support)

| Source | Review Cadence | Tool |
|--------|---------------|------|
| Support emails | Monthly (20min) | HelpScout / Plain |
| GitHub Issues | Weekly (10min) | GitHub |
| GitHub Discussions | Weekly (10min) | GitHub |
| Gumroad reviews | Monthly (5min) | Gumroad |
| PyPI comments | Monthly (5min) | PyPI |
| Twitter mentions | Weekly (5min) | N/A (manual search) |

### 8.5 Customer Success Signals (Enterprise Only)

For Enterprise customers ($499), add a 30-day check-in email:

```
Subject: How's CertifyAI working for your team?

Hi {name},

It's been 30 days since your Enterprise purchase. I wanted to check:
Is CertifyAI helping you prepare for your compliance audit?

Quick 30-second feedback:
[👍] Yes, on track
[🤷] Still setting up
[👎] Stuck on {dropdown: installation / configuration / report interpretation / other}

Anything I can help with?
```

This serves dual purpose: support deflection and churn prevention.

---

## 9. Hours & Boundaries

### 9.1 Published Support Hours

```
Days:    Monday — Friday
Hours:   10:00 — 18:00 IST (UTC+5:30)
         (Obligatory: 4h/day minimum on support)
         (Best-effort: emails read and triaged outside these hours)

Converted:
  US East:   12:30 AM — 8:30 AM ET
  US West:   9:30 PM — 5:30 AM PT (previous day)
  Europe:    5:30 AM — 1:30 PM CET
  UK:        4:30 AM — 12:30 PM GMT
  Australia: 3:30 PM — 11:30 PM AEDT
```

**Published on:** certifyai.dev/support (linked from README, purchase confirmation, and email signature)

### 9.2 Response Expectations

- **During hours:** Fast replies (within a few hours, often within minutes)
- **Outside hours:** "Best effort." Auto-reply set: "Thanks for your message. I'll respond during support hours ({hours}). For urgent issues, reply with URGENT in the subject line."
- **Weekends:** No support unless it's a critical security fix. Auto-reply: "I'm offline for the weekend. I'll respond on Monday. If this is a security issue, please encrypt your email and include [SECURITY] in the subject."
- **Holidays:** Pre-published list of Indian public holidays when support is suspended. No backup coverage.

### 9.3 Holiday Calendar (Published)

```
Jan 26 — Republic Day
Mar 25 — Holi
Apr 14 — Good Friday (observed)
Apr 18 — Ambedkar Jayanti
Aug 15 — Independence Day
Sep/Oct — Dussehra (date varies)
Oct/Nov — Diwali (3 days: 2 before + 1 after)
Nov — Guru Nanak Jayanti
Dec 25 — Christmas

Total: ~10 support holidays per year
```

### 9.4 Out-of-Office Protocol

- **Planned absence:** Publish on certifyai.dev/status at least 7 days in advance. Set auto-responder. Notify Enterprise customers via email.
- **Sick days:** Set auto-responder with expected recovery date (or "as soon as possible"). Enterprise customers notified via email.
- **Emergency (1-3 days):** Auto-responder only. No proactive notifications.
- **Extended emergency (3+ days):** Pause all non-critical support. Auto-responder explains situation. On return: 72h grace period — all SLAs double.
- **Sabbatical/break (1-2 weeks):** Publish 30 days in advance. Auto-responder with clear return date. No support during this period.

### 9.5 Why These Boundaries Matter

Solo dev burnout is the #1 killer of indie products. Boundaries are not laziness — they are sustainability. Every hour spent on support is an hour NOT spent on:
- Building features that reduce future support needs
- Marketing to acquire new customers
- Resting and maintaining cognitive ability

**Rule of thumb:** Support should consume no more than 20% of the builder's working time. If support exceeds 25%, either raise prices or improve self-service.

---

## 10. Proactive Monitoring

CertifyAI is self-hosted — there is no server infrastructure to monitor. However, there are several signals that indicate product health and customer sentiment.

### 10.1 What to Monitor

| Signal | Tool | Cadence | Why It Matters |
|--------|------|---------|----------------|
| PyPI downloads | pepy.tech / PyPI Stats API | Weekly | Adoption growth, sudden drop = issue |
| Gumroad sales | Gumroad dashboard | Weekly | Revenue. Sudden drop = investigate |
| Gumroad refunds | Gumroad dashboard | Weekly | Refund rate > 10% = product issue |
| GitHub Issues (new) | GitHub | Daily | Bug reports, feature requests |
| GitHub Discussions (new) | GitHub | Every 2 days | Community questions, sentiment |
| Support email volume | HelpScout / Plain | Weekly | Spike = launch issue or documentation gap |
| Support email sentiment | Manual skim | Weekly | Are people frustrated or satisfied? |
| SSL cert (certifyai.dev) | UptimeRobot (free) | Monthly | Low effort, high impact if down |
| Custom domain (docs) | Manual check | Monthly | Ensure docs site is accessible |

### 10.2 Monitoring Actions

| Signal | Normal Range | Action if Outside Range |
|--------|-------------|------------------------|
| PyPI downloads | 50-200/week | If < 50: increase marketing. If > 200 unexpectedly: check for issue. |
| Gumroad sales | 5-10/week | If < 3: investigate. If > 15: capacity check (can I handle support?). |
| Refund rate | <10% | If > 10%: deep-dive into refund reasons. Pause marketing until fixed. |
| Support volume | <20 tickets/week | If > 30: triage bottleneck. Is there a common issue? Push fix/docs. |
| Negative sentiment | <2 tickets/week negative | If > 5 negative: product quality issue. Prioritize fix. |

### 10.3 Automated Alerts

- **GitHub watch:** Email notifications for new issues and discussions
- **Gumroad notifications:** Email for each sale (switch to daily digest if volume exceeds 5/day)
- **PyPI RSS:** Weekly manual check (no need for real-time)
- **No monitoring PagerDuty/OpsGenie needed** — there are no servers to page

### 10.4 What NOT to Monitor

- **Customer's installation health** — impossible, self-hosted
- **Customer's evidence vault** — impossible, self-hosted
- **Model uptime** — customer's responsibility
- **Real-time support queue** — would create anxiety without actionability

---

## 11. Tools & Stack

### 11.1 Recommended Tools (Solo-Dev Budget)

| Tool | Purpose | Cost | Why |
|------|---------|------|-----|
| **HelpScout** | Shared inbox (or Plain.com) | Free tier / $25/mo for Plain | Clean UI, canned responses, mailbox per tier |
| **GitHub** | Issues, Discussions, Projects | Free | Already using it for code |
| **Gumroad** | Payments, license keys, refunds | 8.5% + $0.30 per sale | Already using it for sales |
| **Loom** | Video responses | Free tier | 5-min video answer replaces 3 email back-and-forths |
| **Calendly** (optional) | Enterprise config calls | Free tier | Limited to 30-min slots, 1/week max |
| **Simple Google Sheet** | Refund tracking, ticket tagging | Free | Low ceremony, easy to export |
| **certifyai.dev/status** | Status page | Free (GitHub Pages) | HTML page, updated manually |

### 11.2 Setup Guide

1. **Set up support@certifyai.dev** → forward to HelpScout/Plain
2. **Create mailboxes:** `pro@` and `enterprise@` (or use tags) — Pro and Enterprise get different SLAs
3. **Create canned responses** for all 10 templates in Section 4
4. **Set up auto-responders** for off-hours, weekends, holidays
5. **Publish support page** at certifyai.dev/support with:
   - Hours, SLAs, tiers
   - Link to docs
   - Link to GitHub Issues/Discussions
   - GPG key for security reports
   - Holiday calendar
6. **Set up `certifyai doctor`** diagnostic command in the CLI
7. **Add error message framework** to all CLI error output (see Section 5.2)

### 11.3 Anti-Patterns to Avoid

- ❌ **Slack community:** Creates expectation of real-time support. Exhausting. Expensive. Avoid until v2 at minimum.
- ❌ **Discord server:** Same problem as Slack. Community becomes a de facto support channel with no boundaries.
- ❌ **Phone number:** Never publish a phone number. Not even for Enterprise.
- ❌ **"Support" as a feature:** Don't compete on support quality. Compete on product quality. Support is a safety net, not a selling point.
- ❌ **24/7 SLAs:** Impossible for solo dev. Don't promise what you can't deliver.

---

## 12. Appendix: Quick-Reference Cheat Sheet

### Ticket Triage Decision Tree

```
New ticket arrives
│
├─ Contains "refund" or "cancel"?
│   └─ Yes → Process immediately. No questions. Template 4.6.
│
├─ Contains security report or [SECURITY]?
│   └─ Yes → Acknowledge within 24h. Move to encrypted email.
│
├─ Free tier user?
│   └─ Yes → Auto-reply: "Please use GitHub Issues (bugs) or
│             Discussions (questions). Support is for Pro/Enterprise
│             customers only. Upgrade at certifyai.dev/pricing."
│
├─ Enterprise user?
│   └─ Yes → Priority queue. 24h SLA. Personal response.
│
├─ Pro user?
│   └─ Yes → Standard queue. 48h SLA. Template as needed.
│
└─ Unknown?
    └─ Check Gumroad. If paid, update their record. If not paid,
        redirect to free tier support path.
```

### Severity Quick-Assign

| Symptom | Severity | Response |
|---------|----------|----------|
| `pip install` fails with error | Critical | Investigate + workaround within 24h |
| CLI crashes on `init` or `run` | Critical | Log GH issue + patch or workaround within 24h |
| SQLite "malformed" error | Critical | Recovery steps + fix within 24h |
| API key configuration question | Normal | Template 4.3 |
| Report interpretation question | Normal | Template 4.5 |
| Feature request | Low | Template 4.7 |
| Typo in documentation | Low | Fix within 1 week |
| Security vulnerability | Security | GPG → acknowledge within 72h |

### Daily Support Workflow (Target: 30 min/day)

```
1. Check inbox (HelpScout/Plain)               5 min
2. Respond to new urgent tickets (if any)      10 min
3. Respond to existing threads                  10 min
4. Check GitHub Issues (new + comments)         5 min
5. Close loop (tag tickets, update sheet)       0-5 min
                                                ─────
                                                Total: ~30 min
```

### Weekly Support Review (Target: 15 min/week)

```
1. Review new GitHub Discussions               5 min
2. Check Gumroad refund rate                   2 min
3. Check PyPI download trend                   2 min
4. Update known issues page if needed          3 min
5. Update FAQ if needed                         3 min
                                                ─────
                                                Total: ~15 min
```

### Monthly Support Review (Target: 20 min/month)

```
1. Export last 30 days of tickets              2 min
2. Tag/categorize trends                       5 min
3. Check refund reasons                         3 min
4. Update roadmap priorities (1-2 items)        5 min
5. Write doc update if needed                   5 min
                                                ─────
                                                Total: ~20 min
```
