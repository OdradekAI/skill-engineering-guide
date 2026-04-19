---
name: scaffolding
description: "Use when generating project structure for new bundle-plugins, adding or removing platform support (Claude Code, Cursor, Codex, OpenCode, Gemini CLI, OpenClaw), updating platform manifests, or migrating hooks and configuration between platforms"
allowed-tools: Bash(bundles-forge bump-version *)
---

# Scaffolding Bundle-Plugins

## Overview

Generate new bundle-plugin projects and manage platform support across their lifecycle. Handles initial project generation (greenfield) and ongoing platform adaptation (add, fix, migrate, remove).

**Core principle:** Generate only what's needed. Every platform, every file has a reason to exist. This skill generates structure only — it does not run its own scripts. Validation is delegated to `bundles-forge:auditing`; version checks to `bundles-forge bump-version`.

**Skill type:** Hybrid — follow the generation/adaptation process rigidly, but mode selection and component choices are flexible based on user context.

**Announce at start:** "I'm using the scaffolding skill to [generate your project / add <platform> support / remove <platform> support / add <component> / remove <component>]."

## Entry Detection

Determine the operation based on context:

1. **Design document provided** (from `bundles-forge:blueprinting`) → **New Project** flow
2. **User request + no existing project** → **New Project** flow
3. **User request + existing project** → **Platform Adaptation** flow (add / fix / migrate / remove)

## New Project: Scaffold Layers

For new projects, first select a mode:
- **Design document** specifies the mode (minimal or intelligent)
- **Direct invocation** — choose between:
  - **intelligent** — recommend architecture based on user description, avoid unnecessary components
  - **custom** — present the full architecture option set, ask the user about each component

### Minimal Mode (quick packaging)

Lean plugin for marketplace distribution:

| File | Purpose |
|------|---------|
| `.claude-plugin/plugin.json` | Plugin identity and metadata |
| `skills/<skill-name>/SKILL.md` | One directory per skill |
| `README.md` | Installation instructions and skill catalog |
| `LICENSE` | Default MIT unless specified |

No hooks, no bootstrap, no version infrastructure. Add these later by re-running scaffolding in platform adaptation mode.

### Intelligent Mode

#### Core

Generated for all intelligent-mode projects regardless of platform selection:

| File | Purpose |
|------|---------|
| `package.json` | Project identity and version |
| `README.md` | Installation per platform, skill catalog |
| `LICENSE` | Default MIT unless specified |
| `.gitignore` | node_modules, .worktrees, OS files |
| `.version-bump.json` | Version sync manifest |
| `skills/<skill-name>/SKILL.md` | One directory per skill |
| `commands/<entry-skill>.md` | One command per entry-point skill |

#### Platform Adapters (selected platforms only)

| Platform | Files |
|----------|-------|
| Claude Code | `.claude-plugin/plugin.json`, `hooks/hooks.json`, `hooks/run-hook.cmd`, `hooks/session-start` |
| Cursor | `.cursor-plugin/plugin.json`, `hooks/hooks-cursor.json`, `hooks/session-start` |
| Codex | `.codex/INSTALL.md`, `AGENTS.md` |
| OpenCode | `.opencode/plugins/<name>.js`, `.opencode/INSTALL.md` |
| Gemini CLI | `gemini-extension.json`, `GEMINI.md` |

For platform-specific wiring details, read `references/platform-adapters.md`.

#### Bootstrap (if requested)

| File | Purpose |
|------|---------|
| `skills/using-<project>/SKILL.md` | Meta-skill: instruction priority, skill routing table |
| `skills/using-<project>/references/` | Per-platform tool mappings |

#### Optional Components (only if specified)

