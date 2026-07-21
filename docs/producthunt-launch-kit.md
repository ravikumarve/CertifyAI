# CertifyAI — Product Hunt Launch Kit

**Prepared by:** Growth Hacker (The Agency)
**Date:** July 21, 2026
**Target Launch:** Week 9-10 of build (CLI + TUI working, post-Closed Beta)
**Category:** Developer Tools / Compliance (select both if PH allows multi-category)
**Launch Day:** Tuesday or Wednesday (highest visibility for dev tools)

---

## Table of Contents

1. [Product Hunt Listing](#1-product-hunt-listing)
2. [Target Makers & Influencers](#2-target-makers--influencers)
3. [Visual Assets Spec](#3-visual-assets-spec)
4. [Launch Day Schedule](#4-launch-day-schedule)
5. [Support Mobilization](#5-support-mobilization)
6. [Comment Engagement Strategy](#6-comment-engagement-strategy)
7. [Cross-Promotion Plan](#7-cross-promotion-plan)
8. [Post-Launch Follow-up](#8-post-launch-follow-up)
9. [Success Metrics](#9-success-metrics)

---

## 1. Product Hunt Listing

### Tagline (60 char max)

```
Self-hosted AI compliance testing for EU AI Act, SOC 2 & NIST
```

**Backup:** `Test your LLMs for jailbreak, PII leakage & bias. Self-hosted. $149.`

### Short Description (260 char max)

```
CertifyAI is a downloadable CLI + TUI that tests LLMs against 30+ attack scenarios, maps results to EU AI Act/SOC 2/NIST AI RMF, and generates auditor-ready PDF reports with a crypto-verified evidence chain. Bring your own API key. No subscription. Works air-gapped with Ollama.
```

### Full Description (3 paragraphs)

**Paragraph 1 — Hook:**

> Every company deploying LLMs faces a ticking clock. The EU AI Act's high-risk deadline is December 2027 (fines up to €35M or 7% global revenue). SOC 2 auditors now ask: "How do you test your AI for PII leakage, jailbreak, or hallucination?" And NIST AI RMF requires continuous measurement — not a one-time pentest.
>
> The problem? Existing tools are either enterprise SaaS platforms costing $10K–$150K/year (Vanta, Credo AI, Drata) that cannot actually test LLM runtime behavior, or fragmented open-source components (Garak, Guardrails AI, Rebuff) that require weeks of engineering to stitch together.
>
> **CertifyAI is neither. It's a downloadable compliance engine that runs on your machine. $149. No subscription. Ready in 10 minutes.**

**Paragraph 2 — How it works:**

> Install with `pip install certifyai`. Run `certifyai init` to configure your LLM provider (OpenAI, Anthropic, Azure, Ollama, Gemini, or any of 100+ via LiteLLM). Run `certifyai run` to execute 30 attack scenarios across 6 categories: prompt injection, jailbreak, PII leakage, policy violation, hallucination, and bias.
>
> Every result is logged to an append-only evidence vault with SHA-256 hash chaining — cryptographic proof that no evidence was tampered with. Run `certifyai vault --verify` to prove integrity. Generate compliance reports mapped to EU AI Act articles, SOC 2 Common Criteria, NIST AI RMF categories, and ISO 42001 controls. Export as PDF, SARIF, or JSON.
>
> Works fully air-gapped with local models (Ollama). No data leaves your machine. The Pro tier ($149 one-time) adds the Web Dashboard, PDF reports, and full compliance framework mapping. The Enterprise tier ($499) adds white-label branding, source access, and commercial license.

**Paragraph 3 — Why now:**

> We built CertifyAI because we watched 78% of organizations scramble for EU AI Act readiness with no affordable tooling. The incumbents are SaaS platforms priced at $30K+/year that can't tell you if your AI is actually dangerous — they only monitor your S3 buckets and IAM roles. The open-source alternatives require 4-8 weeks of engineering to assemble, and they lack the compliance mapping and evidence integrity that auditors demand.
>
> CertifyAI is our answer: a developer-first, self-hosted boilerplate that turns a terminal into a compliance engine. It's the tool we wish existed when our own startup was preparing for SOC 2 Type II.
>
> Free tier available on PyPI (10 attack scenarios, JSON reports). Pro at $149 on Gumroad. Enterprise at $499. No recurring fees. No vendor lock-in. Your evidence, your machine, your compliance.

### First Comment (for PH community)

Post this immediately after the listing goes live:

> Hey Product Hunt! 👋
>
> I built CertifyAI because I was staring down an SOC 2 Type II audit and realized: every compliance tool costs $10K+/year and none of them can actually test an LLM for PII leakage or jailbreak.
>
> **Here's what makes it different:**
> - **Self-hosted, not SaaS** — runs on your machine, no data leaves, no subscription
> - **Crypto-verified evidence** — every attack result is SHA-256 chained to the previous one (auditors love this)
> - **10-minute setup** — `pip install certifyai` → `certifyai init` → `certifyai run` → PDF report
> - **Works with any LLM** — OpenAI, Anthropic, Ollama, Azure, Gemini, 100+ via LiteLLM
> - **Air-gapped capable** — works fully offline with local models
> - **$149 one-time** — not $30K/year
>
> **Free tier** available now: 10 attack scenarios, JSON reports, full evidence vault.
> **Pro tier** ($149): 30 attacks, PDF reports, Web Dashboard, EU AI Act + SOC 2 + NIST AI RMF + ISO 42001 mapping.
>
> Would love your feedback — especially from fellow devs who've been through compliance audits and know how painful this is. What attack scenarios should we add next? What compliance frameworks do you need?
>
> Happy to answer any questions in the comments!

---

## 2. Target Makers & Influencers

### Tier 1: High-Priority Makers (Must Reach Pre-Launch)

| Maker | Handle | Why They'd Care | Pre-Launch Approach |
|-------|--------|----------------|---------------------|
| **Chris Messina** | @chrismessina | Invented the hashtag, prolific PH maker, loves category-creating dev tools | DM: "Category-creating dev tool launching soon — self-hosted AI compliance. Would love your early take." |
| **Michael Seibel** | @michaelseibel | YC CEO, startup compliance is his world | Tag in pre-launch tweet. YC startups need SOC 2 — CertifyAI solves it cheaply. |
| **Sarah Guo** | @saranormous | AI investor at Conviction, deeply interested in AI safety/governance | Email: "Your essay on AI regulation resonated. We built the tool startups need." |
| **Logan Kilpatrick** | @official_logan | AI developer relations (ex-OpenAI, now Google), massive dev audience | DM: "We built a CLI that tests LLM compliance across providers — think you'd dig it." |
| **Sahil Lavingia** | @shl | Gumroad CEO = boilerplate royalty. Knows the $149 business model intimately. | DM: "Gumroad boilerplate launching soon — AI compliance CLI. Would love your blessing." |
| **Pieter Levels** | @levelsio | Solo dev icon, builds everything himself, hates SaaS subscriptions | DM: "Built a self-hosted AI compliance tool. $149 one-time, no sub. Your kind of product." |

### Tier 2: Developer Tools Makers

| Maker | Handle | Why They'd Care | Pre-Launch Approach |
|-------|--------|----------------|---------------------|
| **Guillermo Rauch** | @rauchg | Vercel CEO — dev tools ecosystem. If he retweets, the dev community sees it. | DM: "Dev tool launching on PH soon — self-hosted AI compliance. Would mean a lot if you checked it out." |
| **David Heinemeier Hansson (DHH)** | @dhh | HEY.com, Ruby on Rails. Hates SaaS pricing. Self-hosted advocate. | DM: "Self-hosted compliance tool. One-time payment. No recurring fees. Made for people who hate SaaS." |
| **Alexey Aylarov** | @alexey | founder of Motion (PH #1), knows what makes a winning launch | DM: "Motion-level dev tool launch strategy — would appreciate your insight on positioning." |
| **Ben Tossell** | @bentossell | Makerlog founder, PH power user, launching dev tools for years | DM: "Launching a CLI dev tool on PH next month — any tips from your experience?" |
| **Raman Khanna** | @ramank | Founder of Pory.io, writes about PH launches, consults on them | DM: "Would you be open to reviewing our PH assets before launch? Happy to compensate." |

### Tier 3: AI/ML Community Influencers

| Maker | Handle | Why They'd Care | Pre-Launch Approach |
|-------|--------|----------------|---------------------|
| **Andrew Ng** | @andrewng | DeepLearning.AI — his endorsement is the gold standard | Tag in pre-launch thread. CertifyAI addresses his AI safety concerns pragmatically. |
| **Yann LeCun** | @ylecun | Meta AI chief — cares about bias/testing methodology | Reply to his threads about AI safety with a genuine question + mention of CertifyAI |
| **Sasha Luccioni** | @sashaluccioni | AI ethics researcher at Hugging Face, works on bias/impact | DM: "Built a bias testing module for LLMs. Would love your feedback on our methodology." |
| **Simon Willison** | @simonw | Creator of Datasette, massive CLI/developer tool audience. Loves self-hosted tools. | DM: "Building a CLI compliance tool for LLMs. Uses SQLite + Click — your ecosystem. Want early access?" |

### Pre-Launch Outreach Sequence

**T-14 days:** Send DM/email to all Tier 1 makers with a personalized note + early access link (free Pro license). No ask — just "would love your thoughts."

**T-7 days:** Follow up with Tier 2. Include a 30-second demo GIF.

**T-3 days:** Ask Tier 1 contacts if they'd be willing to upvote and/or comment on launch day. Make it easy: "Here's a link to the PH page. If you like it, an upvote would mean the world. No pressure either way."

**T-1 day:** DM everyone on the list with the PH link + specific time window.

**Launch day:** Tag everyone who said yes. Reply to their comments within 15 minutes.

### Maker Outreach Templates

**DM Template (Tier 1 — Personalized):**

> Hey {name},
>
> I'm a solo developer launching a tool I think you'll resonate with.
>
> CertifyAI is a self-hosted CLI that tests LLMs for compliance (EU AI Act, SOC 2). It's like Vanta/Credo AI but:
> - Runs on your machine (no SaaS)
> - $149 one-time (not $30K/year)
> - Tests actual LLM behavior (injection, PII, jailbreak, bias)
>
> The category doesn't really exist yet — downloadable AI compliance. I'd love your take on the positioning.
>
> Early access here (free Pro license): {gumroad_link}
>
> No pressure — just genuinely value your opinion.

**DM Template (Tier 3 — AI Community):**

> Hey {name},
>
> Love your work on {specific thing they do}. I'm building a tool in a related space.
>
> CertifyAI is a CLI that runs 30 attack scenarios against LLMs and maps results to compliance frameworks (EU AI Act, NIST AI RMF). Open-source-ish (free tier on PyPI).
>
> Question for you: our {bias/hallucination} testing methodology currently {approach}. Would love your input on whether this is defensible for auditor submission.
>
> Early access here if you want to poke around: {link}

---

## 3. Visual Assets Spec

### Thumbnail / Hero Image (1200×628px — Open Graph standard)

**Design brief:**
- Dark background (terminal aesthetic — #0a0a0f or VS Code dark theme)
- Terminal window in center with `certifyai run` output showing colored pass/fail results
- Floating badges: "EU AI Act ✓", "SOC 2 ✓", "NIST AI RMF ✓" in top-right
- Tagline overlay: "Self-Hosted AI Compliance. $149."
- Green checkmark + red X indicators from the terminal output
- Font: JetBrains Mono for terminal text, Inter for tagline
- **DO NOT**: generic robot/gears/clipboard icons. Real terminal output.

**Tool suggestions:** Figma (template), Canva (quick), Carbon.sh (for terminal screenshots)

### Screenshots Required (5-7 images)

1. **`screenshot-01-hero-terminal.png`** — Full terminal window showing `certifyai run` in progress with Rich progress bars. 6 categories streaming with pass/fail per attack. Caption: "30 attack scenarios execute against your LLM in 2-5 minutes. Each result logged with SHA-256 evidence hash."

2. **`screenshot-02-evidence-vault.png`** — `certifyai vault --verify` output showing hash chain integrity. Green "All entries verified" banner. Caption: "Cryptographic evidence chain. No tampering possible. Auditors love this."

3. **`screenshot-03-pdf-report.png`** — PDF report cover page + one sample page showing attack result + framework mapping. Caption: "Auditor-ready PDF reports. Mapped to EU AI Act articles, SOC 2 CC controls, and NIST AI RMF categories."

4. **`screenshot-04-tui-dashboard.png`** — Textual TUI dashboard showing overall pass/fail metrics, recent runs, and compliance scores. Caption: "Full terminal UI for browsing results, comparing runs, and verifying evidence — all without leaving the terminal."

5. **`screenshot-05-web-dashboard.png`** — Next.js Web Dashboard showing run history table or compliance overview page. Caption: "Optional Web Dashboard for GUI access to the same data. No API server — reads SQLite directly."

6. **`screenshot-06-quick-setup.png`** — `certifyai init` wizard. 3-step config: provider selection, model name, API key. Caption: "Interactive setup wizard. 60 seconds to first attack run."

7. **`screenshot-07-multi-provider.png`** — Command showing `certifyai run --provider openai --model gpt-4o` alongside a note about Ollama/anthropic/azure support. Caption: "Works with 100+ LLM providers via LiteLLM. Bring your own key. No vendor lock-in."

### GIF / Video Specifications

**Main Demo GIF (max 30 seconds, <5MB for PH upload):**

| Frame | Time | Content |
|-------|------|---------|
| 1 | 0-3s | `pip install certifyai` completes (speed up to 2x) |
| 2 | 3-6s | `certifyai init` — type provider, paste key, hit enter |
| 3 | 6-18s | `certifyai run` — progress bars fill, attacks complete (speed to show 3-4 completing) |
| 4 | 18-22s | `certifyai vault --verify` — green verification output |
| 5 | 22-27s | `certifyai report --format pdf` — file path output |
| 6 | 27-30s | Quick preview of PDF report opening + Zoom out to show Web Dashboard |

**GIF tooling:** vhs (https://github.com/charmbracelet/vhs) — scriptable terminal recording. Write a `.tape` file that types the commands automatically. Produces clean, consistent GIFs.

**VHS .tape file template:**

```tape
Output: certifyai-demo.gif
Set FontSize 14
Set Theme "Dracula"
Set Width 800
Set Height 600
Set Padding 12

Type "pip install certifyai" Sleep 500ms Enter Sleep 3s
# Install output
Type "certifyai init" Sleep 300ms Enter Sleep 1s
Type "openai" Enter Sleep 500ms
Type "gpt-4o" Enter Sleep 500ms
Type "sk-..." Sleep 2s Enter
Type "y" Sleep 1s Enter
Type "certifyai run" Sleep 500ms Enter
Sleep 8s
# Run completes
Type "certifyai vault --verify" Sleep 300ms Enter Sleep 2s
Type "certifyai report --format pdf" Sleep 300ms Enter Sleep 2s
```

**Backup GIF options:** Terminal.sx, Asciinema (convert to GIF via agg), or screen recording with Kap (macOS) cleaned up in GIPHY Capture.

### Product Hunt Gallery Requirements

| Asset | Count | Format | Dimensions | Max Size |
|-------|-------|--------|------------|----------|
| Thumbnail/Hero | 1 | PNG/JPG | 1200×628 | 5MB |
| Screenshots | 5-7 | PNG | 1280×800 (or 16:10) | 5MB each |
| GIF | 1 | GIF | 800×600 or 16:10 | 5MB |
| Video (optional) | 0-1 | MP4 | 1920×1080 | 100MB |

---

## 4. Launch Day Schedule

### T-24 Hours (Monday 8:00 AM — Day Before Launch)

- [ ] **Final PH listing review:** Tagline, description, screenshots. Read everything out loud. Check for typos, unclear phrasing, missing call-to-action.
- [ ] **GIF verification:** Upload GIF to PH preview. Does it autoplay? Does it loop cleanly? Is it under 5MB?
- [ ] **Maker profile:** Ensure your PH maker profile is complete with bio, Twitter link, GitHub link.
- [ ] **Landing page:** certifyai.dev (or GitHub README if no landing page) — ensure it's polished. Test on mobile + desktop.
- [ ] **Gumroad links:** Test the purchase flow end-to-end. Buy a $1 test product to confirm checkout works.
- [ ] **PyPI package:** Run `pip install certifyai` in a clean environment. Confirm install works.
- [ ] **First comment draft:** Have the PH first comment ready in a text file. Proofread.
- [ ] **Social drafts:** Pre-write tweets for launch (+2h, +4h, +8h, +24h). Queue in a scheduler (Buffer/Hypefury) or just have them in a doc.
- [ ] **DM list final check:** Confirm maker DM list. Send final reminders: "PH launch tomorrow 6 AM PT. Link here. Would love your support."
- [ ] **Discord/community prep:** Post "launching tomorrow" in every community you're part of. Include time + link.
- [ ] **Backup everything:** Save PH draft as JSON (PH has a draft export feature). Screenshot every field.

### T-2 Hours (Tuesday 4:00 AM PT / 11:00 UTC)

- [ ] Wake up. Coffee. No alcohol.
- [ ] **Final asset check:** Refresh PH draft page. Confirm all images load. Confirm GIF plays.
- [ ] **Gumroad/purchase test:** Run another test purchase to confirm everything is live.
- [ ] **PyPI check:** `pip install certifyai` in a fresh venv. Confirm latest version is published.
- [ ] **Close all other apps.** No distractions. Focus mode.
- [ ] **Open PH dashboard** in a pinned tab. Open social media in another tab.
- [ ] **Set phone on Do Not Disturb** (except for maker DMs).

### T+0 (6:00 AM PT / 13:00 UTC — Launch)

- [ ] **Hit "Publish"** on Product Hunt.
- [ ] **Post first comment immediately** (the one you prepared in Section 1).
- [ ] **Update Twitter/X:** "We're live on Product Hunt! 🚀 CertifyAI — self-hosted AI compliance testing. Test your LLMs for injection, PII, jailbreak, bias. $149 one-time. No subscription. {link}"
  - Pin this tweet to your profile.
  - Tag PH (Product Hunt official account).
- [ ] **DM all Tier 1 makers** with the live link. Personal note.
- [ ] **Post in Discord communities** you're part of: "Hey team, we just launched on Product Hunt. If you're dealing with AI compliance, would love your support: {link}"
- [ ] **Enable PH notifications.** Reply to every comment within 10 minutes for the first 2 hours.

### T+2 Hours (8:00 AM PT — Engagement Push)

- [ ] **First comment engagement:** Reply to every comment so far. Thank the person. Answer their question. If they ask a tough question, answer honestly and say what you're doing about it.
  - Template: "Thanks {name}! Great question about {topic}. Here's how we handle it: {answer}. What's your use case — are you preparing for {SOC 2 / EU AI Act / internal audit}?"
- [ ] **Post a community update** as a new PH comment (not a reply — a top-level comment):
  - "Wow, the response has been incredible! We've already seen comments from {mention 2-3 specific interesting comments}. Here's what's coming next: CI/CD integration (most requested), custom attack SDK, and scheduled monitoring. What else would you like to see?"
- [ ] **Post on Reddit r/SaaS:** "We just launched a self-hosted AI compliance tool on PH. $149 one-time. Here's why we built it instead of paying Vanta $10K/yr."
- [ ] **Post on Reddit r/MachineLearning:** "We built a CLI that tests LLMs for injection/PII/jailbreak/bias and generates compliance reports. Free tier available on PyPI."
- [ ] **Post on Hacker News** (if you pre-wrote the Show HN — see Section 7):
  - Do NOT post at peak US time. Aim for 7:00 AM ET / 11:00 UTC for maximum HN front page time.

### T+4 Hours (10:00 AM PT — Social Push)

- [ ] **Second tweet:** Include a 30-second demo GIF. "See how CertifyAI works: `pip install certifyai` → `certifyai run` → auditor-ready PDF in 10 minutes. {gif} {link}"
  - Tag relevant makers who haven't replied yet. Ask a question to drive engagement.
- [ ] **LinkedIn post:** Longer form. 3 paragraphs (hook → how it works → why now). Tag relevant connections.
- [ ] **Dev.to cross-post** (see Section 7). Publish your "I built a free, self-hosted AI compliance checker" article. Link to PH.
- [ ] **Check PH rankings.** If you're in top 3, accelerate. If you're not in top 10, double down on DMs and community posts.
- [ ] **Monitor comments relentlessly.** Every 15 minutes. Reply instantly.

### T+8 Hours (2:00 PM PT — Update Post)

- [ ] **Post an update on PH** as a new top-level comment:
  - "Update at 8 hours: We hit {number} upvotes, {number} comments! 🎉 Here's what we're hearing from the community: {top 3 requests}. We're tracking everything. Keep the feedback coming!"
- [ ] **Third tweet:** Share a testimonial or interesting comment you received. "PH commenter {name} said: '{quote}'. This is exactly why we built CertifyAI. {link}"
- [ ] **GH stars:** Check GitHub repo stars. If they're climbing, tweet about it. "We hit {number} GitHub stars on launch day!"

### T+12 Hours (6:00 PM PT — Evening Push)

- [ ] **Post in relevant Slack/Discord communities:**
  - AI Safety Discord
  - DevOps Community
  - Startups Discord
  - Python Community
  - Your local developer community
- [ ] **DM anyone who hasn't replied yet** with a gentle nudge: "No pressure at all — just wanted to make sure you saw this. Would love your support if you think it's useful: {link}"
- [ ] **Monitor HN thread** if you posted there. Reply to every comment.

### T+24 Hours (6:00 AM PT — Next Day — Thanks Post)

- [ ] **Post a thank-you comment** on PH:
  - "24 hours later and we're blown away. {number} upvotes, {number} comments — thank you PH community! 🎉
  - Here's what we're shipping next based on your feedback: {3 things}
  - Special thanks to {tag 3-5 makers who supported}
  - CertifyAI is available now on PyPI (free) and Gumroad (Pro $149, Enterprise $499). Download, test your LLM, and tell us what you think."
- [ ] **Thank-you tweet:** "We launched CertifyAI on Product Hunt 24 hours ago. Here are the numbers: {upvotes}, {comments}, {Pro sales}, {PyPI downloads}. Thank you to everyone who supported us. {link}"
- [ ] **Email all design partners** with the launch results. Thank them for their support.
- [ ] **Email all pre-launch signups** (if you had a waitlist) with launch announcement + special offer (if you choose to do one).
- [ ] **Analyze what worked:**
  - Which makers drove the most traffic?
  - Which channels drove the most upvotes?
  - What questions got the most engagement?
  - What was the conversion rate from PH → Gumroad?

---

## 5. Support Mobilization

### Tier 1: Personal Network (DM These People)

**Priority:** Friends and colleagues who will upvote immediately. These are your first 20-30 votes.

```markdown
Name relationship message
```

Draft message:

> Hey {name},
>
> I just launched CertifyAI on Product Hunt! It's a self-hosted AI compliance tool I've been building (tests LLMs for injection/PII/jailbreak/bias, generates compliance reports).
>
> If you have 30 seconds, an upvote would mean the world: {link}
>
> Thank you! 🙏

### Tier 2: Professional Network

LinkedIn connections, former coworkers, Twitter mutuals. These are your next 30-50 voters.

**LinkedIn DM:**

> Hi {name},
>
> Hope you're doing well! I just launched a product I've been building called CertifyAI on Product Hunt.
>
> It's a self-hosted compliance engine for LLMs — test your AI for prompt injection, PII leakage, jailbreak, and bias, then generate auditor-ready compliance reports mapped to EU AI Act/SOC 2/NIST AI RMF.
>
> If this sounds useful or you know someone who needs it, an upvote on PH would really help: {link}
>
> Thanks so much!

### Discord Communities to Post In

| Community | Channel | Best Time | Message Style |
|-----------|---------|-----------|---------------|
| **AI Safety Server** | #projects | T+0 | Technical: "Built a CLI that tests LLM safety across 30 scenarios with evidence vault. PH launch today." |
| **Python Discord** | #projects | T+2 | Tech-focused: "CLI tool on PyPI that tests LLM compliance. Uses Click + Textual + Rich." |
| **Indie Hackers** | #launches | T+0 | Founder story: "Solo dev launches self-hosted AI compliance tool on PH. $149 one-time." |
| **r/SaaS Discord** | #launches | T+4 | Business-focused: "Launched my $149 boilerplate on PH. Here's the strategy." |
| **Makerlog** | #shipping | T+0 | Ship-focussed: "🚢 CertifyAI is live on PH!" |

### How to Get the First 50 Upvotes

The first 50 upvotes in the first 2 hours determine whether PH's algorithm boosts you to the front page. This is critical.

**Strategy:**
1. **T-24h** — DM 10 close friends: "Can you upvote at exactly 6:00 AM PT tomorrow?"
2. **T-0** — As soon as you publish, DM 20 people from Tier 1 with the live link
3. **T+15min** — Post in 3 Discord servers
4. **T+30min** — Post on Twitter/X with the link
5. **T+1h** — DM 20 more people from Tier 2
6. **T+2h** — If you're below 50 upvotes, start posting in communities aggressively. If you're above 50, maintain momentum.

**What NOT to do:**
- Do NOT use upvote-for-upvote groups. PH algorithm detects vote rings and can penalize.
- Do NOT ask for upvotes in a public PH comment. It looks desperate.
- Do NOT create multiple accounts to upvote. You will be banned.

### Ask Template for Communities

> Hey everyone!
>
> I just launched my self-built project on Product Hunt and would love your support.
>
> CertifyAI is a self-hosted compliance testing tool for LLMs. It runs 30 attack scenarios (injection, jailbreak, PII, bias, hallucination, policy), maps results to EU AI Act / SOC 2 / NIST AI RMF, and generates auditor-ready PDF reports with crypto-verified evidence.
>
> Free tier on PyPI. Pro at $149 (Gumroad).
>
> If this resonates, an upvote would mean the world: {link}
>
> Happy to answer questions here or on PH!

---

## 6. Comment Engagement Strategy

### Golden Rules

1. **Reply to every single comment. Not "most." ALL.** This is non-negotiable. PH ranks products partly by maker responsiveness.
2. **First reply within 10 minutes.** Set notifications on. Have a laptop open.
3. **Never reply with a one-liner.** Show you read their comment. Reference something specific.
4. **Never be defensive.** If someone criticizes, thank them. Explain your reasoning. Then shut up.
5. **Every reply ends with a question** to continue the conversation. "What's your use case?" "What compliance frameworks do you need?"
6. **Tag people who ask good questions** in your update posts.

### Common Questions — Reply Templates

**Q: How is this different from Garak/Garak OSS?**

> Great question! Garak is excellent for red-teaming — but it stops there. CertifyAI adds three layers Garak doesn't have: (1) compliance framework mapping — your injection test result automatically maps to EU AI Act Article 14, not just a raw pass/fail. (2) Evidence vault with SHA-256 hash chain — crypto-verifiable proof for auditors. (3) Unified reporting — PDF, SARIF, JSON in one command.
>
> Think of Garak as a component. CertifyAI is a product. You can definitely use both. What's your current red-teaming setup?

**Q: Can this replace Vanta/Drata for SOC 2?**

> No — and I want to be really clear about that. Vanta and Drata are comprehensive GRC platforms that cover infrastructure monitoring, policy management, and auditor workflows. CertifyAI does one thing: tests your LLM's runtime behavior and generates compliance evidence.
>
> For SOC 2 specifically: if your auditor asks "how do you test your AI system for PII leakage?" — that's CertifyAI's job. If they ask "show me your access control policy for AWS IAM" — that's Vanta's job. They're complementary.
>
> Are you currently using a GRC platform?

**Q: Why $149? Why not open-source?**

> Fair question. The free tier on PyPI is genuinely useful — 10 attack scenarios, JSON reports, full evidence vault. That's not going anywhere.
>
> The Pro tier ($149) is for teams that need PDF reports for auditors, compliance framework mapping, and the Web Dashboard. It's priced like a developer tool (think: Sentry Pro, PostHog), not like enterprise compliance software ($30K+/year). One-time payment. Works forever.
>
> I'm a solo developer. The Pro and Enterprise tiers fund development. If I gave everything away, I couldn't maintain it.

**Q: How do I know the evidence is actually tamper-proof?**

> Every attack result generates a SHA-256 hash. Each new result includes the previous hash. Together they form an append-only chain.
>
> To verify: run `certifyai vault --verify`. The tool walks the entire chain from the first evidence entry to the latest, recomputes each hash, and confirms nothing changed.
>
> If any entry was modified or deleted after creation, the verification fails with a clear error showing exactly which entry was tampered.
>
> We published the verification algorithm in our docs so auditors can independently verify: {docs link}

**Q: Does this work with local/Ollama models?**

> Yes! That's actually one of our most tested scenarios. `certifyai run --provider ollama --model llama3` works fully offline. No internet connection needed at runtime. That's the entire point of the self-hosted approach.
>
> We also support Azure OpenAI (HIPAA BAA, important for healthcare), Anthropic, Gemini, and any OpenAI-compatible endpoint.
>
> Are you running Ollama in production or for development?

**Q: What if I need a feature that's not in the free tier?**

> Great question. The free tier is designed to give you a real taste — you can run 10 attacks, see results, and verify the evidence chain. If you find it genuinely useful, then the Pro upgrade unlocks 30 attacks, compliance framework mapping, PDF reports, and the Web Dashboard.
>
> What specific feature are you looking for? If it's something we can add to the free tier, I'll consider it for the next release.

**Q: Is this EU AI Act compliant? Like, certified?**

> Important clarification: CertifyAI is a **tool for generating compliance evidence**, not a certification body. We don't certify anything. What we do:
> - Map your attack results to specific EU AI Act articles (Art. 9 — Risk Management, Art. 14 — Human Oversight, etc.)
> - Generate auditor-ready evidence with cryptographic integrity
>
> Whether your system is "EU AI Act compliant" depends on your implementation, risk assessment, and documentation — not on running a tool. CertifyAI gives you the evidence layer. You still need to interpret it in your compliance context.
>
> We're working on an "Evidence Guide" document for auditors that explains how to evaluate CertifyAI output. Want me to ping you when it's ready?

**Q: Solo developer? How do I know you'll be around to support this?**

> Honest answer: I've been building developer tools for {X years}. This is not a side project — it's my full-time focus. The boilerplate model (no servers, no ops) means my costs are near-zero, so there's no pressure to shut down.
>
> I've also published a public roadmap: {link}. You can see exactly what's planned for the next 6 months.
>
> If you need more assurance, the Enterprise tier includes priority email support with a 24-hour SLA. But I understand concern about solo dev sustainability — it's a valid question.

### Handling Criticism

**If someone says "This is just a wrapper around Garak":**

> I can see why you'd think that, but CertifyAI does several things Garak doesn't: compliance framework mapping, evidence vault with hash chain, PDF report generation, Web Dashboard, multi-framework support. Garak is a red-teaming library. CertifyAI is a compliance product. They operate at different layers.
>
> That said, I have huge respect for Garak and the Garak team. Their work on LLM vulnerability scanning is foundational. If you're using Garak, I'd love to hear what you think of CertifyAI's compliance reporting layer on top.

**If someone says "$149 for a CLI tool is too expensive":**

> The free tier is available on PyPI and includes 10 attack scenarios, JSON reports, and the full evidence vault. You can evaluate the tool completely before paying anything.
>
> Pro ($149) adds PDF reports for auditors, compliance framework mapping, and the Web Dashboard. It's priced like a developer tool (Sentry Pro, PostHog), not enterprise compliance software. One payment, not annual subscription.
>
> For perspective: building equivalent functionality yourself takes 4-8 weeks of engineering time, which at $150K/year salary is $12K-$32K. $149 saves you 40-100x that.

**If someone says "The market doesn't exist / nobody needs this":**

> The EU AI Act high-risk deadline is December 2027 with fines up to €35M. SOC 2 Type II audits increasingly ask about AI testing. 78% of organizations are not ready. 362 AI incidents were documented in 2025 — a 56% increase YoY.
>
> I think the market exists — it's just being served poorly (either $30K+/year enterprise SaaS that can't test AI, or fragmented OSS that takes weeks to assemble).
>
> But I could be wrong! What's your take — are teams not asking for this yet in your experience?

### The "Friends" Comment Strategy

Ask 3-5 friends to post genuine questions on PH (not "great product!" — those feel fake and don't help). Coordinate:

- Friend 1: "How does the evidence vault work for SOC 2 auditors?" → You reply with detailed vault explanation
- Friend 2: "Does this work with Ollama? We're air-gapped." → You reply with air-gapped workflow
- Friend 3: "What's the roadmap for CI/CD integration?" → You reply with planned GitHub Actions support

These authentic Q&As create social proof more effectively than generic praise.

---

## 7. Cross-Promotion Plan

### Hacker News "Show HN" Post

**Post at:** 7:00 AM ET / 11:00 UTC (PH launch at 6:00 PT = 9:00 ET — stagger by 2 hours to avoid diluting attention)

**Title:**

> Show HN: CertifyAI – Self-hosted AI compliance testing (EU AI Act, SOC 2, NIST)

**Body:**

> I built a self-hosted CLI that tests LLMs for compliance.
>
> Context: Every company deploying LLMs faces regulatory pressure (EU AI Act, SOC 2, NIST AI RMF). Current tools are either enterprise SaaS at $10K-$150K/year (Vanta, Credo AI, Drata) — which can't actually test AI runtime behavior — or fragmented OSS tools that require weeks to assemble.
>
> CertifyAI is a downloadable Python package:
> - 30 attack scenarios (injection, jailbreak, PII, bias, hallucination, policy)
> - Maps results to EU AI Act articles, SOC 2 Common Criteria, NIST AI RMF
> - Crypto-verified evidence vault (SHA-256 hash chain)
> - Auditor-ready PDF reports
> - Works air-gapped with Ollama
>
> `pip install certifyai` → `certifyai init` → `certifyai run` → PDF report in 10 minutes.
>
> Free tier on PyPI (10 attacks, JSON reports). Pro at $149 on Gumroad.
>
> Would love your feedback — especially from teams preparing for SOC 2 or EU AI Act audits. What scenarios should we add? What compliance frameworks do you need?

**HN Engagement Strategy:**
- Reply to EVERY comment. HN is unforgiving of ignored questions.
- Be humble. This is a "Show HN" — you're showing, not selling. Never say "we" if you're solo. Say "I."
- If someone says it already exists: "Thanks for pointing that out! I looked at {tool} but chose to build because {reason}. What do you use currently?"
- If someone asks about enterprise features: Be honest about limitations. "Not yet — the Web Dashboard is single-user in v1. CI/CD plugins are planned for v2. You can use the CLI in CI with subprocess today."

### Reddit r/MachineLearning Post

**Title:**

> I built a CLI that tests LLMs for injection, PII leakage, jailbreak, and bias — generates compliance reports mapped to EU AI Act / SOC 2

**Body:**

> I'm a solo developer building CertifyAI, a self-hosted compliance testing tool for LLMs. It runs 30 attack scenarios against any LLM endpoint (OpenAI, Anthropic, Ollama, Azure, Gemini), evaluates responses, and maps results to regulatory frameworks.
>
> The core idea: you bring your LLM key, CertifyAI runs the attack battery, logs everything with SHA-256 evidence chain, and generates auditor-ready reports.
>
> Why I built it: I was preparing for SOC 2 Type II and realized there's no affordable tool that actually tests AI behavior. Existing tools either monitor infrastructure (Vanta, Drata) or require stitching together 5+ OSS projects.
>
> **Technical details:**
> - Python + Click (CLI) + Textual (TUI) + LiteLLM (provider abstraction)
> - SQLite backend with WAL mode for concurrent CLI + Web Dashboard reads
> - Evidence vault with append-only SHA-256 hash chain
> - Pydantic v2 for data models and config validation
> - Jinja2 + WeasyPrint for PDF report generation
>
> Free tier on PyPI: 10 attack scenarios, JSON reports, full evidence vault.
> Pro tier ($149 on Gumroad): 30 attacks, PDF reports, compliance mapping, Web Dashboard.
>
> GitHub: {link}
> PH launch: {link}
>
> Happy to answer technical questions about the architecture, attack methodology, or compliance mapping approach.

### Reddit r/SaaS Post

**Title:**

> We launched a self-hosted AI compliance tool on Product Hunt. Here are the numbers.

**Body:**

> Hit #1 Product of the Day? Or didn't crack top 10? Be honest. Post the real numbers.
>
> What we learned:
> - Conversion from PH → Gumroad: {X}%
> - Comments: {Y} — the most common question was: "How is this different from Garak?"
> - Our biggest mistake: {honest reflection}
>
> Full breakdown in the comments if you're interested.

### Dev.to Article

**Title:** "I built a free, self-hosted AI compliance checker. Here's why."

**Structure:**
1. The problem: 78% of orgs unprepared for EU AI Act, no affordable tooling exists
2. The math: DIY costs 4-8 weeks of engineering ($12K-$32K), enterprise SaaS costs $10K-$150K/yr
3. The build: 8 weeks, Python/Click/Textual/LiteLLM, SQLite, 30 attack scenarios
4. The launch: Product Hunt, HN, Reddit — what worked, what didn't
5. The pricing: Free tier on PyPI, $149 Pro, $499 Enterprise
6. The ask: "Download it. Break it. Tell me what to fix."

**Post on:** Launch day (T+4h) to maximize cross-traffic from Dev.to → PH.
**Include:** Link to PH, GitHub repo, Gumroad.

### Twitter/X Thread

**Post at T+0, pin to profile:**

```
1/ We just launched on Product Hunt!

CertifyAI is a self-hosted CLI that tests LLMs for compliance. Here's why I built it:

2/ Every company deploying LLMs needs compliance evidence:
- EU AI Act (fines up to €35M)
- SOC 2 (auditors are asking about AI)
- NIST AI RMF (continuous measurement required)

3/ Current options:
• Enterprise SaaS: $10K-$150K/yr (can't test AI behavior)
• OSS: free but needs weeks to assemble
• DIY: $12K-$32K in engineering time

4/ CertifyAI: $149 one-time. 10 minute setup. Works on your machine. 30 attack scenarios. Auditor-ready PDF reports. Crypto-verified evidence.

5/ Free tier on PyPI: 10 attacks, JSON reports, full evidence vault.
Pro: 30 attacks, PDF reports, compliance framework mapping, Web Dashboard.

{link}

6/ I'm a solo dev who needed this tool and couldn't find it. So I built it. Would love your feedback!
```

### Cross-Promotion Timing Schedule

| Time (PT) | Channel | Action |
|-----------|---------|--------|
| T+0 (6:00 AM) | Product Hunt | Publish listing + first comment |
| T+0 (6:00 AM) | Twitter/X | Launch tweet (pinned) |
| T+0 (6:00 AM) | Discord (3 servers) | Project links |
| T+1 (7:00 AM) | LinkedIn | Launch post |
| T+2 (8:00 AM) | Reddit r/MachineLearning | Technical post |
| T+2 (8:00 AM) | Reddit r/SaaS | Launch post |
| T+2 (8:00 AM) | Hacker News | Show HN (staggered) |
| T+4 (10:00 AM) | Dev.to | Blog post |
| T+4 (10:00 AM) | Twitter/X | GIF demo tweet |
| T+6 (12:00 PM) | Indie Hackers | Launch story |
| T+8 (2:00 PM) | Twitter/X | Testimonial tweet |
| T+24 (6:00 AM) | All channels | Thank-you posts |

### Email Sequence for Launch Day Signups

Collect emails via Gumroad purchase + optional signup on certifyai.dev landing page.

**Email 1: Welcome (immediate after purchase/download)**

> Subject: Welcome to CertifyAI
>
> Thanks for downloading/purchasing CertifyAI!
>
> Quick start: pip install certifyai → certifyai init → certifyai run
>
> Docs: {link}
> GitHub: {link}
> Discord: {link}
>
> I'm here if you need help. Reply to this email anytime.

**Email 2: Pro tips (Day 2)**

> Subject: Getting the most out of CertifyAI
>
> Three things Pro users do:
> 1. Run against multiple providers: `certifyai run --provider openai --model gpt-4o && ...`
> 2. Compare runs: `certifyai report --diff run_a run_b`
> 3. Verify evidence before sharing: `certifyai vault --verify`
>
> Have you generated your first report yet? Reply and let me know how it went.

**Email 3: Case study (Day 7)**

> Subject: How {name} used CertifyAI for SOC 2 evidence
>
> [Case study content]
>
> What's your compliance story? I'd love to hear it.

---

## 8. Post-Launch Follow-up

### If You Win #1 Product of the Day

**Immediate actions:**
1. **Screenshot the #1 badge.** It goes on your website, GitHub README, and social profiles forever.
2. **Post within 1 hour:** "We just hit #1 Product of the Day on Product Hunt! 🎉 Thank you to everyone who supported us. Special thanks to {tag 5-10 key supporters}. Here's what's next: {roadmap highlights}."
3. **Email list:** Send "We hit #1 on Product Hunt!" email with the badge + thank you + call-to-action to download.
4. **Update LinkedIn banner** to include "Product Hunt #1 Product of the Day"
5. **Monitor server load.** If the PH traffic spike brings down your landing page, handle it gracefully (even a static HTML fallback is fine).

**Landing page update:**
Add banner: "🏆 Product Hunt #1 Product of the Day — [Link to PH]"

**GitHub README:**
Add badge: `[![Product Hunt](https://img.shields.io/badge/Product%20Hunt-%231-ff6154)](link)`

**What it means for revenue:**
- Expect 3x-5x normal daily sales for the next 3 days
- Expect a long tail of traffic for 2-4 weeks
- This is the best SEO boost you'll get — PH backlinks are nofollow but high-quality

### If You Don't Win #1 (Top 5 or Top 10)

**Analysis (24-48 hours post-launch):**

| Question | What to Look For |
|----------|-----------------|
| Was the total upvote count respectable? | >200 upvotes is solid for a dev tool. <100 means something was off. |
| What was the comment-to-upvote ratio? | >0.2 comments/upvote is great engagement. <0.1 means people scrolled past. |
| Which comment types got the most replies? | This tells you what messaging resonates. |
| Which channels drove traffic? | Check PH dashboard referral data. |
| What was the Gumroad conversion rate? | Target: >2% of PH visitors click through to Gumroad. |

**Adjustment actions:**
1. **If upvotes were low (<100):** The problem is likely positioning, not product. The tagline or description didn't hook people. Revise for the next launch attempt (re-launch is possible on PH after significant changes).
2. **If comments were low but upvotes were okay:** People liked the idea but weren't engaged enough to comment. Add a more provocative first comment next time. Ask a specific question.
3. **If Gumroad conversion was low:** The $149 price may feel high for PH's audience (who are often early adopters expecting discounts). Consider a PH-exclusive coupon code: "PH2026" for 20% off.
4. **If PH traffic didn't convert to PyPI installs:** Make sure the landing page has a clear, above-the-fold install command. PH users are impatient. `pip install certifyai` should be visible in the first 3 seconds.

**Re-launch strategy (if needed):**
- Wait 3-4 months
- Ship major new features (CI/CD integration, doubled attack library, GitHub Actions)
- Choose a different category angle ("CI/CD" instead of "Compliance")
- Recruit a different set of makers to support
- Try a different day of the week

### Post-Launch Email Sequence (for launch day signups)

**Audience:** People who signed up for waitlist OR purchased via Gumroad during launch

**Sequence:**

| Email | Timing | Subject | Content |
|-------|--------|---------|---------|
| 1 | Immediate | Welcome to CertifyAI | Quick start, docs link, support info |
| 2 | Day 2 | Pro tips for your first compliance report | 3 things Pro users do, report generation tricks |
| 3 | Day 7 | How [name] used CertifyAI for SOC 2 | Case study / testimonial |
| 4 | Day 14 | What's coming in v1.1 | Roadmap update, feature requests |
| 5 | Day 30 | CertifyAI in 30 days | Usage stats (if telemetry enabled), community highlights |

**Free tier users (PyPI installers, no email — you can't email them):**
- In-app upgrade prompts: `certifyai upgrade --pro` command in CLI
- Banner in TUI: "Unlock 30 attacks + PDF reports + compliance mapping. Upgrade to Pro."
- Footer in JSON reports: "Generated with CertifyAI Lite. Upgrade to Pro at gumroad.com/certifyai"

### Long-tail (Week 2-4 Post-Launch)

1. **SEO play:** PH profile page + backlinks from blog posts and Dev.to articles will start ranking within 2-4 weeks. Monitor search console for "AI compliance tool" queries.
2. **GitHub stars:** Continue engaging with issues and PRs. Every star is a potential Pro buyer.
3. **Content marketing:** Write 3 more Dev.to posts targeting different personas:
   - "How to prepare for SOC 2 Type II AI testing" (Priya)
   - "Red-teaming our Llama 3: A practical guide" (Marcus)
   - "From Google Docs to automated compliance: Auditing 15 AI clients" (Elena)
4. **Community building:** Reply to every GitHub issue within 24 hours. Join AI compliance discussions on HN, Reddit, and Discord. Post without links — just be helpful. The links follow naturally.

---

## 9. Success Metrics

### The "Good Launch" Targets

| Metric | Good | Great | Stellar |
|--------|------|-------|---------|
| **Upvotes** | 250+ | 500+ | 1,000+ |
| **Comments** | 50+ | 100+ | 200+ |
| **Pro conversions (Gumroad)** | 20 | 50 | 100 |
| **Enterprise conversions** | 3 | 10 | 20 |
| **PyPI downloads (first 48h)** | 500 | 1,000 | 3,000 |
| **GitHub stars (first week)** | 100 | 300 | 500+ |
| **Revenue (first 48h)** | $3,500 | $10,000 | $25,000+ |
| **PH category ranking** | Top 5 | #3 | #1 Product of the Day |
| **Email signups** | 100 | 300 | 500+ |
| **Design partner testers acquired** | 10 | 25 | 50+ |

### What These Numbers Mean

**Upvotes:**
- <100: Something was off with positioning or the product isn't ready. Re-evaluate.
- 250+: Solid dev tool launch. Respectable for a new category.
- 500+: You've validated category demand. Incumbents will notice.
- 1,000+: Exceptional. You're the exception, not the rule.

**Comments:**
- Comments are more valuable than upvotes. Each comment is a data point about what resonates.
- >0.15 comments per upvote = highly engaged community. Good signal for long-term retention.
- <0.05 = people upvote but don't care enough to engage.

**Conversions:**
- If <3% of PH visitors click through to Gumroad, the PH listing isn't compelling enough.
- If >10% of Gumroad visitors add to cart, pricing is right.
- If cart abandonment >80%, check the checkout flow for friction.

**PyPI downloads:**
- PH traffic is spikey. Expect 60% of downloads in the first 12 hours.
- Repeat installs over the next week indicate genuine interest (not just curiosity).

### Dashboard to Track

Set up a simple dashboard (Airtable, Google Sheets, or Notion) with:

```markdown
| Metric | Source | Current | Target | Status |
|--------|--------|---------|--------|--------|
| PH Upvotes | PH Dashboard | — | 500 | 🟡 |
| PH Comments | PH Dashboard | — | 100 | 🟡 |
| Gumroad Sales | Gumroad | — | 50 Pro / 10 Enterprise | 🟡 |
| PyPI Downloads | PyPI Stats | — | 1,000 | 🟡 |
| GitHub Stars | GitHub | — | 300 | 🟡 |
| HN Upvotes | HN | — | 100 | 🟡 |
| Dev.to Views | Dev.to | — | 5,000 | 🟡 |
| Newsletter Signups | Landing Page | — | 300 | 🟡 |
| Revenue | Gumroad | — | $10,000 | 🟡 |
```

Refresh every 2 hours on launch day. What gets measured gets managed.

### Post-Launch Reflection (Week 2)

Answer these questions honestly:

1. **What was the single most effective channel?** (Top referrer to Gumroad/PyPI)
2. **What question came up most often in PH comments?** (This is your FAQ — add a section to your README)
3. **What was the most common criticism?** (If it's valid, fix it. If it's misunderstanding, clarify your messaging.)
4. **What was the conversion rate: PH visitor → PyPI install → `certifyai init` → first run?**
5. **How many design partners signed up from the launch?**
6. **Would you change anything for a re-launch?** (If yes, document it now while fresh.)

**Benchmark against comparable launches:**

| Product | Category | PH Upvotes | Launch Date | Notes |
|---------|----------|-----------|-------------|-------|
| **Val.town** | Dev tools (edge functions) | ~1,200 | 2023 | Category-creating dev tool |
| **Screenshot.rocks** | Dev tools (screenshots) | ~800 | 2022 | Solo dev, CLI tool |
| **Tinybird** | Dev tools (data) | ~600 | 2022 | Developer-first positioning |
| **Kinsta APM** | Dev tools (monitoring) | ~400 | 2023 | Niche dev tool |
| **CertifyAI (target)** | **Dev tools / compliance** | **500+** | **2026** | **New category** |

---

*This is a living document. Update it after launch with real numbers and lessons learned.*

---

## Appendix A: Launch Day Checklist (One-Page)

### T-24h
- [ ] Final PH listing review
- [ ] GIF verified on PH preview
- [ ] Maker profile complete
- [ ] Gumroad purchase flow tested
- [ ] PyPI install tested from clean env
- [ ] First comment copy ready
- [ ] Social drafts queued
- [ ] Maker DM list finalized
- [ ] Discord posts prepared
- [ ] Backup of all PH listing fields saved

### T-2h
- [ ] Woke up, caffeinated
- [ ] PH draft refreshed — images/GIF confirmed
- [ ] Gumroad test purchase confirmed
- [ ] PyPI latest version confirmed
- [ ] Distractions eliminated
- [ ] Notifications on
- [ ] Phone on DND (except maker DMs)

### T+0 (6:00 AM PT)
- [ ] Published PH listing
- [ ] Posted first PH comment
- [ ] Posted launch tweet (pinned)
- [ ] DMed Tier 1 makers
- [ ] Posted in 3 Discord servers

### T+2h (8:00 AM PT)
- [ ] Replied to ALL PH comments so far
- [ ] Posted community update comment
- [ ] Posted Reddit r/MachineLearning
- [ ] Posted Reddit r/SaaS
- [ ] Posted HN Show HN

### T+4h (10:00 AM PT)
- [ ] Second tweet (GIF demo)
- [ ] LinkedIn post
- [ ] Dev.to article published
- [ ] Checked PH ranking — adjusted strategy

### T+8h (2:00 PM PT)
- [ ] Posted PH update comment (8-hour numbers)
- [ ] Third tweet (testimonial)
- [ ] Posted in additional communities

### T+24h (6:00 AM PT — Next Day)
- [ ] Posted PH thank-you comment
- [ ] Thank-you tweet with numbers
- [ ] Emailed design partners
- [ ] Analyzed what worked
- [ ] Updated README with PH badge
- [ ] Wrote down lessons learned

---

## Appendix B: Quick-Reference Links

| Resource | URL |
|----------|-----|
| PH Listing (draft) | producthunt.com/{draft-slug} |
| Gumroad Pro | gumroad.com/l/certifyai-pro |
| Gumroad Enterprise | gumroad.com/l/certifyai-enterprise |
| PyPI Package | pypi.org/project/certifyai |
| GitHub Repo | github.com/{user}/certifyai |
| Landing Page | certifyai.dev |
| Discord | discord.gg/{invite} |
| Docs | docs.certifyai.dev |
| PH Maker Settings | producthunt.com/settings/profile |
| PH Post Analytics | producthunt.com/posts/{slug}/analytics |
| VHS (GIF tool) | github.com/charmbracelet/vhs |
| Carbon (screenshots) | carbon.sh |
| Hypefury (social scheduler) | hypefury.com |
