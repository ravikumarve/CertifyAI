# 🤖 CertifyAI — Project Command Center

**Project:** Continuous Compliance Engine for AI Runtimes
**Delivery Model:** Shippable Boilerplate (PyPI + Gumroad)
**Primary Stack:** Python 3.11+ (asyncio, Pydantic v2, LiteLLM, Click, Textual), Next.js 14 (Tailwind, motion, recharts), SQLite
**Host:** Dell Latitude 3460 (Ubuntu) — CPU-only, no heavy Docker/K8s

---

## 📋 Project State

| Attribute | Value |
|-----------|-------|
| **Phase** | Phase 4c — TUI Windowed-Frame Finale |
| **Code written** | ~5,700 lines Python + ~800 lines Next.js |
| **Documents** | 17 docs in `docs/` (Waves 1-3) |
| **Git repo** | https://github.com/ravikumarve/CertifyAI |
| **Revenue** | $0 |
| **Next action** | Push Phase 5 commit + `npm run build` + deploy dev server, OR Gumroad launch prep (pricing page, commercial license bundle, README polish) |

---
## Visual verification (mandatory — do not skip)
After any change to layout, styling, component structure, or data
rendering in the web frontend:

1. Open the running dev server URL with agent-browser
2. Capture a full-page screenshot: `agent-browser screenshot --full`
3. If checking interactive elements (buttons, forms, nav), use
   `agent-browser screenshot --annotate` to get numbered element
   references alongside the image
4. If a reference mockup HTML exists in the repo, open it too and
   compare directly — spacing, alignment, colors, missing elements
5. Check the browser console for errors: `agent-browser console`
6. If anything doesn't match or an error is present, fix it and
   repeat steps 1-5 before reporting the task as done

Never report a UI change as complete without having actually seen
it render via a full-page screenshot. A code change that "should"
look right is not verified until confirmed visually.


## Visual verification (mandatory — do not skip)
After any change to a Textual screen (CSS, compose(), widget layout,
DataTable columns, panel titles):

1. Run `pytest tests/test_snapshots.py --snapshot-update` to generate
   fresh SVG captures of every screen
2. Open the generated SVG(s) in tests/__snapshots__/ and read the
   actual content — check for: collapsed/zero-height widgets
   (bordered widgets need explicit height), duplicate table columns
   (add_columns() must be guarded with `if not table.columns`),
   blank/missing labels (bracket text `[...]` must be wrapped in
   rich.text.Text() to avoid Rich markup parsing it as a style tag)
3. If a reference mockup HTML exists, compare structure against it
4. Fix any issue found, regenerate snapshots, and re-check before
   reporting the task as done

Do not run --snapshot-update carelessly — it overwrites the baseline
even for a broken render. Only update the baseline once you've
visually confirmed the new SVG is actually correct.

---

## 🧠 Architecture Decisions

### ADR-001: Boilerplate over SaaS
- **Context:** Original idea targeted enterprise B2B SaaS ($30K–$150K/yr). Solo dev cannot sustain enterprise sales cycles, lacks SOC 2 certification, and cannot provide 24/7 support.
- **Decision:** Pivot to downloadable boilerplate product. Ship as PyPI package (free CLI/TUI) + Gumroad bundle (paid Pro/Enterprise tiers with Web Dashboard, docs, commercial license).
- **Consequence:** Eliminates ops burden, certification barrier, and sales cycle. Revenue in weeks instead of months. Zero direct competitors in this category.

### ADR-002: Python monolith for engine + CLI + TUI
- **Context:** LLM ecosystem is Python-dominant (LiteLLM, LangChain eval tools, guardrails libraries). Solo dev needs one language to maintain.
- **Decision:** Core engine, CLI (Click), and TUI (Textual) all in Python 3.11+. Web Dashboard is the only non-Python component (Next.js 14).
- **Consequence:** Single language for 80% of the codebase. Faster development. Customer only needs Python installed for core functionality.

### ADR-003: SQLite as primary database
- **Context:** Boilerplate must be self-contained. PostgreSQL adds setup friction. VectorDB adds complexity.
- **Decision:** SQLite via SQLAlchemy 2.0 + aiosqlite. Single-file database. Evidence vault stored as filesystem directory with SHA-256 hash chain.
- **Consequence:** Zero-infra setup for customer. Easy backup/portability. Optional PostgreSQL for advanced users.

### ADR-004: LiteLLM as sole LLM abstraction
- **Context:** Original idea mentioned LangChain, LlamaIndex, and LiteLLM. Maintaining 3 SDK integrations is scope creep.
- **Decision:** LiteLLM only. Covers 100+ providers (OpenAI, Anthropic, Ollama, Gemini, any OpenAI-compatible endpoint).
- **Consequence:** Simpler codebase. Customer flexibility. Works air-gapped with Ollama.