| Component | Files | When to Include |
|-----------|-------|-----------------|
| Executables | `bin/<tool-name>` | Skills reference CLI tools (see `references/external-integration.md` decision tree) |
| MCP servers | `.mcp.json` | Skills need external service integration (see `references/external-integration.md` decision tree) |
| LSP servers | `.lsp.json` | Skills involve language-specific code intelligence (see `references/external-integration.md` LSP section) |
| Output styles | `output-styles/<style>.md` | Custom output formatting (see `references/external-integration.md` Output Styles section) |
| Default settings | `settings.json` | Default agent activation (see `references/external-integration.md` Default Settings section) |
| User configuration | `userConfig` in `plugin.json` | Skills need user-provided API keys, endpoints, or tokens — Claude Code only (see `references/external-integration.md` userConfig section) |
| Marketplace entry | `.claude-plugin/marketplace.json` | Plugin targets marketplace distribution — declares plugin metadata for the marketplace index |

## New Project: Generation Process

**Minimal mode:**
1. Create plugin manifest from `assets/platforms/claude-code/plugin.json` template
2. Generate skill directories — one per skill
3. Generate README + LICENSE
4. `git init` + initial commit; validate manifest JSON

**Intelligent mode:**

*Phase 1 — Load context:*
1. **Read template index** — load `references/scaffold-templates.md`
2. **Read templates** — load from `assets/` (infrastructure, docs, bootstrap)
3. **Read platform templates** — load from `assets/platforms/<platform>/`
4. **Read anatomy** — load `references/project-anatomy.md`

*Phase 2 — Generate:*
5. **Replace placeholders** — substitute `<project-name>`, `<author-name>`, etc.
6. **Generate per-platform** — only create files for target platforms
7. **Generate skill stubs** — one directory per skill
8. **Generate commands** — one command per entry-point skill
9. **Generate bootstrap** — if requested, create meta-skill with routing table
10. **Generate optional components** — only what the design specifies. For MCP servers, use `assets/mcp-json.md` template and consult `references/external-integration.md` for transport selection and platform differences. When `userConfig` is specified, add the `userConfig` field to `plugin.json` with appropriate `sensitive` flags. When marketplace distribution is specified, generate `.claude-plugin/marketplace.json` with plugin metadata. When CI validation is specified, generate `.github/workflows/validate-plugin.yml` from template

*Phase 3 — Finalize:*
11. `git init` + initial commit; run `bundles-forge bump-version --check`

## Platform Adaptation: Existing Projects

### Adding a Platform

1. **Detect current platforms** — scan for existing manifests (see detection table in `references/platform-adapters.md`)
2. **Identify target** — read `references/platform-adapters.md` for wiring details
3. **Generate adapter files** — from `assets/platforms/<platform>/`, replace `<project-name>` placeholders
4. **Update version sync** — add version-bearing manifests to `.version-bump.json`
5. **Update hooks** — if platform uses session hooks, ensure `session-start` (Bash) handles its JSON format via `run-hook.cmd`. For custom hooks beyond SessionStart, read `references/hooks-configuration.md`
6. **Update documentation** — add install section to README; create platform-specific docs if needed
7. **Verify** — validate manifests, `bundles-forge bump-version --check`, test hooks

### Removing a Platform

1. **Delete manifest files** — remove the platform's manifest directory or file
2. **Update `.version-bump.json`** — remove entries for deleted manifests
3. **Clean hooks** — delete platform-specific hook files; simplify `session-start` if branches removed
4. **Update documentation** — remove install section from README and platform-specific docs
5. **Verify** — `bundles-forge bump-version --check`; run inspector validation

### Adding Optional Components

Add MCP servers, CLI executables, LSP servers, userConfig, output styles, or default settings to an existing project:

