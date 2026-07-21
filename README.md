# CertifyAI

**Continuous compliance engine for AI runtimes.** Test LLM endpoints against prompt injection, jailbreaking, PII leakage, policy violation, hallucination, and bias — with audit-ready evidence mapped to EU AI Act, SOC 2 Type II, and NIST AI RMF.

Self-hosted. No subscription. No cloud dependency. Bring your own LLM API key.

## Status

| Phase | What | Status |
|-------|------|--------|
| 1 | Engine Core — models, CLI, evidence vault, compliance mapper, 44 tests | ✅ |
| 2 | Plugin System — 6 categories, 18 scenarios, external plugin loading | ✅ |
| 3 | LiteLLM Integration — live API tests against NVIDIA NIM | ✅ |
| 4 | SQLite Database — async ORM, persistence, evidence chain, 88 tests | ✅ |
| 4b | CLI Rich UI + TUI — progress bars, tables, terminal dashboard | ✅ |

## Features

- **18 attack scenarios** across 6 categories: bias, hallucination, jailbreak, PII leakage, policy violation, prompt injection
- **Rich CLI** — Progress bars, color-coded result tables, compliance summaries
- **Textual TUI** — Terminal dashboard with live attack monitoring and historical results
- **SQLite database** — Persistent results with WAL mode, aggregation queries, evidence chain
- **Evidence vault** — Append-only SHA-256 hash chain for court-admissible audit trails
- **Compliance mapper** — Built-in frameworks: EU AI Act, SOC 2 Type II, NIST AI RMF
- **Plugin system** — Load custom attack scenarios from external directories
- **LiteLLM integration** — 100+ providers (OpenAI, Anthropic, Ollama, Gemini, any OpenAI-compatible endpoint)

## Quick Start

```bash
# Clone and install
git clone https://github.com/ravikumarve/CertifyAI.git
cd CertifyAI
pip install -e ".[dev,tui]"

# Initialize a project
python -m certifyai.cli.main init

# List available attack categories
python -m certifyai.cli.main list-categories

# Run attacks (dry-run mode — no LLM call)
python -m certifyai.cli.main run --dry-run

# Run against a real LLM (set your API key)
export CERTIFYAI_API_KEY="your-api-key"
python -m certifyai.cli.main run --provider openai --model gpt-4o

# Launch the terminal dashboard
python -m certifyai.tui.app

# Verify evidence vault integrity
python -m certifyai.cli.main verify
```

## CLI Usage

```
certifyai init              Initialize project config and database
certifyai run                Run attack battery against an LLM
certifyai list-categories    List available attack scenarios
certifyai verify             Verify evidence vault integrity
```

### Run Options

| Flag | Default | Description |
|------|---------|-------------|
| `-p`, `--provider` | `openai` | LLM provider (openai, anthropic, ollama, etc.) |
| `-m`, `--model` | `gpt-4o` | Model name |
| `-k`, `--api-key` | `CERTIFYAI_API_KEY` env | API key |
| `--category` | all | Comma-separated categories to run |
| `--db` | `certifyai.db` | SQLite database path |
| `--vault` | `./certifyai_vault` | Evidence vault directory |
| `--report` | — | JSON compliance report output path |
| `--framework` | `eu_ai_act` | Compliance framework |
| `--dry-run` | `false` | Simulate without calling LLM |
| `--concurrency` | `3` | Concurrent LLM calls |

## Project Structure

```
certifyai/
├── cli/                  # Click commands (Rich output)
├── tui/                  # Textual terminal dashboard
├── engine/               # Core logic
│   ├── redteam/          # Attack scenarios (6 categories × 3 scenarios)
│   ├── evidence/         # Vault & SHA-256 hash chain
│   ├── compliance/       # Framework mapper (EU AI Act, SOC 2, NIST AI RMF)
│   └── database/         # SQLAlchemy 2.0 ORM + async DatabaseManager
├── web/                  # Next.js dashboard (future)
├── docs/                 # Documentation suite (17 docs)
├── tests/                # pytest (88 tests — 82 unit + 6 integration)
├── pyproject.toml
└── README.md
```

## Documentation

See [`docs/`](./docs/) for the full specification suite — market research, competitive analysis, PRD, technical architecture, UX flows, test strategy, attack catalog, compliance mapping, security architecture, database schema, pricing, GTM strategy, support plan, and commercial licensing.

```bash
# Run tests
pytest tests/ -v

# Run only unit tests (skip integration)
pytest tests/ -v -m "not integration"

# Run integration tests (requires .env with NVIDIA NIM key)
pytest tests/ -v -m integration --run-integration
```

## License

- Free tier: Apache 2.0
- Pro/Enterprise: Commercial license (see [`docs/commercial-license.md`](./docs/commercial-license.md))

Built with Python 3.11+ | LiteLLM | SQLAlchemy 2.0 | Click | Rich | Textual | Next.js (upcoming)
