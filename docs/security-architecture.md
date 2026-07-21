# CertifyAI — Security Architecture & Threat Model

| Attribute | Value |
|-----------|-------|
| **Author** | Security Architect (The Agency) |
| **Status** | Draft v1 |
| **Version** | 1.0.0 |
| **Last Updated** | 2026-07-21 |
| **Scope** | Threat model (STRIDE), trust boundaries, evidence vault security, API key management, supply chain, secure defaults, incident response |
| **Methodology** | STRIDE per component, defense-in-depth, adversarial perspective |

---

## Table of Contents

1. [Trust Model](#1-trust-model)
2. [Threat Model (STRIDE per Component)](#2-threat-model-stride-per-component)
3. [Evidence Vault Security](#3-evidence-vault-security)
4. [API Key Management](#4-api-key-management)
5. [Web Dashboard Security](#5-web-dashboard-security)
6. [Supply Chain Security](#6-supply-chain-security)
7. [Secure Defaults](#7-secure-defaults)
8. [Incident Response](#8-incident-response)
9. [Security Roadmap](#9-security-roadmap)

---

## 1. Trust Model

### 1.1 Actors and Trust Classifications

| Actor | Trust Level | Rationale |
|-------|-------------|-----------|
| **Customer (primary user)** | **Fully trusted** | Installs and operates CertifyAI on their own machine. Has root/administrator access. Responsible for physical security of the host. |
| **External Auditor** | **Partially trusted** | Receives evidence packages and reports. Trusted to read evidence honestly. Not trusted with API keys or raw config. Given read-only access to evidence exports. |
| **LLM Provider Endpoint** | **Untrusted** | Remote API (OpenAI, Anthropic, Ollama, etc.). CertifyAI sends prompts to it; the provider returns responses. The provider could log prompts, inject malicious responses, or go down. |
| **PyPI / npm Registries** | **Partially trusted** | Distribution channel for the `certifyai` package and its dependencies. Compromise of a dependency or the registry itself could inject malicious code. |
| **GitHub** | **Partially trusted** | Hosts source code, releases, and CI/CD. A GitHub compromise could inject backdoors into signed releases. |
| **Gumroad** | **Partially trusted** | Payment processing and distribution for Pro/Enterprise tiers. Handles license key verification. Not trusted with any customer data beyond email and purchase info. |
| **Plugin Developers (future)** | **Untrusted** | Third-party plugin authors could write malicious attack plugins. Plugins execute local code with the same privileges as the Engine. |

### 1.2 Trust Boundaries

```
                         ┌──────────────────────────────────┐
                         │         CUSTOMER MACHINE          │
                         │  ┌────────────────────────────┐   │
                         │  │    TRUST ZONE              │   │
                         │  │  · Customer (user)         │   │
                         │  │  · CLI / TUI / Engine      │   │
                         │  │  · SQLite DB               │   │
                         │  │  · Evidence Vault          │   │
                         │  │  · Web Dashboard           │   │
                         │  │  · config.toml             │   │
                         │  └────────────────────────────┘   │
                         │              │                      │
                         │              │ HTTP/HTTPS           │
                         │              ▼                      │
                         │  ┌────────────────────────────┐   │
                         │  │    BOUNDARY ZONE           │   │
                         │  │  · PyPI (pip install)      │   │
                         │  │  · npm registry            │   │
                         │  │  · GitHub Releases         │   │
                         │  │  · Gumroad API (license)   │   │
                         │  └────────────────────────────┘   │
                         │              │                      │
                         └──────────────┼──────────────────────┘
                                        │
                                        ▼
                         ┌──────────────────────────────────┐
                         │      UNTRUSTED ZONE               │
                         │  · LLM Provider (API endpoint)    │
                         │  · Network attackers              │
                         │  · Malicious plugins (3rd party)  │
                         └──────────────────────────────────┘
```

**Key trust boundaries:**

1. **Customer machine boundary:** All CertifyAI processes run on the customer's machine. There is no cloud component. The customer is responsible for OS-level security (patching, malware, file permissions).

2. **Network boundary:** HTTPS is the only protocol crossing the machine boundary (LiteLLM → LLM provider, PyPI/npm installs, license check). The Web Dashboard, when exposed beyond localhost, becomes an additional network boundary.

3. **Process boundary:** CLI and TUI share the same Python process as the Engine (in-process calls via import). The Web Dashboard runs as a separate Node.js process but reads the same SQLite file directly. No IPC, no API server, no network between components.

4. **Plugin boundary:** Third-party plugins (future feature) execute Python code within the Engine process. This is the most dangerous trust boundary — plugin code has full access to the customer's machine.

### 1.3 Data Classification

| Data Class | Examples | Storage | Sensitivity |
|------------|----------|---------|-------------|
| **Secrets** | LLM API keys, license keys | `config` table (encrypted), also in `config.toml` (plaintext by default) | **Critical** — exposure allows unauthorized LLM usage at customer's cost |
| **Evidence** | Attack prompts, LLM responses, evaluation results | Filesystem vault (`attack_*.json`) + hash chain in SQLite | **High** — integrity is the product's core value. Disclosure may reveal proprietary prompts. |
| **Config** | Provider settings, concurrency, framework selection | `config` table + `config.toml` | **Low-Medium** — operational settings, not secret |
| **Compliance data** | Framework mappings, clause coverage, pass/fail | SQLite `results` + `framework_cache` tables | **Medium** — business-sensitive (reveals security posture) |
| **Audit logs** | Run history, timestamps, verification records | SQLite `evidence_chain` table | **Low** — metadata only |

---

## 2. Threat Model (STRIDE per Component)

### 2.1 CLI Container

**Trust level:** Runs in the customer's process space. Trusted by design.

| Threat | Scenario | Severity | Current Mitigation | Gap / Residual Risk |
|--------|----------|----------|-------------------|---------------------|
| **Spoofing** | Attacker creates a malicious `certifyai` shim on PATH (e.g., via pip confusion or PATH injection) | **High** | PyPI package name `certifyai` is unique as of v1.0. Package installed to a known Python bin directory. | No integrity check on the binary itself. Customer could unknowingly run a compromised version. Mitigation: checksum verification in docs. |
| **Tampering** | Attacker modifies CLI source files on disk (`.py` files in site-packages) | **High** | Package installed as `--user` or system site-packages, typically read-only to non-root users. | If attacker has write access to site-packages, they can modify any Python code. OS file permissions are the only defense. |
| **Repudiation** | User runs `certifyai run`, then claims they didn't | **Low** | Every run creates a `runs` table entry with `started_at` and `engine_version`. Evidence chain is append-only. | Logs are on the same machine. A sophisticated attacker could delete SQLite entries (though this breaks the evidence chain). |
| **Information Disclosure** | CLI output shows API keys in process list (via `ps aux`) | **High** | API keys passed via config file, not command-line arguments. Click doesn't log arguments by default. | A `--api-key` CLI flag (if added) would leak keys via process listing. **Mitigation: never accept secrets via CLI flags.** |
| **Denial of Service** | Attacker crafts a config that causes infinite loop or OOM | **Low** | `max_concurrency`, `request_timeout`, and `max_retries` have safe defaults. | If user removes limits, engine could exhaust memory. This is self-inflicted. |
| **Elevation of Privilege** | CLI uses `sudo` to access protected resources | **Medium** | CLI runs as the invoking user. No privilege escalation built in. | The `--install-completion` and init commands need write access to config dirs. If run as root inadvertently, config files owned by root become inaccessible to non-root user. |

**CLI-specific attack: Environment variable injection**
```
Scenario: Attacker controls an environment variable read by the config system
(e.g., `OPENAI_API_KEY` set by a CI/CD injection).
Severity: Medium
Mitigation: CLI reads config in priority order: CLI args > env vars > config.toml > DB.
If env vars override config, an attacker who can set env vars can swap API keys.
Residual: Environment variable injection is a CI/CD security problem, not a tool problem.
```

### 2.2 TUI Container

**Trust level:** Same process as Engine. Adds UI complexity that increases attack surface.

| Threat | Scenario | Severity | Current Mitigation | Gap / Residual Risk |
|--------|----------|----------|-------------------|---------------------|
| **Spoofing** | Attacker writes a malicious Textual theme or widget override via config injection | **Medium** | TUI loads themes from the `config` table. Config writes are authenticated (next-auth for dashboard, CLI consent for terminal). | No validation of theme CSS. A malicious theme could exfiltrate data via CSS-based XSS (limited in terminal context). |
| **Tampering** | Attacker modifies screen state to display false run results | **Medium** | TUI reads from SQLite on each screen render. It does not cache results across screens. | A compromised SQLite file = false TUI data. The TUI has no independent integrity check of displayed data. |
| **Repudiation** | TUI triggers a run, user claims TUI did it without their intent | **Low** | TUI requires explicit button press or key binding to start a run. Confirmation dialog before destructive actions. | Same as CLI — logs prove a run occurred, but not who pressed the key. Multi-user not supported. |
| **Information Disclosure** | Terminal scrollback buffer captures sensitive data (API keys, prompts) | **Medium** | Config screen masks API key input (`password=True` in Textual). Run output shows prompts but not keys. | Terminal scrollback is outside CertifyAI's control. User could scroll back and see full prompts. **Mitigation: document `clear` command or `history -c` after use.** |
| **Denial of Service** | TUI renders a huge number of results, causing terminal freeze | **Low** | Textual's virtual rendering handles large datasets. Pagination for run lists. | An attacker who can insert many SQLite rows (e.g., via direct DB access) could cause UI lag on initial screen load. |
| **Elevation of Privilege** | Textual's CSS engine or widget system has a code execution vulnerability | **High** | CertifyAI uses a pinned version of Textual. No custom widget loading from untrusted sources. | Textual is a relatively new framework. A vulnerability in Textual's CSS parser or message system could lead to RCE. **Mitigation: monitor Textual security advisories; text-based UI generally has smaller attack surface than browser-based.** |

**TUI-specific attack: Terminal escape sequence injection**
```
Scenario: An attacker controls data that the TUI displays (e.g., LLM response text
containing ANSI escape sequences). Malicious escape sequences could freeze the
terminal, read keystrokes, or execute commands (in vulnerable terminals like xterm).
Severity: Critical (if terminal is vulnerable) / Low (modern terminals)
Mitigation: Textual sanitizes output and uses its own rendering layer.
However, raw LLM responses are displayed. A response containing \x1b]2;...\x07
could set terminal title or worse.
Residual: CertifyAI should strip/purify ANSI escape sequences from LLM responses
before display. This is a gap.
```

### 2.3 Engine Container

**Trust level:** Core business logic. Most privileged component — has access to everything.

| Threat | Scenario | Severity | Current Mitigation | Gap / Residual Risk |
|--------|----------|----------|-------------------|---------------------|
| **Spoofing** | Attacker creates a malicious plugin that impersonates a legitimate one | **High** (post-v1 with plugin SDK) | v1: only built-in plugins, verified by package integrity. Plugin registry scans `certifyai.engine.plugins` only. | Post-v1: custom plugin directory allows dropping malicious `.py` files. No code signing or hash verification for plugins. |
| **Tampering** | Attacker modifies the evidence hash chain to hide a compliance failure | **Critical** | SHA-256 hash chain. Append-only SQLite trigger. Separate `chain.db` with linked hashes. | See [Section 3 — Evidence Vault Security](#3-evidence-vault-security) for full analysis. |
| **Tampering** | Attacker modifies framework YAML files to change compliance mappings | **Medium** | Framework YAML is shipped as part of the package (read-only in site-packages). Customer can override in `~/.certifyai/frameworks/`. | Custom framework files are not validated against a schema at startup. A malformed YAML could cause the Compliance Mapper to silently skip clauses. |
| **Repudiation** | Engine records a run with wrong `engine_version` due to import confusion | **Low** | `engine_version` is read from `certifyai.__version__` (set at install time). Git tags match PyPI versions. | If customer installs from source without proper version tagging, the version string could be wrong. |
| **Information Disclosure** | LiteLLM logs sensitive data (API keys, prompts) to Python logging or stderr | **High** | CertifyAI configures logging to capture its own messages. LiteLLM's internal logging is not controlled. | LiteLLM may log HTTP request headers (including `Authorization: Bearer <key>`) in debug mode. If customer enables debug logging, API keys could appear in logs. **Mitigation: add `LITELLM_LOG=WARN` environment variable recommendation in documentation.** |
| **Information Disclosure** | Evidence vault files contain full prompt text — sensitive proprietary prompts exposed | **Medium** | No current mitigation. Vault files are JSON on disk. | If prompt injection tests use actual production prompts (not synthetic), evidence files on disk contain those prompts. Customer should be warned. |
| **Denial of Service** | LiteLLM call hangs forever on a non-responsive model endpoint | **Medium** | `request_timeout` default 30s. `max_retries` default 3. `asyncio.TaskGroup` ensures teardown. | A malicious LLM provider could send a slow drip response that consumes connection pool. LiteLLM's timeout should handle this, but it's provider-dependent. |
| **Denial of Service** | Disk fills up with evidence vault files | **Low** | No automatic disk quota. Evidence files are ~5KB each. ~1000 runs = ~5GB. | Customer responsibility to monitor disk. `certifyai vault --prune` could be a future command. |
| **Elevation of Privilege** | Plugin import allows arbitrary code execution | **Critical** | v1: no custom plugins. Built-in plugins are reviewed and tested. | Post-v1 custom plugin SDK: a malicious plugin has full access to the Engine process, SQLite database, credentials, and network. See [Section 1.2 — Plugin boundary](#12-trust-boundaries). |

**Engine-specific attack: Prompt injection via LLM response**
```
Scenario: An LLM provider returns a crafted response that, when read by the Engine's
evaluation pipeline, exploits a regex ReDoS (Regular Expression Denial of Service)
or triggers a deserialization vulnerability.
Severity: Medium-High
Current mitigation: Evaluation uses regex patterns. No eval() or dynamic code execution.
Pydantic v2 validates AttackResult schema strictly.
Gap: A regex with catastrophic backtracking could hang the evaluation thread for
minutes. Mitigation: use `re.match` with timeout or switch to `regex` library
that supports timeouts. Set per-evaluation timeout.
```

### 2.4 Web Dashboard Container

**Trust level:** Optional component (Pro/Enterprise tiers). Adds network attack surface.

| Threat | Scenario | Severity | Current Mitigation | Gap / Residual Risk |
|--------|----------|----------|-------------------|---------------------|
| **Spoofing** | Attacker on the same network accesses the dashboard before auth is configured | **Critical** | Default: `next dev` binds to `localhost:3000`. Next.js 14 does not listen on `0.0.0.0` by default. | If the user starts the dashboard with `HOST=0.0.0.0` or behind a reverse proxy without auth, the dashboard is exposed. **Mitigation: add runtime check — warn if listening on non-localhost without auth configured.** |
| **Spoofing** | Attacker brute-forces the next-auth credentials login | **High** | next-auth credentials provider with username/password. SQLite-backed sessions. | No rate limiting on login attempts by default. `next-auth` does not include built-in brute-force protection. **Mitigation: add `@upstash/ratelimit` or a simple in-memory rate limiter (3 attempts per IP per minute).** |
| **Tampering** | Attacker modifies dashboard pages to display false data | **Medium** | Dashboard is a static Next.js build. Pages are rendered server-side from SQLite data. | If attacker gains write access to the filesystem, they can modify page content. But that's far beyond web app security — that's machine compromise. |
| **Repudiation** | Action performed via dashboard (trigger run, update config) is not logged | **Medium** | Next.js route handlers trigger `certifyai run` via subprocess. The run itself creates audit trail. | Config changes made via the dashboard's settings page are not logged with user attribution. You can't tell who changed a setting. **Mitigation: add audit_log table for config changes.** |
| **Information Disclosure** | Session token leaked via XSS or network sniffing | **High** | next-auth uses `httpOnly` and `secure` cookies (in production). CSRF token on mutations. | No Content Security Policy (CSP) header configured by default. XSS in a page could steal the session. **Mitigation: add CSP header via `next.config.js`.** |
| **Information Disclosure** | `better-sqlite3` error messages leak SQL schema in HTTP responses | **Medium** | Next.js server components catch errors. SQL errors would result in a 500 page, not raw SQL output. | Production builds don't show stack traces. Development mode (`next dev`) does — warn users not to expose dev mode to network. |
| **Denial of Service** | Attacker sends many concurrent requests to a route handler that spawns subprocesses | **Medium** | The "trigger run" endpoint spawns a CLI subprocess. If called 100 times, it spawns 100 processes. | No rate limiting on route handlers. A single `fetch('http://localhost:3000/api/run', {method: 'POST'})` in a loop could OOM the machine. **Mitigation: track if a run is already in progress and reject concurrent requests.** |
| **Denial of Service** | SQLite contention blocks dashboard reads while Engine writes | **Low** | WAL mode allows concurrent reads. Engine writes are short (INSERT of results). | Under heavy load (many results), a write transaction could briefly block reads. Sub-millisecond impact. Acceptable. |
| **Elevation of Privilege** | `better-sqlite3` vulnerability allows SQL injection | **Critical** | Dashboard uses parameterized queries via `better-sqlite3` prepared statements. | SQL injection is mitigated by design. However, if the dashboard ever constructs raw SQL strings (e.g., for dynamic filtering), injection risk returns. **Mitigation: use an ORM wrapper or query builder for any dynamic queries.** |
| **Elevation of Privilege** | The "trigger run" route handler executes arbitrary commands | **Critical** | `child_process.exec('certifyai run')` — the command is hardcoded. No user input in the command string. | If the route handler were to accept user-controlled arguments (e.g., `--attack` from a query parameter), that would enable command injection. **Mitigation: never interpolate user input into subprocess commands.** |

**Dashboard-specific attack: SSRF via malicious report link**
```
Scenario: The dashboard renders a report that contains an external URL (e.g., an
evidence reference pointing to an attacker-controlled server). The Next.js server
uses `fetch()` to load embedded content (if implemented).
Severity: Low (not currently implemented)
Current: Dashboard reads all data from local SQLite. No external fetch calls.
Residual: If future versions add "import from URL" or "report template from URL,"
implement URL allowlist and block private IP ranges.
```

### 2.5 SQLite Database

**Trust level:** Single-file database on filesystem. All components read/write to it.

| Threat | Scenario | Severity | Current Mitigation | Gap / Residual Risk |
|--------|----------|----------|-------------------|---------------------|
| **Spoofing** | Attacker creates a fake `certifyai.db` with fabricated results | **Medium** | Evidence chain verification checks hash integrity against the vault files. | A completely fake database would fail chain verification, but a naive user who only checks the dashboard (not the chain) could be fooled. **Mitigation: dashboard should display chain verification status prominently.** |
| **Tampering** | Attacker modifies `results` table to change pass → fail or vice versa | **High** | No checksum on individual result rows. If attacker modifies `results.status` from 'fail' to 'pass', the evidence chain still has the original hash. | The hash chain only covers evidence vault files, not individual SQLite rows. A discrepancy between `results.status` and the evidence evaluation is possible. **Mitigation: vault --verify should cross-check results table against evidence hashes.** |
| **Tampering** | Attacker deletes rows from `evidence_chain` to remove evidence of tampering | **High** | SQLite trigger rejects DELETE on `evidence_chain` (see [Section 3](#3-evidence-vault-security)). | If attacker disables triggers (`PRAGMA schema.trigger_list`), they can delete rows. This requires SQLite expert-level access. **Mitigation: monitor trigger integrity via vault --verify.** |
| **Tampering** | Attacker modifies `config` table to change LLM provider or API key | **High** | Config values for secrets are encrypted at rest (Fernet). | Non-secret config values (provider, model, concurrency) are plaintext. An attacker with DB write access could change the model to a weaker one for testing. |
| **Information Disclosure** | `certifyai.db` is backed up to an insecure location (Dropbox, S3) exposing results | **Medium** | No built-in encryption of the database file. | Customer responsibility. The DB contains evidence (prompts, responses). **Mitigation: document encryption-at-rest recommendations (BitLocker, FileVault, LUKS).** |
| **Information Disclosure** | SQLite WAL files (`-wal`, `-shm`) contain uncommitted data visible to other processes | **Low** | WAL files are in the same directory as the DB. On a single-user machine, no other process should read them. | If the customer's machine has malware that reads SQLite WAL files, committed and uncommitted data could be leaked. This is an OS-level threat. |
| **Denial of Service** | SQLite database corruption from sudden power loss | **Low** | WAL mode is crash-safe. `PRAGMA integrity_check` can detect corruption. | A corrupt SQLite file can lose data. **Mitigation: document `PRAGMA integrity_check` and backup strategy in deployment guide.** |
| **Elevation of Privilege** | SQL injection via the dashboard or CLI | **Low** | SQLAlchemy (Python) and `better-sqlite3` (Node.js) both use parameterized queries. | See dashboard EoP — if raw SQL is ever constructed, risk increases. |

### 2.6 Filesystem Evidence Vault

**Trust level:** Files are the source of truth for evidence. The chain depends on them.

| Threat | Scenario | Severity | Current Mitigation | Gap / Residual Risk |
|--------|----------|----------|-------------------|---------------------|
| **Spoofing** | Attacker creates fake evidence files in a run directory | **High** | Each evidence file must have a corresponding entry in `evidence_chain`. Random files are ignored by verification. | If attacker creates both the file AND adds a matching entry to `chain.db`, it passes verification. See [Section 3](#3-evidence-vault-security). |
| **Tampering** | Attacker modifies an evidence JSON file to change prompt or response | **Critical** | SHA-256 hash of each evidence file is stored. `vault --verify` recomputes hashes and detects mismatch. | **Detection only, not prevention.** An attacker who also updates the hash file and chain.db can hide the modification. |
| **Tampering** | Attacker deletes an entire run directory | **High** | The chain entry still exists in `evidence_chain` but verification shows files missing. | The run is marked as "tampered" but the evidence is gone. **Mitigation: this is an availability problem, not integrity. Backups solve this.** |
| **Repudiation** | User claims a specific evidence file is not authentic | **Low** | Hash chain provides cryptographic proof of existence at a point in time. | Without an external timestamp (e.g., RFC 3161 timestamp from a trusted authority), the user cannot prove the hash existed before a certain date. **Future mitigation: integrate with timestamp authority.** |
| **Information Disclosure** | Evidence files readable by other users on the same machine | **High** | Vault directory is created with `0o700` permissions (user-only). | On shared machines (CI runners, university clusters), other processes or users could read vault files. **Mitigation: document `chmod` and `umask` recommendations.** |
| **Denial of Service** | Attacker fills the filesystem with fake vault files | **Low** | No quota on vault directory. | Customer responsibility. Malware that fills disk is a host-level threat. |
| **Elevation of Privilege** | Symlink attack: attacker replaces an evidence file with a symlink to `/etc/passwd` | **Low** | Vault reads files, but only during verification. It doesn't follow symlinks for hashing by default. | If a plugin writes evidence to a path controlled by an attacker, a symlink could cause an arbitrary file read during vault operations. **Mitigation: `os.path.realpath()` checks before reading vault files.** |

### 2.7 STRIDE Summary Matrix

| Component | Spoofing | Tampering | Repudiation | Info Disclosure | DoS | Elevation |
|-----------|----------|-----------|-------------|-----------------|-----|-----------|
| **CLI** | High (PATH hijack) | High (code mod) | Low | High (key in args) | Low | Medium (sudo misconfig) |
| **TUI** | Medium (theme CSS) | Medium (screen state) | Low | Medium (scrollback) | Low | High (Textual vuln) |
| **Engine** | High (malicious plugin) | **Critical** (chain tamper) | Low | **High** (log leakage) | Medium (ReDoS) | **Critical** (plugin RCE) |
| **Web Dashboard** | **Critical** (net exposure) | Medium (page mod) | Medium (audit log gap) | **High** (no CSP) | Medium (process spawn) | **Critical** (cmd injection) |
| **SQLite** | Medium (fake DB) | **High** (row mod) | Low | Medium (backup leak) | Low | Low (param queries) |
| **Evidence Vault** | High (fake files) | **Critical** (evidence mod) | Low | High (file perms) | Low | Low (symlink) |

---

## 3. Evidence Vault Security

### 3.1 Hash Chain Design

The evidence vault uses a **SHA-256 hash chain** with a hybrid filesystem + SQLite architecture. This section analyzes its security properties in depth.

#### Chain Construction

```
 ┌─────────────────────────────────────────────────────────────┐
 │                     HASH CHAIN OVERVIEW                      │
 │                                                              │
 │  Genesis (run_0000000)                                       │
 │  previous_hash = "0" * 64   run_hash = SHA-256(run)          │
 │                              │                                │
 │                              ▼                                │
 │  Run a1b2c3d4                                                 │
 │  previous_hash = genensis_run_hash                            │
 │  run_hash = SHA-256(attack_001.json + attack_002.json + ...)  │
 │              │                                                │
 │              ▼                                                │
 │  Run e5f6g7h8                                                 │
 │  previous_hash = a1b2c3d4_run_hash                            │
 │  run_hash = SHA-256(...)                                      │
 │              │                                                │
 │              ▼                                                │
 │  Run h9i0j1k2                                                 │
 │  previous_hash = e5f6g7h8_run_hash                            │
 │  run_hash = SHA-256(...)                                      │
 │                                                              │
 │  Each run_hash = SHA-256( concatenated attack_NNN.hashes )   │
 │  Each attack_NNN.hash = SHA-256(attack_NNN.json)             │
 └─────────────────────────────────────────────────────────────┘
```

#### SHA-256 Sufficiency

- **Collision resistance:** SHA-256 has ~2^128 collision resistance. No practical collision attack exists. Sufficient for evidence integrity.
- **Preimage resistance:** Given a hash, an attacker cannot find a different evidence file that produces the same hash. This prevents hash replacement attacks.
- **Length extension:** SHA-256 (Merkle-Damgård) is vulnerable to length extension attacks, but this is irrelevant here — we're not building MACs, we're storing full hashes.

### 3.2 Append-Only Enforcement

```sql
-- The evidence_chain table has a trigger that prevents UPDATE and DELETE
CREATE TRIGGER IF NOT EXISTS prevent_evidence_chain_update
BEFORE UPDATE ON evidence_chain
BEGIN
    SELECT RAISE(ABORT, 'Evidence chain is append-only. UPDATE forbidden.');
END;

CREATE TRIGGER IF NOT EXISTS prevent_evidence_chain_delete
BEFORE DELETE ON evidence_chain
BEGIN
    SELECT RAISE(ABORT, 'Evidence chain is append-only. DELETE forbidden.');
END;
```

**Attack scenarios against append-only:**

| Attack | Can It Succeed? | Why |
|--------|-----------------|-----|
| **Regular UPDATE** | **Blocked** | SQLite trigger raises `ABORT` before the UPDATE executes. |
| **Regular DELETE** | **Blocked** | Same trigger mechanism. |
| **DROP TABLE evidence_chain** | **Possible** | SQLite triggers don't prevent DDL. If attacker has write access to `chain.db`, they can drop the table. |
| **Disable trigger via PRAGMA** | **Possible** | `PRAGMA schema.trigger_list` shows triggers. SQLite has no "disable triggers" command, but an attacker with the right permissions could recreate the table without triggers. |
| **Edit the .db file binary** | **Possible** | SQLite is a binary format. An attacker with hex editor access can modify pages directly. |
| **Replace chain.db with a custom file** | **Possible** | If attacker has write access to the vault directory, they can replace `chain.db` entirely. |
| **Write to WAL file** | **Possible** | In WAL mode, uncheckpointed writes live in `-wal`. An attacker with write access can manipulate WAL content. |

**Conclusion on append-only:** The SQLite trigger provides **tamper detection for casual tampering** (someone running `DELETE FROM evidence_chain`). It provides **zero protection against a determined attacker with filesystem write access**. This is by design — append-only is a deterrent, not a fortress.

### 3.3 Tamper Detection vs. Tamper Prevention

**This is the single most important security distinction in CertifyAI.**

| Property | Tamper Detection | Tamper Prevention |
|----------|-----------------|-------------------|
| **What it does** | Detects that evidence was modified after creation | Prevents modification from occurring |
| **CertifyAI approach** | SHA-256 hash chain + verification command | **None** (by design — we don't control the host OS) |
| **Effectiveness vs. casual attacker** | **High** — `vault --verify` catches any modification | N/A |
| **Effectiveness vs. root attacker** | **Low** — root can modify everything | N/A |
| **Auditor trust** | **High** — auditor can verify independently | N/A |

**Why CertifyAI chooses detection over prevention:**
- Prevention requires either:
  1. **Hardware security** (TPM, HSMs, YubiKey) — adds cost and complexity unsuitable for a $149 boilerplate
  2. **Remote attestation** (cloud-based chain) — contradicts the offline/boilerplate architecture
  3. **Write-once media** (CD-R, WORM drive) — impractical for a software tool
- Detection is honest: "We cannot prevent tampering on a machine you control. But we can make tampering detectable with cryptographic certainty."

### 3.4 Attack Deep-Dives: Evidence Tampering

#### Attack A: Modify an evidence file

1. **Attacker action:** Edit `attack_001.json` to change a "fail" result to "pass"
2. **Detection:** `vault --verify` recomputes `SHA-256(attack_001.json)` and finds it doesn't match `attack_001.hash`
3. **Outcome:** **Detected.** The run is flagged as "tampered." The `attack_001.hash` file still contains the original hash.
4. **The attacker would need to also:** Update `attack_001.hash` with the new hash, AND update `run.hash` (which is SHA-256 of all concatenated attack hashes), AND update `chain.db`'s `run_hash` for that entry, AND update all subsequent `previous_hash` entries in the chain to maintain linkage.
5. **Feasibility:** Easy for a single file. Becomes combinatorially harder the more files are modified. But still doable for a root attacker with hex editor access to `chain.db`.

#### Attack B: Modify chain.db to match modified evidence

1. **Attacker action:** Modify evidence files AND recompute all hashes AND write the correct new hashes to `chain.db`
2. **Detection:** If the attacker is thorough and the chain is self-consistent, `vault --verify` passes.
3. **Outcome:** **Undetected** — but only if the attacker correctly recomputed every single hash in the chain.
4. **What stops this:** Nothing. If the attacker has write access to both vault files and `chain.db`, they can make the chain consistent with modified data.
5. **Countermeasure:** External verification. If an auditor made a copy of the vault at time T and compares it to the vault at time T+1, any discrepancy is tampering. **This is why the export/import feature exists — auditors should snapshot the vault.**

#### Attack C: Rollback attack (delete the last N runs)

1. **Attacker action:** Delete `chain.db` entries for the last 3 runs and remove corresponding vault directories. The chain now ends at run N-3.
2. **Detection:** `vault --verify` will only verify runs N-3 and earlier. It doesn't know about the deleted runs unless a separate audit log tracks run IDs.
3. **Outcome:** **Detectable only if run IDs are tracked externally.** The `runs` table has a record of all runs — if the `runs` table shows runs that `evidence_chain` doesn't, that's a discrepancy.
4. **Mitigation:** `vault --verify` should cross-reference `runs` table against `evidence_chain` and report orphaned runs.

#### Attack D: Replace the entire vault with a fabricated one

1. **Attacker action:** Delete `~/.certifyai/vault/` and replace with a custom vault containing only "pass" results. Generate a new `chain.db` with matching hashes.
2. **Detection:** Zero — if the vault is self-consistent, `vault --verify` passes.
3. **Mitigation:**
   - The `runs` table in `certifyai.db` references `evidence_chain.run_id`. If the vault is replaced without updating `certifyai.db`, the FK references break.
   - **Cross-database verification** (see gap below).
4. **Gap:** There is currently no mechanism to verify that the `evidence_chain` in the vault's `chain.db` matches the `evidence_chain` reference in `certifyai.db`. They are separate files. A full attack replaces both.

### 3.5 Cross-Database Verification (Gap)

**Current architecture:** CertifyAI has two databases:
- `~/.certifyai/certifyai.db` — main app database (runs, results, config)
- `~/.certifyai/vault/chain.db` — evidence chain database

These are **not cryptographically linked**. An attacker who replaces both files can create a completely fabricated history.

**Recommendation:** Add a **root hash** stored in `certifyai.db` that commits to the state of `chain.db`:

```sql
-- In certifyai.db
CREATE TABLE vault_commitment (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    chain_root_hash TEXT NOT NULL,   -- SHA-256 of the last row in chain.db
    run_count   INTEGER NOT NULL,
    committed_at TEXT NOT NULL,
    signature   TEXT                  -- Future: GPG signature of the hash
);
```

On every `certifyai run` completion:
1. Read the last row of `chain.db`
2. Compute `SHA-256(chain.db_last_row)`
3. INSERT a row into `vault_commitment` in `certifyai.db`

This links the two databases: an attacker must modify BOTH `certifyai.db` and `chain.db` consistently, which doubles the attack cost and creates additional opportunities for forensic detection (e.g., WAL file forensic analysis might show one but not the other).

### 3.6 Root-Level Attacker

**Honest assessment: If an attacker has root access to the customer's machine, all bets are off.**

| Attack Vector | Can CertifyAI detect it? | Can CertifyAI prevent it? |
|-------------|-------------------------|---------------------------|
| Modify vault files + chain.db | No (chain is self-consistent) | No |
| Modify the `certifyai` binary itself | No | No |
| Install a kernel module that intercepts file reads | No | No |
| Steal API keys from memory | No | No |
| Modify the Python runtime to lie about hash computation | No | No |
| Replace `sha256` with a custom module | No | No |

**This is not a CertifyAI weakness.** It's a fundamental property of running software on a machine you don't physically control. The response to "what if the attacker is root?" is:

1. **CertifyAI is not designed to resist nation-state adversaries with root access.** No software on a general-purpose OS can.
2. **Detection shifts to external monitoring:** EDR/XDR tools, file integrity monitoring (OSSEC, Wazuh), OS audit logs.
3. **The evidence chain is still useful:** When an auditor finds that the vault is perfectly self-consistent but the commitment chain shows 0 runs on a date the customer claims they ran tests, that's a red flag. **Consistency anomalies are as telling as hash mismatches.**

### 3.7 Evidence Vault Security Scorecard

| Property | Rating | Notes |
|----------|--------|-------|
| Hash algorithm strength | **A** | SHA-256, industry standard |
| Append-only enforcement | **C** | SQLite trigger — trivially bypassed by root |
| Tamper detection | **A-** | Catches all single-file modifications |
| Tamper prevention | **F** | Not attempted (correct decision) |
| Cross-DB commitment | **D** | No cryptographic link between certifyai.db and chain.db |
| External timestamping | **F** | No timestamps from trusted third parties |
| Auditor verifiability | **A** | `vault --verify` is simple, auditable, and independent |
| Export integrity | **B** | Export bundles include hash chain; auditor can verify offline |

---

## 4. API Key Management

### 4.1 How API Keys Flow

```
                   ┌─────────────────────┐
                   │   config.toml        │
                   │  (user-edited)       │
                   │                     │
                   │  [llm]              │
                   │  provider = "openai" │
                   │  api_key = "sk-..."  │  ← Plaintext!
                   └──────────┬──────────┘
                              │
                              ▼
                   ┌─────────────────────┐
                   │   Config Loader      │
                   │                     │
                   │  Priority order:     │
                   │  1. Env var          │
                   │  2. config.toml      │
                   │  3. SQLite config    │
                   │  4. Keyring          │  (future)
                   └──────────┬──────────┘
                              │
                              ▼
                   ┌─────────────────────┐
                   │   SQLite config      │
                   │   table              │
                   │                     │
                   │  key="llm.api_key"  │
                   │  value=<encrypted>   │  ← Fernet encrypted
                   └─────────────────────┘
                              │
                              ▼
                   ┌─────────────────────┐
                   │   LiteLLM Client     │
                   │                     │
                   │  httpx.Client()     │
                   │  headers={          │
                   │   "Authorization":  │
                   │   "Bearer <key>"    │
                   │  }                  │
                   └─────────────────────┘
```

### 4.2 Storage Options

| Method | Security Level | Description | Status |
|--------|---------------|-------------|--------|
| **Environment variable** | **Good** | `CERTIFYAI_LLM_API_KEY=sk-... certifyai run`. Key never written to disk. | Supported v1 |
| **config.toml** | **Poor** | Plaintext TOML file in `~/.certifyai/config.toml`. Permissions `0o600`. | Default (easy setup) |
| **SQLite config table** | **Good** | Encrypted with `cryptography.fernet`. Key derived from machine ID. | Supported v1 |
| **System keyring** | **Best** | OS keychain (macOS Keychain, Linux Secret Service, Windows Credential Manager). | Planned post-v1 |
| **CLI argument** | **Worst** | `--api-key sk-...` leaks via process listing. | **Explicitly not implemented** |

**config.toml warning:**
The default `config.toml` file stores API keys in **plaintext**. This is the weakest link in the key management chain. The file is created with `0o600` permissions (user-readable only), but:
- Any process running as the same user can read it
- Backup software will include it
- A CI script that `cat` the config file for debugging will expose keys

**Recommendation:** The `certifyai init` wizard should default to environment variables or keyring integration, not config.toml. If config.toml is used, print a prominent warning.

### 4.3 Encryption Implementation

```python
from cryptography.fernet import Fernet
import hashlib
import uuid

def _derive_key() -> bytes:
    """
    Derive encryption key from machine ID.
    
    This means the encrypted config is tied to the specific machine.
    Backing up certifyai.db to another machine and restoring won't work
    for encrypted keys — the customer would need to re-enter them.
    
    Security note: This is NOT strong protection against a sophisticated
    attacker. If they can read the machine ID (/etc/machine-id on Linux,
    or similar on macOS/Windows), they can derive the key.
    """
    machine_id = _get_machine_id()  # e.g., /etc/machine-id
    key = hashlib.sha256(machine_id.encode()).digest()
    return Fernet.generate_key()  # ... but actually derive from machine_id
    
    # Note: The above is simplified. Actual implementation:
    key_material = hashlib.sha256(machine_id.encode()).hexdigest()[:43]
    # Fernet keys must be 32-byte URL-safe base64
    return base64.urlsafe_b64encode(key_material.encode().ljust(32)[:32])

def encrypt_config(value: str) -> str:
    f = Fernet(_derive_key())
    return f.encrypt(value.encode()).decode()

def decrypt_config(value: str) -> str:
    f = Fernet(_derive_key())
    return f.decrypt(value.encode()).decode()
```

**Key derivation weakness:**
- Machine IDs are often **not secret**. On Linux: `/etc/machine-id` is world-readable. On Docker: containers can share machine IDs.
- If the machine ID is guessable or known, the Fernet key is compromised.
- This protection is **obfuscation, not encryption** against a determined attacker with filesystem access.

**True encryption would require:**
- A user-supplied passphrase (defeats zero-config goal)
- A TPM-backed key (adds hardware dependency)
- An HSM or external key manager (overkill for a boilerplate)

**Verdict:** The current encryption is appropriate for:
- Preventing accidental exposure (backup file shared via email, dropped USB drive)
- Preventing casual reading by other users on the same machine
- It is **not** sufficient for compliance requirements that mandate FIPS 140-2 validated encryption

### 4.4 Web Dashboard Key Access

**Question: Can the Web Dashboard read API keys?**

**Short answer:** Yes, indirectly, if the keys are in `config.toml`. No, if they're only in environment variables.

**Technical analysis:**
- The Dashboard reads from `certifyai.db` (SQLite) via `better-sqlite3`
- If the key is stored in the SQLite `config` table (encrypted), the Dashboard would need the Fernet key to decrypt it
- The Dashboard (Node.js) does not have access to the Python Fernet key derivation logic
- **However**, if the key is in `config.toml`, any process running as the same user can read it, including a Node.js process

**Recommendation:**
- The Dashboard settings page should NOT display API keys (show `sk-...XXXX` masked)
- If the Dashboard needs to trigger runs via subprocess, it should pass the key via environment variable to the subprocess, not via CLI argument
- Document that the Dashboard (a Node.js process) has filesystem-level access to all data

### 4.5 API Key Security Scorecard

| Aspect | Rating | Notes |
|--------|--------|-------|
| At-rest encryption | **C** | Fernet with machine-ID-derived key. Obfuscation-level. |
| In-transit encryption | **A** | HTTPS to LLM provider. Keys in Authorization header (Bearer). |
| In-memory exposure | **C** | Key is a plaintext string in Python memory during run. Core dumps or memory dumps could expose it. |
| Config file permissions | **B** | `0o600` by default. Good, but same-user processes can read it. |
| Env var support | **A** | Best practice. Documented. |
| Keyring integration | **F** | Not yet implemented. |
| CLI arg prevention | **A** | Deliberately not supported. |

---

## 5. Web Dashboard Security

### 5.1 Authentication Design

The Web Dashboard uses **next-auth** with a **credentials provider** (username/password). Sessions are backed by SQLite.

```typescript
// pages/api/auth/[...nextauth].ts (or app/api/auth/[...nextauth]/route.ts)
import NextAuth from "next-auth"
import CredentialsProvider from "next-auth/providers/credentials"
import Database from "better-sqlite3"

const db = new Database(process.env.CERTIFYAI_DB_PATH || "~/.certifyai/certifyai.db")

export const authOptions = {
  providers: [
    CredentialsProvider({
      name: "Credentials",
      credentials: {
        username: { label: "Username", type: "text" },
        password: { label: "Password", type: "password" }
      },
      async authorize(credentials) {
        // Look up user in SQLite users table
        const user = db.prepare(
          "SELECT * FROM users WHERE username = ?"
        ).get(credentials.username)
        
        // Verify password hash
        if (user && bcrypt.compare(credentials.password, user.password_hash)) {
          return { id: user.id, name: user.username }
        }
        return null
      }
    })
  ],
  session: {
    strategy: "jwt",  // or "database" — need to decide
    maxAge: 24 * 60 * 60,  // 24 hours
  },
  pages: {
    signIn: "/login",
  },
  callbacks: {
    async session({ session, token }) {
      session.user.id = token.sub
      return session
    }
  }
}
```

**Key security decisions:**

| Decision | Option Chosen | Rationale |
|----------|--------------|-----------|
| **Session strategy** | JWT (default) | Database sessions require a sessions table and DB lookups on every page. JWT is simpler and doesn't increase SQLite load. |
| **Password hashing** | bcrypt (cost=12) | bcrypt is the standard. Argon2id is better but adds a dependency. bcrypt cost=12 balances security vs. login latency. |
| **Default credentials** | `admin` / `certifyai` (with force-change on first login) | Must be documented. `certifyai init` wizard should prompt for initial password. |
| **Rate limiting** | **Not implemented** | Gap — see below. |

### 5.2 Session Management

| Concern | Current State | Risk |
|---------|--------------|------|
| Cookie security | `httpOnly`, `secure` (in prod), `sameSite: 'lax'` | **Low** — standard OWASP practices |
| JWT signing | `NEXTAUTH_SECRET` environment variable (generated during `certifyai init`) | **Medium** — if `NEXTAUTH_SECRET` is weak or leaked, JWTs can be forged |
| Session expiry | 24 hours, sliding | **Low** — reasonable for single-user tool |
| Session revocation | Requires deleting the JWT (user must change `NEXTAUTH_SECRET` to invalidate all sessions) | **Medium** — no "logout all devices" button |
| Concurrent sessions | Multiple JWTs valid until expiry | **Low** — single-user tool, user is likely only using one browser |

**Gap: JWT secret generation**
The `NEXTAUTH_SECRET` is generated during `certifyai init`. If generated with a weak random source or hardcoded, all sessions are forgeable. **Mitigation: use `crypto.randomBytes(32).toString('hex')` and document how to rotate it.**

### 5.3 CSRF Protection

**Current state:**
- next-auth includes CSRF tokens for the `/api/auth` endpoints
- Route handlers for mutations (trigger run, update config) should check for CSRF

**Risk:** If route handlers don't check for CSRF, a malicious website could trigger `POST /api/run` if the user is authenticated and the dashboard is accessible.

**Mitigation:**
- Next.js 14 App Router includes CSRF protection for Server Actions
- For Route Handlers (API routes), implement manual CSRF token check or use `next-auth` middleware
- Since the dashboard is single-user and recommended to run on localhost only, CSRF risk is **low** for default deployments. It becomes **high** if exposed to a network.

**Recommendation:** Add the following middleware:

```typescript
// middleware.ts — protect all /api routes except auth
export { default } from "next-auth/middleware"

export const config = {
  matcher: ["/api/(?!auth).*", "/settings", "/runs/new"]
}
```

### 5.4 Network Exposure Risk

This is the **single highest-risk decision** in the Web Dashboard architecture.

| Deployment Mode | Risk Level | Notes |
|----------------|-----------|-------|
| `localhost:3000` (default) | **Low** | Only accessible from the same machine. Attacker must already have code execution on the machine. |
| `0.0.0.0:3000` (explicit bind) | **Critical** | Accessible from any machine on the network. Dashboard auth is the only gate. |
| Reverse proxy (nginx, Caddy) | **Medium** | Depends on proxy config. If proxy adds auth (Cloudflare Access, basic auth), risk is Medium. If proxy passes through to dashboard auth only, risk is High. |
| Public internet (Cloudflare Tunnel, ngrok) | **Critical** | Exposed to global attack surface. Brute-force, credential stuffing, session hijacking, CVE exploitation. |

**Default behavior:** Next.js `next start` binds to `localhost:3000`. This is secure by default.

**Gap:** There is no startup check that warns the user if `HOST` is set to `0.0.0.0`. Recommendation: add a warning banner in the dashboard if it detects it's not on localhost:

```
⚠️ WARNING: CertifyAI Dashboard is accessible from the network.
Only expose to trusted networks. Ensure strong passwords and keep
the software updated.
```

### 5.5 Content Security Policy

**Current state:** No CSP header configured.

**Why CSP matters:**
- Without CSP, any XSS vulnerability in the dashboard (e.g., displaying an attacker-controlled LLM response) can execute arbitrary JavaScript
- CSP provides defense-in-depth even if input sanitization fails

**Recommended CSP:**
```javascript
// next.config.js
const csp = `
  default-src 'self';
  script-src 'self' 'unsafe-inline';  // 'unsafe-inline' needed for Next.js hydration
  style-src 'self' 'unsafe-inline';
  img-src 'self' data:;
  font-src 'self';
  connect-src 'self';
  form-action 'self';
  base-uri 'self';
  frame-ancestors 'none';
`.replace(/\s{2,}/g, ' ').trim()

module.exports = {
  async headers() {
    return [
      {
        source: '/(.*)',
        headers: [
          { key: 'Content-Security-Policy', value: csp },
          { key: 'X-Content-Type-Options', value: 'nosniff' },
          { key: 'X-Frame-Options', value: 'DENY' },
          { key: 'Referrer-Policy', value: 'strict-origin-when-cross-origin' },
        ],
      },
    ]
  },
}
```

### 5.6 Web Dashboard Security Scorecard

| Control | Status | Rating | Priority |
|---------|--------|--------|----------|
| Authentication | next-auth credentials provider | **B** | Shipped |
| Default to localhost | Yes (Next.js default) | **A** | Shipped |
| Rate limiting | Not implemented | **F** | **Pre-v1 launch** |
| CSP headers | Not configured | **F** | **Pre-v1 launch** |
| XSS sanitization | Not verified (displays LLM responses) | **D** | Post-v1 |
| Password strength enforcement | Not implemented | **D** | Post-v1 |
| Session timeout | 24h | **B** | Shipped |
| CSRF protection | Partial (next-auth handles auth routes) | **C** | Pre-v1 launch |
| Audit logging for config changes | Not implemented | **F** | Post-v1 |
| Runtime network exposure warning | Not implemented | **D** | Pre-v1 launch |

---

## 6. Supply Chain Security

### 6.1 Python Dependency Risk Assessment

| Dependency | Version | Role | Risk Level | Rationale |
|------------|---------|------|------------|-----------|
| **LiteLLM** | ≥1.30 | LLM abstraction | **High** | ~50MB of transitive deps. Large attack surface. Makes network requests to arbitrary URLs. |
| **SQLAlchemy** | ≥2.0 | Database ORM | **Low** | Mature, well-audited. Only connects to local SQLite. |
| **Pydantic v2** | ≥2.5 | Schema validation | **Low** | Mature. Core serialization library. Written in Rust (v2-core) which reduces memory safety bugs. |
| **Click** | ≥8.x | CLI framework | **Low** | Stable, minimal deps. No network. |
| **Rich** | ≥13.x | Terminal formatting | **Low** | Display only. No network. Large but well-maintained. |
| **Textual** | ≥1.x | TUI framework | **Medium** | Newer framework. Larger attack surface (CSS parsing, widget system). Terminal escape handling. |
| **cryptography** | ≥41.0 | Fernet encryption | **Low** | Well-audited. Industry standard. |
| **httpx** | (via LiteLLM) | HTTP client | **Medium** | Makes outbound HTTPS calls. TLS certificate validation is critical. |
| **WeasyPrint** | (Pro tier) | PDF generation | **Medium** | System dependency (Cairo, Pango, libxml). Runs locally only. |
| **Jinja2** | ≥3.x | Report templates | **Low** | Minimal. Template injection risk is nil if templates are static files. |
| **PyYAML** | ≥6.x | Framework YAML parsing | **Medium** | History of CVEs (CVE-2020-14343, CVE-2021-4277). Use `yaml.safe_load()` only. |
| **aiofiles / aiosqlite** | stdlib or latest | Async I/O | **Low** | Minimal surface. |

**LiteLLM is the highest-risk dependency.** Detailed analysis:

| Concern | Assessment |
|---------|-----------|
| **Transitive dependency count** | 100+ packages (guestimate). Each is a potential supply chain risk. |
| **Network access** | Yes — makes HTTPS calls to any LLM provider URL. Could be exploited for SSRF if URL is attacker-controlled. |
| **API key handling** | Receives API keys as function arguments. Must ensure keys don't leak via exceptions or logging. |
| **Maintenance** | Very active (daily releases). Rapid change means faster vulnerability patching but also more API churn. |
| **Vulnerability history** | As of 2026 Q3, no critical CVEs reported. Risk is forward-looking. |

**Recommendation:** Pin ALL dependencies with hash-locked `requirements.txt` or use `pip freeze` at release time. Provide a lockfile:

```bash
# Release process — generate a hash-locked requirements
pip freeze > certifyai/requirements-locked.txt
# Or use pip-compile for better dependency resolution
pip-compile --generate-hashes pyproject.toml -o requirements-locked.txt
```

### 6.2 Node.js Dependencies (Web Dashboard)

| Dependency | Risk Level | Notes |
|------------|-----------|-------|
| **Next.js 14** | **Low-Medium** | Meta-framework. Large surface but well-maintained. |
| **better-sqlite3** | **Low** | Mature. Native addon (compiled from C++). Well-tested. |
| **next-auth** | **Low** | Authentication library. Standard for Next.js. |
| **react** | **Low** | Battle-tested. |
| **recharts** | **Low** | Charting library. No server-side rendering of data. |
| **motion/react** | **Low** | Animation library. No data flow. |
| **tailwindcss** | **Low** | CSS framework. Build-time only. |

### 6.3 SBOM Generation

**Recommendation:** Generate a Software Bill of Materials (SBOM) for every release. Two formats:

```bash
# SPDX format (using pip-license-checker)
pip-license-checker --format spdx > certifyai-sbom.spdx

# CycloneDX format (using cyclonedx-py)
cyclonedx-py --requirements requirements-locked.txt --output certifyai-sbom.xml
```

Include the SBOM in:
- The release artifacts (GitHub Releases)
- The documentation (for enterprise customers who require SBOM review)
- A `certifyai sbom` CLI command that outputs the current installation's SBOM

### 6.4 Signed Releases

| Channel | Signing | Status |
|---------|---------|--------|
| **PyPI** | PyPI requires 2FA for maintainers. No package signing (PyPI doesn't support it natively). | Current |
| **GitHub Releases** | GPG-signed tags. Release artifacts should have `.sig` and `.asc` files. | **Planned** |
| **npm** (Dashboard) | npm package signing via `npm sign`. | **Planned** |

**GPG Key management:**
- Create a dedicated signing key (not the developer's personal key)
- Store the private key encrypted and backed up
- Publish the public key to keys.openpgp.org and include it in the repository
- Sign all Git tags with `git tag -s`

```bash
# Release process
export RELEASE_VERSION=v1.0.0
git tag -s $RELEASE_VERSION -m "CertifyAI $RELEASE_VERSION"
git push origin $RELEASE_VERSION

# Build wheel
python -m build

# Sign wheel
gpg --detach-sign --armor dist/certifyai-$RELEASE_VERSION-py3-none-any.whl

# Upload
twine upload dist/certifyai-$RELEASE_VERSION*
gh release create $RELEASE_VERSION dist/*.whl dist/*.asc
```

### 6.5 CI/CD Pipeline Security

| Stage | Risk | Mitigation |
|-------|------|-----------|
| **Pull request** | Malicious PR modifies release pipeline to inject backdoor | Require PR approval from maintainer. Use `pull_request_target` with caution. |
| **Test** | Tests run with network access — exfiltration possible | Pin CI runner OS version. No secrets in test environment. |
| **Build** | Build environment compromised | Use isolated build runners (GitHub Actions hosted, not self-hosted). |
| **Release** | Release step modified to publish malicious package | 2FA on PyPI. Release workflow requires manual trigger. GPG signature verification in release notes. |
| **Dependabot** | Automated PR merges a malicious dependency update | Disable auto-merge for dependency updates. Review changelog before merging. |

**Recommendation for solo developer:**
- Use a separate GitHub account for releases (reduces risk of account compromise affecting release integrity)
- Store PyPI token in GitHub Actions secrets, never on the development machine
- `twine upload` requires a OTP from authenticator app — never disable 2FA

### 6.6 Supply Chain Security Scorecard

| Control | Status | Rating |
|---------|--------|--------|
| Dependency pinning | In `pyproject.toml` (range-based) | **C** |
| Hash-locked requirements | Not implemented | **F** |
| SBOM generation | Not implemented | **F** |
| GPG-signed releases | Not implemented | **F** |
| PyPI 2FA | (Depends on developer) | **Requires setup** |
| npm signing | Not implemented | **F** |
| Dependabot / Renovate | Not implemented | **F** |
| Vulnerability scanning (pip audit) | Not implemented | **F** |

---

## 7. Secure Defaults

### 7.1 The Secure Defaults Principle

Every security measure in CertifyAI follows this rule: **The default configuration must be the secure configuration.** Users should not need to read documentation to be safe.

### 7.2 Secure by Default

| Setting | Default Value | Why It's Secure | Residual Risk |
|---------|--------------|-----------------|---------------|
| **Web Dashboard host** | `localhost:3000` | Not accessible from other machines | None — this is the strongest default |
| **config.toml permissions** | `0o600` (user read/write only) | Other users on shared machine cannot read API keys | None for single-user machines |
| **SQLite WAL mode** | Enabled | Crash-safe writes | None |
| **Log level** | `WARNING` | No debug logs that might leak API keys or prompts | None |
| **Password hash cost** | bcrypt cost=12 | Slows brute-force by ~250ms per attempt | None |
| **Evidence chain append-only** | Trigger installed on first run | Prevents accidental deletion | Not protection against determined attacker |
| **Concurrent attack limit** | `max_concurrency=5` | Prevents resource exhaustion | User can increase it |
| **Request timeout** | `request_timeout=30s` | Prevents hanging on unresponsive endpoints | User can disable it |
| **Update check** | On by default (weekly) | Users know about security updates | Users can disable it |
| **Telemetry** | Opt-in (disabled by default) | No data leaves machine without consent | None |
| **SARIF output** | Included in free tier | Enables CI/CD security scanning | None |

### 7.3 Requires User Action

| Setting | Recommended Value | Risk If Not Set | Priority |
|---------|-------------------|----------------|----------|
| **Dashboard password** | Strong password (16+ chars, mixed case, special chars) | Auth bypass — anyone on localhost can access dashboard | **Critical — enforced by init wizard** |
| **`NEXTAUTH_SECRET`** | Random 64-char hex string | JWT session tokens can be forged | **Critical — generated by init** |
| **FileVault / BitLocker / LUKS** | Full-disk encryption | SQLite DB and vault files exposed if laptop stolen | **High — documented** |
| **OS-level firewall** | Block ports beyond 3000 (if dashboard used) | Dashboard exposed if user binds to 0.0.0.0 | **Medium — documented** |
| **Backup encryption** | Encrypt vault backups | Evidence integrity lost if backup is tampered | **Medium — documented** |
| **API key rotation** | Rotate keys every 90 days | Stale keys have larger exposure window | **Low — documented** |
| **CertifyAI updates** | `pip install --upgrade certifyai` monthly | Known vulnerabilities unpatched | **High — automatic check** |
| **OS updates** | Keep OS and Python updated | OS-level vulnerabilities expose all data | **High — documented** |

### 7.4 Insecure by Design (Accepted Risks)

These are explicitly acknowledged as insecure by design, with documentation of the risk:

| Feature | Why It's Insecure | Why It's Accepted |
|---------|------------------|-------------------|
| **Plaintext API keys in config.toml** | Keys stored on disk unencrypted | User convenience for initial setup. Env vars are the recommended production approach. |
| **No rate limiting on login** | Brute-force possible | Dashboard is single-user on localhost by default. Rate limiting adds complexity. |
| **No audit log for config changes** | Can't tell who changed a setting or when | Single-user tool. Adding audit logging increases DB schema complexity. |
| **Evidence vault is filesystem-based** | Files have OS-level permissions, not application-enforced | Enables auditor-friendly direct file access. Trade-off accepted per ADR-007. |
| **Dashboard has access to all SQLite data** | No read isolation between dashboard pages | Same-user tool. Read isolation adds complexity with no security benefit for single-user. |

### 7.5 Secure Deployment Checklist

For customers deploying CertifyAI in production (running compliance for real audits):

```
□ Pre-installation:
  □ 1. Verify Python 3.11+ with `python --version`
  □ 2. Install CertifyAI: `pip install certifyai`
  □ 3. Verify package integrity: `pip verify certifyai`
  □ 4. Run `certifyai init` to create config directory

□ API Key Configuration:
  □ 5. Export key via environment variable (RECOMMENDED):
       `export CERTIFYAI_LLM_API_KEY=sk-...`
     OR
  □ 6. Store in config.toml (permissions verified at 0o600)

□ Evidence Vault:
  □ 7. Configure vault path: `certifyai config set vault.path /secure/location`
  □ 8. Verify vault integrity: `certifyai vault --verify`
  □ 9. (Recommended) Enable full-disk encryption on vault directory

□ Web Dashboard (Pro/Enterprise):
  □ 10. Run `certifyai init --dashboard` to set up authentication
  □ 11. Set a strong password (min 16 characters)
  □ 12. Verify dashboard only listens on localhost:
        `netstat -an | grep 3000` → should show 127.0.0.1
  □ 13. (If behind reverse proxy) Configure additional auth layer

□ CI/CD Integration:
  □ 14. API key via CI/CD secrets (GitHub Actions Secrets, GitLab CI Variables)
  □ 15. SARIF output integrated into code review workflow
  □ 16. Evidence export stored in encrypted artifact storage

□ Ongoing:
  □ 17. Enable automatic update checks: `certifyai config set update.check true`
  □ 18. Weekly: `certifyai vault --verify` and check integrity report
  □ 19. Monthly: `pip install --upgrade certifyai`
  □ 20. Quarterly: Rotate API keys
```

---

## 8. Incident Response

### 8.1 The Solo Developer Reality

CertifyAI is built by a solo developer. Incident response procedures must be realistic about:
- **Response time:** A solo dev cannot offer 24/7 response. Realistic SLA: 24-48 hours for critical vulnerabilities.
- **Patch cadence:** Hotfix releases can ship within hours for critical issues. Standard releases are monthly.
- **Communication:** GitHub Security Advisories, PyPI release notes, and a security.txt file.

### 8.2 Vulnerability Disclosure Process

```
                      ┌──────────────────────┐
                      │  Reporter finds       │
                      │  vulnerability        │
                      └──────────┬───────────┘
                                 │
                      ┌──────────▼───────────┐
                      │  Report via           │
                      │  SECURITY.md process   │
                      │                       │
                      │  Email: security@     │
                      │  certifyai.dev        │
                      │  OR GitHub Advisory   │
                      └──────────┬───────────┘
                                 │
                      ┌──────────▼───────────┐
                      │  Acknowledgment        │
                      │  (within 24 hours)     │
                      │                       │
                      │  - Confirm receipt     │
                      │  - Request CVE if needed│
                      │  - Set expectations    │
                      └──────────┬───────────┘
                                 │
                      ┌──────────▼───────────┐
                      │  Triage                │
                      │  (within 48 hours)     │
                      │                       │
                      │  Severity:            │
                      │  Critical → fix ASAP  │
                      │  High → fix < 7 days │
                      │  Medium → next release│
                      │  Low → backlog        │
                      └──────────┬───────────┘
                                 │
                      ┌──────────▼───────────┐
                      │  Fix + Release         │
                      │                       │
                      │  - Develop fix        │
                      │  - Write advisory     │
                      │  - Ship patch release │
                      │  - Credit reporter    │
                      └──────────┬───────────┘
                                 │
                      ┌──────────▼───────────┐
                      │  Disclosure            │
                      │                       │
                      │  - GitHub Advisory    │
                      │  - PyPI release notes │
                      │  - (Optional) Blog    │
                      │  - CVE publication   │
                      └──────────────────────┘
```

### 8.3 Communication Channels

| Channel | Purpose | Access |
|---------|---------|--------|
| **`SECURITY.md`** | Disclosure policy in repository root | Public — all repos |
| **`security@certifyai.dev`** | Encrypted vulnerability reports | GPG key published in SECURITY.md |
| **GitHub Security Advisories** | Private reporting + CVE request | GitHub Security tab |
| **GitHub Discussions** | Security announcements | Public |
| **PyPI release notes** | Patch notes per version | Public |
| **Changelog** | `CHANGELOG.md` with security sections | Repository |

### 8.4 Severity Classification

| Severity | Definition | Response Time | Example |
|----------|-----------|--------------|---------|
| **Critical** | Remote code execution, authentication bypass, evidence chain subversion that requires no physical access | Patch within 24 hours | Dashboard XSS leading to RCE; SHA-256 collision (theoretical); SQL injection via dashboard |
| **High** | API key exposure, evidence tampering via non-root access, privilege escalation | Patch within 7 days | LiteLLM logs API keys; config.toml created with world-readable permissions; plugin system allows code execution |
| **Medium** | Information disclosure (metadata, config), rate-limiting bypass, session fixation | Fix in next release (≤30 days) | Dashboard session cookie not set to `secure`; verbose error messages in API responses; timing attack on login |
| **Low** | Theoretical risks, minor information leaks, defense-in-depth weaknesses | Backlog | Machine-ID-based encryption key derivation; no CSP headers; verbose debug logs in production |

### 8.5 Patch Cadence

| Release Type | Cadence | Version Bump | Distribution Channel |
|-------------|---------|-------------|---------------------|
| **Hotfix** | Within 24-48h of critical vuln | Patch (1.0.0 → 1.0.1) | PyPI + GitHub Release |
| **Security release** | Within 7 days of high vuln | Minor (1.0.0 → 1.1.0) | PyPI + GitHub Release |
| **Standard release** | Monthly | Minor (1.0.0 → 1.1.0) | PyPI + GitHub Release |
| **Major release** | Quarterly | Major (1.0.0 → 2.0.0) | PyPI + GitHub Release + Gumroad |

### 8.6 Post-Incident Process

After every security incident:

1. **Root cause analysis** — Write a brief (1-2 page) document answering:
   - What happened?
   - How was it discovered?
   - What was the impact?
   - Why was it not caught earlier?
   - What changes prevent recurrence?

2. **Fix verification** — Confirm the fix works:
   - Write a regression test that reproduces the vulnerability
   - Verify the test passes with the fix
   - Run full test suite

3. **Communication** — To affected users:
   - GitHub Security Advisory
   - Email to Gumroad customers (if applicable)
   - PyPI release notes
   - No blog post for low/medium issues

4. **Lessons learned** — Update:
   - Threat model (add new attack scenarios)
   - Secure defaults (if the vuln was a default misconfiguration)
   - Test suite (add security regression tests)
   - Security checklist (if user action could have prevented it)

### 8.7 Incident Response Scorecard

| Capability | Status | Notes |
|-----------|--------|-------|
| Disclosure policy (`SECURITY.md`) | **Not created** | Must be added pre-v1 launch |
| Security contact email | **Not set up** | `security@certifyai.dev` needs configuration |
| GPG key for encrypted comms | **Not generated** | Create pre-v1 launch |
| GitHub Security Advisories | **Not configured** | Enable in repository settings |
| CVE request procedure | **Not documented** | Learn process before first CVE |
| Patch automation | **Manual** | Hotfix pipeline should be semi-automated |
| Customer notification list | **Not created** | Collect opt-in security-only emails |

---

## 9. Security Roadmap

### 9.1 Pre-v1 Launch (Must-Have)

| Item | Effort | Impact | Notes |
|------|--------|--------|-------|
| Content Security Policy headers | Low | **High** — prevents XSS | Add to `next.config.js` |
| Rate limiting on dashboard login | Low | **High** — prevents brute-force | In-memory rate limiter (3 attempts/min/IP) |
| Network exposure warning in dashboard | Low | **High** — warns users | Check `req.headers.host` and compare to `localhost` |
| Cross-DB vault commitment | Medium | **High** — links certifyai.db to chain.db | Add `vault_commitment` table + verification |
| `SECURITY.md` in repository root | Low | **High** — enables responsible disclosure | Template from GitHub |
| Runtime warning for env-var API keys in config.toml | Low | **Medium** — prevents accidental plaintext storage | Check during `certifyai init` |
| ANSI escape sequence sanitization in TUI | Low | **Medium** — prevents terminal injection | Filter LLM responses before display |
| `certifyai audit` command | Medium | **Medium** — cross-checks certifyai.db vs chain.db | Reports orphaned runs, hash mismatches, config changes |
| Lock requirements files | Low | **Medium** — supply chain | `pip-compile --generate-hashes` |

### 9.2 v1.1 (High Priority)

| Item | Effort | Impact | Notes |
|------|--------|--------|-------|
| System keyring integration | Medium | **High** — best practice key storage | keyring library supports all major OS keychains |
| GPG-signed releases | Low | **High** — supply chain integrity | Sign wheels + git tags |
| SBOM generation per release | Low | **Medium** — enterprise procurement requirement | cyclonedx-py or pip-license-checker |
| Dashboard audit log table | Medium | **Medium** — track who changed what | Simple table: user, action, timestamp, IP |
| `certifyai init` password strength meter | Low | **Medium** — encourages strong passwords | zxcvbn library integration |
| Environment variable sanitization in error reports | Low | **Medium** — prevent key leakage in bug reports | Scrub `API_KEY` and `SECRET` patterns from logs |
| User-agent reporting to LLM providers | Low | **Low** — but helps providers identify compliance testing | `CertifyAI/1.0.0` User-Agent header |

### 9.3 v1.2 (Medium Priority)

| Item | Effort | Impact | Notes |
|------|--------|--------|-------|
| FIPS 140-2 / FIPS 140-3 compliance mode | High | **High** — government/regulated markets | Replace `hashlib.sha256` with FIPS-certified module |
| Plugin code signing | High | **High** — prevents malicious plugins | Sign plugin `.whl` files; verify before loading |
| Offline integrity check using TOTP-like rotating nonce | Medium | **Medium** — adds time-based verification | Time-to-live for vault entries |
| USB-based vault cold storage export | Medium | **Medium** — physical evidence transfer | Export to FAT32 USB, verify on different machine |
| `certifyai vuln` command | Low | **Medium** — check known CVEs in dependencies | Compare deps against advisory database |
| Argon2id password hashing | Low | **Medium** — better than bcrypt for modern hardware | Replace bcrypt with argon2-cffi |

### 9.4 v2.0 (Post-Revenue, Sustainability)

| Item | Effort | Impact | Notes |
|------|--------|--------|-------|
| TPM-backed key storage for vault encryption | High | **High** — hardware-bound key | tpm2-py library. Only on systems with TPM 2.0. |
| RFC 3161 trusted timestamping | Medium | **High** — proves evidence existed before a date | Send hash to timestamp authority (e.g., DigiCert, Let's Encrypt). Requires internet. |
| Certificate Transparency-like append-only log | High | **High** — prevents rollback attacks | Publish vault root hash to a public CT log (or a personal Golang service) |
| Code signing for all binaries | Medium | **High** — platform trust (macOS Gatekeeper, Windows SmartScreen) | Requires Apple Developer ($99/yr) and Microsoft cert ($300/yr) |
| Remote attestation (optional, for enterprise) | High | **High** — prove vault wasn't tampered | Use TPM quote to prove software state. Audit-only feature. |
| SELinux / AppArmor profile | Low | **Medium** — sandboxing for production deployments | Ship policy files for `certifyai` processes |
| Security-focused hardening guide (STIG-like) | Medium | **Medium** — for regulated deployments | NIST 800-53, CIS Benchmarks alignment |
| Bug bounty program (small scope) | High | **Medium** — finding vulnerabilities before attackers | Limited to $100-$500 per finding. Via Gumroad credits. |

### 9.5 Never (Explicitly Out of Scope)

| Security Feature | Why Not | Alternative |
|-----------------|---------|-------------|
| **Multi-factor authentication** | Single-user tool. Adds friction with limited benefit. | Strong password + localhost-only binding is sufficient. |
| **Full disk encryption built-in** | OS responsibility (FileVault, BitLocker, LUKS). Duplicating this is wrong. | Document full-disk encryption as prerequisite. |
| **Cloud-based evidence backup** | Contradicts the boilerplate/offline architecture. | Export/import for backup. Customer chooses storage. |
| **SOC 2 certification of CertifyAI** | Would cost $50K-$100K/yr for a solo dev. Product doesn't handle customer data. | Evidence chain provides audit trail. SHIM (supplier's HIPAA InfoMap) document instead. |
| **Penetration testing** | $20K-$50K per test. Not affordable pre-revenue. | Regular dependency scanning + THM (Theoretical Hacker Model). |
| **Hardware security module (HSM)** | $2K-$15K for a YubiHSM. Overkill for a $149 product. | TPM integration in v2.0 as a lighter alternative. |

### 9.6 Security Roadmap Visualization

```
Pre-v1         v1.1            v1.2             v2.0
 │              │               │                │
 ├─ CSP headers  ├─ Keyring      ├─ FIPS mode     ├─ TPM-backed keys
 ├─ Rate limit   ├─ GPG signing  ├─ Plugin signing ├─ RFC 3161 timestamp
 ├─ Net warning  ├─ SBOM         ├─ TOTP nonce    ├─ CT log publish
 ├─ X-DB commit  ├─ Audit log    ├─ USB export    ├─ Code signing
 ├─ SECURITY.md  ├─ Pass meter   ├─ `certifyai   ├─ Remote attestation
 ├─ ANSI sanitize├─ Env scrub     │   vuln`       ├─ SELinux profile
 ├─ `audit` cmd  ├─ User-Agent   ├─ Argon2id      └─ STIG guide
 └─ Lockfiles    └─              └─
```

---

## Appendix A: CVE Watchlist

Dependencies to monitor actively for CVEs:

| Dependency | CVE Feed | Why Watch |
|------------|----------|-----------|
| **LiteLLM** | GitHub advisories | Largest dependency. Network-facing. Key-passing. |
| **Textual** | GitHub advisories | TUI framework. CSS parsing. Keyboard handling. |
| **PyYAML** | NVD | History of code execution CVEs via `yaml.load()`. Verify `safe_load` always used. |
| **next-auth** | GitHub advisories | Authentication library. Session handling. JWT verification. |
| **cryptography** | OpenSSL / NVD | Encryption backend. OpenSSL CVEs affect it. |
| **httpx** | NVD | HTTP client used by LiteLLM. TLS verification. HTTP/2 parsing. |

## Appendix B: Security-Related CLI Commands

```bash
# Vault integrity check
certifyai vault --verify                    # Full chain verification
certifyai vault --verify --verbose          # Per-run details
certifyai vault --verify --export report    # Save verification report

# Audit
certifyai audit                             # Cross-check certifyai.db vs chain.db
certifyai audit --config                    # Report config security status (key storage method, file permissions)

# Config security
certifyai config security-check             # Scan for insecure settings
certifyai config migrate-keys --to keyring  # Migrate keys from config.toml to system keyring
certifyai config rotate-encryption-key      # Regenerate Fernet key

# Supply chain
certifyai sbom                              # Output SPDX or CycloneDX SBOM
certifyai verify-signatures                 # Verify plugin signatures (post-v1)
certifyai update --check-only               # Check for security updates without installing

# Dashboard
certifyai dashboard security-check          # Verify auth, CSP, network binding
certifyai dashboard rotate-secret           # Regenerate NEXTAUTH_SECRET
```

## Appendix C: References

- [STRIDE Threat Model (Microsoft)](https://learn.microsoft.com/en-us/azure/security/develop/threat-modeling-tool-threats)
- [OWASP Top 10 (2021)](https://owasp.org/www-project-top-ten/)
- [OWASP ASVS 4.0 — Web Application Security Verification Standard](https://owasp.org/www-project-application-security-verification-standard/)
- [NIST SP 800-53 Rev. 5 — Security and Privacy Controls](https://csrc.nist.gov/publications/detail/sp/800-53/rev-5/final)
- [NIST Cryptographic Standards — SHA-256, AES, FIPS 140](https://csrc.nist.gov/publications/fips)
- [CWE-79: Cross-site Scripting](https://cwe.mitre.org/data/definitions/79.html)
- [CWE-89: SQL Injection](https://cwe.mitre.org/data/definitions/89.html)
- [CWE-200: Information Exposure](https://cwe.mitre.org/data/definitions/200.html)
- [CWE-284: Improper Access Control](https://cwe.mitre.org/data/definitions/284.html)
- [CWE-522: Insufficiently Protected Credentials](https://cwe.mitre.org/data/definitions/522.html)
- [CWE-754: Improper Check for Unusual Conditions (ReDoS)](https://cwe.mitre.org/data/definitions/754.html)
- [Supply Chain Levels for Software Artifacts (SLSA)](https://slsa.dev/)
- [Sigstore / Cosign for container signing](https://www.sigstore.dev/)
- [RFC 3161 — Internet X.509 Public Key Infrastructure Time-Stamp Protocol](https://www.rfc-editor.org/rfc/rfc3161)
- [SPDX — Software Package Data Exchange](https://spdx.dev/)
- [CycloneDX — SBOM Standard](https://cyclonedx.org/)
- EU AI Act (Regulation 2024/1689) — Articles 14, 15, 29
- NIST AI Risk Management Framework (AI RMF 1.0) — Govern, Map, Measure, Manage functions
