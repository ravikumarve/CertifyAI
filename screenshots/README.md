# CertifyAI — Full Workflow Screenshots
Captured: 2026-09-03 — Dell Latitude 3460 (CPU-only) — CertifyAI v0.1.0

## CLI (4 steps)
| File | Command |
|------|---------|
| `cli-01-help.txt/.html` | `certifyai --help` — entry point, 4 commands (init, list-categories, run, verify) |
| `cli-02-list-categories.txt/.html` | `certifyai list-categories` — 6 categories × 18 scenarios |
| `cli-03-dry-run.txt/.html` | `certifyai run --dry-run --db /tmp/...` — 53 attacks, Rich progress + summary Table |
| `cli-04-verify.txt/.html` | `certifyai verify` — SHA-256 hash chain check |

## TUI (Textual — 4 tabs, SVG via pytest-textual-snapshot, terminal 120×50)
| File | Key | Content |
|------|-----|---------|
| `tui-01-dashboard.svg/.html` | `d` | Status cards, recent runs (b6f51880 0% etc.), header `>_ certifyai-tui // v1.0.4` |
| `tui-02-run-attack.svg/.html` | `r` | Execution config, `[ RUN_BATTERY ] [ DRY_RUN ] [ HALT ]`, progress bar, results table |
| `tui-03-results.svg/.html` | `t` | Historical runs drill-down |
| `tui-04-settings.svg/.html` | `s` | PROVIDER CONFIGURATION / PATHS / COMPLIANCE FRAMEWORK, `[ SAVE_CONFIGURATION ]` |

SVGs are headless renders from `tests/__snapshots__/` (86/86 tests pass).

## Web Dashboard (Next.js 16.2.10 production build, http://127.0.0.1:3000)
| File | Route | Content |
|------|-------|---------|
| `web-01-dashboard.png` | `/` | DASHBOARD — 4 stat cards (LAST RUN b6f51880, ATTACKS 53, LAST SCORE 0%, VAULT LOCKED), SCORE TREND, RECENT RESULTS + RECENT RUNS tables |
| `web-02-run-attack.png` | `/run` | ATTACK EXECUTION — COMPLIANCE SCORE 0%, LIVE ATTACK STREAM (53 scenarios, error status), EVIDENCE VAULT LOG 4 entries |
| `web-03-results.png` | `/results` | RESULTS HISTORY — 10 of 10 runs filterable table (PASS 0/53 vs 53/53), provider gpt-4o, score 0%/100% |
| `web-04-settings.png` | `/settings` | SETTINGS — PROVIDER CONFIGURATION (openai/gpt-4o), PATHS (./certifyai_vault, certifyai.db), COMPLIANCE FRAMEWORK (ALL FRAMEWORKS) |

All web pages use Stealth Brutalist theme: #D4FF00 acid-green, #FF0055 red, #00E5FF cyan, #090909/#121212 surfaces.

## How to regenerate
```bash
# CLI
.venv/bin/python -m certifyai.cli.main --help
.venv/bin/python -m certifyai.cli.main list-categories
.venv/bin/python -m certifyai.cli.main run --dry-run --db /tmp/... 
.venv/bin/python -m certifyai.cli.main verify

# TUI SVGs
.venv/bin/python -m pytest tests/test_snapshots.py --snapshot-update

# Web (production)
cd certifyai/web && npm run build && npm run start -- --port 3000 --hostname 127.0.0.1
# then agent-browser capture / /run /results /settings
```