### ADR-005: Shared SQLite file across all interfaces
- **Context:** CLI, TUI, and Web Dashboard all need access to attack results and evidence.
- **Decision:** All three read/write the same `certifyai.db` file. Web Dashboard uses `better-sqlite3` (synchronous Node.js binding) for direct reads. No API server.
- **Consequence:** Eliminates need for a separate backend server. Simplifies deployment. Shared state without sync complexity.

---

## 💾 Session Memory Ledger

### [2026-07-30 14:30] — Windowed-Terminal Frame + Single-Row Header (Mockup Match)
- **State:** Success — 86/86 tests passing, pushed `d1fe7d5`
- **MCP Data Used:** direct file reads (app.py for CSS/compose/event handlers)
- **Agency Agents Deployed:** Orchestrator (direct execution — all CSS, compose, and handler changes)
- **Architectural Decision:** Wrapped whole TUI in `Container(id="outer-frame")` with `border: heavy #444444` and `margin: 1 2` to create a windowed-terminal look sitting on pure black screen. Combined `>_` prompt, 4 tab labels, and version text into ONE horizontal `#tui-header` row (height:2). Hidden `TabbedContent`'s built-in `Tabs` widget (`height:0; overflow:hidden`) to prevent visual duplication. Header-tab Buttons handle clicks via `CertifyAIApp.on_button_pressed` (not Tabs widget). `action_switch_tab` now toggles `.active-tab` CSS class for D4FF00 underline indicator. Footer moved outside `#outer-frame` to avoid `border: heavy` overwriting its content.
- **Key Visual Changes:**
  1. **Outer frame**: `┏━━...┓` top border, `┃` side borders, `┗━━...┛` bottom border — frame chars from `border: heavy`
  2. **Header**: `┃>_│Dashboard│Run_Attack│Results│Settings│certifyai-tui // v1.0.4┃` — `>_` in acid green, active tab white bold, others muted, version `#444444`
  3. **Dashboard**: 2×2 stat cards + Recent Runs data table with 7 columns
  4. **Run Attack, Results, Settings** — all properly frame-wrapped
  5. **Footer**: hotkey bar below frame bottom border
- **Mockup Reference:** `certifyai_tui_simulator_stealth_brutalist_full.html` (all 4 pages, replaces old single-page version)
- **Build Status:** Pushed to GitHub (`d1fe7d5`)
- **Next Turn Directive:** Continue Phase 5 Web Dashboard polish, or begin Gumroad launch prep (pricing page, commercial license bundle, README polish)

### [2026-07-30 13:58] — TUI Stealth Brutalism Redesign + Snapshot Fix
- **State:** Success — 4 snapshot SVGs generated, 86/86 tests passing
- **Files Modified:** `certifyai/tui/app.py` (CSS rewrite, compose restructure), `tests/test_snapshots.py` (press keys fixed)
- **MCP Data Used:** direct file reads, `runpy`/`export_screenshot()`/`take_svg_screenshot()` debugging across isolated apps
- **Agents Deployed:** Orchestrator (direct execution — all CSS, compose, test changes)
- **Architectural Decision:** Added `Container, Vertical { height: auto; }` to CSS — Textual's default `height: 1fr` on Container causes `take_svg_screenshot` (used by `snap_compare` fixture) to collapse parent layout when Container/Vertical subclasses are yielded inside TabPane. `run_test()` is unaffected but `snap_compare` uses `app.run(headless=True)` which manifests the bug.
- **Changes Made:**
  1. **Header bar**: Replaced `Header()` with custom `Container(id="header-bar")` containing `Static(" >_ ", id="header-prompt")` and `Static("certifyai-tui // v1.0.3", id="header-version")`, using `layout: horizontal` (not `dock: left/right` — that broke SVG export)
  2. **CSS (Stealth Brutalism)**: Full rewrite — `#D4FF00` acid-green, `#FF0055` electric-red, `#00E5FF` cyber-blue, `#090909`/`#121212`/`#222222` surfaces
  3. **Tab bindings**: Snapshot press keys fixed from numbers to letters (`"2"`→`"r"`, `"3"`→`"t"`, `"4"`→`"s"`)
  4. **Run Attack compose**: Restructured — config info, buttons, progress bar in single `#run-config-panel` with green border + `border_title=" EXECUTION_CONFIG "`
  5. **DataTable columns**: Changed to `("ID", "SCENARIO", "CATEGORY", "STATUS")` with colored Rich markup status
  6. **Root cause**: Textual's `Container` default CSS has `height: 1fr`. When a `Container`/`Vertical` subclass is `yield`ed inside a `TabPane`, `take_svg_screenshot` (headless `app.run()`) computes 1fr height = fill all space, collapsing the parent TabbedContent which pushes header-bar off-screen. `run_test()` doesn't trigger this. Fix: override with `Container, Vertical { height: auto; }` globally.
