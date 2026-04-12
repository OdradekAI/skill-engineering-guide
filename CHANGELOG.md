# Changelog

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