1. **Determine component type** — read `references/external-integration.md` decision tree to choose the right integration level
2. **Generate component files** — create the corresponding file(s) at their default location (`.mcp.json`, `.lsp.json`, `output-styles/`, `settings.json`, or `userConfig` in `plugin.json`)
3. **Update plugin manifests** — add component declarations to `plugin.json` for platforms that require explicit paths (Cursor). For Claude Code, convention-based discovery handles most components automatically
4. **Update skill references** — add `allowed-tools` frontmatter for new CLI/MCP tools, add `${user_config.KEY}` references where skills need user-provided values
5. **Update README** — add setup instructions for the new component (especially MCP server config for non-Claude Code platforms, LSP binary installation)
6. **Verify** — run inspector validation to confirm structural integrity

### Removing Optional Components

Remove MCP servers, CLI executables, or LSP servers from an existing project. Read `references/external-integration.md` "Optional Component Removal" section for step-by-step instructions covering:

- Removing MCP servers (`.mcp.json`, `plugin.json mcpServers`, skill references, README)
- Removing CLI executables (`bin/`, `allowed-tools`, skill body)
- Removing LSP servers (`.lsp.json`, README)
- Downgrading MCP to CLI (replace MCP with lighter CLI alternative)

## Post-Action Validation

**Step 1 — Deterministic checks (script):** Run `bundles-forge audit-skill <target-dir>` to verify structure, manifests, version sync, and frontmatter. Review any critical or warning findings before proceeding.

**Step 2 — Semantic inspection (agent):** Dispatch the `inspector` agent (`agents/inspector.md`) for semantic validation that scripts cannot cover (template quality, hook logic coherence, design alignment). The inspector adjusts scope based on context:
- **New project** → full inspection (template quality, optional components, hook semantics, design coherence)
- **Platform adaptation** → focused inspection (hook semantics and template quality for affected platforms)

**If subagent dispatch is unavailable:** Ask — "Subagents are not available. Run validation inline?" If confirmed, read `agents/inspector.md` and follow its instructions within this conversation, then report PASS/FAIL.

## Common Mistakes

| Mistake | Fix |
|---------|-----|
| Generating all platforms regardless of design | Only create files for selected platforms |
| Forgetting `.version-bump.json` entries | Every version-bearing manifest needs an entry |
| Hardcoding author in templates | Pull from git config or ask |
| Missing `session-start` or `run-hook.cmd` in hook config | Claude Code uses `run-hook.cmd session-start`; Cursor runs `./hooks/session-start` directly; both require bash |
| Bootstrap skill > 200 lines | Keep lean — extract to `references/` |
| Wrong hook format (PascalCase vs camelCase) | Claude Code: `SessionStart`, Cursor: `sessionStart` |
| Copying template without customizing | Replace every `<project-name>` placeholder |
| Using intelligent mode infrastructure for minimal | Minimal mode avoids over-engineering |
| Using MCP when CLI suffices | Consult `references/external-integration.md` decision tree — prefer CLI for stateless, single-shot tools |
| Using `../` paths to reference files outside the plugin | After marketplace install, plugins are cached — `../` paths break. Keep all files within the plugin root |
| Writing persistent data to `${CLAUDE_PLUGIN_ROOT}` | `PLUGIN_ROOT` changes on each update. Use `${CLAUDE_PLUGIN_DATA}` for caches, installed dependencies, and generated state |

## Inputs

- `design-document` (optional) — from `bundles-forge:blueprinting` with project mode, name, platforms, skill inventory, bootstrap strategy, and components
- `project-directory` (optional) — existing bundle-plugin project root for platform adaptation
- `target-platform` (optional) — platform to add or remove

## Outputs

- `scaffold-output` — generated project structure or adapted platform files. Consumed by the orchestrating skill (blueprinting or optimizing) for subsequent phases
- `inspector-report` (optional) — validation report in `.bundles-forge/blueprints/`

## Integration

**Called by:**
- **bundles-forge:blueprinting** — Phase 1 of the new-project pipeline
- **bundles-forge:optimizing** — Platform Coverage routing for adding new platforms
- User directly — for platform adaptation or ad-hoc project generation

**Pairs with:**
- **bundles-forge:releasing** — version infrastructure and sync