- **Key Insight:** `take_svg_screenshot` uses `app.run(headless=True, auto_pilot=...)` which creates a fresh asyncio loop. `run_test()` uses the existing test loop. The `height: 1fr` bug only manifests in `app.run()` path, making `snap_compare` produce broken SVGs while manual `run_test()` debugging shows correct layout.
- **Build Status:** 86/86 tests pass (82 unit + 4 snapshot). All 4 SVGs at `tests/__snapshots__/test_snapshots/*.svg` (49–58 KB each) include the `>_` prompt and version text on line 0.
- **Next Turn Directive:** Commit and push to GitHub, then begin Gumroad launch prep (pricing page, commercial license bundle, README polish) OR start next feature sprint.

### [2026-07-22 07:30] — Fix 5 bugs: duplicate render, trend smoothing, stats, vault, settings
- **State:** Success — 10 files changed, pushed `38f7a5a`, 82 tests pass, build clean
- **Fixes Applied:**
  - **#1 Duplicate page content**: Removed `overflow-y-auto` cascade that caused flex content to overflow. Main now has `min-h-screen overflow-y-auto`, inner wrapper constrains flex children. AttackTable has scrollable tbody with `sticky top-0` thead and `min-h-0` flex chain — prevents DOM nesting artifacts.
  - **#2 Trend smoothing**: `type="monotone"` → `type="linear"` on recharts Line. Straight segments between real data points can't invent fake peaks.
  - **#3 Stats consistency**: `_dashboard()` now returns latest-run `passed`/`failed`/`total` instead of SQL SUM across all runs. All-time aggregates exposed as `all_time_passed`/`all_time_total`. All 4 stat cards show "Latest Run" subtitle. Results header shows "TOTAL ATTACKS (all-time)" for context.
  - **#4 Vault log**: Engine runner `_persist_results()` now computes SHA-256 run hash from result hashes, chains to previous entry via `previous_hash`, and saves `EvidenceChainRecord` with rich metadata (message, level, passed/failed). DB columns mapped to frontend VaultEntry shape in `db_query.py`. Two vault entries now visible in API with messages like "Run aafca4bc — 53/53 passed, score 100%".
  - **#5 Settings polish**: Source badge moved to separate line (was inline with subtitle — text collision). `null` values now render as `"—"` instead of literal `"null"`.
- **Build Status:** Build clean. 7 routes live.
- **Next Turn Directive:** Gumroad launch prep (pricing page, commercial license bundle, README polish), or deploy dev server, or start next feature sprint.
---
- **State:** Success — 6 files modified/created, build compiles clean, 7 routes verified live
- **MCP Data Used:** direct file reads (all 12 source files across app/, components/, lib/)
- **Agents Deployed:** Orchestrator (direct execution — trend chart component, results filter, polish pass)
- **Changes Made:**
  - **New: `components/trend-chart.tsx`** — recharts `LineChart` with acid-green score trend over time, dark-themed CartesianGrid, tooltip, dynamic Y axis 0-100%, auto-fetches from `/api/dashboard?mode=runs`
  - **Updated: `app/page.tsx`** — integrated TrendChart below StatsCards, added spinner loading state, RETRY button on error, response_time_ms display on recent results table
  - **Updated: `app/results/page.tsx`** — added text search (by ID/provider/model), status filter dropdown (All/Pass/Fail/Running/Error), sort by date/score↑/score↓, StatusBadge component, "X of Y runs" count, empty filter state
  - **Updated: `app/settings/page.tsx`** — dynamic section rendering from API, shows config source badge, flattened nested config entries, spinner loading, empty state
  - **Updated: `components/sidebar.tsx`** — nav items with active dot indicator + glow, color-coded status dots (green/red/grey), cleaner status panel layout
  - **Updated: `components/attack-table.tsx`** — added Response column (ms), spinning indicator during execution, colSpan=5
  - **Updated: `components/vault-log.tsx`** — improved time formatting, color-coded log levels (FAIL=red, WARN=orange), adaptive font-size for long hashes
  - **Updated: `lib/types.ts`** — added `attack_name`, `evaluation` fields to AttackResult; added `skipped`, `engine_version` to RunSummary; updated VaultEntry with all DB columns
  - **Updated: `app/globals.css`** — added `.loading-spinner`, `.brut-badge`, `.brut-input` utility classes
