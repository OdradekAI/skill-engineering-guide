# Scaffold Templates

Index of ready-to-use template files for generating new bundle-plugins. All templates live in `assets/` — read each file directly when generating.

Replace all placeholders before writing to the target project.

## Placeholder Reference

| Placeholder | Source |
|-------------|--------|
| `<project-name>` | Design or existing project name (kebab-case) |
| `<Project Name>` | Title-cased project name |
| `<author-name>` | User or git config |
| `<author-email>` | User or git config |
| `<repo-url>` | User-provided or constructed |
| `<one-line description>` | From design or user |

---

## Template Inventory

### Infrastructure (always generated)

| Template File | Target Path | Purpose |
|---------------|-------------|---------|
| `assets/hooks/session-start` | `hooks/session-start` | Bootstrap injection script (Bash; shared across Claude Code, Cursor) |
| `assets/hooks/run-hook.cmd` | `hooks/run-hook.cmd` | Cross-platform polyglot wrapper (CMD+Bash; finds bash on Windows) |
| `assets/root/version-bump.json` | `.version-bump.json` | Version sync config (adapt `files` array to target platforms) |
| `assets/root/gitignore` | `.gitignore` | Standard ignores |
| `assets/root/package.json` | `package.json` | Project identity (omit `main` if OpenCode not targeted) |

### Documentation (always generated)

| Template File | Target Path | Purpose |
|---------------|-------------|---------|
| `assets/root/README.md` | `README.md` | Project README (adapt sections per target platforms) |

### Bootstrap Skill (if bootstrap requested)

| Template File | Target Path | Purpose |
|---------------|-------------|---------|
| `assets/root/using-skill.md` | `skills/using-<project-name>/SKILL.md` | Meta-skill: instruction priority, skill routing table |

### Optional Components (if specified in design)

| Template File | Target Path | Purpose |
|---------------|-------------|---------|
| `assets/scripts/bump_version.py` | `scripts/bump_version.py` | Standalone version sync tool for CI (not needed if using `bundles-forge` CLI) |
| `assets/mcp-json.md` | `.mcp.json` | MCP server definitions (choose transport from template variants) |
| `assets/.github/workflows/validate-plugin.yml` | `.github/workflows/validate-plugin.yml` | CI validation workflow (JSON manifests, version drift, skill quality, security) |

### Platform Adapters

Platform-specific manifest templates live in `assets/platforms/`. Use those when generating per-platform files (plugin.json, hooks.json, etc.). The Claude Code `hooks.json` template includes a top-level `description` (use `<Project Name>` placeholder) and per-handler `timeout: 10`.

| Template File | Target Path | Purpose |
|---------------|-------------|---------|
| `assets/platforms/codex/AGENTS.md` | `AGENTS.md` | Codex pointer to CLAUDE.md (only if Codex targeted) |
| `assets/platforms/gemini/GEMINI.md` | `GEMINI.md` | Gemini CLI context file (only if Gemini targeted) |

---

## Generation Notes

- **Hooks:** Claude Code template uses `run-hook.cmd session-start`; Cursor runs `./hooks/session-start` directly (see `assets/platforms/*/hooks*.json`)
- **`.version-bump.json`:** only include entries for platforms that have version-bearing manifest files
- **`package.json`:** omit the `main` field if OpenCode is not a target platform
- **Bootstrap skill:** keep under 200 lines — extract heavy content to `references/`
