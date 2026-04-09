# Changelog

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
