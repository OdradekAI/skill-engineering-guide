# Changelog

## [Unreleased]

## [1.8.6] - 2026-04-22

### Added

- **GitHub issue templates** — bug report, feature request, and platform support request templates with structured triage fields; `config.yml` disables blank issues
- **Pull request template** — contribution checklist covering validation commands, rigor evidence, and human review gate

### Changed

- **Input normalization inlined** — critical normalization steps (workspace resolution, common input types, failure handling) moved from `references/input-normalization.md` into auditing and optimizing SKILL.md; reference file demoted to supplementary edge-case documentation
- **CLAUDE.md expanded** — `.bundles-forge/` runtime output directory added to Directory Layout section
- **Audit report examples consolidated** — replaced dated audit pair (`superpowers-v5.0.7-audit.2026-04-20.md/.zh.md`) with revised GLM 5.1 reports; improved per-skill analysis formatting and scoring transparency

## [1.8.5] - 2026-04-21

### Changed

- **Audit scoring formula updated** — warning penalty now capped per check ID (`capped_warning_penalty = sum(min(count_per_check_id, 3))`), preventing a single noisy check from overwhelming the score
- **`audit_docs.py` D2 enhanced** — cross-reference validation now resolves `<project>:<name>` against both `skills/` directories and `agents/*.md` files, not just skills
- **Optimizing guide expanded** — added Target 7 (Deprecation and Migration) covering skill deprecation, renaming, splitting, merging, and platform cleanup; all "6 targets" references updated to "7 targets"
- **Releasing guide restructured** — inserted Step 4 (Local Testing) between Change Review and Version Bump; steps renumbered 4→5 through 7→8
- **Prerequisites clarified** — README now documents `python` or `python3` with `find_python()` auto-detection instead of requiring only `python`

### Fixed

- **Auditing guide check list corrected** — `audit_skill.py` description updated from `Q1-Q15, S9, X1-X4, C1, G1-G5` to accurate `Q1-Q15, S9, X1-X4`
- **Troubleshooting guide D3/D6 descriptions fixed** — D3 now correctly describes platform manifest sync; D6 correctly describes README sync (previously swapped)
- **Session-start prompt size** — concepts guide updated from ~120 bytes to accurate ~180 bytes

## [1.8.4] - 2026-04-21

### Removed

- **`commands/` directory deleted** — all 8 `/bundles-*` slash command stubs removed; skills are now invoked exclusively via `bundles-forge:<skill-name>` references or automatic description matching
- **Command concept removed from documentation** — "Skill vs Command" distinction, Command row in Key Concepts table, and command-related sections removed from `docs/concepts-guide.md/.zh.md`

### Changed

- **Skill invocation model simplified** — all documentation, guides (EN + ZH), and README files updated from `/bundles-*` slash commands to `bundles-forge:<skill-name>` invocation syntax (e.g. `bundles-forge:auditing`, `bundles-forge:blueprinting`)
- **README "Commands" section → "Invoking Skills"** — command table replaced with concise invocation explanation in both `README.md` and `README.zh.md`
- **Architecture diagrams updated** — Mermaid flowcharts in both READMEs simplified by removing command nodes; flow now starts directly from skill entry points
- **Platform manifests cleaned** — `"commands"` field removed from `.cursor-plugin/plugin.json` and scaffolding Cursor template
- **`audit_docs.py` D6/D7 updated** — D6 no longer checks command table sync; D7 now validates `bundles-forge:<skill-name>` references instead of `/bundles-*` slash commands between EN/ZH guide pairs
- **Auditor agent updated** — report next-step recommendations changed from `/bundles-optimize` to `bundles-forge:optimizing`
- **Scaffolding skill streamlined** — command generation step removed from scaffold pipeline; project anatomy reference removes `commands/` section
- **Testing skill updated** — component discovery checklist no longer includes commands
- **Codex INSTALL.md updated** — symlink instructions no longer reference `commands/` directory
- **Audit report examples added** — `examples/superpowers-v5.0.7-audit.2026-04-20.md` and `.zh.md`

## [1.8.3] - 2026-04-20

### Added

- **`.gitattributes`** — enforces LF for polyglot scripts (`bin/bundles-forge`, hook scripts) and CRLF for `.cmd` wrappers, preventing cross-platform line-ending issues
- **`hooks/session-start` (Bash)** — replaces `session-start.py` for bootstrap injection; dynamically discovers skills by scanning `skills/*/SKILL.md`; uses `printf`-based JSON output to avoid bash 5.3+ heredoc hang
- **`hooks/run-hook.cmd` (polyglot wrapper)** — CMD+Bash polyglot that finds Git for Windows bash on Windows (standard locations + PATH) and runs bash directly on Unix; exits silently if no bash found
- **Audit report examples (GLM 5.1)** — `examples/superpowers-v5.0.7-audit.glm51.md` and `.zh.md` worked audit reports
- **Copilot CLI / SDK standard detection** — `session-start` now emits `{"additionalContext": "..."}` (SDK standard) as fallback for Copilot CLI and unknown platforms, replacing the previous plain-text fallback

### Changed

- **CLI `bin/bundles-forge` hardened** — shell preamble now uses `find_python()` probe that validates interpreter via `--version` before `exec`, skipping Windows Store stubs that masquerade as `python3`
- **`bin/bundles-forge.cmd` rewritten** — Python probe loop tries `python3` then `python` with `--version` validation; clearer error messages with install URL
- **Session-start hook migrated Python → Bash** — `hooks/session-start.py` deleted; new extensionless Bash script with three-way platform detection (CURSOR_PLUGIN_ROOT → Cursor, CLAUDE_PLUGIN_ROOT → Claude Code, COPILOT_CLI/fallback → SDK standard)
- **Hook configs updated** — Claude Code `hooks.json` now invokes `run-hook.cmd session-start`; Cursor `hooks-cursor.json` runs `./hooks/session-start` directly (no Python dependency)
- **Scaffolding templates migrated** — `assets/hooks/session-start.py` replaced by `assets/hooks/session-start` (Bash) + `assets/hooks/run-hook.cmd`; all scaffolding references (`platform-adapters.md`, `project-anatomy.md`, `scaffold-templates.md`, `hooks-configuration.md`, `SKILL.md`) updated
- **Audit checks updated** — H2 now checks for `hooks/session-start` (Bash); new H2b checks for `hooks/run-hook.cmd`; H3/H6/H8/H12/T4 updated for Bash hook terminology
- **Integration tests rewritten** — removed pure-Python simulation tests; bash subprocess tests use `_find_bash()` with Git Bash priority and `@unittest.skipUnless`; added `run-hook.cmd` existence and polyglot format checks; new SDK-standard fallback assertion
- **CLI dispatcher tests enhanced** — `test_polyglot_header_format` → `test_polyglot_format` with assertions for `find_python` probe and `exec "$PYTHON"` pattern
- **Documentation synced** — `AGENTS.md`, `CLAUDE.md`, concepts/scaffolding/troubleshooting guides and their `.zh.md` translations updated for Bash hook migration

