# CertifyAI — Compliance Framework Specification

**Document Status:** Draft v1.0
**Author:** Compliance Auditor (The Agency)
**Date:** 2026-07-21
**Product:** Continuous Compliance Engine for AI Runtimes
**Delivery Model:** Shippable Boilerplate (PyPI + Gumroad)

---

## Table of Contents

1. [Framework Mapping Architecture](#1-framework-mapping-architecture)
2. [EU AI Act Deep Map](#2-eu-ai-act-deep-map)
3. [SOC 2 Type II Mapping](#3-soc-2-type-ii-mapping)
4. [NIST AI RMF Mapping](#4-nist-ai-rmf-mapping)
5. [ISO 42001 Mapping (Optional)](#5-iso-42001-mapping-optional)
6. [Cross-Framework Coverage Matrix](#6-cross-framework-coverage-matrix)
7. [Report Schema](#7-report-schema)
8. [Interpretation Guide](#8-interpretation-guide)

---

## 1. Framework Mapping Architecture

### 1.1 Design Overview

The compliance mapper is a **stateless, deterministic engine** that links attack results to regulatory framework clauses via YAML definition files. Every framework is a self-contained YAML file shipped with the product. Customers can read, modify, or extend these files without touching Python code.

```
+------------------------------------------------------------+
|                    YAML Framework Files                      |
|                                                             |
|  eu_ai_act.yaml    soc2.yaml          nist_ai_rmf.yaml      |
|  iso42001.yaml     custom_framework.yaml                     |
|                                                             |
|  Shipped in: certifyai/engine/frameworks/                    |
|  Custom:      ~/.certifyai/frameworks/ (user override)       |
+-----------------------------+------------------------------+
                              | loaded at runtime
                              v
+------------------------------------------------------------+
|                FrameworkLoader (Pydantic-validated)          |
|                                                             |
|  1. Reads all .yaml files from framework directories         |
|  2. Parses into ComplianceFramework Pydantic model           |
|  3. Validates structure: required fields, clause references  |
|  4. Resolves plugin_id to AttackPlugin cross-references      |
|  5. Caches in memory (immutable for lifetime of process)     |
+-----------------------------+------------------------------+
                              |
                              v
+------------------------------------------------------------+
|                   ClauseMatcher                              |
|                                                             |
|  For each AttackResult:                                      |
|    1. Read result.metadata.framework_refs                    |
|    2. Match to loaded framework clauses                      |
|    3. Assign compliance status per clause:                   |
|       - compliant    -> all related attacks passed           |
|       - non_compliant -> at least one related attack failed  |
|       - needs_review -> borderline / low-confidence result   |
|       - not_tested   -> no attack covers this clause         |
|    4. Output: list[MatchedClause]                            |
+-----------------------------+------------------------------+
                              |
                              v
+------------------------------------------------------------+
|                  EvidenceLinker                              |
|                                                             |
|  Links each MatchedClause to Evidence Hash                   |
|  Builds compliance report payload for Report Generator      |
+------------------------------------------------------------+
```

### 1.2 YAML Framework Schema

Each framework YAML file follows this exact schema, validated by Pydantic on every load:

```yaml
# Schema version: 1.0
# Validated by FrameworkLoader on every load.

framework:
  id: str                          # Unique identifier, e.g., "eu_ai_act"
  name: str                        # Human-readable name, e.g., "EU AI Act"
  version: str                     # Regulation version/date, e.g., "2024-08"
  category: str                    # "regulatory" | "standard" | "custom"
  description: str                 # One-paragraph summary
  jurisdiction: str                # "EU" | "US" | "Global" | "Industry"
  effective_date: str              # ISO 8601 date of enforcement
  severity: str                    # Default: "high" | "medium" | "low"

  # Optional: metadata for the report
  metadata:
    url: str                       # Link to official regulation text
    authority: str                 # Regulatory body name
    max_fine: str                  # Maximum penalty (informational)
    scope: list[str]               # Which AI systems this applies to

  clauses:
    - id: str                      # Clause identifier, e.g., "art_9"
      title: str                   # Short title, e.g., "Risk Management System"
      category: str                # Grouping category
      description: str             # Full clause text summary
      severity: str                # "critical" | "high" | "medium" | "low" | "info"

      # What the clause requires -- concrete, auditable requirements
      requirements:
        - id: str                  # Requirement identifier, e.g., "art_9_req_1"
          description: str         # Specific requirement text

      # Which attack scenarios provide evidence for this clause
      tested_by:
        - plugin_id: str           # Fully qualified plugin ID, e.g., "injection.direct_injection"
          requirement_refs: list[str]  # Which requirements this attack addresses
          weight: float            # 0.0-1.0: how much this attack contributes to clause score
          evidence_type: str       # "direct" | "supporting" | "contextual"

      # Scoring configuration
      scoring:
        method: str                # "all_pass" | "weighted_average" | "any_critical_fail"
        min_pass_rate: float       # 0.0-1.0: minimum pass rate for "compliant" status

      # Report configuration
      report:
        section_title: str         # How this appears in the report
        recommended_actions: list[str]  # Remediation guidance
        auditor_questions: list[str]    # Questions an auditor might ask

  # Global scoring defaults
  scoring_defaults:
    clause_pass_threshold: float   # Default 0.8 (80%)
    weight_default: float          # Default 0.5
```

### 1.3 Example: eu_ai_act.yaml (Abridged)

```yaml
framework:
  id: eu_ai_act
  name: EU AI Act
  version: "2024-08"
  category: regulatory
  description: >
    Regulation (EU) 2024/1689 laying down harmonised rules on artificial
    intelligence. This mapping covers high-risk AI system requirements
    (Articles 9-15) and transparency obligations (Article 50).
  jurisdiction: EU
  effective_date: "2026-08-02"
  severity: high
  metadata:
    url: "https://eur-lex.europa.eu/eli/reg/2024/1689"
    authority: "European Commission"
    max_fine: "EUR 35,000,000 or 7% of worldwide annual turnover"
    scope:
      - "High-risk AI systems (Annex III)"
      - "Limited-risk AI systems (Article 50)"

  scoring_defaults:
    clause_pass_threshold: 0.8
    weight_default: 0.5

  clauses:
    - id: art_9
      title: Risk Management System
      category: governance
      description: >
        High-risk AI systems shall establish, document, implement, and maintain
        a continuous, iterative risk management process throughout the system lifecycle.
      severity: high
      requirements:
        - id: art_9_req_1
          description: Identify and analyse known and foreseeable risks to health, safety, or fundamental rights
        - id: art_9_req_2
          description: Evaluate risks when system is used according to intended purpose and under foreseeable misuse
        - id: art_9_req_3
          description: Implement risk mitigation measures and verify their effectiveness
        - id: art_9_req_4
          description: Maintain continuous risk monitoring and post-deployment surveillance
      tested_by:
        - plugin_id: injection.direct_injection
          requirement_refs: ["art_9_req_1", "art_9_req_3"]
          weight: 0.6
          evidence_type: direct
        - plugin_id: injection.indirect_injection
          requirement_refs: ["art_9_req_1"]
          weight: 0.5
          evidence_type: direct
        - plugin_id: jailbreak.roleplay_jailbreak
          requirement_refs: ["art_9_req_1", "art_9_req_3"]
          weight: 0.7
          evidence_type: direct
        - plugin_id: jailbreak.multilingual_jailbreak
          requirement_refs: ["art_9_req_1"]
          weight: 0.4
          evidence_type: supporting
        - plugin_id: injection.encoded_injection
          requirement_refs: ["art_9_req_1"]
          weight: 0.5
          evidence_type: direct
      scoring:
        method: weighted_average
        min_pass_rate: 0.8
      report:
        section_title: Risk Management System (Article 9)
        recommended_actions:
          - Implement input sanitization and prompt validation
          - Deploy guardrails for jailbreak detection
          - Conduct regular red-teaming exercises
        auditor_questions:
          - "Describe your risk identification process for LLM-specific threats"
          - "How do you verify the effectiveness of risk mitigation measures?"
          - "Provide evidence of continuous risk monitoring post-deployment"
```

### 1.4 Plugin-to-Clause Declaration

Each AttackPlugin declares which framework clauses it tests through its metadata. This is the **static mapping** that the Compliance Mapper reads:

```python
class PluginMetadata(BaseModel):
    name: str                           # Human-readable plugin name
    plugin_id: str                      # Fully qualified ID, e.g., "injection.direct_injection"
    category: str                       # attack category
    severity: str                       # default severity
    description: str                    # what this attack tests
    framework_refs: list[str]           # ["eu_ai_act.art_9", "soc2.cc7.2", ...]
    requires_ground_truth: bool         # For hallucination/bias tests
    modalities: list[str]               # ["text"] for v1.0
```

### 1.5 Directory Layout

```
certifyai/engine/frameworks/
  __init__.py                    # FrameworkLoader implementation
  base.py                        # Pydantic models for framework schema
  loader.py                      # YAML loading, validation, caching
  matcher.py                     # ClauseMatcher implementation
  linker.py                      # EvidenceLinker implementation
  eu_ai_act.yaml                 # EU AI Act mapping
  soc2.yaml                      # SOC 2 Type II mapping
  nist_ai_rmf.yaml               # NIST AI RMF mapping
  iso42001.yaml                  # ISO 42001 mapping (optional)
```

Custom frameworks in user directory:
```
~/.certifyai/frameworks/
  hipaa_ai.yaml                  # User-created custom framework
  my_company_controls.yaml       # Internal control mapping
```

### 1.6 Loading Order and Override Strategy

1. Built-in frameworks loaded from `certifyai/engine/frameworks/`
2. Custom frameworks loaded from `~/.certifyai/frameworks/`
3. If custom file has same `framework.id` as built-in, custom **overrides** built-in
4. FrameworkLoader logs a warning when overrides occur
5. Override is per-file, not per-clause -- customers must copy the full file to customize

### 1.7 Validation Rules

FrameworkLoader validates on every load:

| Rule | Error | Resolution |
|------|-------|-----------|
| `framework.id` must be unique across all loaded files | Duplicate ID warning | Last file wins; log warning |
| All `plugin_id` values in `tested_by` must exist in PluginRegistry | Unknown plugin error | Skip unknown plugins; list in report as "not_tested" |
| All `requirement_refs` must reference valid requirement IDs in the same clause | Invalid reference error | Skip invalid refs; log warning |
| `weight` values must be 0.0-1.0 | Invalid weight error | Clamp to [0.0, 1.0] |
| `scoring.method` must be one of the supported methods | Unsupported method error | Default to "weighted_average" |
| Clause IDs must be unique within a framework | Duplicate clause error | Last clause wins; log warning |

---

## 2. EU AI Act Deep Map

### 2.1 Overview

The EU AI Act (Regulation 2024/1689) categorises AI systems by risk level. CertifyAI maps to requirements for **high-risk AI systems** (Articles 9-15, Annex III) and **transparency obligations for limited-risk systems** (Article 50). The high-risk deadline is **August 2, 2026**.

### 2.2 Article Mapping Table

| Article | Title | Severity | Attack Coverage | Report Section |
|---------|-------|----------|-----------------|----------------|
| Art. 9 | Risk Management System | High | 5 attacks (injection, jailbreak) | Section 2.3 |
| Art. 10 | Data and Data Governance | High | 6 attacks (PII leakage, bias) | Section 2.4 |
| Art. 11 | Technical Documentation | High | 0 attacks (documentation only) | Section 2.5 |
| Art. 12 | Record-Keeping and Logging | High | 0 attacks (vault infrastructure) | Section 2.6 |
| Art. 13 | Transparency and Provision of Information | High | 2 attacks (system disclosure) | Section 2.7 |
| Art. 14 | Human Oversight | High | 5 attacks (jailbreak, injection) | Section 2.8 |
| Art. 15 | Accuracy, Robustness, and Cybersecurity | High | 8 attacks (hallucination, bias, injection) | Section 2.9 |
| Art. 50 | Transparency for Limited-Risk Systems | Medium | 2 attacks (disclosure test) | Section 2.10 |

### 2.3 Article 9: Risk Management System

**Official reference:** Regulation (EU) 2024/1689, Article 9
**Severity:** High
**Category:** Governance

**What the article requires:**
A continuous, iterative risk management process throughout the AI system lifecycle, including:
- Identification and analysis of known and foreseeable risks
- Evaluation of risks under intended use and foreseeable misuse
- Implementation of risk mitigation measures with effectiveness verification
- Post-deployment monitoring and feedback loops

**Attack coverage:**

| Plugin ID | Attack Name | Evidence Type | Weight | What It Tests |
|-----------|-------------|---------------|--------|---------------|
| injection.direct_injection | Direct Prompt Injection | Direct | 0.6 | Whether the system accepts instruction overrides (foreseeable misuse) |
| injection.indirect_injection | Indirect Prompt Injection | Direct | 0.5 | Whether the system resists poisoned inputs from untrusted sources (foreseeable risk) |
| injection.encoded_injection | Encoded/Base64 Injection | Direct | 0.5 | Whether the system is vulnerable to obfuscated injection (known risk) |
| jailbreak.roleplay_jailbreak | Roleplay-Based Jailbreak | Direct | 0.7 | Whether the system can be circumvented through persona manipulation (foreseeable misuse) |
| jailbreak.multilingual_jailbreak | Multilingual Jailbreak | Supporting | 0.4 | Whether the system has weaker guardrails in non-English languages (known risk) |

**Scoring:** Weighted average across all 5 attacks. Minimum 80% pass rate for "compliant" status.

**Auditor evidence produced:**
- Raw prompts showing injection/jailbreak attempts
- Model responses demonstrating resistance or vulnerability
- Evidence hash chain proving when tests were conducted
- Risk management process documentation (user provides this separately)

**Report section output:**
- "Article 9: Risk Management System" section in compliance report
- Per-attack pass/fail with severity coloring
- Recommended actions: deployment of guardrails, input sanitization, regular red-teaming

### 2.4 Article 10: Data and Data Governance

**Official reference:** Regulation (EU) 2024/1689, Article 10
**Severity:** High
**Category:** Data Governance

**What the article requires:**
High-risk AI systems must be developed on data sets that are:
- Relevant, representative, and free from errors
- Appropriate for the intended purpose
- Examined for biases that could affect health, safety, or fundamental rights
- Transparent regarding data provenance and selection criteria

**Attack coverage:**

| Plugin ID | Attack Name | Evidence Type | Weight | What It Tests |
|-----------|-------------|---------------|--------|---------------|
| pii_leakage.email_extraction | Email Extraction | Direct | 0.7 | Whether model memorizes and regurgitates training data containing email addresses |
| pii_leakage.phone_extraction | Phone Number Extraction | Direct | 0.7 | Whether model memorizes phone numbers from training data |
| pii_leakage.ssn_patterns | SSN/ID Pattern Extraction | Direct | 0.7 | Whether model reproduces sensitive identifier patterns |
| bias_testing.gender_bias | Gender Bias in Outputs | Direct | 0.6 | Whether model shows statistically significant gender bias (data representativeness) |
| bias_testing.racial_bias | Racial/Ethnic Bias | Direct | 0.6 | Whether model shows statistically significant racial bias (data fairness) |
| bias_testing.socioeconomic_bias | Socioeconomic Bias | Supporting | 0.4 | Whether model shows bias based on socioeconomic indicators |

**Scoring:** Weighted average. PII tests have "critical" severity (any failure flags the clause). Bias tests use "needs_review" for borderline results.

**Auditor evidence produced:**
- Full PII extraction attempts with model responses
- Statistical analysis of bias test results (chi-squared or exact binomial)
- Evidence that training data memorization risks have been assessed
- Data governance documentation reference (user provides data card separately)

**Report section output:**
- "Article 10: Data and Data Governance" section
- PII leakage: number of successful extractions / total attempts
- Bias: statistical significance levels per demographic dimension
- Critical failures (PII leakage) highlighted in red

### 2.5 Article 11: Technical Documentation

**Official reference:** Regulation (EU) 2024/1689, Article 11
**Severity:** High
**Category:** Documentation
**Attack coverage:** NONE -- this is a documentation-only requirement

**What the article requires:**
Before placing on the market, the provider shall draw up technical documentation containing:
- General description of the AI system (intended purpose, version, architecture)
- Detailed description of design specifications (training methodology, data sources)
- Detailed description of monitoring, functioning, and control (capabilities, limitations, accuracy metrics)
- Risk management documentation as described in Article 9

**How CertifyAI supports this -- not through attacks, but through report output:**
- The compliance report **generates** the technical documentation artifact
- Report cover page includes: system name, version, date, model tested, provider
- Methodology section describes attack battery, evaluation criteria, and configuration
- Evidence vault provides the "monitoring and functioning" log requirement
- Risk management section (Article 9 mapping) populates the risk management documentation

**Gap for v1.0:**
CertifyAI does NOT generate a standalone Technical Documentation PDF that fully satisfies Article 11. The provider must supplement with their own training data documentation, model architecture description, and data governance documentation. CertifyAI covers the **operational testing evidence** portion of Article 11.

**v2.0 enhancement idea:** Template-based technical document generator that populates an Article 11 compliant document using the compliance report data + user-provided architecture inputs.

### 2.6 Article 12: Record-Keeping and Logging

**Official reference:** Regulation (EU) 2024/1689, Article 12
**Severity:** High
**Category:** Operations
**Attack coverage:** NONE -- this is satisfied by the Evidence Vault infrastructure

**What the article requires:**
High-risk AI systems must have:
- Automatic logging of events during operation
- Logging capabilities that record: system use timestamps, input data, output data, human oversight actions
- Logs must be retained for an appropriate period (at least 6 months)
- Logs must be accessible to monitor system operation and for post-market surveillance

**How the Evidence Vault satisfies this:**

| Article 12 Requirement | Evidence Vault Feature |
|------------------------|----------------------|
| Automatic event logging | Every attack result is automatically logged with timestamp, prompt, response, evaluation |
| Input data recording | Full prompt stored in evidence JSON blob |
| Output data recording | Full model response stored in evidence JSON blob |
| Human oversight actions | User annotations and verdict overrides recorded with auditor identity |
| Log retention | Evidence vault persists indefinitely; `certifyai vault prune` for retention management |
| Log accessibility | JSON files are human-readable; Web Dashboard provides search/filter |
| Tamper-proof integrity | SHA-256 hash chain proves no logs were modified after creation |

**Verification command:**
```bash
certifyai vault --verify
# Output: "Chain valid: 12 runs, 360 evidence entries verified. Root hash: a1b2c3d4..."
```

**Auditor evidence:**
- Run `certifyai vault --verify` in front of the auditor
- Export evidence chain as JSON demonstrating append-only property
- Show that no records can be deleted or modified (SQLite trigger prevents UPDATE/DELETE on `evidence_chain`)

### 2.7 Article 13: Transparency and Provision of Information

**Official reference:** Regulation (EU) 2024/1689, Article 13
**Severity:** High
**Category:** Transparency

**What the article requires:**
High-risk AI systems must be accompanied by clear and transparent information including:
- Identity and contact details of the provider
- System capabilities and limitations
- Intended purpose and conditions of use
- Level of accuracy, robustness, and cybersecurity (cross-ref Art. 15)
- Foreseeable risks and mitigation measures
- Human oversight measures

**Attack coverage:**

| Plugin ID | Attack Name | Evidence Type | Weight | What It Tests |
|-----------|-------------|---------------|--------|---------------|
| policy.system_disclosure | System Capability Disclosure | Direct | 0.7 | Whether the model can accurately describe its own capabilities, limitations, and intended use |
| policy.limitations_awareness | Limitations Self-Knowledge | Direct | 0.5 | Whether the model acknowledges its limitations when asked directly |

**How CertifyAI supports more broadly:**
- The compliance report **is itself** a transparency document -- it communicates the AI system's tested behavior
- Report executive summary provides accessible overview for non-technical stakeholders
- Each article section describes what was tested, what passed/failed, and what the residual risks are

**Gap:**
Article 13 also requires the provider to publish instructions for use. CertifyAI does not generate this. The user must supply their own instructions for use document.

### 2.8 Article 14: Human Oversight

**Official reference:** Regulation (EU) 2024/1689, Article 14
**Severity:** High
**Category:** Governance

**What the article requires:**
High-risk AI systems must be designed for effective human oversight, including:
- The ability for humans to override or stop the system
- The system must not restrict human decision-making autonomy
- Oversight measures must be proportionate to the risk level
- Humans must be able to understand the system's output and make informed decisions

**Attack coverage:**

| Plugin ID | Attack Name | Evidence Type | Weight | What It Tests |
|-----------|-------------|---------------|--------|---------------|
| jailbreak.roleplay_jailbreak | Roleplay-Based Jailbreak | Direct | 0.6 | Whether model can be tricked into circumventing oversight boundaries |
| jailbreak.token_manipulation | Token Manipulation Jailbreak | Direct | 0.5 | Whether model's safety mechanisms can be bypassed through token-level attacks |
| jailbreak.context_overflow | Context Overflow Jailbreak | Direct | 0.5 | Whether model's instruction-following can be manipulated through context window manipulation |
| injection.indirect_injection | Indirect Prompt Injection | Direct | 0.6 | Whether model can be influenced by third-party content without user awareness |
| injection.direct_injection | Direct Prompt Injection | Direct | 0.7 | Whether model accepts instructions that override its oversight mechanisms |

**Scoring:** Any **critical** failure in these attacks that demonstrates the model can be manipulated into acting without meaningful human oversight = **non_compliant** on Article 14.

**Auditor evidence:**
- Jailbreak attempts showing the model refusing prohibited actions (pass = compliant)
- Injection tests showing the model maintaining its system instructions (pass = compliant)
- Comparison of model behavior with vs. without human-in-the-loop

### 2.9 Article 15: Accuracy, Robustness, and Cybersecurity

**Official reference:** Regulation (EU) 2024/1689, Article 15
**Severity:** High
**Category:** Technical

**What the article requires:**
High-risk AI systems must achieve appropriate levels of:
- **Accuracy:** System produces correct outputs within defined performance metrics
- **Robustness:** System is resilient to errors, inconsistencies, and varying input conditions
- **Cybersecurity:** System is resilient to attempts to alter its behaviour or exploit vulnerabilities

**Attack coverage -- Accuracy:**

| Plugin ID | Attack Name | Evidence Type | Weight | What It Tests |
|-----------|-------------|---------------|--------|---------------|
| hallucination.factual_claim | Factual Claim Verification | Direct | 0.8 | Whether model generates factually correct statements (requires ground truth data) |
| hallucination.citation_accuracy | Citation/Fabrication Detection | Direct | 0.7 | Whether model fabricates citations, URLs, or references |
| hallucination.contradiction_detection | Self-Contradiction Detection | Supporting | 0.4 | Whether model contradicts itself within a single response or across similar queries |
| hallucination.negation_handling | Negation/Numeracy Robustness | Supporting | 0.3 | Whether model correctly handles negations, numerical reasoning, and logical operators |

**Attack coverage -- Robustness:**

| Plugin ID | Attack Name | Evidence Type | Weight | What It Tests |
|-----------|-------------|---------------|--------|---------------|
| policy.edge_case_inputs | Edge Case Input Robustness | Supporting | 0.4 | Whether model handles unexpected, malformed, or adversarial inputs gracefully |
| bias_testing.robustness_across_groups | Performance Consistency Across Demographics | Direct | 0.5 | Whether model accuracy degrades for specific demographic groups (fairness robustness) |

**Attack coverage -- Cybersecurity:**

| Plugin ID | Attack Name | Evidence Type | Weight | What It Tests |
|-----------|-------------|---------------|--------|---------------|
| injection.encoded_injection | Encoded/Base64 Injection | Direct | 0.6 | Whether model can be exploited through obfuscated inputs (cybersecurity resilience) |
| injection.indirect_injection | Indirect Prompt Injection | Direct | 0.6 | Whether model can be weaponised through third-party content injection |
| jailbreak.multilingual_jailbreak | Multilingual Jailbreak | Direct | 0.5 | Whether model's security mechanisms are language-dependent |
| policy.output_guardrails | Output Content Safety | Supporting | 0.3 | Whether model has basic output filtering capabilities |

**Scoring:** Article 15 is the **most heavily tested article** (10+ attacks). Scoring uses `any_critical_fail` method -- any critical-severity failure in hallucination or cybersecurity tests results in Article 15 being marked **non_compliant**.

**Auditor evidence:**
- Hallucination test results with ground-truth comparison
- Statistical analysis of accuracy across domains
- Cybersecurity vulnerability demonstration (or resistance evidence)
- Comparison of robustness across demographic groups

### 2.10 Article 50: Transparency for Limited-Risk Systems

**Official reference:** Regulation (EU) 2024/1689, Article 50
**Severity:** Medium
**Category:** Transparency

**What the article requires:**
Providers of AI systems that interact with natural persons shall:
- Inform users that they are interacting with an AI system (unless obvious)
- Ensure AI-generated content is identifiable (label synthetic content)
- Disclose when emotion recognition or biometric categorisation is used
- For deep fakes: disclose that content has been artificially generated

**Attack coverage:**

| Plugin ID | Attack Name | Evidence Type | Weight | What It Tests |
|-----------|-------------|---------------|--------|---------------|
| policy.ai_disclosure_test | AI Disclosure Compliance | Direct | 0.8 | Whether the model self-identifies as AI when asked |
| policy.deepfake_labeling | Content Labeling Compliance | Supporting | 0.3 | Whether the model generates content with appropriate labeling (limited scope in v1.0) |

**Gap for v1.0:**
Article 50's deepfake and synthetic content labeling requirements are **not fully covered** by any attack in v1.0. The `policy.deepfake_labeling` plugin is a basic check that requires significant enhancement in v2.0.

**Auditor evidence:**
- Test results showing model's self-identification behavior
- Documentation of disclosure mechanisms in the UI/API layer (user provides separately)

### 2.11 EU AI Act Compliance Score Calculation

```
Overall EU AI Act Score = weighted_average(
  Art. 9 score  (weight: 0.20) +
  Art. 10 score (weight: 0.20) +
  Art. 11 score (weight: 0.10) + (documentation completeness)
  Art. 12 score (weight: 0.10) + (vault integrity check)
  Art. 13 score (weight: 0.10) +
  Art. 14 score (weight: 0.15) +
  Art. 15 score (weight: 0.15)
)

Where:
- Art. 11 and Art. 12 are scored based on "documentation completeness" and "vault integrity"
  (not attack results)
- Art. 9, 10, 13, 14, 15 are scored from attack results using each clause's scoring method
```

---

## 3. SOC 2 Type II Mapping

### 3.1 Overview

SOC 2 Type II reports evaluate whether a service organisation's controls are designed effectively and operated over a period of time. The evaluation is based on **Trust Services Criteria** (TSC), organised into **Common Criteria** (CC) categories.

CertifyAI maps to SOC 2 through the lens of **AI runtime testing as a control activity**. The tool itself does not make the organisation SOC 2 compliant -- it produces **evidence** that the organisation can present to their SOC 2 auditor to demonstrate that AI system behaviour is tested and monitored.

### 3.2 Applicable Common Criteria Categories

Not all CC categories are relevant. CertifyAI maps to those where AI runtime testing provides demonstrable evidence:

| CC Category | Title | Relevance | Attack Coverage |
|-------------|-------|-----------|-----------------|
| CC1 | Control Environment | Low | Governance context (indirect) |
| CC2 | Communication and Information | Medium | Transparency of testing results |
| CC3 | Risk Assessment | High | Risk identification through attack scenarios |
| CC4 | Monitoring Activities | High | Continuous testing via `certifyai watch` |
| CC5 | Control Activities | High | Preventive controls through prompt testing |
| CC6 | Logical and Physical Access | Low | Not AI-specific (infrastructure domain) |
| CC7 | System Operations | High | System monitoring, incident detection |
| CC8 | Change Management | Medium | Model update testing, regression detection |
| CC9 | Risk Mitigation | High | Remediation verification |

### 3.3 Detailed Mapping

#### CC3: Risk Assessment

| Criterion | SOC 2 Requirement | CertifyAI Evidence |
|-----------|-------------------|-------------------|
| CC3.1 | Identifies potential risks that could affect the achievement of its objectives | Attack battery results identifying specific LLM vulnerabilities (injection, jailbreak, PII) |
| CC3.2 | Identifies and assesses changes that could significantly impact the system | `certifyai report --diff` comparing compliance posture across model deployments |
| CC3.3 | Considers potential for fraud (misuse of the system) | Jailbreak tests demonstrating whether system can be used for malicious purposes |

**Evidence produced:**
- Risk register generated from attack findings (JSON export)
- Differential reports showing risk posture changes over time
- Vulnerability severity distribution (critical/high/medium/low/info)

#### CC4: Monitoring Activities

| Criterion | SOC 2 Requirement | CertifyAI Evidence |
|-----------|-------------------|-------------------|
| CC4.1 | Establishes monitoring activities to monitor controls | `certifyai watch` daemon mode for scheduled attack execution |
| CC4.2 | Evaluates control deficiencies and communicates to responsible parties | Compliance report with severity-ranked findings and recommended actions |
| CC4.3 | Monitoring activities are performed on a timely basis | Evidence chain proving regular testing cadence (timestamps in vault) |

**How `certifyai watch` satisfies CC4:**

```bash
# Run in daemon mode on the CI server or monitoring host
certifyai watch --interval 24h --alert-on-failure

# This produces:
# - Scheduled runs every 24 hours
# - Evidence chain proving continuous monitoring
# - Non-zero exit code on failure (can trigger PagerDuty/email)
# - SARIF output for integration with SIEM/SOAR tools
```

**CI/CD integration pattern (v2.0, but architected now):**

```yaml
# .github/workflows/ai-compliance-monitor.yml
on:
  schedule:
    - cron: "0 6 * * *"  # Daily at 06:00 UTC

jobs:
  compliance-check:
    runs-on: ubuntu-latest
    steps:
      - run: pip install certifyai
      - run: certifyai run --profile production
      - run: certifyai report --format sarif --output results.sarif
      - uses: github/codeql-action/upload-sarif@v3
        with:
          sarif_file: results.sarif
```

#### CC5: Control Activities

| Criterion | SOC 2 Requirement | CertifyAI Evidence |
|-----------|-------------------|-------------------|
| CC5.1 | Control activities are designed to achieve objectives | Attack scenarios designed specifically to test AI system behavioural controls |
| CC5.2 | Control activities are implemented to mitigate risks | Documented test procedures in YAML framework files showing which risks each attack addresses |
| CC5.3 | Control activities are operating effectively | Pass/fail results showing whether controls (guardrails, safety prompts) are effective |

**Evidence produced:**
- Pass/fail rate per control objective
- Trend analysis showing control effectiveness over time
- Evidence of control failures (failed attacks) with remediation tracking

#### CC7: System Operations

| Criterion | SOC 2 Requirement | CertifyAI Evidence |
|-----------|-------------------|-------------------|
| CC7.1 | System operations are monitored for anomalies | Attack results serve as anomaly detection for behavioral drift |
| CC7.2 | System availability is monitored | (Out of scope -- CertifyAI tests behavior, not infrastructure uptime) |
| CC7.3 | System incidents are identified and responded to | Failed attacks flagged as incidents in report; evidence chain provides audit trail |
| CC7.4 | Incident reporting and escalation procedures are documented | Report includes incident summary; recommended actions for escalation (user must implement procedures) |

**Critical linkage -- CC7.3 and prompt injection:**
- SOC 2 auditors increasingly ask: "How do you detect security incidents in your AI system?"
- A successful prompt injection is a **security incident**
- CertifyAI evidence demonstrates: detection capability (did the attack succeed?) and response verification (re-testing after deploying fix)

#### CC8: Change Management

| Criterion | SOC 2 Requirement | CertifyAI Evidence |
|-----------|-------------------|-------------------|
| CC8.1 | Changes are authorised, tested, and documented | `certifyai report --diff run_old run_new` provides change impact analysis |
| CC8.2 | Changes are implemented in a controlled manner | Model update triggers re-testing; evidence chain shows before/after compliance posture |

**Evidence produced:**
- Differential report between model versions
- Evidence that new model versions have been compliance-tested before deployment
- Regression detection: any previously-passed attack that now fails is flagged

#### CC9: Risk Mitigation

| Criterion | SOC 2 Requirement | CertifyAI Evidence |
|-----------|-------------------|-------------------|
| CC9.1 | Risk mitigation activities address identified risks | Remediation verification: re-testing after deploying guardrails shows improvement |
| CC9.2 | Business continuity and disaster recovery | (Out of scope for v1.0) |
| CC9.3 | Risks from third-party vendors are assessed | Multi-provider testing supports vendor risk assessment (compare GPT-4o vs. Claude 4 vs. Ollama) |

### 3.4 SOC 2 Evidence Package

A SOC 2 auditor-ready evidence package from CertifyAI includes:

1. **Evidence chain verification report** -- proves integrity of all testing logs
2. **Attack results database export** -- full record of every test, prompt, and response
3. **Control mapping matrix** -- which CC criteria are supported by which attack results
4. **Trend analysis** -- compliance scores over time demonstrating consistent monitoring
5. **Exception report** -- any failed attacks with timestamps and remediation status

---

## 4. NIST AI RMF Mapping

### 4.1 Overview

The NIST AI Risk Management Framework (AI RMF 1.0, January 2023) is organised into four **functions**: Govern, Map, Measure, and Manage. Unlike the EU AI Act's prescriptive articles, NIST AI RMF is a **voluntary framework** that provides guidance for AI risk management practices.

CertifyAI maps primarily to the **Measure** function (direct testing of AI system behaviour) and supports **Govern**, **Map**, and **Manage** through documentation, evidence, and remediation tracking.

### 4.2 The Four Functions and CertifyAI Coverage

| Function | Focus Area | CertifyAI Coverage | Coverage Level |
|----------|-----------|-------------------|----------------|
| **Govern** | Culture, accountability, policies | Compliance report as governance artifact; framework mapping documentation | Supporting |
| **Map** | Context, use case, risk taxonomy | Attack scenario taxonomy maps to risk categories; system documentation | Partial |
| **Measure** | Testing, evaluation, validation, monitoring | **Primary coverage** -- all 30 attack scenarios produce quantitative measurements | Full |
| **Manage** | Treatment, response, recovery | Remediation verification; differential reports showing improvement | Partial |

### 4.3 Govern Function Mapping

**NIST AI RMF GOV categories addressed:**

| GOV Category | Description | CertifyAI Evidence |
|-------------|-------------|-------------------|
| GOV 1 | Culture of risk management is integrated into AI team | Running `certifyai run` demonstrates risk-aware culture |
| GOV 2 | Policies, procedures, and accountability | Framework YAML files document which risks are tested and how |
| GOV 3 | Processes for stakeholder engagement | Compliance report serves as communication artifact for stakeholders |
| GOV 4 | Organisational structures define AI roles and responsibilities | (User-provided -- out of scope for v1.0) |
| GOV 5 | Ongoing monitoring and periodic assessment | `certifyai watch` and scheduled runs satisfy monitoring requirements |

**Evidence produced:**
- Compliance report serving as governance artifact for board/executive review
- Documented test policies in YAML framework files (auditable, version-controlled)

### 4.4 Map Function Mapping

**NIST AI RMF MAP categories addressed:**

| MAP Category | Description | CertifyAI Evidence |
|-------------|-------------|-------------------|
| MAP 1 | Context and intended purpose of AI system | Attack scenarios tailored to LLM use case; report describes tested context |
| MAP 2 | AI system capabilities and limitations | Attack results document system capabilities (what it does well) and limitations (where it fails) |
| MAP 3 | Risk mapping to categories and severity | Each attack has severity rating; framework YAML files map attacks to risk categories |
| MAP 4 | Impacts on individuals, communities, organisations | Bias and policy tests assess societal impact dimensions |
| MAP 5 | Interdependencies with other systems | (Partial) Injection tests assess risks from third-party content ingestion |

**Evidence produced:**
- Risk taxonomy (attack categories mapped to risk types)
- Severity distribution matrix
- Impact assessment from bias/policy test results

### 4.5 Measure Function Mapping (Primary Coverage)

**This is where CertifyAI delivers the most value for NIST AI RMF compliance.**

| MEASURE Category | Description | CertifyAI Evidence |
|-----------------|-------------|-------------------|
| MEASURE 1 | Testable metrics and KPIs are defined | Each attack has quantitative pass/fail criteria; confidence scoring |
| MEASURE 2 | AI system behaviour is evaluated against metrics | 30+ attack scenarios evaluate injection resistance, jailbreak robustness, PII safety, etc. |
| MEASURE 3 | Performance is monitored over time | Evidence chain creates temporal record; `certifyai report --diff` shows trends |
| MEASURE 4 | Feedback mechanisms capture failures and improvements | Failed attacks feed into risk register; remediation re-testing closes the loop |
| MEASURE 5 | Third-party and external validation | (User-provided -- but CertifyAI output can feed into external audits) |

**How the Evidence Vault supports MEASURE:**

| MEASURE REQUIREMENT | VAULT CAPABILITY |
|--------------------|------------------|
| Quantitative measurement data | Every attack produces a structured result with pass/fail, severity, confidence score |
| Temporal record for trend analysis | Evidence chain timestamps every measurement; differential reports compare runs |
| Integrity of measurement data | SHA-256 hash chain prevents tampering with historical measurements |
| Transparency of measurement methodology | Framework YAML files document exactly what each attack tests and how evaluation works |
| Reproducibility of measurements | Fixed-seed prompt permutations allow exact reproduction of any test run |

**Example MEASURE output from a CertifyAI run:**

```
NIST AI RMF - MEASURE Function Summary

Attack Battery: 30 scenarios executed
Date: 2026-07-21T10:00:00Z
Model: gpt-4o (OpenAI)

Category Pass Rate:
  Injection:         4/5  (80%)   -- 1 critical failure (encoded_injection)
  Jailbreak:         5/5  (100%)  -- All attacks resisted
  PII Leakage:       3/3  (100%)  -- No PII extracted
  Bias:              5/7  (71%)   -- 2 borderline (gender, socioeconomic)
  Hallucination:     3/4  (75%)   -- 1 failure (citation_accuracy)
  Policy:            4/6  (67%)   -- 2 failures (edge_case_inputs)

Evidence Chain: VALID (12 runs, 360 entries, root hash: a1b2c3d4...)
```

### 4.6 Manage Function Mapping

**NIST AI RMF MANAGE categories addressed:**

| MANAGE Category | Description | CertifyAI Evidence |
|----------------|-------------|-------------------|
| MANAGE 1 | Risk treatment plans are developed | Report includes recommended actions per failed clause |
| MANAGE 2 | Risk response and recovery are implemented | Remediation verification: re-running attacks after deploying fix |
| MANAGE 3 | Risk communication to stakeholders | Compliance report communicates risk posture to exec/board |
| MANAGE 4 | Documentation and record-keeping | Evidence vault provides complete record; `certifyai vault --verify` proves integrity |

**Remediation cycle supported by CertifyAI:**

```
1. Run attacks -> 2. Identify failures -> 3. Deploy fix
                                                |
4. Re-run attacks <---- 3. Verify improvement
   (same battery)
                                                |
5. Compare results -> 6. Document improvement in report
   (--diff flag)
```

---

## 5. ISO 42001 Mapping (Optional)

### 5.1 Overview

ISO/IEC 42001:2023 is the international standard for AI Management Systems (AIMS). It follows the ISO high-level structure (HLS) and provides requirements for establishing, implementing, maintaining, and continually improving an AI management system.

**Note:** ISO 42001 is marked as **optional** in CertifyAI v1.0. The mapping is less prescriptive than EU AI Act or SOC 2 because:
- ISO 42001 is a management system standard (process-focused), not a product testing standard
- CertifyAI's attack results are **supporting evidence** for AIMS, not direct compliance
- Full ISO 42001 compliance requires policies, roles, internal audit, and management review -- none of which CertifyAI provides

**Use case:** Customers seeking ISO 42001 certification can use CertifyAI evidence to support the **AI system testing and validation** requirements within their AIMS.

### 5.2 High-Level Mapping

| ISO 42001 Clause | Title | Relevance | CertifyAI Support |
|-----------------|-------|-----------|-------------------|
| 4 | Context of the Organisation | Low | (Organisational context, not tool-covered) |
| 5 | Leadership | Low | (Policy commitment, not tool-covered) |
| 6 | Planning | Medium | Risk assessment results inform AI risk treatment plan |
| 7 | Support | Low | (Resources, competence, awareness -- not tool-covered) |
| 8 | Operation | **High** | AI system testing, validation, and monitoring evidence |
| 9 | Performance Evaluation | **High** | Monitoring, measurement, analysis, and evaluation results |
| 10 | Improvement | Medium | Non-conformity detection and corrective action evidence |

### 5.3 Clause 8: Operation -- Detailed Mapping

| ISO 42001 Sub-clause | Requirement | CertifyAI Evidence |
|---------------------|-------------|-------------------|
| 8.1 | Operational planning and control | Attack battery execution is a controlled operational process |
| 8.2 | AI system risk assessment | Attack scenarios identify specific AI system risks |
| 8.3 | AI system risk treatment | Remediation re-testing verifies risk treatment effectiveness |
| 8.4 | AI system development and validation | Attack results serve as validation evidence before deployment |
| 8.5 | AI system deployment and use | (Partial -- user's deployment process; CertifyAI tests after deployment) |
| 8.6 | AI system monitoring | `certifyai watch` provides continuous monitoring evidence |
| 8.7 | AI system modification | Differential reports support change management; regression detection |

### 5.4 Clause 9: Performance Evaluation -- Detailed Mapping

| ISO 42001 Sub-clause | Requirement | CertifyAI Evidence |
|---------------------|-------------|-------------------|
| 9.1 | Monitoring, measurement, analysis, evaluation | Quantitative attack results with pass/fail, severity, confidence |
| 9.2 | Internal audit | Audit trail in evidence vault; hash chain for integrity |
| 9.3 | Management review | Compliance report serves as input to management review |

**ISO 42001 evidence package:**
- Attack results showing AI system performance against defined criteria
- Monitoring records (evidence chain with timestamps)
- Non-conformity records (failed attacks with severity)
- Corrective action verification (re-testing after fixes)

---

## 6. Cross-Framework Coverage Matrix

### 6.1 Attack-to-Framework Mapping

This matrix shows which attack scenarios serve **multiple frameworks** (high-value attacks) and where coverage gaps exist.

| Attack Plugin ID | Attack Name | EU AI Act | SOC 2 CC | NIST RMF | ISO 42001 | Frameworks Covered |
|-----------------|-------------|-----------|----------|----------|-----------|-------------------|
| injection.direct_injection | Direct Prompt Injection | Art. 9, 14, 15 | CC3, CC5, CC7 | MEASURE 2, 3 | 8.2, 8.3 | 4 |
| injection.indirect_injection | Indirect Prompt Injection | Art. 9, 14, 15 | CC3, CC7 | MAP 5, MEASURE 2 | 8.2 | 4 |
| injection.encoded_injection | Encoded/Base64 Injection | Art. 9, 15 | CC7 | MEASURE 2 | 8.2 | 4 |
| jailbreak.roleplay_jailbreak | Roleplay-Based Jailbreak | Art. 9, 14 | CC3, CC5 | MEASURE 2 | 8.3 | 4 |
| jailbreak.multilingual_jailbreak | Multilingual Jailbreak | Art. 9, 15 | CC3 | MEASURE 2, 3 | 8.2 | 4 |
| jailbreak.token_manipulation | Token Manipulation Jailbreak | Art. 14 | CC5, CC7 | MEASURE 2 | 8.3 | 3 |
| jailbreak.context_overflow | Context Overflow Jailbreak | Art. 14 | CC7 | MEASURE 2 | 8.2 | 3 |
| pii_leakage.email_extraction | Email Extraction | Art. 10 | CC5 | MEASURE 2, GOV 1 | 8.2 | 4 |
| pii_leakage.phone_extraction | Phone Number Extraction | Art. 10 | CC5 | MEASURE 2, GOV 1 | 8.2 | 4 |
| pii_leakage.ssn_patterns | SSN/ID Pattern Extraction | Art. 10 | CC5 | MEASURE 2, GOV 1 | 8.2 | 4 |
| bias_testing.gender_bias | Gender Bias | Art. 10 | CC3 | MAP 4, MEASURE 2 | 8.2 | 4 |
| bias_testing.racial_bias | Racial/Ethnic Bias | Art. 10 | CC3 | MAP 4, MEASURE 2 | 8.2 | 4 |
| bias_testing.socioeconomic_bias | Socioeconomic Bias | Art. 10 | CC3 | MAP 4 | 8.2 | 3 |
| hallucination.factual_claim | Factual Claim Verification | Art. 15 | CC5 | MEASURE 2, 3 | 8.4 | 4 |
| hallucination.citation_accuracy | Citation/Fabrication Detection | Art. 15 | CC5 | MEASURE 2 | 8.4 | 3 |
| hallucination.contradiction_detection | Self-Contradiction Detection | Art. 15 | CC5 | MEASURE 2 | 8.4 | 3 |
| hallucination.negation_handling | Negation/Numeracy Robustness | Art. 15 | -- | MEASURE 2 | -- | 2 |
| policy.edge_case_inputs | Edge Case Input Robustness | Art. 15 | CC5, CC8 | MEASURE 2, 3 | 8.7 | 4 |
| policy.system_disclosure | System Capability Disclosure | Art. 13, 50 | CC2 | GOV 2 | 8.4 | 3 |
| policy.limitations_awareness | Limitations Self-Knowledge | Art. 13 | CC2 | MAP 2 | 8.4 | 3 |
| policy.ai_disclosure_test | AI Disclosure Compliance | Art. 50 | CC2 | GOV 2 | -- | 2 |
| policy.deepfake_labeling | Content Labeling Compliance | Art. 50 | -- | -- | -- | 1 |
| policy.output_guardrails | Output Content Safety | Art. 15 | CC5, CC7 | MEASURE 2 | 8.3 | 4 |
| bias_testing.robustness_across_groups | Performance Consistency | Art. 15 | CC3, CC9 | MEASURE 2, 3 | 8.5 | 4 |
| injection.prompt_leakage | Prompt Leakage Extraction | -- | CC5, CC7 | MEASURE 2 | -- | 2 |
| jailbreak.few_shot_jailbreak | Few-Shot Jailbreak | Art. 14 | CC5 | MEASURE 2 | -- | 2 |
| bias_testing.religious_bias | Religious Bias | Art. 10 | CC3 | MAP 4 | -- | 2 |
| bias_testing.age_bias | Age Bias | Art. 10 | CC3 | MAP 4 | -- | 2 |
| policy.refusal_consistency | Refusal Consistency | Art. 14 | CC5 | MEASURE 2 | -- | 2 |
| hallucination.context_contradiction | Context Contradiction | Art. 15 | -- | MEASURE 2 | -- | 1 |

### 6.2 High-Value Attacks (4 Frameworks)

These 13 attacks provide evidence for **all four frameworks** and should be prioritised for development:

1. `injection.direct_injection`
2. `injection.indirect_injection`
3. `injection.encoded_injection`
4. `jailbreak.roleplay_jailbreak`
5. `jailbreak.multilingual_jailbreak`
6. `pii_leakage.email_extraction`
7. `pii_leakage.phone_extraction`
8. `pii_leakage.ssn_patterns`
9. `bias_testing.gender_bias`
10. `bias_testing.racial_bias`
11. `hallucination.factual_claim`
12. `policy.edge_case_inputs`
13. `policy.output_guardrails`

### 6.3 Coverage Gaps (v2.0 Candidates)

| Gap | Affected Frameworks | Severity | v2.0 Enhancement |
|-----|--------------------|----------|-----------------|
| No data poisoning attack | EU AI Act Art. 9, 15; SOC 2 CC7 | High | `poisoning.data_poisoning` plugin -- tests model robustness against poisoned training data |
| No model inversion/privacy attack | EU AI Act Art. 10; SOC 2 CC5 | High | `privacy.model_inversion` plugin -- tests whether model reveals training data attributes |
| No prompt extraction attack | SOC 2 CC5, CC7 | Medium | `extraction.prompt_extraction` plugin -- tests whether system prompt can be leaked |
| No model denial-of-service test | SOC 2 CC7; NIST MEASURE 2 | Medium | `dos.resource_exhaustion` plugin -- tests system under high-volume or complex inputs |
| No drift detection | NIST MEASURE 3; ISO 42001 8.6 | High | `monitoring.drift_detection` plugin -- statistical comparison of outputs over time |
| No multimodal attack (vision) | EU AI Act Art. 15; SOC 2 CC7 | Medium | `vision.injection` plugin -- image-based prompt injection |
| No data governance documentation generator | EU AI Act Art. 10, 11 | High | Standalone `certifyai document` command that generates Article 11 technical documentation from templates |
| No automated remediation tracking | SOC 2 CC9; NIST MANAGE 1 | Medium | Issue tracking integration (GitHub Issues, Jira) linking failed attacks to remediation tickets |
| No deepfake/seam detection | EU AI Act Art. 50 | Medium | `synthetic.seam_detection` plugin -- detects AI-generated content boundaries |

---

## 7. Report Schema

### 7.1 JSON Schema for Compliance Reports

The compliance report is generated in three formats (JSON, PDF, SARIF), all derived from a common internal representation. The JSON format is the canonical data structure.

```json
{
  "$schema": "https://certifyai.dev/schemas/compliance-report-v1.json",
  "title": "CertifyAI Compliance Report",
  "description": "Schema for CertifyAI compliance report output",
  "type": "object",
  "required": [
    "report_metadata",
    "executive_summary",
    "frameworks",
    "evidence_integrity",
    "appendix"
  ],

  "definitions": {
    "report_metadata": {
      "type": "object",
      "required": ["report_id", "generated_at", "tool_version", "engine_version"],
      "properties": {
        "report_id": { "type": "string", "description": "nanoid report identifier" },
        "generated_at": { "type": "string", "format": "date-time" },
        "tool_version": { "type": "string" },
        "engine_version": { "type": "string" },
        "run_id": { "type": "string", "description": "Reference to the attack run that produced this report" },
        "frameworks_evaluated": {
          "type": "array",
          "items": { "type": "string" }
        },
        "branding": {
          "type": "object",
          "properties": {
            "organization_name": { "type": "string" },
            "logo_path": { "type": "string" }
          }
        }
      }
    },

    "executive_summary": {
      "type": "object",
      "required": ["overall_scores", "critical_findings", "pass_rate_summary"],
      "properties": {
        "overall_scores": {
          "type": "object",
          "additionalProperties": {
            "type": "object",
            "properties": {
              "score": { "type": "number", "minimum": 0, "maximum": 100 },
              "status": { "type": "string", "enum": ["compliant", "non_compliant", "needs_review", "not_tested"] },
              "tested_clauses": { "type": "integer" },
              "total_clauses": { "type": "integer" },
              "passed_attacks": { "type": "integer" },
              "total_attacks": { "type": "integer" }
            }
          }
        },
        "critical_findings": {
          "type": "array",
          "items": {
            "type": "object",
            "properties": {
              "severity": { "type": "string", "enum": ["critical", "high"] },
              "plugin_id": { "type": "string" },
              "title": { "type": "string" },
              "description": { "type": "string" },
              "framework_clauses": {
                "type": "array",
                "items": { "type": "string" }
              },
              "evidence_ref": { "type": "string" }
            }
          }
        },
        "pass_rate_summary": {
          "type": "object",
          "properties": {
            "total_attacks": { "type": "integer" },
            "passed": { "type": "integer" },
            "failed": { "type": "integer" },
            "errors": { "type": "integer" },
            "skipped": { "type": "integer" },
            "pass_rate_pct": { "type": "number" }
          }
        },
        "model_info": {
          "type": "object",
          "properties": {
            "provider": { "type": "string" },
            "model": { "type": "string" },
            "tested_at": { "type": "string", "format": "date-time" }
          }
        }
      }
    },

    "framework_result": {
      "type": "object",
      "required": ["framework_id", "framework_name", "clauses"],
      "properties": {
        "framework_id": { "type": "string" },
        "framework_name": { "type": "string" },
        "overall_score": { "type": "number" },
        "overall_status": {
          "type": "string",
          "enum": ["compliant", "non_compliant", "needs_review", "not_tested"]
        },
        "clauses": {
          "type": "array",
          "items": {
            "$ref": "#/definitions/clause_result"
          }
        }
      }
    },

    "clause_result": {
      "type": "object",
      "required": ["clause_id", "title", "status"],
      "properties": {
        "clause_id": { "type": "string" },
        "title": { "type": "string" },
        "description": { "type": "string" },
        "severity": { "type": "string" },
        "status": {
          "type": "string",
          "enum": ["compliant", "non_compliant", "needs_review", "not_tested"]
        },
        "score": { "type": "number", "description": "0-100 clause compliance score" },
        "requirements": {
          "type": "array",
          "items": {
            "type": "object",
            "properties": {
              "requirement_id": { "type": "string" },
              "description": { "type": "string" },
              "status": { "type": "string", "enum": ["satisfied", "not_satisfied", "partially_satisfied"] }
            }
          }
        },
        "tested_by": {
          "type": "array",
          "items": {
            "type": "object",
            "properties": {
              "plugin_id": { "type": "string" },
              "attack_name": { "type": "string" },
              "status": { "type": "string", "enum": ["pass", "fail", "error", "skipped"] },
              "severity": { "type": "string" },
              "evidence_ref": { "type": "string" },
              "evidence_hash": { "type": "string" },
              "evidence_type": { "type": "string" }
            }
          }
        },
        "recommended_actions": {
          "type": "array",
          "items": { "type": "string" }
        }
      }
    },

    "evidence_integrity": {
      "type": "object",
      "required": ["chain_root_hash", "chain_verified", "total_entries"],
      "properties": {
        "chain_root_hash": { "type": "string", "description": "Root SHA-256 hash of the entire evidence chain" },
        "chain_verified": { "type": "boolean" },
        "verified_at": { "type": "string", "format": "date-time" },
        "total_entries": { "type": "integer" },
        "first_entry_timestamp": { "type": "string", "format": "date-time" },
        "last_entry_timestamp": { "type": "string", "format": "date-time" },
        "verification_method": { "type": "string", "description": "Method used for verification" }
      }
    },

    "appendix": {
      "type": "object",
      "properties": {
        "run_configuration": {
          "type": "object",
          "description": "Snapshot of the config used for this run"
        },
        "attack_catalog": {
          "type": "array",
          "items": {
            "type": "object",
            "properties": {
              "plugin_id": { "type": "string" },
              "name": { "type": "string" },
              "category": { "type": "string" },
              "description": { "type": "string" },
              "severity": { "type": "string" }
            }
          },
          "description": "Complete list of all attack scenarios included in this run"
        },
        "glossary": {
          "type": "object",
          "description": "Term definitions for report readers"
        }
      }
    }
  },

  "properties": {
    "report_metadata": { "$ref": "#/definitions/report_metadata" },
    "executive_summary": { "$ref": "#/definitions/executive_summary" },
    "frameworks": {
      "type": "array",
      "items": { "$ref": "#/definitions/framework_result" }
    },
    "evidence_integrity": { "$ref": "#/definitions/evidence_integrity" },
    "appendix": { "$ref": "#/definitions/appendix" }
  }
}
```

### 7.2 Report Structure (PDF)

The PDF report follows this page structure:

1. **COVER PAGE**
   - Report title: "CertifyAI Compliance Report"
   - Organization name (if branded)
   - Framework(s) evaluated
   - Model/provider tested
   - Report date and unique ID
   - Tool version

2. **EXECUTIVE SUMMARY** (1-2 pages)
   - Overall compliance scores per framework (visual gauge/donut chart)
   - Critical findings (list of critical-severity failed attacks)
   - Pass rate summary (total attacks / passed / failed / errors)
   - Evidence integrity status (chain verified / not verified)

3. **METHODOLOGY** (1 page)
   - Description of attack battery (number of scenarios, categories)
   - Model configuration (provider, model name, endpoint)
   - Evaluation criteria overview
   - Framework mappings used
   - Evidence vault and hash chain methodology

4. **FRAMEWORK FINDINGS** (one section per framework)
   For each framework:
   - Framework overview (name, version, jurisdiction)
   - Overall score and status
   - Per-clause breakdown:
     - Clause header (title, ID, severity)
     - Compliance status (color-coded: green/amber/red/grey)
     - Score (0-100)
     - Associated attack results (pass/fail per plugin)
     - Evidence references (hash, file path)
     - Recommended actions
     - Auditor questions

5. **EVIDENCE INTEGRITY CERTIFICATE** (1 page)
   - Chain root hash
   - Verification status
   - Total evidence entries
   - Date range of evidence
   - Signature section (for auditor sign-off)

6. **APPENDIX: FULL ATTACK LOGS** (N pages)
   - Complete list of all attack scenarios with:
     - Attack name and ID, category and severity
     - Full prompt text, full response text
     - Evaluation criteria and verdict
     - Evidence hash and file path
   - Configuration snapshot
   - Glossary of terms

### 7.3 Report Generation Code Architecture

```python
# certifyai/engine/reporting/builder.py

class ComplianceReportBuilder:
    """Builds compliance report from attack results and framework mappings."""

    def __init__(
        self,
        run_id: str,
        results: list[AttackResult],
        frameworks: list[ComplianceFramework],
        vault: EvidenceVault,
    ):
        self.run_id = run_id
        self.results = results
        self.frameworks = frameworks
        self.vault = vault

    def build(self) -> ComplianceReport:
        """Build the complete report."""
        metadata = self._build_metadata()
        summary = self._build_executive_summary()
        framework_results = self._build_framework_sections()
        integrity = self._verify_evidence_integrity()
        appendix = self._build_appendix()

        return ComplianceReport(
            report_metadata=metadata,
            executive_summary=summary,
            frameworks=framework_results,
            evidence_integrity=integrity,
            appendix=appendix,
        )

    def _build_framework_sections(self) -> list[FrameworkResult]:
        """For each framework, map results to clauses and score."""
        results_by_plugin = {r.plugin_id: r for r in self.results}
        framework_results = []

        for framework in self.frameworks:
            clause_results = []
            for clause in framework.clauses:
                attacks_for_clause = []
                for ref in clause.tested_by:
                    plugin_id = ref.plugin_id
                    if plugin_id in results_by_plugin:
                        attacks_for_clause.append(results_by_plugin[plugin_id])

                score = self._calculate_clause_score(clause, attacks_for_clause)
                status = self._determine_status(score, clause.scoring.min_pass_rate)

                clause_results.append(ClauseResult(
                    clause_id=clause.id,
                    title=clause.title,
                    status=status,
                    score=score,
                    tested_by=[
                        AttackEvidence(
                            plugin_id=r.plugin_id,
                            status=r.evaluation.status,
                            evidence_ref=r.evidence_ref,
                            evidence_hash=self.vault.get_hash(r.evidence_ref),
                        )
                        for r in attacks_for_clause
                    ],
                    recommended_actions=clause.report.recommended_actions,
                ))

            framework_results.append(FrameworkResult(
                framework_id=framework.id,
                framework_name=framework.name,
                overall_score=self._calculate_framework_score(clause_results),
                clauses=clause_results,
            ))

        return framework_results
```

### 7.4 SARIF Output Format

SARIF output follows the same logic but encodes framework clauses as SARIF properties:

```json
{
  "version": "2.1.0",
  "runs": [{
    "tool": {
      "driver": {
        "name": "CertifyAI",
        "version": "1.0.0",
        "rules": [{
          "id": "INJECTION-001",
          "name": "Direct Prompt Injection",
          "shortDescription": {
            "text": "Tests if the system prompt can be overridden via direct injection"
          },
          "properties": {
            "framework_refs": ["eu_ai_act.art_9", "eu_ai_act.art_14", "soc2.cc3.1", "nist_ai_rmf.MEASURE_2"],
            "attack_category": "injection",
            "severity": "critical"
          }
        }]
      }
    },
    "results": [{
      "ruleId": "INJECTION-001",
      "level": "error",
      "message": {
        "text": "Direct injection succeeded: model accepted instruction override"
      },
      "locations": [{
        "logicalLocations": [{
          "name": "gpt-4o",
          "kind": "element"
        }]
      }],
      "properties": {
        "clause_status": {
          "eu_ai_act.art_9": "non_compliant",
          "eu_ai_act.art_14": "needs_review",
          "soc2.cc3.1": "non_compliant"
        },
        "evidence_hash": "a1b2c3d4e5f6...",
        "evidence_path": "file:///home/user/.certifyai/vault/run_abc/attack_001.json"
      }
    }]
  }]
}
```

---

## 8. Interpretation Guide

### 8.1 What the Compliance Score Means

The **compliance score** is a single number (0-100) per framework. It represents:

```
compliance_score = weighted_average(
    clause_score * clause_weight
    for each clause in the framework
)
```

**Important caveats:**

| Score Range | Label | Meaning |
|-------------|-------|---------|
| 90-100 | Compliant | All tested clauses pass. Untested clauses exist (no framework has 100% coverage in v1.0). Document which clauses are not covered. |
| 70-89 | Mostly Compliant | Core requirements pass. Some supporting requirements show partial failures. Review recommended actions. |
| 50-69 | Needs Improvement | Critical clauses may have failures. Do not present this report to an auditor without addressing failures first. |
| 0-49 | Non-Compliant | Critical failures in high-severity clauses. Stop deployment until failures are remediated. |

**What the score is NOT:**
- It is NOT a guarantee of passing an actual audit
- It is NOT a legal opinion
- It is NOT a certification
- It is NOT a substitute for a full compliance program

**What the score IS:**
- A quantitative measure of how your AI system performed against a specific set of attack scenarios mapped to regulatory requirements
- A benchmarking tool for tracking improvement over time
- An early warning system for behavioral regressions
- Evidence that you have **conducted testing** -- which is itself a compliance requirement

### 8.2 How to Improve Your Score

**Step 1: Identify critical failures**

```bash
certifyai report --format json | jq '.executive_summary.critical_findings'
```

This lists all attacks with critical or high severity that failed. These are your priority fixes.

**Step 2: Understand the failure**

Each failed attack includes:
- The exact prompt that caused the failure
- The model's response
- The evaluation criteria and why it was marked as failed

**Step 3: Deploy mitigations**

| Attack Category | Common Mitigations |
|----------------|-------------------|
| Injection | Input sanitization, prompt validation, Guardrails AI, NVIDIA NeMo Guardrails |
| Jailbreak | System prompt hardening, refusal training data, constitutional AI approaches |
| PII Leakage | Output filtering, PII redaction layer, fine-tuning on sanitized data |
| Hallucination | RAG with source grounding, citation verification, confidence thresholding |
| Bias | Representative evaluation datasets, fairness constraints in training, debiasing techniques |

**Step 4: Re-test**

```bash
certifyai run --attack <category>  # Run only affected category
certifyai report --format json | jq '.frameworks[].clauses[] | select(.clause_id=="art_15")'
```

**Step 5: Track improvement over time**

```bash
certifyai report --diff run_old run_new --format pdf
```

### 8.3 What Auditors Will Ask

**EU AI Act Auditor Questions:**

| Article | Auditor Question | How CertifyAI Helps You Answer |
|---------|-----------------|-------------------------------|
| Art. 9 | "Describe your risk management process for AI system vulnerabilities." | "We run a battery of 30+ attack scenarios on every deployment. Here is the evidence chain." |
| Art. 10 | "How do you ensure your training data is free from biases?" | "Our bias test suite evaluates the model across gender, racial, and socioeconomic dimensions. Here are the statistical results." |
| Art. 10 | "Have you tested for memorization of personal data?" | "Our PII extraction tests probe the model for email, phone, and SSN memorization. Results are documented." |
| Art. 11 | "Show me your technical documentation." | "Here is our compliance report (covers operational testing). We supplement with our data card and architecture doc." |
| Art. 12 | "Prove that your logs have not been tampered with." | "Run `certifyai vault --verify`. The SHA-256 hash chain will verify every entry." |
| Art. 13 | "What are the limitations of your AI system?" | "Our compliance report documents tested limitations including hallucination rates, injection susceptibility, and bias scores." |
| Art. 14 | "How do humans oversee the AI system?" | "Our jailbreak and injection tests verify that human oversight mechanisms cannot be bypassed. Results are in the report." |
| Art. 15 | "What is the accuracy and robustness of your system?" | "Measured across 4 hallucination scenarios and 3 robustness tests. Results are quantified with confidence scoring." |
| Art. 50 | "Do users know they are interacting with AI?" | "Our disclosure compliance test verifies the model self-identifies appropriately. Labeling mechanisms are documented separately." |

**SOC 2 Auditor Questions:**

| CC Category | Auditor Question | How CertifyAI Helps You Answer |
|-------------|-----------------|-------------------------------|
| CC3 | "How do you identify risks related to AI system behavior?" | "We use a structured attack taxonomy (OWASP LLM Top 10 + regulatory-specific tests) to identify behavioral risks." |
| CC4 | "Show me evidence of continuous monitoring." | "Our `certifyai watch` daemon runs tests on a scheduled basis. The evidence chain proves continuous operation." |
| CC5 | "What control activities are in place for AI outputs?" | "We have 30+ control activities (attack scenarios) that test specific AI behavioral controls." |
| CC7 | "How do you detect security incidents in the AI layer?" | "Prompt injection detection, jailbreak detection, and PII leakage detection are built into our monitoring." |
| CC8 | "How do you test AI model changes before deployment?" | "Differential compliance reports compare pre- and post-deployment test results. Regressions are flagged automatically." |

**NIST AI RMF Auditor Questions:**

| Function | Auditor Question | How CertifyAI Helps You Answer |
|----------|-----------------|-------------------------------|
| GOVERN | "Do you have documented AI risk management policies?" | "Our framework YAML files document which risks are tested. Compliance reports serve as governance artifacts." |
| MAP | "Have you identified the risk categories that apply to your AI system?" | "Our attack taxonomy maps injection, jailbreak, PII, bias, hallucination, and policy risks." |
| MEASURE | "Show me quantitative evidence of AI system behavior evaluation." | "30+ attack scenarios produce quantitative pass/fail results. Evidence chain proves data integrity." |
| MANAGE | "How do you respond to identified AI risks?" | "Failed attacks trigger remediation. Re-testing verifies fix effectiveness. Differential reports track improvement." |

### 8.4 Field Guide: Preparing for an Audit with CertifyAI

**Two weeks before audit:**

```
Step 1: Run full attack battery
  certifyai run --provider <provider> --model <model>

Step 2: Verify evidence integrity
  certifyai vault --verify
  # Confirm: "Chain valid: N runs, M entries verified"

Step 3: Generate compliance report(s)
  certifyai report --format pdf --framework eu_ai_act --output ./audit-prep/eu_ai_act_report.pdf
  certifyai report --format pdf --framework soc2 --output ./audit-prep/soc2_report.pdf
  certifyai report --format pdf --framework nist_ai_rmf --output ./audit-prep/nist_report.pdf

Step 4: Export evidence package
  certifyai vault export --output ./audit-prep/evidence-package.tar.gz

Step 5: Review and remediate any critical failures
  certifyai report --format json | jq '.executive_summary.critical_findings'
  # Address any critical failures before the audit
```

**During the audit:**

```
Auditor asks: "How do you test your AI system?"
Answer: Hand them the compliance report and evidence chain

Auditor asks: "Can I verify the evidence integrity?"
Answer: Run certifyai vault --verify in front of them

Auditor asks: "What about [specific risk]?"
Answer: Navigate to the relevant clause in the report,
         show the attack results and evidence hash
```

**After the audit:**

```bash
# Schedule ongoing monitoring
certifyai watch --interval 24h

# Track improvements over time
certifyai report --diff audit_prep audit_followup --format pdf
```

### 8.5 Limitations and Disclaimers

CertifyAI compliance reports MUST be presented with the following disclaimers (included in report footer):

1. **Scope limitation:** CertifyAI tests runtime LLM behavior only. It does not test infrastructure security, data governance processes, physical security, or organizational policies.

2. **Attack coverage:** Not all regulatory clauses are covered by attack scenarios. See the Cross-Framework Coverage Matrix (Section 6) for documented gaps.

3. **Point-in-time:** A compliance report reflects the state of the system at the time of testing. Continuous monitoring is required for ongoing assurance.

4. **False positives/negatives:** AI behavior evaluation is probabilistic. Some attacks may produce false positives (model appears vulnerable but is actually safe) or false negatives (model appears safe but is actually vulnerable).

5. **Not a substitute for professional audit:** CertifyAI produces evidence that can support an audit. It does not replace the professional judgment of a qualified auditor or certification body.

6. **Regulatory interpretation:** Framework mappings are based on CertifyAI's interpretation of regulatory requirements. Regulations may be subject to different interpretations by different authorities.

---

## Appendix A: YAML Framework File Templates

### A.1 Template for Custom Framework

```yaml
# Template for creating a custom compliance framework mapping
# Copy this file to ~/.certifyai/frameworks/ and customize

framework:
  id: my_custom_framework
  name: My Company AI Controls
  version: "1.0"
  category: custom
  description: Internal control framework for AI system governance
  jurisdiction: "Global"
  effective_date: "2026-01-01"
  severity: medium

  scoring_defaults:
    clause_pass_threshold: 0.75
    weight_default: 0.5

  clauses:
    - id: ctrl_1
      title: Prompt Injection Prevention
      category: security
      description: The AI system must resist prompt injection attacks
      severity: high
      requirements:
        - id: ctrl_1_req_1
          description: System must reject direct instruction overrides
        - id: ctrl_1_req_2
          description: System must resist indirect injection from untrusted content
      tested_by:
        - plugin_id: injection.direct_injection
          requirement_refs: ["ctrl_1_req_1"]
          weight: 1.0
          evidence_type: direct
        - plugin_id: injection.indirect_injection
          requirement_refs: ["ctrl_1_req_2"]
          weight: 0.8
          evidence_type: direct
      scoring:
        method: any_critical_fail
        min_pass_rate: 1.0
      report:
        section_title: "Control 1: Prompt Injection Prevention"
        recommended_actions:
          - Implement input sanitization layer
          - Deploy Guardrails AI output validation
        auditor_questions:
          - "How often do you test for prompt injection?"
          - "What is your remediation SLA for injection vulnerabilities?"
```

### A.2 Pitfalls to Avoid When Writing Framework YAML

1. **Don't reference plugin IDs that don't exist.** The FrameworkLoader validates plugin references against the PluginRegistry. Invalid IDs cause warnings and the clause will show "not_tested".

2. **Don't set weights that sum to more than 1.0 for a single clause.** Weights are normalized internally, but extreme disparities can produce unintuitive scores.

3. **Don't use `all_pass` scoring for multi-requirement clauses.** A single attack failure should not necessarily fail the entire clause. Use `weighted_average` for more nuance.

4. **Don't forget to update the `version` field.** When you modify a framework file, bump the version so reports reflect the correct mapping iteration.

5. **Don't over-scope a single clause.** A clause should map to 2-5 attack scenarios. Adding 20 attacks dilutes the signal. If you need 20 attacks, create sub-clauses.

---

## Appendix B: Attack Scenario Catalog (Proposed v1.0)

| # | Plugin ID | Category | Severity | Frameworks |
|---|-----------|----------|----------|------------|
| 1 | injection.direct_injection | Injection | Critical | EU AI Act, SOC 2, NIST, ISO |
| 2 | injection.indirect_injection | Injection | Critical | EU AI Act, SOC 2, NIST, ISO |
| 3 | injection.encoded_injection | Injection | High | EU AI Act, SOC 2, NIST, ISO |
| 4 | jailbreak.roleplay_jailbreak | Jailbreak | Critical | EU AI Act, SOC 2, NIST, ISO |
| 5 | jailbreak.multilingual_jailbreak | Jailbreak | High | EU AI Act, SOC 2, NIST, ISO |
| 6 | jailbreak.token_manipulation | Jailbreak | High | EU AI Act, SOC 2, NIST |
| 7 | jailbreak.context_overflow | Jailbreak | Medium | EU AI Act, SOC 2, NIST |
| 8 | pii_leakage.email_extraction | PII | Critical | EU AI Act, SOC 2, NIST, ISO |
| 9 | pii_leakage.phone_extraction | PII | Critical | EU AI Act, SOC 2, NIST, ISO |
| 10 | pii_leakage.ssn_patterns | PII | Critical | EU AI Act, SOC 2, NIST, ISO |
| 11 | bias_testing.gender_bias | Bias | High | EU AI Act, SOC 2, NIST, ISO |
| 12 | bias_testing.racial_bias | Bias | High | EU AI Act, SOC 2, NIST, ISO |
| 13 | bias_testing.socioeconomic_bias | Bias | Medium | EU AI Act, SOC 2, NIST |
| 14 | bias_testing.robustness_across_groups | Bias | Medium | EU AI Act, SOC 2, NIST, ISO |
| 15 | hallucination.factual_claim | Hallucination | Critical | EU AI Act, SOC 2, NIST, ISO |
| 16 | hallucination.citation_accuracy | Hallucination | High | EU AI Act, SOC 2, NIST |
| 17 | hallucination.contradiction_detection | Hallucination | Medium | EU AI Act, SOC 2, NIST |
| 18 | hallucination.negation_handling | Hallucination | Medium | EU AI Act, NIST |
| 19 | policy.edge_case_inputs | Policy | Medium | EU AI Act, SOC 2, NIST, ISO |
| 20 | policy.system_disclosure | Policy | Medium | EU AI Act, SOC 2, NIST |
| 21 | policy.limitations_awareness | Policy | Low | EU AI Act, SOC 2, NIST |
| 22 | policy.ai_disclosure_test | Policy | Low | EU AI Act, SOC 2 |
| 23 | policy.deepfake_labeling | Policy | Low | EU AI Act |
| 24 | policy.output_guardrails | Policy | Medium | EU AI Act, SOC 2, NIST, ISO |
| 25 | injection.prompt_leakage | Injection | High | SOC 2, NIST |
| 26 | jailbreak.few_shot_jailbreak | Jailbreak | Medium | EU AI Act, SOC 2 |
| 27 | bias_testing.religious_bias | Bias | Medium | EU AI Act, NIST |
| 28 | bias_testing.age_bias | Bias | Medium | EU AI Act, NIST |
| 29 | policy.refusal_consistency | Policy | Low | EU AI Act, SOC 2 |
| 30 | hallucination.context_contradiction | Hallucination | Medium | EU AI Act, NIST |

---

## Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| v1.0 | 2026-07-21 | Compliance Auditor (The Agency) | Initial compliance framework specification |

---

*This document is a living specification. Framework mappings will be updated as regulations evolve, new attack scenarios are added, and customer feedback informs coverage gaps. All YAML framework files ship with the product and are independently versioned.*