- **Build Status:** `npx next build` compiles clean (zero TS/ESLint errors). 7 routes: `/`, `/run`, `/results`, `/settings` (static) + `/api/dashboard` (dynamic). All live-verified HTTP 200.
- **Next Turn Directive:** Push Phase 5 commit + `npm run build` + deploy dev server, OR Gumroad launch prep (pricing page, commercial license bundle, README polish)
- **MCP Data Used:** direct file reads (Textual Button source at .venv/lib/python3.12/site-packages/textual/widgets/_button.py), Python REPL tests of Content.from_text()
- **Agents Deployed:** Orchestrator (direct execution — 1 import + 3 string→Text changes + 1 commit)
- **Root Cause Found:** Textual's `Content.from_text()` parses `[` as Rich markup delimiters. The string `" [ RUN_BATTERY ] "` was parsed as a markup tag `[RUN_BATTERY]`, reducing visible plain text to just `'  '` (two spaces). The button rendered an empty label with a full border box — exactly matching the "blank box" symptom.
- **Fix:** Wrapped all three button labels in `rich.text.Text()` objects: `Button(Text(" [ RUN_BATTERY ] "), ...)`. This bypasses `Content.from_text()` markup parsing, preserving brackets as literal characters.
- **Why height:3→5 didn't help:** The label text was never being rendered at all — CSS height couldn't fix a content absence issue.
- **Build Status:** Pushed to GitHub (`7a37ffb`)
- **Next Turn Directive:** Phase 5 — Web Dashboard (Next.js) OR Gumroad prep
- **State:** Success — 1 fix applied, 82 tests passing, pushed `734ea1a`
- **MCP Data Used:** direct file reads (Textual Button.DEFAULT_CSS for line-pad inspection, certifyai/tui/app.py CSS block)
- **Agents Deployed:** Orchestrator (direct execution — 1 CSS edit + 1 commit)
- **Root Cause Found:** Button inherits `line-pad: 1` from Textual default CSS (1 row padding above and below text). With `height: 3` and `border: solid`, content area = 1 row, but the internal Label needs 3 rows (line-pad top + text + line-pad bottom). Label gets squeezed to 1 row, text disappears. `height: 5` gives 3 rows of content — exact fit.
- **Diagnostic Path:** Tested Rich markup bracket theory (negative — Rich correctly treats `[ RUN_BATTERY ]` as plain text), then inspected Button.DEFAULT_CSS to find inherited `line-pad: 1` as the hidden constraint.
- **Note:** Rich markup brackets `[...]` confirmed NOT the cause — Textual does NOT choke on them.
- **Build Status:** Pushed to GitHub (`734ea1a`)
- **Next Turn Directive:** Phase 5 — Web Dashboard (Next.js) OR Gumroad prep
- **State:** Success — 2 fixes applied, 82 tests passing, pushed `35108cd`
- **MCP Data Used:** direct file reads (certifyai/tui/app.py for clear() calls and CSS)
- **Agents Deployed:** Orchestrator (direct execution — 2 edits + 1 commit)
- **Fixes Applied:**
  1. Changed `table.clear()` → `table.clear(columns=True)` in `_start_run()` and `on_attack_finished()` — DataTable.clear() only removes rows by default, so `add_columns()` was stacking duplicate columns on each subsequent run (confirmed 3× triple columns in screenshot)
  2. Bumped `#run-buttons Button` width from 18→22 — `[ RUN_BATTERY ]` is 17 chars, border consumes 2 cols, leaving only 16 usable
- **Note:** CSS height:3 fix for Buttons is correct in code but may appear stale if Textual process wasn't killed/restarted (no hot-reload for inline CSS)
- **Build Status:** Pushed to GitHub (`35108cd`)
- **Next Turn Directive:** Phase 5 — Web Dashboard (Next.js) OR Gumroad prep
- **State:** Success — 2 fixes applied, 82 tests passing, pushed `152a1f0`
- **MCP Data Used:** direct file reads (certifyai/tui/app.py CSS block)
- **Agents Deployed:** Orchestrator (direct execution — 2 CSS/logic edits + 1 commit)
- **Fixes Applied:**
  1. Added `height: 3;` to base `Button` CSS — same root cause as tab fix; full solid border was consuming default height, making RUN_BATTERY/DRY_RUN/HALT/Save buttons invisible
  2. Set `show_percentage=False` on ProgressBar — bar was still showing built-in "0%" label below custom "#run-progress-text" Static