### Fixed

- **Manifest version sync** — all platform manifests (`.claude-plugin/plugin.json`, `.claude-plugin/marketplace.json`, `.cursor-plugin/plugin.json`, `gemini-extension.json`) synced to v1.8.3

## [1.8.2] - 2026-04-19

### Added

- **CLI dispatcher test suite** — `TestCLIDispatcher` with 5 tests: `--help` exits 0, no-args shows help, unknown command exits 1, `audit-plugin --json` via dispatcher, polyglot header format validation

### Changed

- **CLI dispatcher polyglot** — `bin/bundles-forge` converted from `#!/usr/bin/env python3` shebang to shell/Python polyglot (`#!/bin/sh` + `'''exec'` line that tries `python3` then `python` via `exec`)
- **Concepts guide updated** — `bin/` section now describes the CLI dispatcher routing subcommands (`audit-skill`, `audit-security`, `audit-plugin`, etc.) to scripts, replacing the "not used" note
- **Auditing SKILL.md streamlined** — plugin context now documents `<plugin-root>` resolution (`$CLAUDE_PLUGIN_ROOT` / `$CURSOR_PLUGIN_ROOT` / `.`); failure handling recommends retry via `bundles-forge` CLI instead of CMD wrapper bypass

## [1.8.1] - 2026-04-19

### Added

- **`--output-dir` CLI flag** — all audit scripts (`audit_plugin`, `audit_docs`, `audit_security`, `audit_skill`, `audit_workflow`) now accept `--output-dir` to save results to a specified directory with timestamped filenames

### Changed

- **Auditing SKILL.md restructured** — Full Project Audit section rewritten as explicit Steps 1-4 (Script Baseline → Dispatch Auditor → Behavioral Verification → Verify Final Report) with Prerequisites, Action, Expected Output, and Failure Handling for each step
- **`audit_workflow.py` standardized** — migrated from manual `argparse` to shared `_cli.py` `make_parser()` for consistent CLI behavior across all scripts
- **Auditor agent updated** — fallback command now includes `--output-dir .bundles-forge/audits` flag

### Fixed

- **Windows CMD wrapper** — `bundles-forge.cmd` now forwards exit codes correctly via `exit /b %ERRORLEVEL%`

## [1.8.0] - 2026-04-19

### Added

- **Comprehensive audit report example** — `examples/superpowers-v5.0.7-audit.md` and `.zh.md` worked audit reports for the superpowers bundle-plugin
- **Plugin context documentation** — auditing SKILL.md now documents workspace resolution when running as an installed plugin (`$CLAUDE_PROJECT_DIR` / `<target-dir>`)
- **Shared finding classification** — `classify_finding_category()` and `count_by_severity()` extracted to `_parsing.py` as shared utilities across audit scripts

### Changed

- **CLI parameter rename** — `project-root` → `target-dir` across all scripts (`_cli.py`, `audit_docs.py`, `audit_plugin.py`, `audit_security.py`, `audit_skill.py`, `audit_workflow.py`, `generate_checklists.py`, `bump_version.py`), SKILL.md files, and documentation
- **Output directory structure** — audit reports now write to `.bundles-forge/audits/`, eval results to `.bundles-forge/evals/`, and inspector reports to `.bundles-forge/blueprints/` (previously all flat under `.bundles-forge/`)
- **`audit_docs.py` refactored** — project metadata detection now uses shared `detect_project_meta()` from `_parsing.py` instead of inline logic (2 occurrences deduplicated)
- **`audit_workflow.py` refactored** — severity counting replaced with shared `count_by_severity()` from `_parsing.py`
- **`audit_skill.py` refactored** — `_classify_finding()` replaced with shared `classify_finding_category()` from `_parsing.py`; severity counting uses shared `count_by_severity()`
- **Documentation synced** — all `docs/` guides (auditing, authoring, cli-reference, concepts, optimizing, releasing) and their `.zh.md` translations updated with new `target-dir` terminology
- **CLAUDE.md** — CLI examples updated from `[project-root]` to `[target-dir]`
- **Agents updated** — `auditor.md`, `evaluator.md`, `inspector.md` aligned with terminology changes

## [1.7.8] - 2026-04-17

### Added

- **2 new test suites** — `test_skill_quality.py` (description format, cross-references, Integration symmetry) and `test_workflow_chains.py` (live project workflow integrity, Calls/Called-by symmetry, graph connectivity); total suites now 6
- **Testing prompt samples** — `tests/prompts/testing.yml` for testing skill trigger evaluation
- **Audit report examples** — `examples/bundles-forge-v1.7.7-audit.md` and `.zh.md` worked audit reports
- **Security triage protocol** — auditor agent now classifies suspicious findings as FP/Accepted/TP with rationale table in report
- **Suspicious Triage table** — added to `plugin-report-template.md` for traceable security disposition
- **New references** — `ab-eval-protocol.md`, `restructuring-operations.md`, `adaptive-mode-questions.md` extracted from skill bodies

### Changed

- **AGENTS.md rewritten** — converted from simple agent guidelines to comprehensive PROJECT KNOWLEDGE BASE format (Codex-compatible)
- **CLAUDE.md streamlined** — condensed Skill Architecture, Session Bootstrap, Agent Dispatch, and Platform Manifests sections; references AGENTS.md for details
- **blueprinting SKILL.md** — extracted adaptive mode questions 4a-7 to `references/adaptive-mode-questions.md`
- **optimizing SKILL.md** — extracted A/B eval protocol and restructuring operations to `references/`; simplified inline content
- **CI matrix expanded** — added Windows (3.12) matrix entry and `audit-workflow` step to `validate-plugin.yml`
- **audit_docs.py** — improved AGENTS.md skill list parsing with fallback from table-based to content scan
- **audit_security.py** — added SC11 `superseded-by:` exclusion; skip `node_modules` in scan

### Fixed

- **README/README.zh.md** — added `python` PATH prerequisite note for systems with only `python3`
- **using-bundles-forge SKILL.md** — added OpenClaw discovery documentation

## [1.7.7] - 2026-04-16

### Added

- **Testing skill** — new `bundles-forge:testing` executor for dynamic plugin verification: dev-marketplace setup, hook smoke tests, component discovery, and cross-platform readiness checks
- **`/bundles-test` command** — slash command stub routing to the testing skill
- **CI workflow** — `.github/workflows/validate-plugin.yml` for automated JSON validation, version/checklist drift, audit, and Python test matrix (3.9 + 3.12)
- **Hooks configuration reference** — `skills/scaffolding/references/hooks-configuration.md` with comprehensive hook authoring guide
- **Deprecation guide** — `skills/optimizing/references/deprecation-guide.md` for safe skill deprecation and migration workflows
- **Platform test guides** — `skills/testing/references/platform-test-guides.md` with per-platform local testing instructions

