---
name: scaffolding
description: "Use when generating project structure for new bundle-plugins — supports minimal packaging (skills + manifest) and full multi-platform projects with hooks, bootstrap, and version infrastructure. Use after design is complete"
---

# Scaffolding Bundle-Plugins

## Overview

Generate a bundle-plugin project from a design blueprint. Supports two modes: **minimal** (quick packaging of standalone skills) and **intelligent** (full multi-platform project with hooks, bootstrap, and version infrastructure).

**Core principle:** Generate only what's needed. Every platform, every file has a reason to exist.

**Announce at start:** "I'm using the scaffolding skill to generate your project."

## Prerequisites

A design document from `bundles-forge:designing` or equivalent information:
- Project mode (minimal / intelligent)
- Project name (kebab-case)
- Target platforms (minimal mode defaults to Claude Code only)
- Skill inventory (with visibility classification for intelligent mode)
- Bootstrap strategy (yes/no — always no in minimal mode)
- Advanced components list (intelligent mode only)

## Scaffold Layers

Generate only what's needed — layers activate based on the design mode.

### Minimal Mode (quick packaging)

Only generated when design specifies minimal mode. Produces a lean plugin ready for marketplace distribution:

| File | Purpose |
|------|---------|
| `.claude-plugin/plugin.json` | Plugin identity and metadata |
| `skills/<skill-name>/SKILL.md` | One directory per skill |
| `README.md` | Installation instructions and skill catalog |
| `LICENSE` | Default MIT unless specified |

No hooks, no bootstrap, no version infrastructure. Users can add these later via `bundles-forge:adapting-platforms` or by re-running with intelligent mode.

### Intelligent Mode — Core

Generated for all intelligent-mode projects regardless of platform selection:

| File | Purpose |
|------|---------|
| `package.json` | Project identity and version |
| `README.md` | Installation per platform, skill catalog |
| `LICENSE` | Default MIT unless specified |
| `.gitignore` | node_modules, .worktrees, OS files |
| `.version-bump.json` | Version sync manifest |
| `scripts/bump-version.sh` | Version management tool |
| `skills/<skill-name>/SKILL.md` | One directory per skill |
| `commands/<entry-skill>.md` | One command per entry-point skill (from visibility classification) |

### Intelligent Mode — Platform Adapters (only for selected platforms)

| Platform | Files |
|----------|-------|
| Claude Code | `.claude-plugin/plugin.json`, `hooks/hooks.json`, `hooks/session-start`, `hooks/run-hook.cmd` |
| Cursor | `.cursor-plugin/plugin.json`, `hooks/hooks-cursor.json` |
| Codex | `.codex/INSTALL.md`, `AGENTS.md` |
| OpenCode | `.opencode/plugins/<name>.js`, `.opencode/INSTALL.md` |
| Gemini CLI | `gemini-extension.json`, `GEMINI.md` |

### Intelligent Mode — Bootstrap (if requested)

| File | Purpose |
|------|---------|
| `skills/using-<project>/SKILL.md` | Meta-skill: instruction priority, skill access, routing table |
| `skills/using-<project>/references/` | Per-platform tool mappings (only for selected platforms) |

### Intelligent Mode — Optional Components (only if specified in design)

| Component | Files | When to Include |
|-----------|-------|-----------------|
| Executables | `bin/<tool-name>` | Skills reference CLI tools that should be on PATH |
| MCP servers | `.mcp.json` | Skills need external service integration |
| LSP servers | `.lsp.json` | Skills involve language-specific code intelligence |
| Output styles | `output-styles/<style>.md` | Project needs custom output formatting |
| Default settings | `settings.json` | Project should activate a default agent |

## Generation Process

**Minimal mode:**
1. **Create plugin manifest** — generate `.claude-plugin/plugin.json` with project metadata
2. **Generate skill directories** — one directory per skill from the design
3. **Generate README + LICENSE** — minimal docs with skill catalog
4. **Done** — no further steps needed

**Intelligent mode:**
1. **Read template index** — load `references/scaffold-templates.md` for the template inventory and placeholder reference
2. **Read templates** — load the needed template files from `assets/` (infrastructure, docs, bootstrap)
3. **Read platform templates** — for per-platform files, load from `adapting-platforms/assets/<platform>/`
4. **Read anatomy** — load `references/project-anatomy.md` for structure details
5. **Replace placeholders** — substitute `<project-name>`, `<author-name>`, etc.
6. **Generate per-platform** — only create files for target platforms
7. **Generate skill stubs** — one directory per skill from the design
8. **Generate commands** — one command file per entry-point skill
9. **Generate bootstrap** — if requested, create meta-skill with routing table
10. **Generate optional components** — create any advanced component files specified in the design

## Post-Scaffold Checklist

**Minimal mode:**
1. **Initialize git** — `git init`, create initial commit
2. **Validate manifest** — confirm `.claude-plugin/plugin.json` is valid JSON with correct name
3. **Report** — show the user the generated structure and next steps

**Intelligent mode:**
1. **Initialize git** — `git init`, create initial commit
2. **Verify version sync** — run `scripts/bump-version.sh --check`
3. **Validate manifests** — each platform manifest references correct paths
4. **Test bootstrap** — if created, verify it loads on at least one target platform
5. **Security baseline** — run `bundles-forge:auditing` on generated hooks and plugin code
6. **Report** — show the user the generated structure and next steps

Dispatch the `reviewer` agent (`agents/reviewer.md`) for automated validation if subagents are available.

## Quick Reference: Placeholder Map

| Placeholder | Source |
|-------------|--------|
| `<project-name>` | Design: project name |
| `<Project Name>` | Title-cased project name |
| `<author-name>` | User or git config |
| `<author-email>` | User or git config |
| `<repo-url>` | User-provided or constructed |
| `<one-line description>` | From design or user |

## Common Mistakes

| Mistake | Fix |
|---------|-----|
| Generating all platforms regardless of design | Only create files for selected platforms |
| Forgetting `.version-bump.json` entries for new platforms | Every version-bearing manifest needs an entry |
| Hardcoding author in templates | Pull from git config or ask |
| Missing `run-hook.cmd` for Windows | Always include if any hook-based platform is targeted |
| Bootstrap skill > 200 lines | Keep lean — extract to `references/` |
| Forgetting `chmod +x` on scripts | Note in post-scaffold checklist |
| Using intelligent mode infrastructure for minimal projects | Minimal mode exists to avoid over-engineering |
| Forgetting commands for entry-point skills | Each entry-point skill gets a matching command file |
| Generating optional components not in the design | Only create what the design document specifies |

## Integration

**Called by:**
- **bundles-forge:designing** — after design approval

**Calls:**
- **bundles-forge:auditing** — post-scaffold verification
**Pairs with:**
- **bundles-forge:releasing** — version infrastructure setup
- **bundles-forge:adapting-platforms** — adding platforms later
