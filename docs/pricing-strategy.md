# CertifyAI — Pricing Strategy Document

**Prepared by:** Pricing Analyst (The Agency)
**Date:** July 21, 2026
**Classification:** Internal — Strategy Decision Support
**Status:** Pre-build — informing Gumroad listing and launch pricing

---

## Table of Contents

1. [Value Quantification](#1-value-quantification)
2. [Competitive Pricing Analysis](#2-competitive-pricing-analysis)
3. [Cost Structure](#3-cost-structure)
4. [Tier Architecture](#4-tier-architecture)
5. [Willingness-to-Pay Analysis](#5-willingness-to-pay-analysis)
6. [Discount Strategy](#6-discount-strategy)
7. [Revenue Projections](#7-revenue-projections)
8. [Recommendation](#8-recommendation)

---

## 1. Value Quantification

### 1.1 The Value-Based Price Floor

CertifyAI replaces or supplements three distinct alternatives. Each defines a price ceiling:

**Alternative A: DIY with Open-Source Tools (the price floor anchor)**

A team replicating CertifyAI Pro must integrate Garak (prompt injection), Guardrails AI (output validation), Rebuff (jailbreak detection), a custom evidence store, a PDF report generator, and compliance mapping — all stitched together with glue code.

| Component | Engineering Time (weeks) | Salary Cost ($150K/yr fully loaded) |
|-----------|-------------------------|-------------------------------------|
| Evaluate & select OSS components | 0.5 | $1,500 |
| Integration & testing (API wiring) | 2.0 | $6,000 |
| Build evidence vault (SHA-256 chain) | 1.0 | $3,000 |
| Build compliance mapping layer | 1.5 | $4,500 |
| Build PDF report generator | 1.0 | $3,000 |
| Testing, debugging, documentation | 1.0 | $3,000 |
| **TOTAL DIY Cost** | **7.0 weeks** | **$21,000** |

Range at $150K–$200K/yr: **$12K–$32K** (per competitive-analysis.md).

**CertifyAI Pro price: $149. ROI for buyer: 80–215x in year one.**

**Alternative B: Enterprise SaaS (the perceived value anchor)**

| Competitor | Minimum Entry | Perceived Value | Gap to CertifyAI Pro |
|------------|--------------|-----------------|---------------------|
| Vanta | $7,500/yr | SOC 2 automation | **50x price** |
| Credo AI | $30,000/yr | AI governance docs | **201x price** |
| Drata | $15,000/yr | SOC 2 automation | **100x price** |
| IBM watsonx | $50,000/yr | Full ML lifecycle | **335x price** |

**Alternative C: Professional Services (the urgency anchor)**

- Single AI red-teaming engagement (PWC, Deloitte, Trail of Bits): **$15K–$50K**
- CertifyAI Pro ($149) generates comparable evidence continuously, not point-in-time
- Value gap: **100–335x**

### 1.2 Value-Stacked Price Ceilings

| Value Dimension | Customer Savings | CertifyAI's Share |
|----------------|-----------------|-------------------|
| Engineering time (vs DIY) | $12K–$32K saved once | $149 = 0.5%–1.2% |
| SaaS subscription avoided (vs Vanta) | $7.5K/yr | $149 = 2.0% of year 1 |
| SaaS subscription avoided (vs Credo AI) | $30K–$150K/yr | $149 = 0.1%–0.5% |
| Compliance readiness speed | 2–5 months compressed to 1 afternoon | Price insensitive for urgent buyers |

**Conclusion:** The value-based price floor (what the customer saves) supports $149–$499 pricing with massive surplus. At $149, the customer captures 99.3% of the DIY savings. This is appropriate for a boilerplate product — the extraction ratio is deliberately low to maximize adoption.

---

## 2. Competitive Pricing Analysis

### 2.1 Feature-Price Comparison Matrix

| Product | Price | Runtime Testing | Framework Mapping | Evidence Vault | Self-Hosted | PDF Reports | Price Per Feature (30 features) |
|---------|-------|----------------|-------------------|---------------|-------------|-------------|--------------------------------|
| **CertifyAI Free** | **$0** | ✅ 10 attacks | ❌ | ❌ | ✅ | ❌ | — |
| **CertifyAI Pro** | **$149** | ✅ 30 attacks | ✅ 4 frameworks | ✅ SHA-256 | ✅ | ✅ PDF+SARIF | **$4.97** |
| **CertifyAI Enterprise** | **$499** | ✅ 30+ | ✅ 4 + custom | ✅ SHA-256 | ✅ | ✅ White-label | **$16.63** |
| Vanta | $7,500/yr | ❌ | ⚠️ Shallow | ✅ | ❌ | ✅ | $250.00 |
| Credo AI | $30,000/yr | ❌ | ✅ Deep | ⚠️ Docs-only | ❌ | ✅ | $1,000.00 |
| Drata | $15,000/yr | ❌ | ❌ AI frameworks | ❌ | ❌ | ✅ | $500.00 |
| IBM watsonx | $50,000/yr | ❌ | ✅ | ❌ | ✅ Hybrid | ✅ | $1,666.67 |
| Garak (OSS) | $0 | ✅ | ❌ | ❌ | ✅ | ❌ | — |
| DIY | $12K–$32K (time) | ✅ Partial | ❌ Build it | ❌ Build it | ✅ | ❌ Build it | $400+ in time |

### 2.2 Price Positioning Map

```
$100K+│
       │                                              ● Credo AI Enterprise
       │                                              ● IBM watsonx
$50K   │
       │                                  ● Vanta Enterprise
$15K   │                     ● Drata
       │          ● Vanta Starter
$7.5K  │
       │
$1K    │
       │
$499   │                              ● CertifyAI Enterprise
$149   │                    ● CertifyAI Pro
$0     │ ● CertifyAI Free  ● Garak (OSS)
       └───────────────────────────────────────────────────────────
            Static Infra    Runtime Testing    Documentation    DIY-Build
                                       Product Approach
```

CertifyAI is the **only** product in the runtime-testing + self-hosted quadrant. The nearest competitor at any price is Garak (free, no compliance mapping, no reports). The nearest paid competitor at any feature set is 50x more expensive.

### 2.3 Value Metric Analysis

SaaS competitors price per: **seat**, **integration**, **model**, **month**.

CertifyAI's value metric: **per-installation, one-time**. This is the correct choice because:

| Metric | Risk of Misalignment | Why |
|--------|---------------------|-----|
| Per-seat | High | Most installations are single-user (engineer or consultant). Seat pricing punishes the solo dev. |
| Per-model | Medium | Customers may test 1–20 models. Per-model pricing creates friction. CertifyAI's model count is a config, not a license boundary. |
| Per-attack | Low but limiting | Free tier caps at 10 attacks explicitly to create conversion pressure. Pro/E enterprise are unlimited. |
| **Per-installation (one-time)** | **Best alignment** | The customer gets all value immediately. Zero friction. Zero renewal risk. No usage anxiety. |

**Key insight:** CertifyAI's pricing simplicity (one price, all features, no tiers of monthly fees) is itself a competitive advantage against Vanta's "$7.5K + add-ons" pricing opacity.

---

## 3. Cost Structure

### 3.1 Direct Costs Per Sale

| Cost Item | Free Tier | Pro ($149) | Enterprise ($499) |
|-----------|-----------|------------|-------------------|
| Gumroad transaction fee (8.5% + $0.50) | $0.00 | $13.17 | $42.92 |
| PyPI hosting | $0 | $0 | $0 |
| Gumroad hosting | $0 | $0 | $0 |
| Email support time (est.) | $0 | ~$5.00 | ~$15.00 |
| CDN / updates bandwidth | ~$0.01 | ~$0.01 | ~$0.01 |
| **Total direct cost** | **~$0.01** | **~$18.18** | **~$57.93** |
| **Gross margin** | **N/A** | **87.8%** | **88.4%** |

Support time calculation:
- Pro: 30 min per buyer, lifetime. At solo dev opportunity cost ($75/hr = $150K salary / 2000 hrs): $37.50 per buyer if every buyer needs 30 min. Estimated actual: 10 min avg = $12.50. But most buyers need near-zero support. Assume 20% of buyers need 30 min → avg 6 min → $7.50. Rounded to $5.00.
- Enterprise: 60 min per buyer, higher expectations. 40% need 45 min → avg 18 min → $22.50. Rounded to $15.00.

### 3.2 Fixed Costs (Monthly)

| Cost Item | Amount | Notes |
|-----------|--------|-------|
| Domain (certifyai.dev) | $1.50/mo | Annual $18 |
| Gumroad Pro account | $10.00/mo | Required for custom checkout / license keys |
| Landing page hosting (Vercel) | $0/mo | Free tier sufficient |
| Documentation hosting (Vercel) | $0/mo | Free tier or subdomain |
| GitHub Copilot (optional) | $10.00/mo | Productivity multiplier |
| Total fixed costs | ~$21.50/mo | Negligible |

### 3.3 Fully Loaded Cost Per Hour (Solo Dev Time)

| Cost Element | Value |
|-------------|-------|
| Developer time cost (opportunity) | $75/hr ($150K/yr) |
| Build time to v1.0 | 8 weeks = 320 hours |
| Build cost (sunk) | $24,000 (implicit) |
| Monthly support + maintenance | 20–40 hrs/mo = $1,500–$3,000/mo |
| Monthly content marketing | 10 hrs/mo = $750/mo |

### 3.4 Break-Even Analysis

| Metric | Value |
|--------|-------|
| Build sunk cost (implicit) | $24,000 |
| Monthly maintenance + marketing | $2,250/mo |
| Gross margin (blended Pro + Enterprise, 75:25 mix) | ~88% |
| Blended ASP (75% Pro + 25% Enterprise) | $236.50 |
| Net per sale (blended) | ~$198.00 |
| Sales to recover build cost | 122 units |
| Sales to cover monthly costs (per month) | 12 units @ $198 = $2,376 |

| Scenario | Units to Break-Even (Build + 12mo Ops) | Time to Break-Even |
|----------|---------------------------------------|-------------------|
| Pessimistic (mix skews Pro-heavy) | 122 + (12 x 12) = 266 units | 12 months at 22/mo |
| Base case (blended) | 122 + (12 x 12) = 266 units | 6–8 months at 35–45/mo |
| Optimistic (mix skews Enterprise) | 90 + (12 x 12) = 234 units | 4–5 months at 50–60/mo |

**Note:** Build cost is implicit (your time). Cash break-even is effectively $0 — Gumroad/PyPI have no monthly minimums beyond $10/mo. You are never cash-negative. The break-even analysis above measures time-to-value-recovery.

### 3.5 Margin Comparison vs. SaaS Competitors

| Company | Est. Gross Margin | Cost Driver |
|---------|-------------------|-------------|
| Vanta | ~70–75% | Cloud infra, SOC 2 compliance, sales team ($350M funded) |
| Credo AI | ~65–75% | Cloud infra, sales team, FedRAMP |
| Drata | ~70–75% | Cloud infra, sales, integrations |
| **CertifyAI** | **~88%** | **No hosting, no sales, no cloud. Solo dev labor is the only significant cost.** |

CertifyAI's margin advantage is structural — no cloud infrastructure, no sales team, no SOC 2 compliance cost. The trade-off: revenue per customer is 50–500x lower, so volume must compensate.

---

## 4. Tier Architecture

### 4.1 Current Tier Structure (Proposed)

| Feature | Free (PyPI) | Pro ($149 Gumroad) | Enterprise ($499 Gumroad) |
|---------|-------------|-------------------|--------------------------|
| Attack scenarios | 10 (2 per category) | 30 (all) | 30 (all) + custom |
| Report formats | JSON only | JSON + PDF + SARIF | JSON + PDF + SARIF + custom templates |
| Compliance framework mapping | Raw results only (no mapping) | EU AI Act + SOC 2 + NIST AI RMF + ISO 42001 | Same + custom framework builder |
| Web Dashboard | ❌ | ✅ | ✅ |
| Evidence vault (SHA-256) | ✅ (always on) | ✅ | ✅ |
| White-label / custom branding | ❌ | ❌ | ✅ |
| Source code access | ❌ (binary only) | ❌ | ✅ (full source) |
| Commercial license | ❌ (Apache 2.0) | ✅ | ✅ |
| Updates | ❌ (version pinned) | 1 year of updates | Lifetime updates |
| Support | GitHub Issues | Email (48hr SLA) | Email (24hr SLA) + priority |
| Price | **$0** | **$149** | **$499** |

### 4.2 Free Tier Conversion Mechanics

**What creates conversion pressure (intentional friction points):**

1. **Attack count: 10 vs 30.** The free tier gives exactly 2 attacks per category (injection, jailbreak, PII, policy, hallucination). A user testing their model against the OWASP LLM Top 10 will see 5 categories covered — but many high-value attacks (encoded injection, multi-turn jailbreak, anti-SB defusal, persona modulation) live in the Pro tier.

2. **No compliance framework mapping.** Free tier shows raw pass/fail per attack. Pro tier maps results to "EU AI Act Article 14 — Human Oversight" or "SOC 2 CC6.1 — Access Controls." For anyone needing auditor-ready evidence, the free tier is a teaser.

3. **No Web Dashboard.** CLI + TUI work well, but the Web Dashboard with visual charts, run comparison, and compliance tree view is a clear upgrade. The TUI is good. The Dashboard is *delightful*.

4. **No commercial license.** Free tier is Apache 2.0. Consultancies (Elena's persona) *cannot* use it for client work without a commercial license → forces Pro or Enterprise purchase.

5. **No PDF reports.** JSON output is developer-friendly. But auditors want PDFs with branding, executive summaries, and evidence certificates. No PDF = no audit handoff.

**What does NOT differ (anti-friction):**
- Same CLI/TUI interface
- Same performance
- Same underlying engine
- Same evidence vault integrity
- Same installation experience

**Why NOT to cripple the free tier further:**
Every friction point above forces upgrade for anyone with a real compliance need, while keeping the free tier genuinely useful for evaluation, hobbyists, and developers who want to explore without commitment. Crippling the CLI further (artificial delays, watermarked reports, expiration) would violate developer-tool norms and reduce conversion — users would uninstall before upgrading.

**Conversion flow:**
```
pip install → certifyai init → certifyai run (10 attacks) → JSON report
    ↓ sees "10/30 attacks — upgrade for compliance mapping"
    ↓ visits certifyai.dev — sees Pro features
    ↓ Gumroad checkout ($149) → license key → certifyai upgrade --key xyz
    → 30 attacks + PDF reports + framework mapping
```

### 4.3 Pro Tier: $149 vs $99 vs $199 — Sensitivity Analysis

Test three price points for the Pro tier:

#### $99 Pro (aggressive)

| Factor | Impact |
|--------|--------|
| Conversion rate (est.) | ~12–18% (higher volume) |
| Revenue per buyer | $90.32 net |
| Revenue to match $149 @ 10% | Need 16.5% conversion (1.65x volume) |
| Perception | "Cheap" — may signal lower quality vs $149 developer tools |
| Risk | Undervalues the product. Buyer WTP data (below) shows $149 is within range. |
| **Net assessment** | Leaves $50/unit on the table. Volume would need to increase 65% to compensate — unlikely given the niche market size. |

#### $149 Pro (recommended)

| Factor | Impact |
|--------|--------|
| Conversion rate (est.) | ~8–12% |
| Revenue per buyer | $135.83 net |
| Perception | "Developer tool pricing" — matches Sentry Team ($26/mo), PostHog ($0.0033/event → ~$150/mo for small teams), Linear ($14/user/mo) |
| Price relative to DIY | 0.7% of DIY cost ($21K avg) — trivial |
| Price relative to Vanta | 2.0% of Vanta year 1 ($7.5K) |
| Buyer decision type | **Impulse** — no procurement needed under $500 |
| **Net assessment** | Optimal. Low enough for impulse, high enough for quality signal. |

#### $199 Pro (premium)

| Factor | Impact |
|--------|--------|
| Conversion rate (est.) | ~4–7% (loses the bottom of the market) |
| Revenue per buyer | $181.59 net |
| Revenue to match $149 @ 10% | Need 7.5% conversion — achievable but risky |
| Perception | "Expensive for a CLI tool" — crosses the $150 psychological barrier |
| Risk | 78% of orgs not ready for EU AI Act — high price + high urgency = fewer trials |
| **Net assessment** | Too high for the "try before buy" CLI model. At $199, you need stronger social proof (reviews, case studies) that won't exist at launch. |

**Sensitivity analysis at ±20%:**

```
Price:              $99          $149          $199
Conv. rate:         15%          10%           6%
Rev/100 free users: $99 x 15 = $1,485    $149 x 10 = $1,490    $199 x 6 = $1,194
```

At the estimated conversion rates, **$149 and $99 are revenue-equivalent** per 100 free users. $199 underperforms both. Since $149 signals higher quality and leaves room for discounts, it is the clear winner.

### 4.4 Enterprise Tier: $499 vs $349 — Justification

Enterprise tier buyers differ from Pro buyers in three ways:
1. **They need a commercial license** (consultancies, agencies, or companies whose legal team flags Apache 2.0)
2. **They want white-label reports** (consultants who resell compliance reports to clients)
3. **They need source access** (custom framework mappings, advanced customization)

| Price Point | Rationale | Volume | Net Revenue/Unit |
|-------------|-----------|--------|-----------------|
| $349 | Too close to Pro ($149). Buyers ask: "What do I get for 2.3x more?" Source access + white-label justify 2.3x, but feels like Pro+ not Enterprise. | Higher volume but cannibalizes Pro upgrades | $306.08 net |
| $499 | Clear segmentation. Enterprise is 3.35x Pro. White-label + source + lifetime updates + priority support justifies the premium. Fits within the "under $500 impulse" threshold for funded teams. | Lower volume but higher trust signal | $456.08 net |
| $699 | Exceeds the $500 impulse threshold. Triggers procurement questions. Too close to Vanta's "I could just buy Vanta" territory. | Very low volume | $639.58 net |

**White-label value quantification:**

Consultants charge $150–$500/hr. Elena (our persona) bills $250/hr. A CertifyAI Enterprise report that saves her 4 hours per client engagement (vs manual testing) is worth $1,000 in saved time. At $499, she captures $501 in value from the tool *per engagement*. If she has 15 clients doing quarterly audits, the annual value is $30,060 saved — for a $499 tool.

| Customer Type | Value of White-Label / Year | Price Paid | Value Captured |
|---------------|---------------------------|------------|----------------|
| Consultant (15 clients, quarterly) | $30,060 (60 hrs saved @ $250/hr - $149 Pro) | $499 | $29,561/yr |
| Agency (5 clients, monthly) | $12,000 (48 hrs saved @ $250/hr - $149 Pro) | $499 | $11,501/yr |
| Enterprise team (internal reports) | $3,000 (custom branding for exec presentations) | $499 | $2,501/yr |

**Conclusion:** $499 is the correct Enterprise price. It's within the "use the company card" threshold for most funded startups and consultancies, while being clearly premium above Pro.

### 4.5 Optional Add-On: Annual Update Subscription ($49/yr)

**Proposal:** Offer a $49/yr update subscription for Pro tier buyers who want to keep receiving new attack scenarios, regulatory framework updates, and feature releases beyond year 1.

| Factor | Analysis |
|--------|----------|
| Current Pro includes | 1 year of updates from purchase date |
| After year 1 | User keeps the product as-is. Attacks and frameworks are frozen as of purchase. |
| Subscription price | $49/yr — 33% of Pro purchase price |
| Renewal likelihood | ~40% (est.) — users who actively run compliance quarterly will renew |
| LTV impact | $149 + ($49 x 2 years x 40% renewal) = $188.20 avg Pro LTV vs $149 one-time |

**Why offer it?**
- Single purchase at $149 has no recurring revenue. A $49/yr option adds LTV without forcing SaaS economics.
- Attack scenarios and frameworks are the product's living value. Users who care about staying current will pay.
- Creates a service relationship — renewal reminds users the product is active.

**Why NOT bundle it?**
- $149 + $49/yr first year = $198. Too close to the psychological $200 barrier.
- Keep the first year free as part of the Pro purchase. The update subscription is a separate purchase from year 2 onward.

**Recommendation:** Ship Pro at $149 with 1 year updates. Add a $49/yr update subscription on Gumroad as a separate product. Enterprise includes lifetime updates (part of the $499 value proposition).

---

## 5. Willingness-to-Pay Analysis

### 5.1 Segment Heatmap

| Buyer Segment | Population (Est.) | Max WTP | CertifyAI Price | Price Relative to Max | Decision Type |
|---------------|-------------------|---------|-----------------|----------------------|---------------|
| Solo dev / Indie hacker | 500,000+ | $0–$79 | Free (never convert) | Within range | Personal card |
| Pre-funding startup | 150,000 | $79–$149 | $149 Pro | At ceiling | Founder's card |
| Funded startup (Seed–Series A) | 50,000 | $149–$499 | $149 Pro | Below max | Company card |
| Scale-up (Series B+) | 10,000 | $499–$2,000 | $499 Enterprise | At floor | Procurement card |
| AI/ML consultancy | 2,000 | $499–$999 | $499 Enterprise | Below max | Billed to client |
| Enterprise pilot team | 5,000 | $499–$5,000 | $499 Enterprise | At floor | Corp card / PO |

### 5.2 Price Elasticity Estimate

For a developer tool under $500, one-time purchase, no ongoing commitment:

| Price Point | Est. Conversion (from active free users) | Elasticity |
|-------------|----------------------------------------|------------|
| $49 | 25–35% | — |
| $99 | 15–20% | Elastic (2x price → 0.6x volume) |
| $149 | 8–12% | Unit elastic (1.5x price → 0.6x volume) |
| $199 | 4–7% | Elastic (1.33x price → 0.5x volume) |
| $299 | 2–3% | Highly elastic (1.5x price → 0.33x volume) |

**Elasticity coefficient (ε) across range:**
- $99→$149: ε ≈ -1.2 (somewhat elastic — revenue neutral)
- $149→$199: ε ≈ -1.5 (elastic — revenue declines)
- $199→$299: ε ≈ -2.0 (highly elastic — revenue drops sharply)

**Optimal revenue point:** $99–$149 band. Within this band, total revenue from 100 free users is approximately flat ($1,485–$1,490 per our earlier calculation). At $149, you get higher per-unit revenue with only slightly lower volume, AND the higher price signals quality.

### 5.3 Behavioral Pricing Anchors

| Anchor Point | Buyer Psychology | CertifyAI Strategy |
|-------------|-----------------|-------------------|
| $0 | "Worth trying" → Free tier hooks them | ✅ 10 attacks, real value |
| $49 | "Like a SaaS month" → Too low for perceived value | ❌ Avoid — signals "toy" |
| $99 | "Good dev tool price" → Low friction | ❌ Leaves money on table |
| **$149** | **"Serious tool, one-time cost"** → Impulse buy | **✅ Optimal** |
| $199 | "Expensive CLI" → Crosses mental barrier | ❌ Risks conversion drop |
| $499 | "Enterprise tool" → Procurement if over $500, but just under | ✅ Fits "under $500" rule |
| $1,000+ | "Needs approval" → Requires sales process | ❌ Solo dev cannot support |

**The $500 barrier:** Most startups have a self-serve purchasing policy for items under $500. The CTO or engineer can use a company card without vendor approval, security review, or legal review. CertifyAI's Enterprise tier at $499 stays *just under* this threshold. This is intentional.

### 5.4 Van Westendorp Price Sensitivity Meter (Est.)

From developer tool surveys and adjacent product data:

| Van Westendorp Point | Pro Tier | Enterprise Tier |
|---------------------|----------|-----------------|
| Too cheap (quality concerns) | $19 | $79 |
| Cheap (good value) | $79 | $199 |
| Expensive (still might buy) | $199 | $799 |
| Too expensive (won't consider) | $499 | $1,999 |
| **Optimal Price Point (OPP)** | **$99–$149** | **$349–$499** |

CertifyAI's Pro ($149) and Enterprise ($499) fall within their respective OPP ranges.

---

## 6. Discount Strategy

### 6.1 Launch Discount

**Recommendation: 20% off first 100 buyers (Pro: $119, Enterprise: $399)**

| Factor | With Discount | Without Discount |
|--------|--------------|------------------|
| First 100 Pro revenue | $119 x 100 = $11,900 ($10,742 net) | $149 x 100 = $14,900 ($13,583 net) |
| Discount cost | $30/unit = $3,000 total | $0 |
| Launch urgency | Higher — "limited to first 100" creates FOMO | Neutral |
| Signaling | "20% off for early adopters" — fair for pre-revenue product | "Full price for unproven product" |
| Post-launch price anchor | "Was $149, now $149" — no anchor problem | "Always $149" — consistent |
| Risk | Early buyers angry if price drops later | None |

**Counter-argument:** The PRD (Section 7) explicitly recommends against introductory pricing: "discounting signals low confidence." This is valid for established products. For a **launch** of a pre-revenue boilerplate with zero social proof, a limited discount creates urgency and rewards early adopters. The key: **make it truly limited** (first 100 only, clearly countdown) and **never repeat it**.

**Revised recommendation:** Ship at full price ($149/$499). Do NOT offer a general discount. Instead, offer a **beta-tester reward**: the 5 design partners in Phase 1 get free lifetime Pro licenses. This is not a discount — it's compensation for feedback.

### 6.2 Annual Update Subscription Pricing

| Detail | Value |
|--------|-------|
| Price | $49/yr |
| Who can buy | Pro tier owners after year 1 |
| What it includes | New attack scenarios, regulatory framework updates, feature releases (but not Pro-to-Enterprise upgrade) |
| Renewal price | $49/yr (fixed for first 3 years) |
| How to sell | Separate Gumroad product, license key upgrade via `certifyai upgrade --subscribe` |

**Value justification:** $49/yr = 33% of Pro price. If the customer runs 4 compliance sweeps per year, each sweep costs them $12.25 in tooling. The value of catching one compliance violation that would have cost €35M in fines is... incidental. The point is that $49/yr is below any expense threshold for an active user.

**LTV impact of subscription:**

```
LTV = Purchase + (Subscription × Years × Renewal Probability)
Pro (no sub):                  LTV = $149
Pro + sub (1yr renewal):       LTV = $149 + ($49 × 1 × 0.40) = $168.60
Pro + sub (3yr renewal):       LTV = $149 + ($49 × 3 × 0.40) = $207.80
Pro + sub (5yr renewal):       LTV = $149 + ($49 × 5 × 0.30) = $222.50
```

At a 40% annual renewal rate, the subscription adds $19.60/yr to LTV. This is modest but meaningful — and requires zero additional work for the developer (the subscription automates).

### 6.3 What NOT to Do

| Discount Tactic | Why to Avoid |
|----------------|-------------|
| Enterprise discount if customers "ask for it" | If you discount Enterprise, you train customers to ask for discounts. $499 is already 23% of the "under $500 impulse" budget. Don't leave room. |
| Student / academic discount | Students are not the target buyer. They won't convert to Pro. Free tier is enough. |
| Volume licensing (5+ seats) | v1.0 is single-user. Multi-seat licensing adds complexity with zero revenue benefit for a solo dev. Defer to v2.0 if demand emerges. |
| Annual vs monthly pricing | One-time purchase only. Monthly billing for a CLI tool is parasitic. |
| Free tier time bomb (30-day trial) | Cripples conversion. Developer tools must be permanently useful at the free tier. Time bombs signal desperation. |
| "Name your price" / PWYW | Attracts the wrong customers. Erodes the "this is worth $149" signal. |

### 6.4 Bundle Strategy

**Recommendation: Do NOT bundle Pro + Enterprise on Gumroad as a single purchase.** They are separate products with separate license keys. Maintain clear segmentation:
- PyPI: Free (no key needed)
- Gumroad product 1: CertifyAI Pro — $149
- Gumroad product 2: CertifyAI Enterprise — $499
- Gumroad product 3: CertifyAI Update Subscription — $49/yr

The buyer selects their tier intentionally. No confusion. No support burden from "I thought I bought Enterprise but I got Pro."

---

## 7. Revenue Projections

### 7.1 Assumptions

| Variable | Pessimistic | Base | Optimistic |
|----------|------------|------|------------|
| Free users (month 12) | 500 | 2,000 | 5,000 |
| Pro conversion rate (of active free) | 5% | 10% | 15% |
| Enterprise % of paid (of total paid) | 10% | 20% | 30% |
| Pro price | $149 | $149 | $149 |
| Enterprise price | $499 | $499 | $499 |
| Monthly growth (free users) | 10% | 15% | 20% |
| Update sub adoption (year 2) | 15% | 25% | 35% |
| Paid user churn | N/A (one-time) | N/A | N/A |

### 7.2 Month 1–12 Revenue (Base Case)

| Month | Free Users (Cumulative) | New Pro Sales | New Enterprise Sales | Pro Revenue | Enterprise Revenue | Monthly Total | Cumulative |
|-------|------------------------|---------------|---------------------|-------------|-------------------|--------------|------------|
| 1 | 500 | 40 | 5 | $5,960 | $2,495 | $8,455 | $8,455 |
| 2 | 800 | 60 | 8 | $8,940 | $3,992 | $12,932 | $21,387 |
| 3 | 1,100 | 80 | 10 | $11,920 | $4,990 | $16,910 | $38,297 |
| 4 | 1,400 | 90 | 12 | $13,410 | $5,988 | $19,398 | $57,695 |
| 5 | 1,600 | 100 | 14 | $14,900 | $6,986 | $21,886 | $79,581 |
| 6 | 1,800 | 110 | 15 | $16,390 | $7,485 | $23,875 | $103,456 |
| 7 | 1,950 | 115 | 16 | $17,135 | $7,984 | $25,119 | $128,575 |
| 8 | 2,050 | 120 | 17 | $17,880 | $8,483 | $26,363 | $154,938 |
| 9 | 2,100 | 120 | 17 | $17,880 | $8,483 | $26,363 | $181,301 |
| 10 | 2,150 | 120 | 18 | $17,880 | $8,982 | $26,862 | $208,163 |
| 11 | 2,100 | 115 | 17 | $17,135 | $8,483 | $25,618 | $233,781 |
| 12 | 2,000 | 100 | 15 | $14,900 | $7,485 | $22,385 | $256,166 |

**Year 1 Pro sales:** 1,170 @ $149 = **$174,330 gross**
**Year 1 Enterprise sales:** 164 @ $499 = **$81,836 gross**
**Year 1 total gross revenue:** **$256,166**
**Year 1 total net revenue (after Gumroad fees):** **$233,868**

### 7.3 Scenario Comparison

| Metric | Pessimistic | Base | Optimistic |
|--------|------------|------|------------|
| Y1 Pro units | 515 | 1,170 | 2,700 |
| Y1 Enterprise units | 57 | 164 | 525 |
| Y1 gross revenue | $78,288 | $256,166 | $664,575 |
| Y1 net revenue | $70,932 | $233,868 | $608,204 |
| Y1 net monthly avg (months 6-12) | $4,200 | $16,200 | $42,500 |
| Monthly free users (Y1 end) | 500 | 2,000 | 5,000 |
| Conversion rate | 5% | 10% | 15% |

### 7.4 Unit Economics by Tier

| Metric | Free User | Pro Buyer | Enterprise Buyer |
|--------|-----------|-----------|-----------------|
| COGS (support + fees) | $0.01 | $18.18 | $57.93 |
| Revenue | $0.00 | $149.00 | $499.00 |
| Gross profit | -$0.01 | $130.82 | $441.07 |
| Gross margin | N/A | 87.8% | 88.4% |
| Marketing cost to acquire | $0 (PyPI organic) | $0–$5 (content marketing, prorated) | $0–$5 |
| **LTV** | **$0** | **$149–$223** (with sub) | **$499** (lifetime) |
| Payback period | N/A | Instant (no CAC) | Instant |

### 7.5 Y2 Revenue Impact of Update Subscriptions

Assuming 25% of Y1 Pro buyers subscribe at $49/yr in Y2:

| Source | Revenue |
|--------|---------|
| New Pro sales (Y2, est. growth 20%) | ~1,400 × $149 = $208,600 |
| New Enterprise sales (Y2) | ~200 × $499 = $99,800 |
| Update subscriptions (25% of 1,170 Y1 Pro buyers) | 293 × $49 = $14,357 |
| **Y2 gross revenue (est.)** | **$322,757** |
| Y2 net (after fees) | **$295,546** |

The subscription is not a significant revenue driver at scale, but it adds $14K+ in nearly zero-effort income.

### 7.6 Sensitivity to Price Change

| Scenario | Pro Price | Base Conv. | Y1 Revenue | Change from Base |
|----------|-----------|------------|------------|------------------|
| Base | $149 | 10% | $256,166 | — |
| Pro at $99 | $99 | 15% | $236,768 | -7.6% |
| Pro at $199 | $199 | 6% | $208,410 | -18.6% |
| Enterprise at $349 | $149/$349 | 10%/22% | $248,702 | -2.9% |
| Enterprise at $699 | $149/$699 | 10%/8% | $232,413 | -9.3% |
| 15% conversion at $149 | $149 | 15% | $375,208 | +46.5% |

**Key finding:** Revenue is most sensitive to **conversion rate**, not price. A 5 percentage point increase in conversion (10% → 15%) adds 46.5% more revenue. This means the pricing team's energy should go to improving free-to-Pro conversion (better upgrade prompts, clearer value differentiation, compelling trial) rather than optimizing the price point by ±$20.

---

## 8. Recommendation

### 8.1 Final Price Points

| Tier | Price | Rationale |
|------|-------|-----------|
| **Free (Lite)** | **$0** | 10 attack scenarios, JSON output, no compliance mapping. Good enough to evaluate, limited enough to create upgrade desire. |
| **Pro** | **$149** | Optimal point in the $99–$199 range. Revenue-neutral with $99 at estimated conversion rates. Signals quality. Under $150 impulse threshold. 99.3% of DIY savings passed to customer. |
| **Enterprise** | **$499** | 3.35x Pro premium justified by white-label, source access, lifetime updates. Under $500 corporate card threshold. Clear value for consultants and funded teams. |
| **Update Subscription** | **$49/yr** | Optional add-on for Pro buyers after year 1. 33% of Pro price. Expected 25–40% annual renewal. Adds $12–$20/yr to LTV per subscriber. |

### 8.2 Positioning

| Message | Target | Where |
|---------|--------|-------|
| "Free to try. $149 to ship." | Solo devs, startups | PyPI README, landing page |
| "80x cheaper than the alternative. Ready in 10 minutes." | Tech leads comparing to Vanta/DIY | Competitive landing pages, blog posts |
| "Your compliance tool should cost less than your mechanical keyboard." | Indie developers | Social media, dev community posts |
| "White-label compliance for 10 clients. One-time payment." | Consultants (Elena persona) | Enterprise landing page |

### 8.3 Launch Pricing Decision

**DO NOT offer a launch discount.** Rationale:
1. The product is pre-revenue with zero social proof. Early adopters in developer tools *expect* to pay full price. Discounting signals uncertainty.
2. The limited 100-buyer discount from Section 6.1 would cost $3,000 in foregone revenue for minimal FOMO benefit.
3. If a discount is absolutely necessary to close first 100 sales, offer a **bonus** instead: "First 100 buyers get lifetime updates (instead of 1 year)." This costs nothing and increases LTV.
4. Keep the $49/yr update subscription as a separate Gumroad product. Do NOT bundle it into Pro.

**Revised launch bonus instead of discount:**
- First 100 Pro buyers: Lifetime updates (normally $49/yr after year 1) → effectively a $49+ value
- First 50 Enterprise buyers: Priority feature requests + direct Slack channel (zero marginal cost)
- Cost to you: $0. Perceived value to buyer: $49–$500.

### 8.4 Implementation Checklist

| Action | Responsible | Deadline |
|--------|------------|----------|
| Set Gumroad product: CertifyAI Pro @ $149 | Dev | Before GA launch |
| Set Gumroad product: CertifyAI Enterprise @ $499 | Dev | Before GA launch |
| Set Gumroad product: CertifyAI Update Subscription @ $49/yr | Dev | Month 6 (when first Pro buyers hit year 1) |
| Implement `certifyai upgrade --key` in CLI | Dev | Phase 1 |
| Implement license key validation (offline, public-key signed) | Dev | Phase 1 |
| Implement free tier attack cap (10/30) | Dev | Phase 1 |
| Implement upgrade prompt in CLI (`certifyai upgrade --pro`) | Dev | Phase 1 |
| Implement upgrade prompt in reports (PDF/JSON footer) | Dev | Phase 1 |
| Add Gumroad license key verification for Enterprise features (white-label, source) | Dev | Phase 2 |

### 8.5 Review Cadence

| Review Point | Timing | Trigger | Action |
|-------------|--------|---------|--------|
| Launch week | Day 7 post-GA | <10 Pro sales in week 1 | Evaluate conversion funnel. Is "10 attacks free → $149 Pro" clear? |
| Month 1 | Day 30 | <5% conversion rate | Interview 10 free users. What stops them from upgrading? |
| Month 3 | Day 90 | <$15K/mo revenue | Consider test: raise Pro to $199 for new buyers, grandfather existing. Measure conversion delta. |
| Month 6 | Day 180 | Any | First update subscription renewal window opens. Measure take rate. |
| Competitor arrival | Within 1 week | Copycat at ≤$99 | Do NOT race to $49. Compete on attack library depth and compliance mapping coverage. |
| Year 1 | Day 365 | Any | Review if $149/$499 still fits market. Consider price increase if brand is established. |

### 8.6 Price Increase Path (If Applicable)

If CertifyAI achieves significant distribution and brand recognition by Year 2, a price increase from $149 to $199 Pro is viable:

| Condition | Rationale |
|-----------|-----------|
| Product has 100+ verified reviews / testimonials | Social proof justifies premium |
| Attack library has grown from 30 to 50+ scenarios | More value delivered, higher price justified |
| Compliance framework coverage has expanded (e.g., HIPAA AI, Colorado AI Act) | Regulatory breadth = compliance value |
| Direct competitors exist at $99 | Price leader stays above, competes on quality |
| Free tier has 5,000+ active users | Conversion funnel has volume to absorb lower rate |

**Price increase mechanism:**
- New buyers: $199 from date X
- Existing buyers: Grandfathered at $149, including $49/yr update subscription stays at $49
- Gumroad supports per-product pricing changes with existing license terms preserved

---

## Appendix A: Pricing Math Reference

### A.1 Net Revenue Formulas

```
Gumroad fee structure (Pro account): 8.5% + $0.50 per transaction

Pro buyer:
  Gross:    $149.00
  Fee:      $149.00 × 0.085 + $0.50 = $13.17
  Net:      $149.00 - $13.17 = $135.83
  Margin:   91.2%

Enterprise buyer:
  Gross:    $499.00
  Fee:      $499.00 × 0.085 + $0.50 = $42.92
  Net:      $499.00 - $42.92 = $456.08
  Margin:   91.4%

Update subscription ($49/yr):
  Gross:    $49.00
  Fee:      $49.00 × 0.085 + $0.50 = $4.67
  Net:      $49.00 - $4.67 = $44.33
  Margin:   90.5%
```

### A.2 Break-Even Math

```
Monthly fixed costs: ~$21.50 (Gumroad Pro + domain + tools)

Pro margin per unit: $135.83
Enterprise margin per unit: $456.08

Units to cover monthly fixed costs:
  Pro only:           $21.50 / $135.83 = 0.16 units → effectively 1 unit covers the month
  Enterprise only:    $21.50 / $456.08 = 0.05 units → 1 unit covers 5 months

Profit per month after 10 sales (blended):
  10 × (0.80 × $135.83 + 0.20 × $456.08) - $21.50 = $1,976.90

Break-even including build cost ($24,000 implicit):
  Blended net per unit: $199.88
  Units to recover build: $24,000 / $199.88 = 120 units
  Time at base case (10 Pro + 2.5 Enterprise/month): ~8 months
```

### A.3 Conversion Sensitivity

```
Revenue from 1,000 monthly active free users:

Conv. Rate  | Pro Only Revenue | Enterprise @ 20% of Paid | Total Revenue
------------|-----------------|--------------------------|--------------
    5%      | 50 × $149 = $7,450   | 10 × $499 = $4,990         | $12,440
    8%      | 80 × $149 = $11,920  | 16 × $499 = $7,984         | $19,904
   10%      | 100 × $149 = $14,900 | 20 × $499 = $9,980         | $24,880
   12%      | 120 × $149 = $17,880 | 24 × $499 = $11,976        | $29,856
   15%      | 150 × $149 = $22,350 | 30 × $499 = $14,970        | $37,320

Every 1% increase in conversion = +$2,477/mo at base enterprise mix.
```

### A.4 Enterprise Mix Sensitivity

```
From 1,000 MAU at 10% paid conversion (= 100 paid buyers):

Enterprise % | Pro Revenue | Enterprise Revenue | Total Revenue
-------------|------------|-------------------|--------------
     0%      | 100 × $149 = $14,900    | 0 × $499 = $0        | $14,900
    10%      | 90 × $149 = $13,410     | 10 × $499 = $4,990   | $18,400
    20%      | 80 × $149 = $11,920     | 20 × $499 = $9,980   | $21,900
    30%      | 70 × $149 = $10,430     | 30 × $499 = $14,970  | $25,400
    40%      | 60 × $149 = $8,940      | 40 × $499 = $19,960  | $28,900

Enterprise conversion is more sensitive than Pro pricing: moving from 10% to 20% Enterprise mix adds $3,500/mo — equivalent to increasing Pro conversion from 10% to 12.4%.
```

---

*End of Pricing Strategy Document — Estimated total lines: ~9,500 words across 8 sections + appendix. Prepared for CertifyAI product launch.*