### Changed

- **Skill count updated to 8** — all project files now reference 8 skills including the new testing skill
- **Release pipeline expanded** — releasing now includes a testing phase between audit and version bump
- **Session bootstrap simplified** — `session-start.py` emits a lightweight one-line prompt; full routing context loaded on demand via the Skill tool
- **Installation instructions updated** — README install steps now use dev-marketplace workflow (`/plugin marketplace add` + `/plugin install`)
- **GitHub organization URL updated** — `odradekai` → `OdradekAI` across README and install docs
- **Using-bundles-forge streamlined** — removed "Red Flags" section; added testing to routing tables and priority order

## [1.7.6] - 2026-04-16

### Added

- **OpenClaw platform support** — 6th platform added; includes `.clawhubignore`, `hooks/openclaw-bootstrap/` hook-pack (HOOK.md + handler.js), scaffolding templates (`assets/platforms/openclaw/`), and `using-bundles-forge/references/openclaw-tools.md` tool mapping
- **OpenClaw installation docs** — `README.md` and `README.zh.md` both include OpenClaw install/verify instructions via `openclaw bundles install`
- **Audit checks H10/H11** — new checklist entries for OpenClaw hook-pack HOOK.md metadata and handler.js ESM conventions

### Changed

- **Platform count updated to 6** — all project files (`AGENTS.md`, `CLAUDE.md`, `README.md`, `README.zh.md`, `concepts-guide.md/.zh.md`, `scaffolding/SKILL.md`, `skill-writing-guide.md`, `platform-adapters.md`) now reference 6 platforms including OpenClaw
- **Platform differences table expanded** — `platform-adapters.md` includes OpenClaw column with discovery, hook format, and skills path info
- **OpenClaw limitation documented** — hook-pack wiring in Claude bundles noted as forward-compatible pending OpenClaw support extension

## [1.7.5] - 2026-04-16

### Changed