- **Build Status:** Pushed to GitHub (`152a1f0`)
- **Next Turn Directive:** Phase 5 — Web Dashboard (Next.js) OR Gumroad prep OR whatever is next
- **State:** Success — 5 fixes applied, 82 tests passing, pushed `7b7dca9`
- **MCP Data Used:** direct file reads (certifyai/tui/app.py for CSS and compose methods)
- **Agents Deployed:** Orchestrator (direct execution — 4 CSS/logic edits + 1 commit)
- **Fixes Applied:**
  1. Added `height: 3;` to `Tabs Tab` CSS — tab text was invisible because border consumed all default height
  2. Changed `show_eta=True` → `show_eta=False` on ProgressBar — eliminated duplicate progress readout (custom `#run-progress-text` + ProgressBar's built-in label were stacking)
  3. Added `border_title = "EXECUTION_CONFIG"` on `#run-config-summary` Container — uses Textual's native border-title rendering instead of trying to fake absolute positioning
  4. Tab labels uppercased (`DASHBOARD`, `RUN_ATTACK`, `RESULTS`, `SETTINGS`) per mockup
  5. Button labels wrapped in brackets (`[ RUN_BATTERY ]`, `[ DRY_RUN ]`, `[ HALT ]`) per mockup
- **Build Status:** Pushed to GitHub (`7b7dca9`)
- **Next Turn Directive:** Phase 5 — Begin Web Dashboard (Next.js 14 + Tailwind + recharts) OR Gumroad prep (pricing page, commercial license bundle) OR other direction

### [2026-07-21 20:00] — Phase 4b: CLI Rich UI & TUI Polish Complete
- **State:** Success — 4 files modified, 88 tests passing, Rich+TUI end-to-end verified
- **MCP Data Used:** direct file reads (cli/main.py, tui/app.py, engine/runner.py, database/models.py)
- **Agents Deployed:** Orchestrator (CLI Rich refinements, bug fixes), general agent (TUI rewrite)
- **Architectural Decisions:**
  - CLI uses Rich `Progress` bar during attack execution (via `progress_callback` on `AttackRunner`)
  - CLI uses Rich `Panel` for config header and results summary, `Table` for per-result/verify/categories
  - TUI uses Textual v8 with 4 tab panes (Dashboard, Run Attack, Results, Settings) and `@work` decorator for async runs
  - `AttackRunner` now accepts optional `progress_callback(scenario_name, result)` for live updates
  - Bug fixes: `config_json` serialized to JSON string (not dict), `evaluation` field serialized, status CHECK constraint widened
- **CLI Enhancements:**
  - `run`: Progress bar live update, summary Panel, color-coded results Table, --concurrency option
  - `list-categories`: Rich Table with category/severity/scenarios
  - `verify`: Rich Table with run IDs, status icons, mismatch count
  - `init`: Rich Panel with config summary
- **TUI Features (certifyai/tui/app.py, 804 lines):**
  - Dashboard tab: status cards, last 5 runs table, auto-refresh
  - Run Attack tab: Start/Dry Run buttons, progress bar, per-scenario results table
  - Results tab: historical runs table with per-attack detail drill-down
  - Settings tab: provider/model/api-key/vault/db inputs, framework dropdown, save to certifyai.yaml
- **Bug Fixes:**
  - `config_json` column: dict→JSON string serialization (was `sqlite3.ProgrammingError`)
  - `evaluation` column: dict→JSON string serialization in ResultRecord creation
  - `runs.status` CHECK constraint: widened to include 'pass', 'error', 'skipped' values
  - Rich `Style(color="dim")` → `Style(color="grey58")` for skipped status
- **Test Results:** 88/88 tests passing (82 unit + 6 integration)
- **Build Status:** Pending push to GitHub
- **Next Turn Directive:** Phase 5 — Begin Web Dashboard (Next.js 14 + Tailwind + recharts) OR Gumroad prep (pricing page, commercial license bundle)

### [2026-07-21 19:45] — Phase 4: SQLite Database Layer Complete
- **State:** Success — 13 new files, 88 tests passing, CLI wired end-to-end
- **MCP Data Used:** code_tree (project structure), direct file reads (models.py, runner.py, vault.py for cross-reference)
- **Agents Deployed:** Orchestrator (direct execution — all database code, runner wiring, CLI updates, tests)
- **Architectural Decisions:**
  - SQLAlchemy 2.0 async + aiosqlite with WAL mode for concurrent CLI+web reads
  - 5 tables: `runs`, `results`, `evidence_chain`, `config`, `_schema_version` — no `users` or `framework_cache` (added post-v1)
  - JSON evidence vault remains as parallel output system (dual-write for backwards compatibility)
  - Engine version embedded in `_schema_version` for migration tracking
  - Evidence chain entries computed from vault hash files and linked via SHA-256
- **Files Created (4):**
  - `certifyai/engine/database/__init__.py` — Package init
  - `certifyai/engine/database/models.py` — 5 ORM tables with SQLAlchemy 2.0 mapped_column
  - `certifyai/engine/database/manager.py` — DatabaseManager class (init, CRUD, aggregation, chain)
  - `tests/test_database.py` — 20 tests (models, CRUD, aggregation, chain linking, schema version, WAL)
- **Files Modified (2):**
  - `certifyai/engine/runner.py` — `AttackRunner` accepts `db_manager` param, calls `_persist_results()` after run
  - `certifyai/cli/main.py` — `init` command creates DB schema, `run` command accepts `--db` and stores evidence chain
- **Test Results:** 88/88 tests passing (82 unit + 6 integration, 17 new database tests)
- **Build Status:** Pending push to GitHub
- **Next Turn Directive:** Phase 5 — Begin Web Dashboard (Next.js 14 + Tailwind + recharts) OR TUI polish

### [2026-07-21 19:15] — Phase 3: LiteLLM Integration Tests with NVIDIA NIM
- **State**: Success — 6 integration tests passing against live NVIDIA NIM API
- **MCP Data Used**: direct file reads (lite_llm.py, models.py for API config)
- **Agents Deployed**: Orchestrator (direct execution — conftest dotenv loading, integration test file)
- **Architectural Decisions**:
  - `.env` file auto-loaded via `python-dotenv` in `conftest.py` at module import time
  - Integration tests guarded by `--run-integration` flag + `pytest.mark.integration`
  - NVIDIA NIM free tier rate limits handled gracefully (tests skip on 429)
  - Only `prompt_injection` category used for attack-run tests (3 scenarios, 2 concurrency)
- **Files Created (1)**:
  - `tests/test_integration_llm.py` — 6 tests (basic completion, attack execution, performance)
- **Files Modified (2)**:
  - `tests/conftest.py` — Added automatic `.env` loading via `python-dotenv`
  - `.env` — Local only (gitignored), contains NVIDIA NIM API key
- **Test Results**: 71/71 passing — unit (65) + integration (6)
- **Build Status**: Pushed to GitHub (after next commit)
- **Next Turn Directive**: Phase 4 — Web Dashboard (Next.js 14 + Tailwind + recharts), OR SQLite database wiring

### [2026-07-21 18:30] — Phase 2: Plugin System Complete (6 categories, 18 scenarios, external loading)
- **State**: Success — 7 new/changed files, 65/65 tests passing
- **MCP Data Used**: code_tree (existing plugin structure), direct file reads (existing plugins for pattern matching)
- **Agents Deployed**: Orchestrator (direct execution — all plugin code, registry rewrite, CLI update, tests)
- **Architectural Decisions**:
  - 6 attack categories × 3 scenarios each = 18 built-in scenarios
  - External plugins load from user-specified directories via `--plugin-dir` (multiple allowed)
  - External plugins append scenarios to built-in ones (no override — all scenarios run)
  - `plugin_template.py` lives in the package but is excluded from production loading
  - `list-categories` CLI command for discovering available attacks
- **Files Created (5)**:
  - `certifyai/engine/redteam/policy_violation.py` — 3 scenarios (harmful content, ToS, impersonation)
  - `certifyai/engine/redteam/hallucination.py` — 3 scenarios (factual grounding, citations, statistics)
  - `certifyai/engine/redteam/bias.py` — 3 scenarios (stereotyping, allocation, cultural)
  - `certifyai/engine/redteam/plugin_template.py` — Annotated template with evaluation recipes
  - `tests/test_plugins.py` — 21 tests (registry, loading, external, integrity)
- **Files Modified (2)**:
  - `certifyai/engine/registry.py` — Added `_load_external_plugins()`, `reload()`, `list_categories()`
  - `certifyai/cli/main.py` — Added `--plugin-dir`, `list-categories` command
- **Test Results**: 65/65 passing — models (17), evidence (10), compliance (11), plugins (21), hasher (6)
- **Build Status**: Pushed to GitHub (`4729cc6`)
- **Next Turn Directive**: Phase 3 — LiteLLM integration tests with real provider, OR begin Web Dashboard (Next.js 14 + Tailwind + recharts), OR SQLite database wiring

### [2026-07-21 16:30] — Engine Core Phase 1 Complete (Models + CLI + Evidence + Compliance + 44 Tests)
- **State**: Success — Phase 1 implementation complete. 26 new files created.
- **MCP Data Used**: code_tree (AST verification for existing file structure), direct file reads (models.py, runner.py for cross-reference consistency)
- **Agents Deployed**: Orchestrator (direct execution — wrote all engine core files, CLI, tests)
- **Architectural Decisions**:
  - `AttackResult` requires `category` and `severity` as mandatory fields (reflects real model schema)
  - Evidence vault uses append-only SHA-256 hash chain with per-file `.hash` sidecar files
  - Compliance mapper supports pluggable YAML framework definitions in a `frameworks/` dir
  - CLI uses `RunConfig` + `ProviderConfig` (not the deprecated `AttackConfig`)
  - MockLLMClient returns predetermined responses for dry-run testing
- **Files Created (26)**:
  - `certifyai/engine/evidence/__init__.py`, `hasher.py`, `vault.py`
  - `certifyai/engine/compliance/__init__.py`, `mapper.py`
  - `certifyai/engine/compliance/frameworks/eu_ai_act.yaml`, `soc2.yaml`, `nist_ai_rmf.yaml`
  - `certifyai/cli/__init__.py`, `main.py`
  - `certifyai/tui/__init__.py`, `app.py`
  - `tests/__init__.py`, `conftest.py`, `test_models.py`, `test_evidence.py`, `test_compliance.py`
- **Test Results**: 44/44 tests passing — models (17), evidence (10), compliance (11), hasher (6)
- **Build Status**: `pip install -e ".[dev]"` works in venv. CLI `--help` responds. 52 ruff warnings (mostly line-length) — not blocking for alpha.
- **Next Turn Directive**: Phase 2 — Plugin system completion (scenario registry + attack plugin template), LiteLLM integration tests with real provider, or begin Web Dashboard (Next.js)

### [2026-07-21 15:00] — GitHub Repository Created & Initial Commit Pushed
- **State:** Success — Repo created at `https://github.com/ravikumarve/CertifyAI`
- **Description:** "Continuous compliance engine for AI runtimes. Self-hosted CLI + TUI + Web Dashboard that tests LLMs against 30+ attack scenarios and generates audit-ready evidence for EU AI Act, SOC 2 Type II, and NIST AI RMF. No subscription. No cloud dependency. Bring your own LLM key."
- **Files pushed:** 21 files — README.md, idea.md, AGENTS.md, .gitignore, and 17 docs
- **Commit message:** "Initial commit: complete documentation suite for CertifyAI"
- **Branch:** main
- **Next Turn Directive:** Begin implementation — pyproject.toml scaffold, Pydantic models, LiteLLM integration, attack plugin system

### [2026-07-21 14:30] — Wave 3 Docs Complete (GTM Suite + Commercial License)
- **State:** Success — All 17 docs complete (Waves 1-3), 20,668 total lines, 1.1MB
- **MCP Data Used:** direct file reads (agent profiles, existing docs for cross-reference consistency)
- **Agency Agents Deployed:** @pricing-analyst (pricing-strategy.md), @content-creator (gumroad-listing.md + devto-content-plan.md), @growth-hacker (producthunt-launch-kit.md), @social-media-strategist (community-launch-strategy.md), @support-responder (support-plan.md), @legal-compliance-checker (commercial-license.md)
- **Docs Created in Wave 3:**
  - `docs/pricing-strategy.md` — 729 lines, value quantification ($12K–$32K DIY vs $149), WTP by 5 segments, 12-month revenue projections ($78K–$665K), $149 recommended
  - `docs/gumroad-listing.md` — 312 lines, full Pro + Enterprise listing copy, comparison table, FAQ, refund policy
  - `docs/producthunt-launch-kit.md` — 956 lines, tagline, 18 target makers, hour-by-hour schedule, 8 comment templates, cross-promotion with HN/Reddit
  - `docs/devto-content-plan.md` — 612 lines, 8 article plan with headlines, structures, code snippets, Reddit blurbs
  - `docs/community-launch-strategy.md` — 1,088 lines, 4 Reddit post drafts, 18-tweet X thread, LinkedIn posts, platform-specific norms
  - `docs/support-plan.md` — 1,027 lines, tier definitions, 10 email templates, self-service architecture, 90% ticket deflection target
  - `docs/commercial-license.md` — 351 lines, Apache 2.0 vs Pro vs Enterprise, plain-English EULA, India governing law, explicit compliance disclaimer
- **Key Business Decisions:** $149 Pro / $499 Enterprise confirmed with sensitivity analysis. India jurisdiction for licensing. No Discord for v1 (GitHub Discussions only). Support hard-walled by tier. 14-day no-questions refund.
- **Next Turn Directive:** Phase 1 — Begin coding (Engine Core: pyproject.toml → Pydantic models → LiteLLM integration → Attack plugin system)

### [2026-07-21 13:00] — Wave 2 Docs Complete (UX Flows + Test Strategy + Attack Catalog + Compliance Spec + Security + DB Schema)
- **State:** Success — All 10 docs complete (Wave 1 + Wave 2), 15,593 total lines, 836KB
- **MCP Data Used:** code_tree (structure verification), direct file reads (agent profiles, existing docs for context)
- **Agency Agents Deployed:** @ux-architect (ux-flows.md), @test-automation-engineer (test-strategy.md), @model-qa-specialist (attack-scenario-catalog.md), @compliance-auditor (compliance-framework-spec.md), @security-architect (security-architecture.md), @database-optimizer (database-schema.md)
- **Docs Created in Wave 2:**
  - `docs/ux-flows.md` — 2,343 lines, 3 persona journeys, 7 CLI flowcharts, 6 TUI screens, 8 dashboard pages, 9 error recovery flows
  - `docs/test-strategy.md` — 2,924 lines, pyramid strategy, Playwright E2E, property-based tests (hypothesis), CI pipeline with flake quarantine
  - `docs/attack-scenario-catalog.md` — 2,136 lines, 36 attack scenarios (6 categories × 6 each), plugin interface spec, scoring methodology
  - `docs/compliance-framework-spec.md` — 1,670 lines, EU AI Act Art. 9-15 deep map, SOC 2 CC3-CC9, NIST AI RMF 4 functions, ISO 42001, report JSON Schema
  - `docs/security-architecture.md` — 1,253 lines, STRIDE threat model (36 attack scenarios), evidence vault adversarial analysis, API key management, supply chain risk, 5-phase security roadmap
  - `docs/database-schema.md` — 1,752 lines, 7 tables with full CREATE TABLE SQL, 15 query patterns, index strategy, WAL mode config, PostgreSQL migration path, query cookbook
- **Key Architectural Decisions:** Evidence chain is detect-only (not prevent-only) — cross-DB commitment needed pre-v1. LiteLLM flagged as highest supply chain risk. WAL mode for concurrent CLI+Dashboard SQLite reads. 13 high-value attacks serving all 4 frameworks identified.
- **Next Turn Directive:** Wave 3 — GTM documents (Pricing, Gumroad Listing, PH Launch Kit, Dev.to Content Plan, Community Strategy, Support Plan) OR begin Phase 1 coding

### [2026-07-21 12:00] — Wave 1 Docs Complete (Market Research + Competitive Analysis + PRD + Technical Architecture)
- **State:** Success — All 4 foundation documents created, 3,515 total lines
- **MCP Data Used:** websearch (competitor research, EU AI Act timeline, market sizing data), code_tree (project structure verification)
- **Agency Agents Deployed:** @trend-researcher (market-research-report.md), @business-strategist (competitive-analysis.md), @product-manager (PRD.md), @software-architect (technical-architecture.md)
- **Docs Created:**
  - `docs/market-research-report.md` — 357 lines, $492M TAM analysis, 25 sources, 4 customer segments, risk-adjusted entry recommendation
  - `docs/competitive-analysis.md` — 721 lines, 8 competitor deep-dives, positioning maps, Porter's Five Forces, 12-18 month competitive window assessment
  - `docs/PRD.md` — 863 lines, 3 personas (Priya/Marcus/Elena), 13 user stories, 7 non-goals with rationale, 3-phase launch plan
  - `docs/technical-architecture.md` — 1,574 lines, C4 architecture model, 8 ADRs, complete SQLite schema, plugin attack architecture, evolution strategy
- **Key Architectural Decisions:** ADR-006 (plugin attack architecture), ADR-007 (hybrid filesystem+SQLite evidence vault), ADR-008 (direct SQLite reads from Next.js, no API server)
- **Next Turn Directive:** Wave 2 — UX Flows, Test Strategy, Attack Scenario Catalog, Compliance Framework Spec, Security Architecture, Database Schema

### [2026-07-21 10:00] — CertifyAI Idea Validation & Pivot
- **State:** Success — Idea validated, pivoted from enterprise SaaS to boilerplate product
- **MCP Data Used:** websearch (competitor analysis: Vanta, Credo AI, Drata, IBM watsonx, Holistic AI), websearch (regulatory landscape: EU AI Act enforcement 2026, fines up to €35M/7%, Digital Omnibus delay), websearch (market size: $3.4B AI governance market at 39.4% CAGR)
- **Agents Deployed:** Orchestrator (direct execution — competitive research, regulatory analysis, feasibility assessment)
- **Architectural Decisions:** ADR-001 through ADR-005 (see above)
- **Key Findings:**
  - 78% of orgs not ready for EU AI Act (Aug 2026 deadline)
  - No competitor ships a downloadable AI compliance engine
  - Incumbents (Vanta $350M, Credo AI $41M) are SaaS-only at $30K+/yr
  - Boilerplate model eliminates all 5 critical risks for solo dev
- **Build Status:** Pre-code phase complete. idea.md rewritten with full tech stack + 8-week build plan. AGENTS.md created.
- **Next Turn Directive:** Begin Phase 1 implementation (Engine Core — weeks 1-3) OR validate demand first (write Dev.to posts, launch waitlist, gauge community response before writing code)

---

## 🎯 Quick Reference

### Key Commands (for development)
```bash
# Run all tests
pytest tests/ -v

# Run unit tests only (skip integration)
pytest tests/ -v -m "not integration"

# Run integration tests (requires .env with NVIDIA NIM key)
pytest tests/ -v -m integration --run-integration

# CLI
python -m certifyai.cli.main init --db /path/to/certifyai.db
python -m certifyai.cli.main run --provider openai --model gpt-4o --db /path/to/certifyai.db

# TUI
python -m certifyai.tui.app
```

### Directory Structure
```
certifyai/
├── cli/                  # Click commands
├── tui/                  # Textual screens
├── engine/               # Core logic
│   ├── redteam/          # Attack scenarios (6 categories, 18 scenarios)
│   ├── evidence/         # Vault & SHA-256 hash chain
│   ├── compliance/       # Framework mapper (EU AI Act, SOC 2, NIST AI RMF)
│   └── database/         # SQLAlchemy 2.0 ORM + async DatabaseManager
├── web/                  # Next.js dashboard (future)
├── docs/                 # MkDocs documentation
├── tests/                # pytest (88 tests — 82 unit + 6 integration)
├── pyproject.toml
└── README.md
```
