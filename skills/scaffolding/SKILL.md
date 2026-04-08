---
name: scaffolding
description: "Use when generating the initial directory structure, manifests, hooks, scripts, and bootstrap skill for new bundles, creating a bundles project from scratch, or setting up project infrastructure — use after design is complete (invoke bundles-forge:designing first if no design exists)"
---

# Scaffolding Bundles

## Overview

Generate a complete bundles project from a design blueprint. The scaffold includes platform manifests, session hooks, version infrastructure, and skill directories — everything needed for a working multi-platform bundles project.

**Core principle:** Generate only what's needed. Every platform, every file has a reason to exist.

**Announce at start:** "I'm using the scaffolding skill to generate your project."

## Prerequisites

A design document from `bundles-forge:designing` or equivalent information:
- Project name (kebab-case)
- Target platforms
- Skill inventory
- Bootstrap strategy (yes/no)

## Scaffold Layers

Generate only what's needed — layers activate based on the design:

### Always Generated

| File | Purpose |
|------|---------|
| `package.json` | Project identity and version |
| `README.md` | Installation per platform, skill catalog |
| `LICENSE` | Default MIT unless specified |
| `.gitignore` | node_modules, .worktrees, OS files |
| `.version-bump.json` | Version sync manifest |
| `scripts/bump-version.sh` | Version management tool |
| `skills/<skill-name>/SKILL.md` | One directory per skill |

### Per-Platform (only for selected platforms)

| Platform | Files |
|----------|-------|
| Claude Code | `.claude-plugin/plugin.json`, `hooks/hooks.json`, `hooks/session-start`, `hooks/run-hook.cmd` |
| Cursor | `.cursor-plugin/plugin.json`, `hooks/hooks-cursor.json` |
| Codex | `.codex/INSTALL.md`, `AGENTS.md` |
| OpenCode | `.opencode/plugins/<name>.js`, `.opencode/INSTALL.md` |
| Copilot CLI | Shares Claude Code hooks (env detection in `session-start`) |
| Gemini CLI | `gemini-extension.json`, `GEMINI.md` |

### If Bootstrap Skill Requested

| File | Purpose |
|------|---------|
| `skills/using-<project>/SKILL.md` | Meta-skill: instruction priority, skill access, routing table |
| `skills/using-<project>/references/` | Per-platform tool mappings (only for selected platforms) |

## Generation Process

1. **Read template index** — load `references/scaffold-templates.md` for the template inventory and placeholder reference
2. **Read templates** — load the needed template files from `assets/` (infrastructure, docs, bootstrap)
3. **Read platform templates** — for per-platform files, load from `adapting-platforms/assets/<platform>/`
4. **Read anatomy** — load `references/project-anatomy.md` for structure details
5. **Replace placeholders** — substitute `<project-name>`, `<author-name>`, etc.
6. **Generate per-platform** — only create files for target platforms
5. **Generate skill stubs** — one directory per skill from the design
6. **Generate bootstrap** — if requested, create meta-skill with routing table

## Post-Scaffold Checklist

After generating all files:

1. **Initialize git** — `git init`, create initial commit
2. **Verify version sync** — run `scripts/bump-version.sh --check`
3. **Validate manifests** — each platform manifest references correct paths
4. **Test bootstrap** — if created, verify it loads on at least one target platform
5. **Security baseline** — run `bundles-forge:scanning-security` on generated hooks and plugin code
6. **Report** — show the user the generated structure and next steps

Dispatch the `scaffold-reviewer` agent (`agents/scaffold-reviewer.md`) for automated validation if subagents are available.

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

## Integration

**Called by:**
- **bundles-forge:designing** — after design approval

**Calls:**
- **bundles-forge:auditing** — post-scaffold verification
- **bundles-forge:scanning-security** — post-scaffold security baseline

**Pairs with:**
- **bundles-forge:managing-versions** — version infrastructure setup
- **bundles-forge:adapting-platforms** — adding platforms later