- **CLI command references standardized** — all 30 files updated from internal script paths (`audit_plugin.py`, `bump_version.py`, etc.) to `bundles-forge <subcommand>` CLI format across English and Chinese documentation
- **Version tooling decoupled** — `bump_version.py` removed dependency on `_cli.py`/`BundlesForgeError`, uses direct `sys.exit(1)` for self-contained operation; V4 and V8 audit checks removed (no longer needed since scripts aren't bundled per-project)
- **Scaffolding simplified** — `bump_version.py` moved from required core files to optional component; `session-start.py` template now uses `<project-name>` placeholder instead of hardcoded project name

### Fixed

- **Smarter path resolution** — `audit_skill.py` X2 check now resolves relative paths via cross-references before reporting missing paths
- **Generic bootstrap detection** — `audit_docs.py` D1 skill list sync uses `using-*` pattern matching instead of hardcoded `using-bundles-forge`

## [1.7.4] - 2026-04-15

### Added

- **Cross-skill redundancy detection** — `audit_skill.py` C1 check now includes paragraph-hash dedup that detects identical paragraphs across different SKILL.md and references/ files (3+ line threshold, skips auto-generated files)
- **Orphan reference detection (X4)** — `audit_skill.py` new X4 check scans each skill's `references/` directory for `.md` and `.json` files not referenced by `SKILL.md` or sibling reference files
- **Mermaid dependency graph** — `audit_workflow.py` output now includes a `mermaid` field with a Mermaid flowchart of the skill dependency graph (hub/spoke subgraph grouping when layer metadata is available)
- **Unified error handling** — new `BundlesForgeError` exception class in `_cli.py` with `run_main()` wrapper; all scripts now raise exceptions instead of calling `sys.exit()` directly for input validation errors, producing clean error messages without tracebacks
- **New tests** — 31 new tests covering BundlesForgeError, run_main, generate_mermaid, paragraph hash helpers, X4 orphan detection, Mermaid integration, and C1 redundancy (total: 152 tests, up from 121)
- **Input normalization reference** — new `skills/auditing/references/input-normalization.md` canonical reference for path/URL/archive normalization
- **CLI Reference docs** — new `docs/cli-reference.md` and `docs/cli-reference.zh.md` with all subcommands, options, and exit codes
- **Troubleshooting Guide** — new `docs/troubleshooting-guide.md` and `docs/troubleshooting-guide.zh.md` covering common issues and platform-specific problems
- **Python 3.9+ version guard** — CLI dispatcher now exits early with a clear message on older Python versions

### Changed

- **`_graph.run_graph_analysis()`** — now returns `(findings, graph)` tuple instead of just findings, enabling Mermaid generation without redundant graph construction
- **`audit-checks.json`** — added X4 entry; regenerated checklist tables
- **Documentation** — updated `cli-reference.md/.zh.md` and `auditing-guide.md/.zh.md` with X4 and Mermaid features; docs index updated with new reference guides

## [1.7.3] - 2026-04-15

### Changed

- **Blueprinting skill** — renamed pipeline phases to named steps (Scaffold, Author Content, Wire Workflow, Run Audit); moved sufficiency check into Phase 2 checkpoint; added HARD-GATE justification table and quick-mode behavior summary; streamlined Context Exploration with skip-if-answered guidance for Scenario B/C
- **Optimizing skill** — consolidated 8 targets into 6 (merged Token Efficiency + Progressive Disclosure into Content Optimization; removed standalone Platform Coverage — delegates to scaffolding directly); reorganized process into Diagnose → Classify & Route → Apply → Verify
- **Optimizing guides (EN/ZH)** — updated target counts, renumbered all targets, revised scope tables and routing tables
- **Blueprinting guides (EN/ZH)** — aligned pipeline naming with SKILL.md, updated cross-references from numbered targets to named targets
- **README (EN/ZH)** — updated mermaid flowcharts (blueprinting now dispatches to authoring directly), updated optimization target counts and pipeline step names

### Fixed

- **Cross-reference consistency** — all "Target N" references across skills, agents, guides, and READMEs updated to use named targets (e.g., "Skill & Workflow Restructuring target" instead of "Target 7")
- **Quick-mode question count** — blueprinting guides corrected from "3 architecture questions" to "4 architecture questions"

## [1.7.2] - 2026-04-15

### Changed

- **Blueprinting skill** — added over-scoping challenge, immediate contradiction surfacing, assumptions declaration step, and verification gates for each pipeline phase
- **Optimizing skill** — added optimization action classification (FIX/DERIVED/CAPTURED), skill health assessment across four dimensions, and workflow gap detection guidance
- **Blueprinting references** — extracted platform table to `references/platform-reference.md` and advanced component mapping to `references/advanced-components.md`

### Fixed

- **Audit check ID references** — optimizing SKILL.md now correctly cites Q1-Q15 and X1-X3 (was Q1-Q12 and X1-X2) and W1-W4 (was G1-G4)
- **Quick-mode step count** — blueprinting guides (EN/ZH) updated from "3 questions" to "5 steps" to reflect added assumptions declaration and mode selection

## [1.7.1] - 2026-04-14

### Fixed

- **Security scanner false-positive reduction** — `audit_security.py` now distinguishes `skill_reference` files from `skill_content`, downgrading SC1/SC2 from critical to warning in reference docs; HK4 only fires when actual network imports are present; SC12 skips code fences and inline backtick-wrapped references

### Added

- **Comprehensive v1.7.0 audit report** — `examples/bundles-forge-v1.7.0-audit.zh.md` with full 10-category qualitative assessment, false-positive analysis, and fix recommendations
- **Security scanner refinement tests** — 9 new tests in `TestSecurityScannerRefinements` covering `skill_reference` classification, SC1/SC2 downgrade, HK4 network-import gating, and SC12 code-fence/backtick suppression

## [1.7.0] - 2026-04-14

### Added

- **`bin/bundles-forge` CLI dispatcher** — unified cross-platform entry point (`bundles-forge` on Unix, `bundles-forge.cmd` on Windows) routing subcommands (`audit-skill`, `audit-plugin`, `audit-docs`, `audit-security`, `audit-workflow`, `checklists`, `bump-version`) to their Python scripts
- **`docs/index.md` and `docs/index.zh.md`** — bilingual documentation index linking all guides
- **Audit infrastructure modules** — `_graph.py` (skill dependency graph analysis), `_parsing.py` (SKILL.md frontmatter/body parsing), `_scoring.py` (baseline score computation) shared across audit scripts
- **`audit-checks.json` registry** — centralized audit check definitions; `generate_checklists.py` regenerates checklist tables from this single source
- **`plugin-checklist.md`** — generated plugin-level audit checklist
- **`source-of-truth-policy.md`** — defines the hierarchy (skills > agents > docs > CLAUDE.md) and contradiction resolution protocol
- **Blueprinting references** — `composition-analysis.md`, `decomposition-analysis.md`, `design-document-template.md` for structured skill design
- **Releasing references** — `distribution-strategy.md` (platform publish options), `version-infrastructure.md` (`.version-bump.json` schema and setup guide)
- **Python session hook** — `hooks/session-start.py` replaces shell scripts for cross-platform portability (Windows/macOS/Linux)
- **Python test infrastructure** — `tests/run_all.py` test runner, `tests/test_graph_fixtures.py` with 3 fixture suites (circular deps, unreachable skills, missing sections)

### Changed

- **All 7 documentation guides** rewritten for clarity, structure, and consistency across English and Chinese versions
- **All 7 skills** updated — blueprinting three-phase interview flow, auditing script reorganization, releasing reference extraction, scaffolding template sync, authoring quality checklist, optimizing diagnostic improvements
- **Agents** (`auditor`, `inspector`, `evaluator`) updated for script renaming and scoring alignment
- **CLAUDE.md** — added `bin/` to directory layout, corrected platform manifests table, scoped `--json` claim to audit scripts
- **README.md / README.zh.md** — updated CLI command examples, contributing section now requires `checklists --check`
- **Test suite** refactored from shell to Python (`unittest`), consolidated under `tests/`
- **Audit scripts** consolidated from root `scripts/` to `skills/auditing/scripts/`; releasing script moved to `skills/releasing/scripts/`

### Removed

- **Root `scripts/` directory** — `audit_skill.py`, `lint_skills.py`, `_cli.py` moved to `skills/auditing/scripts/`
- **Shell hook scripts** — `hooks/session-start` (bash), `hooks/run-hook.cmd` replaced by `hooks/session-start.py`
- **Shell test scripts** — `test-bootstrap-injection.sh`, `test-skill-discovery.sh`, `test-version-sync.sh` replaced by Python equivalents
- **Old audit examples** — `examples/bundles-forge-v1.5.{1,2,3}-audit{,.zh}.md`
- **`audit-checklist.md`** — replaced by `audit-checks.json` registry and generated checklists

## [1.6.2] - 2026-04-12

### Changed

- **`scripts/scan_security.py` confidence layer** — rules now carry a `confidence` field (`deterministic` or `suspicious`). Context-sensitive regex matches in natural-language content (SKILL.md, references/, agent prompts) are classified as `suspicious` and excluded from scoring and exit codes. Deterministic rules in executable code (hooks, plugins, scripts) remain fully scored. Report output separates suspicious items into a "needs review" section.
- **`scripts/audit_project.py` scoring** — `compute_baseline_score()` filters out suspicious findings; `_flat_findings()` propagates confidence; markdown output adds a "Suspicious (needs review)" section; T8 (missing A/B eval) downgraded from warning to info.
- **`scripts/audit_skill.py` scoring** — `compute_baseline_score()` aligned with audit_project.py to filter suspicious findings.
- **`scripts/check_docs.py` D6 bilingual link comparison** — `.zh.md` suffix now treated as equivalent to `.md` when comparing README link sets, eliminating false asymmetry reports.

### Fixed

- **Security scan false positives** — SEC-001 through SEC-004 (4 critical findings in reference docs) no longer inflate scores or block CI/CD. Root cause: regex patterns matched documentation *about* security risks, not actual risk instructions.

### Added

- **Pure-Python bootstrap tests** — `TestBootstrapInjection` rewritten to simulate hook logic in Python, removing bash dependency. All 5 previously-skipped tests now run on Windows. Original bash tests retained as additional validation when bash is available.
- **Confidence field tests** — 4 new tests in `TestScanSecurity` verify confidence field presence, suspicious exclusion from exit code, and summary structure.
- **`examples/bundles-forge-v1.6.1-audit.zh.md`** — v1.6.1 audit report (Chinese).

## [1.6.1] - 2026-04-12

### Added

- **`docs/authoring-guide.md`** and **`docs/authoring-guide.zh.md`** — user-oriented bilingual guide for the authoring skill covering path selection, writing conventions, agent authoring, validation, and common pitfalls.
- **`examples/bundles-forge-v1.6.0-audit.zh.md`** — v1.6.0 audit report (Chinese).
- **Artifact mapping annotations** in `blueprinting`, `optimizing`, and `releasing` Integration sections — documents how artifact IDs translate between orchestrators and executors (direct match vs indirect mapping).

### Changed

- **`scripts/check_docs.py` D7 check** — replaced hardcoded guide-name exceptions with proper EN→ZH link normalization (`*.md` → `*.zh.md`) for bilingual link comparison.

### Removed

- **`examples/bundles-forge-v1.4.3-audit.zh.md`** — superseded by v1.6.0 audit report.

## [1.6.0] - 2026-04-12

### Removed

- **`skills/porting/` skill deleted** — platform adaptation (add/remove/migrate platforms) merged into `scaffolding`. All assets moved from `skills/porting/assets/` to `skills/scaffolding/assets/platforms/`. References in `platform-adapters.md` relocated to `skills/scaffolding/references/`. Skill count reduced from 8 to 7.
- **`tests/prompts/porting.yml`** — test prompts for the removed skill.

### Added

- **`skills/authoring/SKILL.md` major rewrite** — expanded from a short writing guide into a 4-path execution model (new skill, integrate external, complete stub, improve existing) with entry detection, post-action validation via `lint_skills.py`, agent definition authoring, and three reference files (`skill-writing-guide.md`, `agent-authoring-guide.md`, `quality-checklist.md`).
- **`/bundles-scaffold` command** (`commands/bundles-scaffold.md`) — user-facing entry point for scaffolding, enabling direct project generation and platform adaptation without blueprinting.
- **`scripts/scan_security.py`** — 7-surface security scanner covering SKILL.md content, hook scripts, hook configs (HTTP hooks), OpenCode plugins, agent prompts, bundled scripts, and MCP configs.
- **`scripts/audit_project.py`** — full project audit orchestrator combining `lint_skills`, `scan_security`, and `audit_workflow` with structure, manifest, version sync, hooks, testing, and documentation checks.
- **`docs/scaffolding-guide.md`** and **`docs/scaffolding-guide.zh.md`** — user-oriented guide for the scaffolding skill.
- **`skills/auditing/references/security-checklist.md`** — detailed security pattern list for all 7 attack surfaces.
- **Target 8: Optional Component Management** in `skills/optimizing/SKILL.md` — adding/adjusting userConfig, MCP servers, LSP servers, output styles, and PLUGIN_DATA patterns for maturing projects.
- **`tests/prompts/authoring.yml`** — trigger/non-trigger test prompts for the authoring skill.
- **`tests/test-bootstrap-injection.sh`** — validates session-start hook output.

### Changed

- **Hub-and-spoke architecture model** — skills reorganized into orchestrators (`blueprinting`, `optimizing`, `releasing`), executors (`scaffolding`, `authoring`, `auditing`), and meta-skill (`using-bundles-forge`). Pipeline stages documented consistently across all files.
- **`skills/scaffolding/SKILL.md`** — expanded to include platform adaptation (previously in `porting`): add/remove platforms, manifest updates, hook migration, inspector validation. Now user-invocable via `/bundles-scaffold`.
- **`skills/using-bundles-forge/SKILL.md`** — routing table updated from 8 to 7 skills; replaced flat table with orchestrator/executor/meta sections.
- **Security scanning unified to 7 attack surfaces** across README, auditing-guide, concepts-guide, CLAUDE.md, and `scan_security.py` docstring.
- **Optimization targets unified to 8** across `optimizing/SKILL.md`, optimizing-guide, concepts-guide, and README.
- **`/bundles-*` command count updated to 7** in concepts-guide and Mermaid diagrams.
- **`agents/inspector.md`** — expanded to cover platform adaptation validation in addition to scaffolded structure.
- **All documentation updated** — 7-skill model, no references to `porting` in active documentation. Historical references in `examples/` and `CHANGELOG.md` preserved.
- **Version bumped to 1.6.0** across all synced manifests (`package.json`, `.claude-plugin/plugin.json`, `.claude-plugin/marketplace.json`, `.cursor-plugin/plugin.json`, `gemini-extension.json`).

## [1.5.6] - 2026-04-11

### Added

- **`docs/concepts-guide.md`** — comprehensive concepts guide extracted from README, covering core concepts (Skill, Plugin, Subagent, Hook, MCP), key distinctions, design decisions, and architecture diagrams with links to official Claude documentation.
- **`docs/blueprinting-guide.md`** — user-oriented guide for the blueprinting skill covering scenario selection, interview flow, tips, and troubleshooting.
- **`docs/optimizing-guide.md`** — user-oriented guide for the optimizing skill covering 6 optimization targets, A/B evaluation, feedback iteration, and the audit-optimize cycle.
- **Bilingual documentation** — Chinese translations (`.zh.md`) for all guides: concepts, auditing, releasing, blueprinting, and optimizing.
- **`check_docs.py` D7 check** — guide language sync validation ensuring consistency between English and Chinese guide pairs in `docs/`.

### Changed

- **README.md / README.zh.md** — extracted Key Concepts into a concise summary table linking to `docs/concepts-guide.md`; removed redundant architecture sub-sections (Session Bootstrap, Skill Routing, How Skills Chain, Agent Dispatch) reducing file size by ~82 lines; fixed flowchart labels for precision (`pre-release check`, `platform targets`, `post-adaptation`).
- **`CLAUDE.md`** — added `docs/` directory to layout; updated `check_docs.py` description to 7 checks (D1-D7).
- **`docs/releasing-guide.md`** — updated to reflect D7 check in `check_docs.py` checks table.

## [1.5.5] - 2026-04-11

### Added

- **`scripts/check_docs.py`** — documentation consistency checker with 6 validation checks (D1–D6): skill list sync, cross-reference validity, platform manifest sync, script accuracy, agent list sync, and README data sync.
- **`docs/releasing-guide.md`** — comprehensive human-readable guide to the release pipeline, covering all 8 steps from prerequisites through publishing.

### Changed

- **`skills/releasing/SKILL.md`** — major enhancement: hardened prerequisites (hard/soft requirement split), added Step 0 (prerequisites), Step 3 (documentation sync with change coherence review), CHANGELOG validation rules, and expanded common mistakes table.
- **`CLAUDE.md`** — added `check_docs.py` to commands section and pre-release conventions; clarified platform manifests table with Version-synced column (Codex and OpenCode entries don't carry version strings).
- **`AGENTS.md`** — added `check_docs.py` pre-release instruction.
- **README.md / README.zh.md** — updated releasing skill description and `/bundles-release` flow to include documentation consistency and change coherence review steps.
- **`commands/bundles-release.md`** — updated description to include documentation consistency and change coherence review.
- **`check_docs.py` D3 check** — now respects "Version-synced: No" column in CLAUDE.md platform manifests table, skipping non-version-bearing entries.

## [1.5.4] - 2026-04-11

### Added

- **`agents/auditor.md`** — self-contained 10-category audit executor with full/skill/workflow modes, scoring rules, and report compilation protocol.
- **`agents/evaluator.md`** — single-side A/B skill evaluation runner with chain evaluation support for workflow handoff verification.
- **`agents/inspector.md`** — post-scaffold structural validator for manifests, version sync, hooks, and skill quality.
- **`docs/auditing-guide.md`** — comprehensive guide covering all four audit scopes (full project, single skill, workflow, security-only), their tooling, and CI integration.
- **`scripts/lint_skills.py`** — skill quality linter automating Q1-Q17, S9, X1-X3, and G1-G5 checks with `--json` output and capped warning scoring.
- **`skills/auditing/SKILL.md`** — rewritten with scope auto-detection (project vs skill vs workflow), agent dispatch with inline fallback, and behavioral verification phase.
- **`skills/optimizing/SKILL.md`** — rewritten with 6 optimization targets, scope auto-detection, chain A/B eval, and structured feedback iteration with 3-question validation.
- **`skills/scaffolding/SKILL.md`** — rewritten with minimal/intelligent dual-mode scaffold layers, optional component support, and inspector agent dispatch.
- **`examples/bundles-forge-v1.5.3-audit.zh.md`** — worked audit report example (Chinese) demonstrating the 10-category format.
- **`skills/auditing/references/audit-checklist.md`** — Category 6 (Workflow) placeholder added with pointer to `workflow-checklist.md`, completing the 10-category numbering.

### Changed

- **Category numbering unified to 10 categories** — Workflow is now Category 6; Hooks→7, Testing→8, Documentation→9, Security→10. Updated across `auditing/SKILL.md`, `optimizing/SKILL.md`, `commands/bundles-scan.md`, and `audit-checklist.md`.
- **Scoring formula unified** — `auditor.md` updated from simple `warning × 1` to capped version `capped_warning_penalty = sum(min(count_per_check_id, 3))`, matching `audit-checklist.md` and `workflow-checklist.md`.
- **`AGENTS.md`** — added `using-bundles-forge` to Available Skills table (was listed in count but missing from table).
- **`CLAUDE.md`** — updated architecture documentation with agent dispatch pattern, script inventory, and security rules.

### Fixed

- Category numbering contradiction — Security was referred to as both "Category 9" and "Category 10" across different files; now consistently Category 10.
- `commands/bundles-scan.md` internal contradiction — YAML description said "Category 10" while body said "Category 9"; both now say Category 10.
- `auditor.md` scoring formula mismatch with `audit-checklist.md` — auditor used simple `warning × 1` while checklist used capped version.
- `skills/releasing/SKILL.md` `.version-bump.json` example missing `marketplace.json` entry.
- `audit-checklist.md` total weight unverifiable — listed 9 categories summing to 20 while claiming total = 23; now lists all 10 categories summing to 23.

## [1.5.3] - 2026-04-11

### Added

- **"Key Concepts" section** in both READMEs (en/zh) — explains Skill, Plugin, Subagent, Hook, MCP, Command, Marketplace, LSP Server, and Output Style with Mermaid architecture diagrams showing how they work together in bundles-forge.
- **`maxTurns` limits** on all 3 subagents — auditor (40), evaluator (30), inspector (15) — prevents runaway agent sessions.
- **Step 5b: Behavioral Verification** in `auditing/SKILL.md` — optional evaluator dispatch for W11-W12 chain validation, with two-phase workflow design (auditor handles W1-W10, evaluator handles W11-W12 from parent skill since subagents cannot nest).
- **New audit checks** — T9 (chain eval results), AG7 (subagent nesting detection in agent prompts).
- **Test prompts** — `tests/prompts/` directory with trigger/non-trigger YAML files for all 8 skills.
- **Workflow audit scripts** — `scripts/audit_project.py` and `scripts/audit_workflow.py` now included in the repository.

### Changed

- **Scoring formula** — warnings from the same check ID are now capped at -3 penalty per ID (prevents N skills × -1 multiplicative punishment for a single conceptual gap like missing test prompts). Updated in `audit_project.py`, `audit_workflow.py`, `audit-checklist.md`, and `workflow-checklist.md`.
- **`audit_workflow.py`** — skipped layers now report `None` score instead of defaulting to 10/10; weighted average excludes skipped layers.
- **`auditor.md`** — category weights moved from inline to `audit-checklist.md` reference; W11-W12 behavioral verification delegated to parent skill; report tail uses actionable `/bundles-optimize` command.
- **Audit reports** relocated from `docs/` to `examples/` for clarity.

## [1.5.0] - 2026-04-10

### Added

- **Audit report template system** — six-layer report template (`references/report-template.md`) for full project audits with Go/No-Go decision logic, quantified impact scales, and confidence levels. Separate three-layer template (`references/skill-report-template.md`) for single skill audits.
- **Per-skill breakdown** in audit output — `audit_project.py` markdown reports now include a section with per-skill findings and 4-category score tables; `auditor` agent instructions updated to produce qualitative summaries (Verdict, Strengths, Key Issues) per skill.
- **Evaluator execution observations** — `evaluator` agent reports now include self-reported fields: files referenced, branches taken, unused sections, and estimated info utilization.
- **New lint checks** in `lint_skills.py` — Q13 (token budget enforcement for bootstrap skills), Q14 (`allowed-tools` path validation against actual filesystem), Q15 (conditional block reachability — blocks over 30 lines flagged for extraction to `references/`).
- **Enhanced X3 check** — now validates that prose references to subdirectories (`references/`, `templates/`, etc.) match actual skill directory contents; original X3 (Integration section) renumbered to X4.
- **Auditing documentation** in README (en/zh) — comprehensive section covering Agent-based and script-based audit workflows, scope detection logic, exit codes, and post-audit guidance.
- **Single skill audit mode** in `auditor` agent — 4-category audit with 3-layer report when target is a skill directory instead of a full project.

### Changed

- **`auditing/SKILL.md`** — report step now references the six-layer template instead of inline format; updated check ranges to Q1–Q15 and renumbered cross-reference checks X1–X6.
- **`audit-checklist.md`** — inline report template replaced with pointer to `references/report-template.md`; added Q13–Q15 and X3–X6 check definitions.

## [1.4.3] - 2026-04-09

### Changed

- **`lint_skills.py`** — frontmatter parser now handles YAML block scalars (`|` and `>`), with improved multiline value joining and a rationale comment explaining the zero-dependency design choice.
- **`scan_security.py`** — HK11 regex refined to reduce false positives on common shell redirections (e.g., `>/dev/null`); AG4 (elevated permission claims) now suppresses findings when the line contains negative context (never, do not, prohibited, etc.).
- **`optimizing/SKILL.md`** — A/B evaluation fallback uses randomized execution order (coin flip) to reduce ordering bias when subagents are unavailable.
- **`tests/test-bootstrap-injection.sh`** — platform detection tests upgraded from static `grep` on hook source to runtime output validation (verifies `additional_context` / `hookSpecificOutput` in actual output).

### Added

- **Long session tips** in both READMEs (en/zh) — guidance for managing context accumulation across extended sessions: fresh sessions per lifecycle phase, slash commands for re-anchoring, and script output over inline checks.
- **Clone/download failure handling** in `auditing` and `optimizing` skills — explicit error reporting and user-facing alternatives instead of silent skips.

## [1.4.2] - 2026-04-09

### Changed

- **CLAUDE.md** — comprehensive rewrite with architecture documentation (directory layout, skill lifecycle flow, session bootstrap, agent dispatch), executable commands reference, and key conventions. Replaces the brief contributor guidelines with a full project context file.
- **`bundles-scan` command** — now explicitly describes security-only mode (Category 9 only) instead of generically redirecting to the full audit skill.
- **`hooks/session-start`** — improved error handling: exits with code 1 when bootstrap skill is unreadable instead of silently injecting an error string.
- **`scan_security.py`** — reference markdown files (`references/*.md`) are no longer scanned (documentation, not executable content); scanner self-excludes by absolute-path comparison to avoid false positives on its own source.
- **`auditing/SKILL.md`** — rephrased security checklist table wording to avoid SC2 false positives from the scanner.

### Added

- **Security-only mode** in `auditing` skill — when invoked via `bundles-scan` or explicitly requested, runs only Category 9 (Security) and `scan_security.py`, skipping Categories 1-8.
- **Subagent fallback** in `auditing`, `scaffolding`, and `optimizing` — inline execution path when subagent dispatch is unavailable, with user confirmation prompt.
- **`--dry-run` flag** in `bump_version.py` — preview version bump without writing files.
- **Empty `skills/` directory warning** in `lint_skills.py` — warns when no skill directories are found.
- **Platform removal** section in `porting` skill — step-by-step guide for deprecating platform support.
- **Platform-specific limitations** in `porting/references/platform-adapters.md` — documents Codex bootstrap routing gap and Cursor context-clear re-injection limitation.
- **Safety-boundary exception** in `authoring` — absolute directives (Never/Always) remain appropriate for security gates, version sync, and release pipeline controls.
- **Token efficiency canonical source** cross-reference in `optimizing` — points to `authoring` as the source of truth for token budgets.
- **`test_integration.py`** support in test runner — `run-all.sh` now loops over all Python test files.

## [1.4.1] - 2026-04-09

### Changed

- **Agent renamed** — `reviewer` → `inspector` for post-scaffold validation. "Inspector" better reflects the read-only structural verification role. Updated agent file, scaffolding skill, security checklist, and both READMEs.

### Added

- **Architecture documentation** in README (en/zh) — Agent Dispatch and Command Execution subsections inside the Architecture details block, with mermaid flowcharts showing agent dispatch triggers, command execution chains, and applicable scenarios for each slash command.

## [1.4.0] - 2026-04-09

### Changed

- **Skill naming standardization** — all skill directories now use single-gerund names:
  - `designing` → `blueprinting` (building-metaphor chain with `scaffolding`)
  - `writing-skill` → `authoring`
  - `adapting-platforms` → `porting`
- **Command naming standardization** — all commands now use `bundles-<verb>` prefix for namespace isolation and autocomplete grouping:
  - `/audit-project` → `/bundles-audit`
  - `/blueprint-project` → `/bundles-blueprint`
  - `/optimize-project` → `/bundles-optimize`
  - `/release-project` → `/bundles-release`
  - `/scan-security` → `/bundles-scan`
  - `/use-bundles-forge` → `/bundles-forge`
  Updated command files, README (en/zh) command tables, and all cross-references.

### Fixed

- **Lint false positives on bootstrap skills** — `lint_skills.py` no longer reports missing Overview/Common Mistakes sections (Q10/Q11) for `using-*` bootstrap skills, whose structure intentionally differs from action skills.

## [1.3.3] - 2026-04-09

### Changed

- **Terminology standardization** — "Bundles" → "Bundle-plugin" / "bundle-plugin" across all SKILL.md files, README (en/zh), CLAUDE.md, AGENTS.md, commands, scripts, and references. Establishes "bundle-plugin" as the canonical term.
- **Description length limit** — lowered from 500 to 250 characters across `lint-skills.py`, `audit-checklist.md`, `authoring`, and `optimizing`. Claude Code truncates descriptions beyond 250 chars in the skill listing.
- **All skill descriptions** — rewritten to fit within the 250-character limit while preserving triggering accuracy.
- **`marketplace.json` structure** — `description` moved into `metadata` object to match Claude Code marketplace schema.
- **`package.json` keyword** — `skill-engineering` → `bundle-plugin-engineering`; Claude/Cursor plugin keywords `bundles-engineering` → `bundle-plugin-engineering`.
- **`optimizing` skill** — A/B evaluation now dispatches `evaluator` agents (`agents/evaluator.md`) instead of generic subagents.
- **`scaffolding` skill** — validation now dispatches `reviewer` agent (`agents/reviewer.md`) instead of `scaffold-reviewer`.
- **`auditing` skill** — now references `auditor` agent (`agents/auditor.md`) for automated assessment.

### Added

- **`evaluator` agent** (`agents/evaluator.md`) — runs one side of an A/B skill evaluation for optimization comparisons.
- **Optional Frontmatter Fields** section in `authoring` — documents Claude Code advanced fields: `disable-model-invocation`, `user-invocable`, `allowed-tools`, `context: fork`, `agent`, `argument-hint`, `model`, `effort`, `paths`, `hooks`, `shell`.
- **Claude Code Hook Events** reference in `porting/references/platform-adapters.md` — documents 7 key hook events, hook types, and environment variables (`${CLAUDE_PLUGIN_ROOT}`, `${CLAUDE_PLUGIN_DATA}`).
- **Plugin manifest fields** and **agent restrictions** in platform-adapters reference.
- **`hooks.json` matcher** — added `startup|clear|compact` matcher for `SessionStart` hook.
- **`.gitignore`** — added `.bundles-forge/` pattern for plugin data directory.

### Removed

- **`project-auditor` agent** — replaced by `auditor` (`agents/auditor.md`).
- **`scaffold-reviewer` agent** — replaced by `reviewer` (`agents/reviewer.md`).

## [1.3.2] - 2026-04-09

### Added

- **Minimal/Intelligent dual-mode** in `blueprinting` and `scaffolding` — minimal mode for quick skill packaging (just skills + manifest), intelligent mode for full multi-platform projects with hooks, bootstrap, and version infrastructure.
- **Third-party skill handling** in `blueprinting` — inventory, compatibility analysis, integration intent (repackage vs integrate), and mandatory security audit for imported content.
- **Skill visibility classification** — entry-point skills get matching commands in `commands/`, internal skills are invoked only by other skills in the workflow chain.
- **Advanced components** in `blueprinting` and `scaffolding` — conditional support for `bin/`, `.mcp.json`, `.lsp.json`, `output-styles/`, and `settings.json`.
- **Optional/Advanced components reference** in `scaffolding/references/project-anatomy.md` — documentation for plugin executables, MCP/LSP servers, output styles, settings, userConfig, environment variables, and caching behavior.
- **Commands** for `optimizing` (`bundles-optimize.md`) and `releasing` (`bundles-release.md`) entry-point skills.
- **GitHub Release creation** in `releasing` skill — `gh release create` step after tag push, with fallback to GitHub web UI.

### Changed

- **`using-bundles-forge` routing table** — split into "User Entry Points" (blueprinting, auditing, optimizing, releasing) and "Workflow Skills" (scaffolding, authoring, porting).
- **`scaffolding` description** — rewritten to reflect dual-mode support.
- **`blueprinting` design document template** — now includes mode, visibility column, advanced components, and third-party sources table.

### Removed

- **`commands/scaffold-project.md`** — scaffolding reclassified as workflow skill (invoked by blueprinting, not directly by users).

### Fixed

- **`.gitignore`** — added `__pycache__/` pattern and removed committed `.pyc` files.
- **`.gitignore`** — added missing trailing newline.

## [1.3.1] - 2026-04-08

### Removed

- **Copilot CLI platform support** — removed from all documentation, hooks, manifests, and SKILL.md files. Copilot CLI has no plugin/extension system; this was fictional. Platform count reduced from 6 to 5.
- **`scanning-security` skill** — merged into `auditing` as Category 9 (Security Scan). Security checklist moved to `auditing/references/security-checklist.md`.
- **`iterating-feedback` skill** — merged into `optimizing` as the Feedback Iteration sub-process.
- **`managing-versions` skill** — merged into `releasing` as the Version Management Infrastructure section.
- **`security-scanner` agent** — functionality absorbed by `project-auditor` agent.
- **`package.json` `main` and `type` fields** — misleading for a multi-platform markdown-based project.
- **`hooks.json` `matcher` field** — unnecessary for `SessionStart` hooks per Claude Code docs.

### Changed

- **Skill consolidation: 11 → 8 skills** — three skills absorbed into their natural parents, reducing cognitive load and improving agent routing accuracy.
- **`auditing` skill** — now includes full 5-target security scanning inline, with termination rule (max one re-audit cycle).
- **`optimizing` skill** — now includes feedback iteration workflow with 3-question validation framework.
- **`releasing` skill** — now includes version management infrastructure (`.version-bump.json`, `bump-version.sh` usage).
- **`hooks/session-start`** — simplified platform detection (removed `COPILOT_CLI` branch).
- **`using-bundles-forge` routing table** — updated to 8 skills with revised descriptions and priority order.
- Updated all cross-references: `bundles-forge:scanning-security` → `bundles-forge:auditing`, `bundles-forge:iterating-feedback` → `bundles-forge:optimizing`, `bundles-forge:managing-versions` → `bundles-forge:releasing`.
- Updated README.md and README.zh.md — lifecycle diagram, skill tables, agent list, command mappings.
- Updated `CLAUDE.md` — 5 platforms, 8 skills.
- Updated `AGENTS.md` — expanded from one-line pointer to full quick reference with skill list.
- Updated `project-auditor` agent — now references both quality and security checklists.
- Updated `tests/test-skill-discovery.sh` — expects 8 skills.

### Added

- **"Why Bundles?" section** in both READMEs — concrete explanation of when and why to use the bundles pattern.
- **Python test suite** (`tests/test_scripts.py`) — 12 cross-platform tests covering `lint-skills.py`, `scan-security.py`, `audit-project.py`, and cross-reference integrity.
- **Cycle termination conditions** in `auditing` and `optimizing` to prevent infinite audit-optimize loops.

## [1.3.0] - 2026-04-08

### Changed

- Renamed project from `skill-forge` to `bundles-forge`
- Replaced `skill-project` / `skill-projects` terminology with `bundles` throughout
- Renamed all 11 skill directories:
  - `auditing-skill-projects` → `auditing`
  - `designing-skill-projects` → `designing` → `blueprinting`
  - `optimizing-skill-projects` → `optimizing`
  - `releasing-skill-projects` → `releasing`
  - `scaffolding-skill-projects` → `scaffolding`
  - `adapting-skill-platforms` → `adapting-platforms` → `porting`
  - `iterating-skill-feedback` → `iterating-feedback`
  - `managing-skill-versions` → `managing-versions`
  - `scanning-skill-security` → `scanning-security`
  - `writing-skill-content` → `writing-skill` → `authoring`
  - `using-skill-forge` → `using-bundles-forge`
- Renamed OpenCode plugin file to `bundles-forge.js`
- Renamed command `/use-skill-forge` → `/use-bundles-forge` → `/bundles-forge`
- Updated all repository URLs to `odradekai/bundles-forge`
- Replaced all `skill-forge:` cross-reference prefixes with `bundles-forge:`
- Updated all cross-reference skill names to match new directory names

## [1.2.0] - 2026-04-07

### Added

- New skill: `iterating-skill-feedback` for receiving user feedback about skills, validating suggestions against core goals, forking external skills with identifiers, and automatic post-change auditing
- Scope clarification between `optimizing-skill-projects` (project engineering) and `iterating-skill-feedback` (single-skill effectiveness)

### Changed

- Updated `auditing-skill-projects` integration: added Suggests relationship to `iterating-skill-feedback`
- Updated `optimizing-skill-projects` integration: added Cross-refers relationship to `iterating-skill-feedback`
- Updated `using-skill-forge` routing table, skill priority, and red flags to include the new skill
- Updated workflow diagrams in README to show audit branching into both optimizing and iterating paths

## [1.1.0] - 2026-04-07

### Changed

- Renamed project from `skill-engineering-guide` to `skill-forge`
- Renamed bootstrap skill directory `using-skill-engineering-guide` → `using-skill-forge`
- Renamed OpenCode plugin file to `skill-forge.js`
- Updated all repository URLs to `odradekai/skill-forge`
- Replaced all `seg:` cross-reference prefixes with `skill-forge:`
- Renamed command `/use-seg` → `/use-skill-forge`

### Removed

- Removed project abbreviation `seg` — all references now use the full name `skill-forge`

## [1.0.0] - 2026-04-06

### Added

- Initial release as a structured skill-project
- Refactored from single-skill folder to full plugin architecture following superpowers conventions
- Multi-platform support: Claude Code, Cursor, Codex, OpenCode, Copilot CLI, Gemini CLI
- Platform manifests for all 6 supported platforms
- Session bootstrap hooks with Windows polyglot support
- Version synchronization infrastructure (`.version-bump.json` + `bump-version.sh`)
- **skill-engineering-guide** skill: project scaffolding, auditing, optimization, and platform adaptation
